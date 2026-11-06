"""radar 2 -> radar 3: organisation tables

Copies radar 2's organisation data into radar3, keeping every radar 2 id:

    specialty            <- specialties (all rows)
    consultant           <- consultants (all rows)
    hospital             <- groups (type = 'HOSPITAL'), group id kept as hospital id
    hospital_consultant  <- group_consultants on HOSPITAL groups
    cohort               <- groups (type = 'COHORT'), group id kept as cohort id
    consent              <- consents (all rows)

Hospitals and cohorts keep their radar 2 group ids, so any radar 2 group_id maps
straight to a hospital or cohort id. After each copy the table's id sequence is
moved past the copied ids.

Every row is read from radar 2 and validated against its model before anything
is created, so a row that does not fit stops the migration with every bad row
from every table listed, and nothing is half-copied.

[D1] radar 2 NULLs in the true/false columns (consents.paediatric,
consents.retired, groups.is_transplant_centre) become false.
[D6] radar 2 columns with no radar 3 home are dropped: see each query.

Needs the radar3 schema (step 0, 131fa3437195).

One-way migration.

Revision ID: b39e4dc2ac81
Revises: 9aaa2a094682
Create Date: 2026-11-06 16:09:25.253553

"""

import logging
from collections.abc import Sequence
from typing import NamedTuple

from alembic import op
from pydantic import ValidationError
from sqlalchemy import text
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


class Copy(NamedTuple):
    model: type[SQLModel]  # the radar 3 table
    sql: str  # its radar 2 rows, each column already named as the model's field


# In foreign key order: specialty before consultant, hospital and consultant
# before hospital_consultant.
COPIES = [
    Copy(
        Specialty,
        """
        SELECT id, name AS specialty_name
        FROM public.specialties
        ORDER BY id
        """,
    ),
    Copy(
        Consultant,
        """
        SELECT
            id, specialty_id, first_name, last_name,
            email, telephone_number, gmc_number
        FROM public.consultants
        ORDER BY id
        """,
    ),
    Copy(
        Hospital,
        # [D6] dropped: type (the row filter), instructions, multiple_diagnoses,
        # is_recruitment_number_group, parent_group_id, country_code
        """
        SELECT
            id,
            code AS hospital_code,
            name AS hospital_name,
            short_name AS hospital_short_name,
            COALESCE(is_transplant_centre, false) AS is_transplant_centre  -- [D1]
        FROM public.groups
        WHERE type = 'HOSPITAL'
        ORDER BY id
        """,
    ),
    Copy(
        HospitalConsultant,
        # rows on non-hospital groups have no home: see warn_dropped_consultants
        """
        SELECT gc.id, gc.group_id AS hospital_id, gc.consultant_id
        FROM public.group_consultants AS gc
        JOIN public.groups AS g ON g.id = gc.group_id
        WHERE g.type = 'HOSPITAL'
        ORDER BY gc.id
        """,
    ),
    Copy(
        Cohort,
        # [D6] dropped: type (the row filter), instructions, multiple_diagnoses,
        # is_recruitment_number_group, parent_group_id, is_transplant_centre,
        # country_code
        """
        SELECT
            id,
            code AS cohort_code,
            name AS cohort_name,
            short_name AS cohort_short_name
        FROM public.groups
        WHERE type = 'COHORT'
        ORDER BY id
        """,
    ),
    Copy(
        Consent,
        # [D6] dropped: consent_type, weight
        """
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
        """,
    ),
]


def read_rows(bind, copy: Copy) -> tuple[list[SQLModel], list[str]]:
    """One table's radar 2 rows as validated models, and an error per bad row."""
    rows = []
    errors = []
    for row in bind.execute(text(copy.sql)).mappings():
        try:
            rows.append(copy.model.model_validate(dict(row)))
        except ValidationError as error:
            errors.append(f"{copy.model.__tablename__} id {row['id']}: {error}")
    return rows, errors


def warn_dropped_consultants(bind) -> None:
    """Logs the group_consultants rows on non-hospital groups, which are not copied."""
    rows = bind.execute(
        text("""
        SELECT g.type, count(*)
        FROM public.group_consultants AS gc
        JOIN public.groups AS g ON g.id = gc.group_id
        WHERE g.type <> 'HOSPITAL'
        GROUP BY g.type
        ORDER BY g.type
    """)
    )
    for group_type, count in rows:
        log.warning(
            "group_consultants: %d rows on %s groups not copied (no radar 3 home)",
            count,
            group_type,
        )


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


def upgrade() -> None:
    bind = op.get_bind()

    # read and validate every row first, so nothing is created if any row does
    # not fit; every bad row from every table is listed in one run
    rows: dict[type[SQLModel], list[SQLModel]] = {}
    errors = []
    for copy in COPIES:
        rows[copy.model], copy_errors = read_rows(bind, copy)
        errors += copy_errors
    if errors:
        raise ValueError(
            f"{len(errors)} radar 2 rows do not fit their radar 3 model:\n"
            + "\n".join(errors)
        )
    warn_dropped_consultants(bind)

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for copy in COPIES:
            copy.model.__table__.create(bind)

        with Session(bind=bind) as session:
            for copy in COPIES:
                session.add_all(rows[copy.model])
                session.flush()
                reset_sequence(session, copy.model.__tablename__)
                log.info(
                    "%s: %d rows copied",
                    copy.model.__tablename__,
                    len(rows[copy.model]),
                )
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")