"""radar 2 -> radar 3: patient diagnoses and medications

Revision ID: ebaa154bbec0
Revises: ef7da09260a3
Create Date: 2026-11-18 15:40:00.000000
"""

from collections.abc import Sequence
from typing import Any

from alembic import op
from sqlalchemy import RowMapping, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    Antibody,
    Drug,
    DrugGroup,
    DrugToGroupLink,
    Medication,
    PatientDiagnosis,
)

# revision identifiers, used by Alembic.
revision: str = "ebaa154bbec0"
down_revision: str | Sequence[str] | None = "ef7da09260a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# created in this order, parents before children: most point at patient,
# hospital, data_source, diagnosis or option (made by earlier steps), antibody
# at patient_diagnosis, drug_to_group at drug and drug_group, and medication at
# drug
TABLES: list[type[SQLModel]] = [
    PatientDiagnosis,
    Antibody,
    Drug,
    DrugGroup,
    DrugToGroupLink,
    Medication,
]


def d1(value: bool | None) -> bool:
    """[D1] a radar 2 NULL in a true/false column becomes false."""
    return False if value is None else value


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


def hospital_id(row: RowMapping) -> int | None:
    """[D3] the row's source group if it is a hospital, else NULL. type is the
    source group's, from the join to public.groups."""
    if row["type"] == "HOSPITAL":
        return row["source_group_id"]  # hospital kept the group ids
    return None


def copy_patient_diagnosis(session: Session) -> dict[Any, int]:
    """Copies patient_diagnoses and returns the new ids by radar 2 UUID, for
    antibody."""
    # antibody_id goes to antibody
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                patient_diagnoses.id,
                patient_diagnoses.patient_id,
                patient_diagnoses.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = patient_diagnoses.source_type
                ) AS data_source_id,
                patient_diagnoses.diagnosis_id,
                patient_diagnoses.diagnosis_text,
                patient_diagnoses.symptoms_date,
                patient_diagnoses.from_date,
                patient_diagnoses.to_date,
                patient_diagnoses.gene_test,
                patient_diagnoses.biochemistry,
                patient_diagnoses.clinical_picture,
                patient_diagnoses.biopsy,
                patient_diagnoses.biopsy_diagnosis,
                patient_diagnoses.comments,
                patient_diagnoses.prenatal
            FROM public.patient_diagnoses
            JOIN public.groups ON groups.id = patient_diagnoses.source_group_id
            ORDER BY
                patient_diagnoses.patient_id,
                patient_diagnoses.from_date,
                patient_diagnoses.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "hospital_id": hospital_id(row),  # [D3]
            "data_source_id": row["data_source_id"],  # [D4]
            "diagnosis_id": row["diagnosis_id"],  # diagnosis kept its ids
            "diagnosis_text": row["diagnosis_text"],
            "symptoms_date": row["symptoms_date"],
            "from_date": row["from_date"],
            "to_date": row["to_date"],
            "snapshot_date": None,  # new in radar 3
            "has_gene_test": d1(row["gene_test"]),
            "has_biochemistry": d1(row["biochemistry"]),
            "has_assessment": d1(row["clinical_picture"]),
            "has_biopsy": d1(row["biopsy"]),
            "biopsy_diagnosis_index": row["biopsy_diagnosis"],
            "diagnosis_comments": row["comments"],
            "is_prenatal": d1(row["prenatal"]),
        }
        for row in radar2_rows
    ]

    patient_diagnoses = [PatientDiagnosis.model_validate(row) for row in rows]
    session.add_all(patient_diagnoses)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, patient_diagnoses, strict=True)
    }


def copy_antibody(session: Session, patient_diagnosis_ids: dict[Any, int]) -> None:
    """One row per radar 2 patient_diagnoses row with an antibody_id."""
    # antibody_option_id: the "antibody" option storing that antibody id, NULL
    # if none, which the model rejects; step 0 made one per radar 2 antibody
    radar2_rows = session.execute(
        text("""
        SELECT
            patient_diagnoses.id,
            (
                SELECT option.id
                FROM radar3.option
                WHERE option.option_group = 'antibody'
                  AND option.store_value = patient_diagnoses.antibody_id
            ) AS antibody_option_id
        FROM public.patient_diagnoses
        WHERE patient_diagnoses.antibody_id IS NOT NULL
        ORDER BY
            patient_diagnoses.patient_id,
            patient_diagnoses.from_date,
            patient_diagnoses.id
    """)
    ).mappings()

    rows = [
        {
            # every patient_diagnoses row was copied, so each UUID has a new id
            "patient_diagnosis_id": patient_diagnosis_ids[row["id"]],
            "antibody_option_id": row["antibody_option_id"],
        }
        for row in radar2_rows
    ]

    session.add_all([Antibody.model_validate(row) for row in rows])
    session.flush()


def copy_drug(session: Session) -> None:
    """Copies drugs, keeping their ids, so medication's drug_id copies across."""
    # drug_group_id goes to drug_to_group
    radar2_rows = session.execute(
        text("""
        SELECT drugs.id, drugs.name
        FROM public.drugs
        ORDER BY drugs.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            "drug_name": row["name"],
        }
        for row in radar2_rows
    ]

    session.add_all([Drug.model_validate(row) for row in rows])
    session.flush()
    reset_sequence(session, "drug")


def copy_drug_group(session: Session) -> None:
    """Copies drug_groups, keeping their ids, so drug_to_group's copy across."""
    # parent_drug_group_id is flattened into drug_to_group
    radar2_rows = session.execute(
        text("""
        SELECT drug_groups.id, drug_groups.name
        FROM public.drug_groups
        ORDER BY drug_groups.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            "drug_group_name": row["name"],
        }
        for row in radar2_rows
    ]

    session.add_all([DrugGroup.model_validate(row) for row in rows])
    session.flush()
    reset_sequence(session, "drug_group")


def copy_drug_to_group(session: Session) -> None:
    """One row per drug and group it belongs to: its radar 2 drug_group_id, and
    every group above that one through parent_drug_group_id."""
    # The recursive query starts from each drug's own group, then adds the
    # parent of each group found so far until there is none. UNION, not UNION
    # ALL, drops a pair already found, so a group listed as its own ancestor (a
    # loop in radar 2's data) ends the walk instead of repeating it forever.
    radar2_rows = session.execute(
        text("""
        WITH RECURSIVE drug_group_chain (id, drug_group_id) AS (
            SELECT drugs.id, drugs.drug_group_id
            FROM public.drugs
            WHERE drugs.drug_group_id IS NOT NULL
          UNION
            SELECT drug_group_chain.id, drug_groups.parent_drug_group_id
            FROM drug_group_chain
            JOIN public.drug_groups
                ON drug_groups.id = drug_group_chain.drug_group_id
            WHERE drug_groups.parent_drug_group_id IS NOT NULL
        )
        SELECT drug_group_chain.id, drug_group_chain.drug_group_id
        FROM drug_group_chain
        ORDER BY drug_group_chain.id, drug_group_chain.drug_group_id
    """)
    ).mappings()

    rows = [
        {
            "drug_id": row["id"],  # drug kept its ids
            "drug_group_id": row["drug_group_id"],  # drug_group kept its ids
        }
        for row in radar2_rows
    ]

    session.add_all([DrugToGroupLink.model_validate(row) for row in rows])
    session.flush()


def copy_medication(session: Session) -> dict[Any, int]:
    """Copies medications and current_medications into medication, and returns
    the new ids by radar 2 UUID (from either table)."""
    # a medications row has no date_recorded, and a current_medications row no
    # from_date or to_date: NULL for those in the UNION ALL
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                medications.id,
                medications.patient_id,
                medications.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = medications.source_type
                ) AS data_source_id,
                medications.drug_id,
                NULL::date AS date_recorded,
                medications.from_date,
                medications.to_date,
                medications.dose_quantity,
                medications.dose_unit,
                medications.frequency,
                medications.route,
                medications.drug_text,
                medications.dose_text
            FROM public.medications
            JOIN public.groups ON groups.id = medications.source_group_id
          UNION ALL
            SELECT
                current_medications.id,
                current_medications.patient_id,
                current_medications.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = current_medications.source_type
                ) AS data_source_id,
                current_medications.drug_id,
                current_medications.date_recorded,
                NULL::date AS from_date,
                NULL::date AS to_date,
                current_medications.dose_quantity,
                current_medications.dose_unit,
                current_medications.frequency,
                current_medications.route,
                current_medications.drug_text,
                current_medications.dose_text
            FROM public.current_medications
            JOIN public.groups ON groups.id = current_medications.source_group_id
            ORDER BY patient_id, from_date, date_recorded, id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "hospital_id": hospital_id(row),  # [D3]
            "data_source_id": row["data_source_id"],  # [D4]
            "drug_id": row["drug_id"],  # drug kept its ids
            "snapshot_date": row["date_recorded"],  # current_medications only
            "start_date": row["from_date"],  # medications only
            "finish_date": row["to_date"],  # medications only
            "dose_quantity": row["dose_quantity"],
            "dose_unit": row["dose_unit"],
            "medication_frequency": row["frequency"],
            "medication_route": row["route"],
            "drug_text": row["drug_text"],
            "dose_text": row["dose_text"],
        }
        for row in radar2_rows
    ]

    medications = [Medication.model_validate(row) for row in rows]
    session.add_all(medications)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, medications, strict=True)
    }


def upgrade() -> None:
    bind = op.get_bind()

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in TABLES:
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            patient_diagnosis_ids = copy_patient_diagnosis(session)
            copy_antibody(session, patient_diagnosis_ids)
            copy_drug(session)
            copy_drug_group(session)
            copy_drug_to_group(session)
            copy_medication(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
