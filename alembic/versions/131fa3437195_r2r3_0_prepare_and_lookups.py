"""radar 2 -> radar 3, step 0: radar3 schema and lookup tables

Creates the radar3 schema, then creates and fills the lookup tables later steps
point at: data_source, front_page_stat, identifier, indicator, option, sample_type.

Radar 2 is left untouched in the public schema. Every radar 3 table is created
from its radar_models.radar3 model in the radar3 schema. Rows are read from radar 2
with SQL, checked against the model with model_validate, then added with the session.

option holds every radar 2 enum value, plus every {label, value} from the "options"
arrays in the radar 2 form definitions (public.forms.data), grouped by form and
field: <form slug>.<field name>, e.g. ddls.extraInvolvement, plus radar 2's
antibodies under the group "antibody".

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
    DataSource,
    FrontPageStat,
    Identifier,
    Indicator,
    Option,
    SampleType,
    Relation,
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
ANTIBODY_OPTION_GROUP = "antibody"  # radar 2's antibodies, in option


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
        if (key in seen) or (enum_name in [SAMPLE_TYPE_ENUM,"antibody_type_enum"]):
            continue
        seen.add(key)
        session.add(
            Option.model_validate(
                {"option_group": key[0], "display_label": value, "store_value": value}
            )
        )
    session.flush()


def form_option_group(slug: str, field_name: str | None) -> str:
    """ddls + extraInvolvement -> ddls.extraInvolvement, as named in radar 2"""
    return f"{slug}.{field_name}" if field_name else slug


def seed_form_options(session: Session) -> None:
    """option rows: every {label, value} in every "options" array of every form.

    One query over all of public.forms. The recursive node query walks every
    value in forms.data, at any depth (object members and array elements). Every
    node that is an object with an "options" array (normally a field, so its
    "name" gives the group) has its options unpacked with jsonb_array_elements.

    Uses only jsonb_each, jsonb_array_elements and jsonb_typeof, so it runs on
    PostgreSQL 9.4+ (jsonb_path_query would need 12+).
    """
    rows = session.execute(
        text("""
        WITH RECURSIVE node (slug, value) AS (
            SELECT f.slug, f.data
            FROM public.forms AS f
          UNION ALL
            SELECT n.slug, child.value
            FROM node AS n
            CROSS JOIN LATERAL (
                SELECT member.value
                FROM jsonb_each(
                    CASE WHEN jsonb_typeof(n.value) = 'object'
                         THEN n.value ELSE '{}'::jsonb END
                ) AS member
              UNION ALL
                SELECT element.value
                FROM jsonb_array_elements(
                    CASE WHEN jsonb_typeof(n.value) = 'array'
                         THEN n.value ELSE '[]'::jsonb END
                ) AS element (value)
            ) AS child
        )
        SELECT
            n.slug,
            n.value ->> 'name' AS field_name,
            o.option ->> 'value' AS store_value,
            o.option ->> 'label' AS display_label
        FROM node AS n
        CROSS JOIN LATERAL jsonb_array_elements(
            CASE WHEN jsonb_typeof(n.value -> 'options') = 'array'
                 THEN n.value -> 'options' ELSE '[]'::jsonb END
        ) WITH ORDINALITY AS o (option, position)
        WHERE jsonb_typeof(n.value) = 'object'
        ORDER BY n.slug, field_name, o.position
    """)
    ).all()

    missing = [
        f"{slug}.{field_name}: {store_value!r} / {display_label!r}"
        for slug, field_name, store_value, display_label in rows
        if store_value is None or display_label is None
    ]
    if missing:
        raise ValueError(
            "form options without a value or label:\n" + "\n".join(missing)
        )

    seen: set[tuple[str, str]] = set()
    for slug, field_name, store_value, display_label in rows:
        key = (form_option_group(slug, field_name), store_value)
        if key in seen:
            continue
        seen.add(key)
        session.add(
            Option.model_validate(
                {
                    "option_group": key[0],
                    "display_label": display_label,
                    "store_value": store_value,
                }
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
    """option rows in group "antibody": radar 2's antibodies.

    The string id is both the label and the stored value. radar 2's is_official
    flag is not kept: option has no column for it.
    """
    antibody_ids = session.execute(
        text("SELECT id FROM public.antibodies ORDER BY id")
    ).scalars()

    session.add_all(
        [
            Option.model_validate(
                {
                    "option_group": ANTIBODY_OPTION_GROUP,
                    "display_label": antibody_id,
                    "store_value": antibody_id,
                }
            )
            for antibody_id in antibody_ids
        ]
    )
    session.flush()

def seed_relation(session: Session) -> None:
    RELATIONSHIPS=[
        (1, "Mother"),
        (2, "Father"),
        (3, "Sister"),
        (4, "Brother"),
        (5, "Grandmother - Maternal"),
        (6, "Grandmother - Paternal"),
        (15, "Grandfather - Maternal"),
        (16, "Grandfather - Paternal"),
        (7, "Aunt - Maternal"),
        (8, "Aunt - Paternal"),
        (9, "Uncle - Maternal"),
        (10, "Uncle - Paternal"),
        (11, "Cousin - Maternal"),
        (12, "Cousin - Paternal"),
        (13, "Half Sister"),
        (14, "Half Brother"),
        (17, "Daughter"),
        (18, "Son"),
        (19, "Granddaughter"),
        (20, "Grandson"),
    ]


    rows = [
        {"id": code, "relation_label": label} for code, label in RELATIONSHIPS
    ]

    session.add_all([Relation.model_validate(dict(row)) for row in rows])
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
        Relation.__table__.create(bind)

        with Session(bind=bind) as session:
            seed_data_sources(session)
            seed_identifiers(session)
            seed_indicators(session)
            seed_options(session)
            seed_form_options(session)
            seed_samples(session)
            seed_antibodies(session)
            seed_relation(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")