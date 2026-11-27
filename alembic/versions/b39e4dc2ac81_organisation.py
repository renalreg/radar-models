"""radar 2 -> radar 3: organisation tables
One-way migration.

Revision ID: b39e4dc2ac81
Revises: 9aaa2a094682
Create Date: 2026-11-06 16:09:25.253553
"""

import logging
from collections.abc import Iterable, Sequence

from alembic import op
from pydantic import ValidationError
from sqlalchemy import RowMapping, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    Cohort,
    Consent,
    Consultant,
    Hospital,
    HospitalConsultant,
    Specialty,
)

# revision identifiers, used by Alembic.
revision: str = "b39e4dc2ac81"
down_revision: str | Sequence[str] | None = "9aaa2a094682"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")


def validated(model: type[SQLModel], rows: Iterable[RowMapping]) -> list[SQLModel]:
    """Each radar 2 row checked against the model; raises listing every bad row."""
    valid = []
    errors = []
    for row in rows:
        try:
            valid.append(model.model_validate(dict(row)))
        except ValidationError as error:
            errors.append(f"{model.__tablename__} id {row['id']}: {error}")
    if errors:
        raise ValueError(
            f"{len(errors)} radar 2 rows do not fit {model.__name__}:\n"
            + "\n".join(errors)
        )
    return valid


def reset_sequence(session: Session, table_name: str) -> None:
    """The ids were copied, so move the table's id sequence past them."""
    session.execute(
        text(f"""
        SELECT setval(
            pg_get_serial_sequence('radar3.{table_name}', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.{table_name}),
            false
        )
    """)
    )


def copy_specialty(session: Session) -> None:
    rows = session.execute(
        text("""
        SELECT id, name AS specialty_name
        FROM public.specialties
        ORDER BY id
    """)
    ).mappings()

    session.add_all(validated(Specialty, rows))
    session.flush()
    reset_sequence(session, "specialty")


def copy_consultant(session: Session) -> None:
    rows = session.execute(
        text("""
        SELECT
            id, specialty_id, first_name, last_name,
            email, telephone_number, gmc_number
        FROM public.consultants
        ORDER BY id
    """)
    ).mappings()

    session.add_all(validated(Consultant, rows))
    session.flush()
    reset_sequence(session, "consultant")


def copy_hospital(session: Session) -> None:
    # [D6] dropped: type (the row filter), instructions, multiple_diagnoses,
    # is_recruitment_number_group, parent_group_id, country_code
    rows = session.execute(
        text("""
        SELECT
            id,
            code AS hospital_code,
            name AS hospital_name,
            short_name AS hospital_short_name,
            COALESCE(is_transplant_centre, false) AS is_transplant_centre  -- [D1]
        FROM public.groups
        WHERE type = 'HOSPITAL'
        ORDER BY id
    """)
    ).mappings()

    session.add_all(validated(Hospital, rows))
    session.flush()
    reset_sequence(session, "hospital")


def copy_hospital_consultant(session: Session) -> None:
    # group_id -> hospital_id unchanged, as hospital kept the group ids
    rows = session.execute(
        text("""
        SELECT gc.id, gc.group_id AS hospital_id, gc.consultant_id
        FROM public.group_consultants AS gc
        JOIN public.groups AS g ON g.id = gc.group_id
        WHERE g.type = 'HOSPITAL'
        ORDER BY gc.id
    """)
    ).mappings()

    session.add_all(validated(HospitalConsultant, rows))
    session.flush()
    reset_sequence(session, "hospital_consultant")

    # rows on non-hospital groups have no home in radar 3
    dropped = session.execute(
        text("""
        SELECT g.type, count(*)
        FROM public.group_consultants AS gc
        JOIN public.groups AS g ON g.id = gc.group_id
        WHERE g.type <> 'HOSPITAL'
        GROUP BY g.type
        ORDER BY g.type
    """)
    )
    for group_type, count in dropped:
        log.warning(
            "group_consultants: %d rows on %s groups not copied (no radar 3 home)",
            count,
            group_type,
        )


def copy_cohort(session: Session) -> None:
    # [D6] dropped: type (the row filter), instructions, multiple_diagnoses,
    # is_recruitment_number_group, parent_group_id, is_transplant_centre,
    # country_code
    rows = session.execute(
        text("""
        SELECT
            id,
            code AS cohort_code,
            name AS cohort_name,
            short_name AS cohort_short_name
        FROM public.groups
        WHERE type = 'COHORT'
        ORDER BY id
    """)
    ).mappings()

    session.add_all(validated(Cohort, rows))
    session.flush()
    reset_sequence(session, "cohort")


def copy_consent(session: Session) -> None:
    # [D6] dropped: consent_type, weight
    rows = session.execute(
        text("""
        SELECT
            id,
            code AS consent_code,
            label AS consent_label,
            COALESCE(paediatric, false) AS is_paediatric,  -- [D1]
            from_date AS release_date,
            link_url AS consent_url,
            COALESCE(retired, false) AS is_retired  -- [D1]
        FROM public.consents
        ORDER BY id
    """)
    ).mappings()

    session.add_all(validated(Consent, rows))
    session.flush()
    reset_sequence(session, "consent")


def upgrade() -> None:
    bind = op.get_bind()

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        # parents before children: consultant points at specialty, and
        # hospital_consultant at hospital and consultant
        Specialty.__table__.create(bind)
        Consultant.__table__.create(bind)
        Hospital.__table__.create(bind)
        HospitalConsultant.__table__.create(bind)
        Cohort.__table__.create(bind)
        Consent.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_specialty(session)
            copy_consultant(session)
            copy_hospital(session)
            copy_hospital_consultant(session)
            copy_cohort(session)
            copy_consent(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
