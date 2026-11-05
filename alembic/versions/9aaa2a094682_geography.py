"""radar 2 -> radar 3, step 1: geography tables

Creates the radar 3 geography tables in the radar3 schema from their models and
copies radar 2's rows into them. Rows are read from radar 2 with SQL, checked
against the model with model_validate, then added with the session. Radar 2's
tables are left as they are.

    countries             -> country              new ids; code -> country_code
    ethnicities           -> ethnicity            ids kept
    nationalities         -> nationality          ids kept
    country_ethnicities   -> country_ethnicity    ids kept; country_code -> country_id
    country_nationalities -> country_nationality  ids kept; country_code -> country_id

radar 2 keys countries by their 2-letter code. Later steps that point at a country
join radar3.country on country_code to get its new id.

One-way migration.

Revision ID: 9aaa2a094682
Revises: 131fa3437195
Create Date: 2026-11-03
"""

from alembic import op
from sqlalchemy import text
from sqlmodel import Session

from radar_models.radar3 import (
    Country,
    CountryEthnicity,
    CountryNationality,
    Ethnicity,
    Nationality,
)

revision = "9aaa2a094682"
down_revision = "131fa3437195"
branch_labels = None
depends_on = None


def copy_country(session: Session) -> None:
    rows = session.execute(
        text("""
        SELECT code AS country_code, label AS country_name
        FROM public.countries
        ORDER BY code
    """)
    ).mappings()

    session.add_all([Country.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_ethnicity(session: Session) -> None:
    rows = session.execute(
        text("""
        SELECT id, code AS ethnicity_code, label AS ethnicity_label
        FROM public.ethnicities
        ORDER BY id
    """)
    ).mappings()

    session.add_all([Ethnicity.model_validate(dict(row)) for row in rows])
    session.flush()

    # ids were copied, so move the sequence past them
    session.execute(
        text("""
        SELECT setval(
            pg_get_serial_sequence('radar3.ethnicity', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.ethnicity),
            false
        )
    """)
    )


def copy_nationality(session: Session) -> None:
    rows = session.execute(
        text("""
        SELECT id, label AS nationality_label
        FROM public.nationalities
        ORDER BY id
    """)
    ).mappings()

    session.add_all([Nationality.model_validate(dict(row)) for row in rows])
    session.flush()

    # ids were copied, so move the sequence past them
    session.execute(
        text("""
        SELECT setval(
            pg_get_serial_sequence('radar3.nationality', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.nationality),
            false
        )
    """)
    )


def copy_country_ethnicity(session: Session) -> None:
    # country_id comes from the radar3.country rows copied above
    rows = session.execute(
        text("""
        SELECT ce.id, ce.ethnicity_id, c.id AS country_id
        FROM public.country_ethnicities AS ce
        LEFT JOIN radar3.country AS c ON c.country_code = ce.country_code
        ORDER BY ce.id
    """)
    ).mappings()

    session.add_all([CountryEthnicity.model_validate(dict(row)) for row in rows])
    session.flush()

    # ids were copied, so move the sequence past them
    session.execute(
        text("""
        SELECT setval(
            pg_get_serial_sequence('radar3.country_ethnicity', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.country_ethnicity),
            false
        )
    """)
    )


def copy_country_nationality(session: Session) -> None:
    # country_id comes from the radar3.country rows copied above
    rows = session.execute(
        text("""
        SELECT cn.id, cn.nationality_id, c.id AS country_id
        FROM public.country_nationalities AS cn
        LEFT JOIN radar3.country AS c ON c.country_code = cn.country_code
        ORDER BY cn.id
    """)
    ).mappings()

    session.add_all([CountryNationality.model_validate(dict(row)) for row in rows])
    session.flush()

    # ids were copied, so move the sequence past them
    session.execute(
        text("""
        SELECT setval(
            pg_get_serial_sequence('radar3.country_nationality', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.country_nationality),
            false
        )
    """)
    )


def upgrade() -> None:
    bind = op.get_bind()

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        # parents before children: the link tables point at country,
        # ethnicity and nationality
        Country.__table__.create(bind)
        Ethnicity.__table__.create(bind)
        Nationality.__table__.create(bind)
        CountryEthnicity.__table__.create(bind)
        CountryNationality.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_country(session)
            copy_ethnicity(session)
            copy_nationality(session)
            copy_country_ethnicity(session)
            copy_country_nationality(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")