"""radar 2 -> radar 3, step 0: radar3 schema and lookup tables

Creates the radar3 schema, then creates and fills the lookup tables later steps
point at: data_source, front_page_stat, identifier, indicator, option, sample_type,
antibody_option.

Radar 2 is left untouched in the public schema. Every radar 3 table is created
from its radar_models.radar3 model in the radar3 schema. Rows are read from radar 2
with SQL, checked against the model with model_validate, then added with the session.

One-way migration.

Revision ID: 131fa3437195
Revises: a22849217d2c
Create Date: 2026-11-03

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlmodel import Session

from radar_models.radar3 import (
    AntibodyOption,
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
SAMPLE_TYPE_ENUM = "observation_sample_type"  # seeds sample_type, not option


def seed_data_sources(session: Session) -> None:
    """data_source rows: every source_type radar 2 used, plus the app's constants."""
    used = "\nUNION ".join(
        f"SELECT source_type FROM public.{t}" for t in SOURCE_TYPE_TABLES
    )
    names = set(session.execute(text(used)).scalars())
    names.update(APP_SOURCE_TYPES)
    names.discard(None)

    session.add_all(
        [
            DataSource.model_validate({"data_source_name": name})
            for name in sorted(names)
        ]
    )
    session.flush()


def seed_identifiers(session: Session) -> None:
    """identifier rows: radar 2's OTHER groups, keeping their group ids."""
    rows = session.execute(
        text("""
        SELECT id, code AS identifier_label
        FROM public.groups
        WHERE type = 'OTHER'
        ORDER BY id
    """)
    ).mappings()

    session.add_all([Identifier.model_validate(dict(row)) for row in rows])
    session.flush()

    # ids were copied, so move the sequence past them
    session.execute(
        text("""
        SELECT setval(
            pg_get_serial_sequence('radar3.identifier', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.identifier),
            false
        )
    """)
    )


def seed_indicators(session: Session) -> None:
    """indicator rows: every indication used in radar 2."""
    rows = session.execute(
        text("""
        SELECT DISTINCT indications AS indicator_label
        FROM public.liver_transplants
        WHERE indications IS NOT NULL
        ORDER BY indicator_label
    """)
    ).mappings()

    session.add_all([Indicator.model_validate(dict(row)) for row in rows])
    session.flush()


def seed_options(session: Session) -> None:
    """option rows: every value of every radar 2 enum with enum or type in its name."""
    rows = session.execute(
        text("""
        SELECT t.typname AS enum_name, e.enumlabel AS enum_value
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
          AND (t.typname ILIKE '%enum%' OR t.typname ILIKE '%type%')
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
        if (key in seen) or (enum_name == SAMPLE_TYPE_ENUM):
            continue
        seen.add(key)
        session.add(
            Option.model_validate(
                {"option_group": key[0], "display_label": value, "store_value": value}
            )
        )
    session.flush()


def seed_samples(session: Session) -> None:
    """sample_type rows: the values of radar 2's sample type enum."""
    rows = session.execute(
        text("""
        SELECT e.enumlabel AS sample_type_label
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typname = :enum_name
        ORDER BY sample_type_label
    """),
        {"enum_name": SAMPLE_TYPE_ENUM},
    ).mappings()

    session.add_all([SampleType.model_validate(dict(row)) for row in rows])
    session.flush()


def seed_antibodies(session: Session) -> None:
    """antibody_option rows: radar 2's antibodies (string id becomes the label)."""
    rows = session.execute(
        text("""
        SELECT id AS antibody_label, is_official
        FROM public.antibodies
        ORDER BY id
    """)
    ).mappings()

    session.add_all([AntibodyOption.model_validate(dict(row)) for row in rows])
    session.flush()


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("CREATE SCHEMA radar3"))

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        DataSource.__table__.create(bind)
        FrontPageStat.__table__.create(bind)
        Identifier.__table__.create(bind)
        Indicator.__table__.create(bind)
        Option.__table__.create(bind)
        SampleType.__table__.create(bind)
        AntibodyOption.__table__.create(bind)

        with Session(bind=bind) as session:
            seed_data_sources(session)
            seed_identifiers(session)
            seed_indicators(session)
            seed_options(session)
            seed_samples(session)
            seed_antibodies(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")