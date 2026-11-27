"""radar 2 -> radar 3: posts, cohort diagnoses, diagnosis codes, ins relapses

Copies posts, group_diagnoses, diagnosis_codes and ins_relapses into radar3
with new ids, each row checked with its model. A cohort diagnosis's type
(PRIMARY, SECONDARY) becomes an option in DIAGNOSIS_TYPE_GROUP; group_diagnoses
rows on non-cohort groups are not copied, and their count is logged as a
warning.

[D1] radar 2 NULLs in the true/false columns become false.
[D6] radar 2 columns with no radar 3 home are dropped: see each query.

One-way migration.

Revision ID: 37b72cbd4103
Revises: 46cad851886e
Create Date: 2026-11-27 15:55:00.000000
"""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from alembic import op
from sqlalchemy import Column, select, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import CohortDiagnosis, DiagnosisCode, InsRelapse, Option, Post

# revision identifiers, used by Alembic.
revision: str = "37b72cbd4103"
down_revision: str | Sequence[str] | None = "46cad851886e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

DIAGNOSIS_TYPE_GROUP = "cohort-diagnosis.type"

# radar 2's group_diagnosis_type: store value -> display label
DIAGNOSIS_TYPES = {"PRIMARY": "Primary", "SECONDARY": "Secondary"}


def utc(timestamp: datetime | None, column: Column) -> datetime | None:
    """A radar 2 timestamptz as UTC, with a zone if the radar 3 column takes one."""
    if timestamp is None:
        return None
    in_utc = timestamp.astimezone(UTC)
    return in_utc if column.type.timezone else in_utc.replace(tzinfo=None)


def add_copies(
    session: Session, model: type[SQLModel], copies: list, radar2_table: str
) -> None:
    """Adds copies, which get new ids."""
    session.add_all(copies)
    session.flush()
    log.info(
        "%s: %s rows copied from %s",
        model.__tablename__,
        f"{len(copies):,}",
        radar2_table,
    )


def load_options(session: Session) -> dict[tuple[str, str], int]:
    """Every option's id, by option group and store value."""
    return {
        (option_group, store_value): option_id
        for option_group, store_value, option_id in session.execute(
            select(Option.option_group, Option.store_value, Option.id)
        )
    }


def add_options(
    session: Session,
    options: dict[tuple[str, str], int],
    group: str,
    labels: dict[str, str],
) -> None:
    """Adds labels to option in group, skipping any already there."""
    added = [
        Option.model_validate(
            {"option_group": group, "display_label": label, "store_value": value}
        )
        for value, label in labels.items()
        if (group, value) not in options
    ]
    session.add_all(added)
    session.flush()
    options.update({(o.option_group, o.store_value): o.id for o in added})
    log.info(
        "option: %d added to %s, %d already there",
        len(added),
        group,
        len(labels) - len(added),
    )


def copy_post(session: Session) -> None:
    """Copies posts to post."""
    rows = session.execute(
        text("""
        SELECT posts.id, posts.title, posts.published_date, posts.body
        FROM public.posts
        ORDER BY posts.published_date, posts.id
    """)
    ).mappings()
    published_date = Post.__table__.c.published_date
    add_copies(
        session,
        Post,
        [
            Post.model_validate(
                {
                    "post_title": row["title"],
                    "published_date": utc(row["published_date"], published_date),
                    "post_body": row["body"],
                }
            )
            for row in rows
        ],
        "posts",
    )


def copy_cohort_diagnosis(
    session: Session, options: dict[tuple[str, str], int]
) -> None:
    """Copies group_diagnoses on COHORT groups to cohort_diagnosis."""
    # [D6] dropped: weight
    rows = session.execute(
        text("""
        SELECT
            group_diagnoses.id,
            group_diagnoses.group_id,
            group_diagnoses.diagnosis_id,
            group_diagnoses.type
        FROM public.group_diagnoses
        JOIN public.groups ON groups.id = group_diagnoses.group_id
        WHERE groups.type = 'COHORT'
        ORDER BY group_diagnoses.group_id, group_diagnoses.weight, group_diagnoses.id
    """)
    ).mappings()
    add_copies(
        session,
        CohortDiagnosis,
        [
            CohortDiagnosis.model_validate(
                {
                    "cohort_id": row["group_id"],  # cohort kept the group ids
                    "diagnosis_id": row["diagnosis_id"],  # diagnosis kept its ids
                    "option_id": options[DIAGNOSIS_TYPE_GROUP, row["type"]],
                }
            )
            for row in rows
        ],
        "group_diagnoses",
    )

    # rows on non-cohort groups have no home in radar 3
    dropped = session.execute(
        text("""
        SELECT groups.type, count(*)
        FROM public.group_diagnoses
        JOIN public.groups ON groups.id = group_diagnoses.group_id
        WHERE groups.type <> 'COHORT'
        GROUP BY groups.type
        ORDER BY groups.type
    """)
    )
    for group_type, count in dropped:
        log.warning(
            "group_diagnoses: %d rows on %s groups not copied (no radar 3 home)",
            count,
            group_type,
        )


def copy_diagnosis_code(session: Session) -> None:
    """Copies diagnosis_codes to diagnosis_code."""
    rows = session.execute(
        text("""
        SELECT diagnosis_codes.id, diagnosis_codes.diagnosis_id, diagnosis_codes.code_id
        FROM public.diagnosis_codes
        ORDER BY diagnosis_codes.diagnosis_id, diagnosis_codes.id
    """)
    ).mappings()
    add_copies(
        session,
        DiagnosisCode,
        [
            DiagnosisCode.model_validate(
                {
                    "diagnosis_id": row["diagnosis_id"],  # diagnosis kept its ids
                    "code_id": row["code_id"],  # code kept its ids
                }
            )
            for row in rows
        ],
        "diagnosis_codes",
    )


def copy_ins_relapse(session: Session) -> None:
    """Copies ins_relapses to ins_relapse."""
    rows = session.execute(
        text("""
        SELECT
            relapse.id,
            relapse.patient_id,
            relapse.date_of_relapse,
            relapse.kidney_type,
            relapse.viral_trigger,
            relapse.immunisation_trigger,
            relapse.other_trigger,
            COALESCE(relapse.high_dose_oral_prednisolone, false) AS high_dose_oral_prednisolone,  -- [D1]
            COALESCE(relapse.iv_methyl_prednisolone, false) AS iv_methyl_prednisolone,  -- [D1]
            relapse.date_of_remission,
            relapse.remission_type,
            relapse.peak_acr,
            relapse.peak_pcr,
            relapse.remission_acr,
            relapse.remission_pcr,
            relapse.peak_protein_dipstick,
            relapse.remission_protein_dipstick,
            COALESCE(relapse.relapse_sample_taken, false) AS relapse_sample_taken  -- [D1]
        FROM public.ins_relapses AS relapse
        ORDER BY relapse.patient_id, relapse.date_of_relapse, relapse.id
    """)
    ).mappings()
    add_copies(
        session,
        InsRelapse,
        [
            InsRelapse.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "date_of_relapse": row["date_of_relapse"],
                    "kidney_type": row["kidney_type"],
                    "viral_trigger": row["viral_trigger"],
                    "immunisation_trigger": row["immunisation_trigger"],
                    "other_trigger": row["other_trigger"],
                    "has_high_dose_oral_prednisolone": row[
                        "high_dose_oral_prednisolone"
                    ],
                    "has_iv_methyl_prednisolone": row["iv_methyl_prednisolone"],
                    "date_of_remission": row["date_of_remission"],
                    "remission_type": row["remission_type"],
                    "peak_acr": row["peak_acr"],
                    "peak_pcr": row["peak_pcr"],
                    "remission_acr": row["remission_acr"],
                    "remission_pcr": row["remission_pcr"],
                    "peak_protein_dipstick": row["peak_protein_dipstick"],
                    "remission_protein_dipstick": row["remission_protein_dipstick"],
                    "is_relapse_sample_taken": row["relapse_sample_taken"],
                }
            )
            for row in rows
        ],
        "ins_relapses",
    )


def upgrade() -> None:
    bind = op.get_bind()

    # model tables go to radar3; raw SQL names public.<table> itself
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in (Post, CohortDiagnosis, DiagnosisCode, InsRelapse):
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            options = load_options(session)
            add_options(session, options, DIAGNOSIS_TYPE_GROUP, DIAGNOSIS_TYPES)
            copy_post(session)
            copy_cohort_diagnosis(session, options)
            copy_diagnosis_code(session)
            copy_ins_relapse(session)
    finally:
        # Alembic records the version on this connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
