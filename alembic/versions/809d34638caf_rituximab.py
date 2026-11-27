"""radar 2 -> radar 3: rituximab baseline assessments and criteria

Revision ID: 809d34638caf
Revises: 7e8597a03a37
Create Date: 2026-11-27 14:15:00.000000
"""

import logging
from collections.abc import Sequence
from typing import Any

from alembic import op
from sqlalchemy import RowMapping, select, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    Option,
    RituximabBaselineAssessment,
    RituximabBaselineAssessmentOption,
    RituximabBaselinePreviousTreatment,
    RituximabCriteria,
)

# revision identifiers, used by Alembic.
revision: str = "809d34638caf"
down_revision: str | Sequence[str] | None = "7e8597a03a37"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

SUPPORTIVE_MEDICATION_GROUP = "rituximab-baseline-assessment.supportiveMedication"
PREVIOUS_TREATMENT_GROUP = "rituximab-baseline-assessment.previousTreatment"

# from radar 2's radar/models/rituximab.py: store value -> display label
SUPPORTIVE_MEDICATIONS = {
    "RAAS_BLOCKADE": "RAAS Blockade",
    "ANTICOAGULANT": "Anticoagulant",
    "ANTIPLATELET": "Antiplatelet",
    "STATINS": "Statins",
    "DIURETICS": "Diuretics",
}
TREATMENT_OPTIONS = {
    "chlorambucil": "Chlorambucil",
    "cyclophosphamide": "Cyclophosphamide",
    "rituximab": "Rituximab",
    "tacrolimus": "Tacrolimus",
    "cyclosporine": "Cyclosporine",
}

# a previous_treatment entry's keys besides its own name
TREATMENT_KEYS = {"start_date", "end_date", "total_dose"}


def hospital_id(row: RowMapping) -> int | None:
    """[D3] the source group if it is a hospital, else NULL."""
    if row["type"] == "HOSPITAL":
        return row["source_group_id"]  # hospital kept the group ids
    return None


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


def option_id(options: dict[tuple[str, str], int], group: str, value: str) -> int:
    """The id of value's option in group."""
    return options[group, value]


def previous_treatments(
    previous_treatment: Any, options: dict[tuple[str, str], int], radar2: str
) -> list[dict[str, Any]]:
    """The ticked treatments' fields."""
    if previous_treatment is None:
        return []
    if not isinstance(previous_treatment, dict):
        raise ValueError(f"{radar2} has a previous_treatment that is not an object")

    treatments: list[dict[str, Any]] = []
    for name, treatment in previous_treatment.items():
        if not isinstance(treatment, dict):
            raise ValueError(
                f"{radar2} has a previous_treatment.{name} that is not an object"
            )
        unknown = treatment.keys() - {name, *TREATMENT_KEYS}
        if unknown:
            raise ValueError(
                f"{radar2} has previous_treatment.{name} keys with no radar 3 "
                f"column: {', '.join(sorted(unknown))}"
            )
        if not treatment.get(name):
            continue  # not ticked

        treatments.append(
            {
                "option_id": option_id(options, PREVIOUS_TREATMENT_GROUP, name),
                "total_dose": treatment.get("total_dose"),
                "treatment_start_date": treatment.get("start_date"),
                "treatment_end_date": treatment.get("end_date"),
            }
        )
    return treatments


def copy_baseline_assessment(
    session: Session, options: dict[tuple[str, str], int]
) -> int:
    """Copies baseline assessments with their options and previous treatments."""
    radar2_rows = session.execute(
        text("""
        SELECT
            assessment.id,
            assessment.patient_id,
            assessment.source_group_id,
            groups.type,
            (
                SELECT data_source.id
                FROM radar3.data_source
                WHERE data_source.data_source_name = assessment.source_type
            ) AS data_source_id,
            assessment.date,
            assessment.nephropathy,
            assessment.supportive_medication,
            assessment.previous_treatment,
            assessment.steroids,
            assessment.other_previous_treatment,
            assessment.past_remission,
            assessment.performance_status,
            assessment.comorbidities
        FROM public.rituximab_baseline_assessment AS assessment
        JOIN public.groups ON groups.id = assessment.source_group_id
        ORDER BY assessment.patient_id, assessment.date, assessment.id
    """)
    ).mappings()

    # links wait for the assessment's new id
    copies: list[
        tuple[RituximabBaselineAssessment, list[tuple[type[SQLModel], dict]]]
    ] = []
    for row in radar2_rows:
        radar2 = f"radar 2 rituximab_baseline_assessment {row['id']}"
        assessment = RituximabBaselineAssessment.model_validate(
            {
                "patient_id": row["patient_id"],  # patient kept its ids
                "hospital_id": hospital_id(row),  # [D3]
                "data_source_id": row["data_source_id"],  # [D4]
                "assessment_date": row["date"],
                "nephropathy": row["nephropathy"],
                "has_steroids": row["steroids"],
                "other_previous_treatment": row["other_previous_treatment"],
                "has_past_remission": row["past_remission"],
                "performance_status_index": row["performance_status"],
                "has_comorbidities": row["comorbidities"],
            }
        )

        links: list[tuple[type[SQLModel], dict]] = [
            (
                RituximabBaselineAssessmentOption,
                {
                    "option_id": option_id(
                        options, SUPPORTIVE_MEDICATION_GROUP, medication
                    )
                },
            )
            for medication in dict.fromkeys(row["supportive_medication"] or [])
        ]
        links += [
            (RituximabBaselinePreviousTreatment, treatment)
            for treatment in previous_treatments(
                row["previous_treatment"], options, radar2
            )
        ]

        copies.append((assessment, links))

    session.add_all([assessment for assessment, _ in copies])
    session.flush()

    linked = [
        table.model_validate(
            {"rituximab_baseline_assessment_id": assessment.id, **fields}
        )
        for assessment, links in copies
        for table, fields in links
    ]
    session.add_all(linked)
    session.flush()

    log.info(
        "rituximab_baseline_assessment: %s rows copied, with %s supportive "
        "medications and %s previous treatments",
        f"{len(copies):,}",
        f"{sum(isinstance(r, RituximabBaselineAssessmentOption) for r in linked):,}",
        f"{sum(isinstance(r, RituximabBaselinePreviousTreatment) for r in linked):,}",
    )
    return len(copies)


def copy_criteria(session: Session) -> int:
    """Copies rituximab criteria."""
    radar2_rows = session.execute(
        text("""
        SELECT
            rituximab_criteria.id,
            rituximab_criteria.patient_id,
            rituximab_criteria.date,
            rituximab_criteria.criteria1,
            rituximab_criteria.criteria2,
            rituximab_criteria.criteria3,
            rituximab_criteria.criteria4,
            rituximab_criteria.criteria5,
            rituximab_criteria.criteria6,
            rituximab_criteria.criteria7,
            rituximab_criteria.alkylating_complication,
            rituximab_criteria.alkylating_failure_monitoring_requirements,
            rituximab_criteria.cancer,
            rituximab_criteria.cni_failure_monitoring_requirements,
            rituximab_criteria.cni_therapy_complication,
            rituximab_criteria.diabetes,
            rituximab_criteria.drug_associated_toxicity,
            rituximab_criteria.fall_in_egfr,
            rituximab_criteria.hypersensitivity,
            rituximab_criteria.risk_factors,
            rituximab_criteria.ongoing_severe_disease,
            rituximab_criteria.threatened_fertility,
            rituximab_criteria.mood_disturbance,
            rituximab_criteria.osteoporosis_osteopenia,
            rituximab_criteria.previous_hospitalization
        FROM public.rituximab_criteria
        ORDER BY
            rituximab_criteria.patient_id,
            rituximab_criteria.date,
            rituximab_criteria.id
    """)
    ).mappings()

    copies = [
        RituximabCriteria.model_validate(
            {
                "patient_id": row["patient_id"],  # patient kept its ids
                "assessment_date": row["date"],
                "has_criterion_1": row["criteria1"],
                "has_criterion_2": row["criteria2"],
                "has_criterion_3": row["criteria3"],
                "has_criterion_4": row["criteria4"],
                "has_criterion_5": row["criteria5"],
                "has_criterion_6": row["criteria6"],
                "has_criterion_7": row["criteria7"],
                "has_alkylating_complication": row["alkylating_complication"],
                "has_alkylating_failure_monitoring_requirements": row[
                    "alkylating_failure_monitoring_requirements"
                ],
                "has_cancer": row["cancer"],
                "has_cni_failure_monitoring_requirements": row[
                    "cni_failure_monitoring_requirements"
                ],
                "has_cni_therapy_complication": row["cni_therapy_complication"],
                "has_diabetes": row["diabetes"],
                "has_drug_associated_toxicity": row["drug_associated_toxicity"],
                "has_fall_in_egfr": row["fall_in_egfr"],
                "has_hypersensitivity": row["hypersensitivity"],
                "has_risk_factors": row["risk_factors"],
                "has_ongoing_severe_disease": row["ongoing_severe_disease"],
                "has_threatened_fertility": row["threatened_fertility"],
                "has_mood_disturbance": row["mood_disturbance"],
                "has_osteoporosis_osteopenia": row["osteoporosis_osteopenia"],
                "has_previous_hospitalization": row["previous_hospitalization"],
            }
        )
        for row in radar2_rows
    ]

    session.add_all(copies)
    session.flush()
    return len(copies)


def upgrade() -> None:
    bind = op.get_bind()

    # model tables go to radar3; raw SQL names public.<table> itself
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in (
            RituximabBaselineAssessment,
            RituximabBaselineAssessmentOption,
            RituximabBaselinePreviousTreatment,
            RituximabCriteria,
        ):
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            options = load_options(session)
            add_options(
                session, options, SUPPORTIVE_MEDICATION_GROUP, SUPPORTIVE_MEDICATIONS
            )
            add_options(session, options, PREVIOUS_TREATMENT_GROUP, TREATMENT_OPTIONS)
            copy_baseline_assessment(session, options)
            count = copy_criteria(session)
            log.info("rituximab_criteria: %s rows copied", f"{count:,}")
    finally:
        # Alembic records the version on this connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
