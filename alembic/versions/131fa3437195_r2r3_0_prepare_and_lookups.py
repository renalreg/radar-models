"""radar 2 -> radar 3, step 0: Save and drop the radar 2 views, then create and fill the lookup tables (data_source, relation, indicator, option, sample_type, cohort, hospital, identifier) that later steps point at.

Revision ID: 131fa3437195
Revises: a22849217d2c
Create Date: 2026-11-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text
from sqlmodel import Session

from alembic import op
from radar_models.radar3 import (
    DataSource,
    FrontPageStat,
    Identifier,
    Indicator,
    Option,
    SampleType,
)

# revision identifiers, used by Alembic.
revision: str = "131fa3437195"
down_revision: str | Sequence[str] | None = "a22849217d2c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# radar 2 tables with a source_type column: their distinct values seed data_source
SOURCE_TYPE_TABLES = [
    "current_medications",
    "dialysis",
    "fetal_anomaly_scans",
    "fetal_ultrasounds",
    "hospitalisations",
    "india_ethnicities",
    "liver_imaging",
    "liver_transplants",
    "medications",
    "nephrectomies",
    "nutrition",
    "pathology",
    "patient_addresses",
    "patient_aliases",
    "patient_demographics",
    "patient_diagnoses",
    "patient_numbers",
    "plasmapheresis",
    "renal_imaging",
    "results",
    "rituximab_baseline_assessment",
    "transplants",
]
APP_SOURCE_TYPES = ("RADAR", "UKRDC", "BATCH")  # radar.models.source_types


def run(sql: str) -> sa.CursorResult:
    """Execute SQL on the migration connection."""
    return op.get_bind().execute(sa.text(sql))


def save_and_drop_radar2_views() -> None:
    """Views would block the column type changes: save their SQL, then drop them."""
    run(
        "CREATE TABLE r2r3_radar2_views (view_name text PRIMARY KEY, kind text NOT NULL, definition text NOT NULL)"
    )
    run("""
        INSERT INTO r2r3_radar2_views
        SELECT c.relname, CASE c.relkind WHEN 'm' THEN 'MATERIALIZED VIEW' ELSE 'VIEW' END, pg_get_viewdef(c.oid)
        FROM pg_class AS c
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = current_schema() AND c.relkind IN ('v', 'm')
          AND NOT EXISTS (SELECT 1 FROM pg_depend AS d WHERE d.objid = c.oid AND d.deptype = 'e')
    """)
    for name, kind in run(
        "SELECT view_name, kind FROM r2r3_radar2_views ORDER BY view_name"
    ).all():
        run(f"DROP {kind} IF EXISTS {name} CASCADE")


def seed_data_sources(session) -> None:
    """data_source rows: every source_type radar 2 used, plus the app's constants."""
    used = "\nUNION ".join(f"SELECT source_type FROM {t}" for t in SOURCE_TYPE_TABLES)
    names = set(session.execute(text(used)).scalars())
    names.update(APP_SOURCE_TYPES)
    names.discard(None)

    session.add_all(DataSource(data_source_name=name) for name in sorted(names))
    session.flush()


def seed_identifiers(session) -> None:
    rows = session.execute(
        text("SELECT id, code FROM groups WHERE type = 'OTHER' ORDER BY id")
    ).all()

    session.add_all(
        Identifier(id=group_id, identifier_label=code) for group_id, code in rows
    )
    session.flush()


def seed_indicators(session: Session) -> None:
    """indicator rows: every indication used in radar 2."""
    indications = session.execute(
        text(
            "SELECT DISTINCT indications FROM liver_transplants WHERE indications IS NOT NULL"
        )
    ).scalars()

    session.add_all(Indicator(indicator_label=label) for label in sorted(indications))
    session.flush()


def seed_options(session: Session) -> None:
    """option rows: every value of every radar 2 enum with enum or type in its name."""
    rows = session.execute(
        text("""
        SELECT t.typname AS enum_name, e.enumlabel AS enum_value
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname ILIKE '%enum%'
           OR t.typname ILIKE '%type%'
        ORDER BY t.typname, e.enumsortorder
    """)
    ).all()

    def enum_to_option_group(enum_name: str) -> str:
        """lesion_location_enum -> lesion_location, enum_sex_type -> sex"""
        parts = [p for p in enum_name.split("_") if p.lower() not in ("enum", "type")]
        return "_".join(parts) or enum_name

    seen: set[tuple[str, str]] = set()
    for enum_name, value in rows:
        key = (enum_to_option_group(enum_name), value)
        if (key in seen) or ("sample" in key):
            continue
        seen.add(key)
        session.add(Option(option_group=key[0], display_label=value, store_value=value))

    session.flush()


def seed_samples(session: Session) -> None:
    samples = session.execute(
        text("""
        SELECT e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        WHERE t.typname == 'observation_sample_type'
        ORDER BY t.typname, e.enumsortorder
    """)
    ).scalars()

    session.add_all(SampleType(sample_type_label=label) for label in sorted(samples))
    session.flush()


def upgrade() -> None:
    # drop views
    bind = op.get_bind()
    save_and_drop_radar2_views()
    DataSource.__table__.create(bind)
    FrontPageStat.__table__.create(bind)
    Identifier.__table__.create(bind)
    Indicator.__table__.create(bind)
    Option.__table__.create(bind)
    SampleType.__table__.create(bind)

    with Session(bind=bind) as session:
        seed_data_sources(session)
        seed_identifiers(session)
        seed_indicators(session)
        seed_options(session)
        seed_samples(session)

    pass


def downgrade() -> None:
    """Downgrade schema."""
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3 geography.")
