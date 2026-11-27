"""radar 2 -> radar 3: nurture metadata, salt wasting, observation links

Copies nurture_data, salt_wasting_clinical_features and group_observations
into radar3 with new ids, each row checked with its model, and links each
observation to its options and PV code:

    observations.options  (code, description pairs) -> option, observation_option
    observations.pv_code  -> code (coding_system PV), observation_code

group_observations rows on non-cohort groups are not copied, and their count is
logged as a warning. sample_inventory is created empty: radar 2 has no table
for it.

[D1] radar 2 NULLs in the true/false columns become false.

One-way migration.

Revision ID: 6d974c4f7164
Revises: 37b72cbd4103
Create Date: 2026-11-27 16:30:00.000000
"""

import logging
from collections.abc import Sequence

from alembic import op
from sqlalchemy import select, text
from sqlmodel import Session, SQLModel, col

from radar_models.radar3 import (
    Code,
    CohortObservation,
    NurtureMetadata,
    ObservationCode,
    ObservationOption,
    Option,
    SaltWastingClinicalFeature,
    SampleInventory,
)

# revision identifiers, used by Alembic.
revision: str = "6d974c4f7164"
down_revision: str | Sequence[str] | None = "37b72cbd4103"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

# radar 2 sends pv_code to the UKRDC with sda_coding_standard PV
PV_CODING_SYSTEM = "PV"


def observation_group(observation_id: int) -> str:
    """The option group of an observation's options."""
    return f"observation.{observation_id}"


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


def copy_nurture_metadata(session: Session) -> None:
    """Copies nurture_data to nurture_metadata."""
    rows = session.execute(
        text("""
        SELECT
            nurture.id,
            nurture.patient_id,
            nurture.signed_off_state,
            nurture.follow_up_refused_date,
            nurture.blood_tests,  
            nurture.blood_refused_date,
            nurture.interviews,  
            nurture.interviews_refused_date
        FROM public.nurture_data AS nurture
        ORDER BY nurture.patient_id, nurture.id
    """)
    ).mappings()
    add_copies(
        session,
        NurtureMetadata,
        [
            NurtureMetadata.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "signed_off_state_index": row["signed_off_state"],
                    "follow_up_refused_date": row["follow_up_refused_date"],
                    "has_blood_tests": row["blood_tests"],
                    "blood_refused_date": row["blood_refused_date"],
                    "has_interviews": row["interviews"],
                    "interviews_refused_date": row["interviews_refused_date"],
                }
            )
            for row in rows
        ],
        "nurture_data",
    )


def copy_salt_wasting(session: Session) -> None:
    """Copies salt_wasting_clinical_features to salt_wasting_clinical_feature."""
    rows = session.execute(
        text("""
        SELECT
            salt.id,
            salt.patient_id,
            salt.normal_pregnancy,  
            salt.abnormal_pregnancy_text,
            salt.neurological_problems,  
            salt.seizures,  
            salt.abnormal_gait,  
            salt.deafness,  
           salt.other_neurological_problem,  
            salt.other_neurological_problem_text,
            salt.joint_problems,  
            salt.joint_problems_age,
            salt.x_ray_abnormalitiess,  
            salt.chondrocalcinosis,  
            salt.other_x_ray_abnormality,  
            salt.other_x_ray_abnormality_text
        FROM public.salt_wasting_clinical_features AS salt
        ORDER BY salt.patient_id, salt.id
    """)
    ).mappings()
    add_copies(
        session,
        SaltWastingClinicalFeature,
        [
            SaltWastingClinicalFeature.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "is_normal_pregnancy": row["normal_pregnancy"],
                    "abnormal_pregnancy_text": row["abnormal_pregnancy_text"],
                    "has_neurological_problems": row["neurological_problems"],
                    "has_seizures": row["seizures"],
                    "has_abnormal_gait": row["abnormal_gait"],
                    "has_deafness": row["deafness"],
                    "has_other_neurological_problem": row["other_neurological_problem"],
                    "other_neurological_problem_text": row[
                        "other_neurological_problem_text"
                    ],
                    "has_joint_problems": row["joint_problems"],
                    "joint_problems_age": row["joint_problems_age"],
                    "has_x_ray_abnormalities": row["x_ray_abnormalities"],
                    "has_chondrocalcinosis": row["chondrocalcinosis"],
                    "has_other_x_ray_abnormality": row["other_x_ray_abnormality"],
                    "other_x_ray_abnormality_text": row["other_x_ray_abnormality_text"],
                }
            )
            for row in rows
        ],
        "salt_wasting_clinical_features",
    )


def copy_cohort_observation(session: Session) -> None:
    """Copies group_observations on COHORT groups to cohort_observation."""
    rows = session.execute(
        text("""
        SELECT
            group_observations.id,
            group_observations.group_id,
            group_observations.observation_id,
            group_observations.weight
        FROM public.group_observations
        JOIN public.groups ON groups.id = group_observations.group_id
        WHERE groups.type = 'COHORT'
        ORDER BY
            group_observations.group_id,
            group_observations.weight,
            group_observations.id
    """)
    ).mappings()
    add_copies(
        session,
        CohortObservation,
        [
            CohortObservation.model_validate(
                {
                    "cohort_id": row["group_id"],  # cohort kept the group ids
                    "observation_id": row["observation_id"],  # observation kept its ids
                    "observation_weight": row["weight"],
                }
            )
            for row in rows
        ],
        "group_observations",
    )

    # rows on non-cohort groups have no home in radar 3
    dropped = session.execute(
        text("""
        SELECT groups.type, count(*)
        FROM public.group_observations
        JOIN public.groups ON groups.id = group_observations.group_id
        WHERE groups.type <> 'COHORT'
        GROUP BY groups.type
        ORDER BY groups.type
    """)
    )
    for group_type, count in dropped:
        log.warning(
            "group_observations: %d rows on %s groups not copied (no radar 3 home)",
            count,
            group_type,
        )


def copy_observation_option(session: Session) -> None:
    """Adds each observation's options to option and links them to it."""
    rows = session.execute(
        text("""
        SELECT observations.id, observations.options
        FROM public.observations
        WHERE observations.options IS NOT NULL
        ORDER BY observations.id
    """)
    ).mappings()
    # code -> description, as radar 2's Observation.options_dict reads them
    choices = {
        row["id"]: dict(zip(row["options"][::2], row["options"][1::2])) for row in rows
    }

    existing = {
        (option_group, store_value): option_id
        for option_group, store_value, option_id in session.execute(
            select(Option.option_group, Option.store_value, Option.id)
        )
    }
    added = [
        Option.model_validate(
            {
                "option_group": observation_group(observation_id),
                "display_label": description,
                "store_value": code,
            }
        )
        for observation_id, codes in choices.items()
        for code, description in codes.items()
        if (observation_group(observation_id), code) not in existing
    ]
    session.add_all(added)
    session.flush()
    existing.update({(o.option_group, o.store_value): o.id for o in added})
    log.info(
        "option: %d observation options added, %d already there",
        len(added),
        sum(len(codes) for codes in choices.values()) - len(added),
    )

    add_copies(
        session,
        ObservationOption,
        [
            ObservationOption.model_validate(
                {
                    "observation_id": observation_id,  # observation kept its ids
                    "option_id": existing[observation_group(observation_id), code],
                }
            )
            for observation_id, codes in choices.items()
            for code in codes
        ],
        "observations.options",
    )


def copy_observation_code(session: Session) -> None:
    """Adds each observation's pv_code to code and links it to it."""
    rows = (
        session.execute(
            text("""
        SELECT observations.id, observations.pv_code
        FROM public.observations
        WHERE observations.pv_code IS NOT NULL AND observations.pv_code <> ''
        ORDER BY observations.id
    """)
        )
        .mappings()
        .all()
    )

    existing = {
        code_value: code_id
        for code_value, code_id in session.execute(
            select(Code.code_value, Code.id).where(
                col(Code.coding_system) == PV_CODING_SYSTEM
            )
        )
    }
    pv_codes = dict.fromkeys(row["pv_code"] for row in rows)
    added = [
        Code.model_validate(
            {
                "coding_system": PV_CODING_SYSTEM,
                "code_value": pv_code,
                "code_label": pv_code,  # radar 2 sends pv_code as its description
            }
        )
        for pv_code in pv_codes
        if pv_code not in existing
    ]
    session.add_all(added)
    session.flush()
    existing.update({c.code_value: c.id for c in added})
    log.info(
        "code: %d PV codes added, %d already there",
        len(added),
        len(pv_codes) - len(added),
    )

    add_copies(
        session,
        ObservationCode,
        [
            ObservationCode.model_validate(
                {
                    "observation_id": row["id"],  # observation kept its ids
                    "code_id": existing[row["pv_code"]],
                }
            )
            for row in rows
        ],
        "observations.pv_code",
    )


def upgrade() -> None:
    bind = op.get_bind()

    # model tables go to radar3; raw SQL names public.<table> itself
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in (
            NurtureMetadata,
            SaltWastingClinicalFeature,
            SampleInventory,
            CohortObservation,
            ObservationCode,
            ObservationOption,
        ):
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_nurture_metadata(session)
            copy_salt_wasting(session)
            copy_cohort_observation(session)
            copy_observation_option(session)
            copy_observation_code(session)
    finally:
        # Alembic records the version on this connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
