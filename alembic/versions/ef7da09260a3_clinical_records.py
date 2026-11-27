"""radar 2 -> radar 3: clinical record tables
One-way migration.

Revision ID: ef7da09260a3
Revises: f2655dc80a30
Create Date: 2026-11-18 12:38:31.000000
"""

from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from alembic import op
from sqlalchemy import Column, RowMapping, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    ClinicalLetter,
    Dialysis,
    FetalAnomalyScan,
    FetalUltrasound,
    Genetics,
    Hospitalisation,
    LiverDisease,
    LiverImaging,
    LiverTransplant,
    LiverTransplantIndicator,
    Nephrectomy,
    Nutrition,
    Pathology,
    Plasmapheresis,
    Pregnancy,
    RenalImaging,
    RenalProgression,
    Transplant,
    TransplantBiopsy,
    TransplantRejection,
)

# revision identifiers, used by Alembic.
revision: str = "ef7da09260a3"
down_revision: str | Sequence[str] | None = "f2655dc80a30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# radar 2 timestamps that become radar 3 dates are kept as the day they fall on
# in the UK, where RaDaR's users are, as in the patients step
UK = ZoneInfo("Europe/London")

# created in this order, parents before children: most point at patient,
# hospital, data_source, cohort or indicator (made by earlier steps),
# liver_transplant_indicator at liver_transplant, and transplant_biopsy and
# transplant_rejection at transplant
TABLES: list[type[SQLModel]] = [
    ClinicalLetter,
    Dialysis,
    FetalAnomalyScan,
    FetalUltrasound,
    Genetics,
    Hospitalisation,
    LiverDisease,
    LiverImaging,
    LiverTransplant,
    LiverTransplantIndicator,
    Nephrectomy,
    Nutrition,
    Pathology,
    Plasmapheresis,
    Pregnancy,
    RenalImaging,
    RenalProgression,
    Transplant,
    TransplantBiopsy,
    TransplantRejection,
]


def d1(value: bool | None) -> bool:
    """[D1] a radar 2 NULL in a true/false column becomes false."""
    return False if value is None else value


def uk_date(timestamp: datetime | None) -> date | None:
    """The day a radar 2 timestamp falls on in the UK."""
    return timestamp.astimezone(UK).date() if timestamp is not None else None


def utc(timestamp: datetime | None, column: Column) -> datetime | None:
    """A radar 2 timestamptz as its UTC time, in the form the radar 3 column
    takes: with its zone for a timestamptz column, without one for a timestamp
    column (given a zone, the database would store it in the connection's time
    zone instead).

    SQLModel decides which: a datetime field is timestamptz (UTCDateTime) in
    newer SQLModel, timestamp in older, and a NaiveDatetime field is timestamp.
    """
    if timestamp is None:
        return None
    in_utc = timestamp.astimezone(UTC)
    return in_utc if column.type.timezone else in_utc.replace(tzinfo=None)


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


def copy_dialysis(session: Session) -> dict[Any, int]:
    """Copies dialysis and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                dialysis.id,
                dialysis.patient_id,
                dialysis.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = dialysis.source_type
                ) AS data_source_id,
                dialysis.from_date,
                dialysis.to_date,
                dialysis.modality
            FROM public.dialysis
            JOIN public.groups ON groups.id = dialysis.source_group_id
            ORDER BY dialysis.patient_id, dialysis.from_date, dialysis.id
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
            "timeline_start": row["from_date"],
            "timeline_end": row["to_date"],
            "dialysis_modality_index": row["modality"],
        }
        for row in radar2_rows
    ]

    dialysis = [Dialysis.model_validate(row) for row in rows]
    session.add_all(dialysis)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id for row, record in zip(radar2_rows, dialysis, strict=True)
    }


def copy_fetal_anomaly_scan(session: Session) -> dict[Any, int]:
    """Copies fetal_anomaly_scans and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                fetal_anomaly_scans.id,
                fetal_anomaly_scans.patient_id,
                fetal_anomaly_scans.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = fetal_anomaly_scans.source_type
                ) AS data_source_id,
                fetal_anomaly_scans.date_of_scan,
                fetal_anomaly_scans.gestational_age,
                fetal_anomaly_scans.oligohydramnios,
                fetal_anomaly_scans.right_anomaly_details,
                fetal_anomaly_scans.right_ultrasound_details,
                fetal_anomaly_scans.left_anomaly_details,
                fetal_anomaly_scans.left_ultrasound_details,
                fetal_anomaly_scans.hypoplasia,
                fetal_anomaly_scans.echogenicity,
                fetal_anomaly_scans.hepatic_abnormalities,
                fetal_anomaly_scans.hepatic_abnormality_details,
                fetal_anomaly_scans.lung_abnormalities,
                fetal_anomaly_scans.lung_abnormality_details,
                fetal_anomaly_scans.amnioinfusion,
                fetal_anomaly_scans.amnioinfusion_count
            FROM public.fetal_anomaly_scans
            JOIN public.groups ON groups.id = fetal_anomaly_scans.source_group_id
            ORDER BY
                fetal_anomaly_scans.patient_id,
                fetal_anomaly_scans.date_of_scan,
                fetal_anomaly_scans.id
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
            "date_of_scan": row["date_of_scan"],
            "gestational_age": row["gestational_age"],
            "has_oligohydramnios": d1(row["oligohydramnios"]),
            "right_anomaly_details": row["right_anomaly_details"],
            "right_ultrasound_details": row["right_ultrasound_details"],
            "left_anomaly_details": row["left_anomaly_details"],
            "left_ultrasound_details": row["left_ultrasound_details"],
            "has_hypoplasia": d1(row["hypoplasia"]),
            "has_echogenicity": d1(row["echogenicity"]),
            "has_hepatic_abnormalities": d1(row["hepatic_abnormalities"]),
            "hepatic_abnormality_details": row["hepatic_abnormality_details"],
            "has_lung_abnormalities": d1(row["lung_abnormalities"]),
            "lung_abnormality_details": row["lung_abnormality_details"],
            "has_amnioinfusion": d1(row["amnioinfusion"]),
            "amnioinfusion_count": row["amnioinfusion_count"],
        }
        for row in radar2_rows
    ]

    fetal_anomaly_scans = [FetalAnomalyScan.model_validate(row) for row in rows]
    session.add_all(fetal_anomaly_scans)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, fetal_anomaly_scans, strict=True)
    }


def copy_fetal_ultrasound(session: Session) -> dict[Any, int]:
    """Copies fetal_ultrasounds and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                fetal_ultrasounds.id,
                fetal_ultrasounds.patient_id,
                fetal_ultrasounds.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = fetal_ultrasounds.source_type
                ) AS data_source_id,
                fetal_ultrasounds.date_of_scan,
                fetal_ultrasounds.fetal_identifier,
                fetal_ultrasounds.gestational_age,
                fetal_ultrasounds.head_centile,
                fetal_ultrasounds.abdomen_centile,
                fetal_ultrasounds.uterine_artery_notched,
                fetal_ultrasounds.liquor_volume,
                fetal_ultrasounds.comments
            FROM public.fetal_ultrasounds
            JOIN public.groups ON groups.id = fetal_ultrasounds.source_group_id
            ORDER BY
                fetal_ultrasounds.patient_id,
                fetal_ultrasounds.date_of_scan,
                fetal_ultrasounds.id
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
            "date_of_scan": row["date_of_scan"],
            "fetal_identifier": row["fetal_identifier"],
            "gestational_age": row["gestational_age"],
            "head_centile": row["head_centile"],
            "abdomen_centile": row["abdomen_centile"],
            "is_uterine_artery_notched": d1(row["uterine_artery_notched"]),
            "liquor_volume": row["liquor_volume"],
            "fetal_ultrasound_comment": row["comments"],
        }
        for row in radar2_rows
    ]

    fetal_ultrasounds = [FetalUltrasound.model_validate(row) for row in rows]
    session.add_all(fetal_ultrasounds)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, fetal_ultrasounds, strict=True)
    }


def copy_genetics(session: Session) -> dict[Any, int]:
    """Copies genetics and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                genetics.id,
                genetics.patient_id,
                genetics.group_id,
                genetics.date_sent,
                genetics.laboratory,
                genetics.reference_number,
                genetics.karyotype,
                genetics.results,
                genetics.summary
            FROM public.genetics
            ORDER BY genetics.patient_id, genetics.date_sent, genetics.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "cohort_id": row["group_id"],  # cohort kept the group ids
            "date_sent": utc(row["date_sent"], Genetics.__table__.c.date_sent),
            "laboratory": row["laboratory"],
            "reference_number": row["reference_number"],
            "karyotype_index": row["karyotype"],
            "results": row["results"],
            "summary": row["summary"],
        }
        for row in radar2_rows
    ]

    genetics = [Genetics.model_validate(row) for row in rows]
    session.add_all(genetics)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id for row, record in zip(radar2_rows, genetics, strict=True)
    }


def copy_hospitalisation(session: Session) -> dict[Any, int]:
    """Copies hospitalisations and returns the new ids by radar 2 UUID."""
    # [D6] dropped: comments
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                hospitalisations.id,
                hospitalisations.patient_id,
                hospitalisations.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = hospitalisations.source_type
                ) AS data_source_id,
                hospitalisations.date_of_admission,
                hospitalisations.date_of_discharge,
                hospitalisations.reason_for_admission
            FROM public.hospitalisations
            JOIN public.groups ON groups.id = hospitalisations.source_group_id
            ORDER BY
                hospitalisations.patient_id,
                hospitalisations.date_of_admission,
                hospitalisations.id
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
            "date_of_admission": uk_date(row["date_of_admission"]),
            "date_of_discharge": uk_date(row["date_of_discharge"]),
            # [D14] the radar 3 name is likely a typo for reason_for_admission
            "reason_of_admission": row["reason_for_admission"],
        }
        for row in radar2_rows
    ]

    hospitalisations = [Hospitalisation.model_validate(row) for row in rows]
    session.add_all(hospitalisations)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, hospitalisations, strict=True)
    }


def copy_liver_disease(session: Session) -> dict[Any, int]:
    """Copies liver_diseases and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                liver_diseases.id,
                liver_diseases.patient_id,
                liver_diseases.portal_hypertension,
                liver_diseases.portal_hypertension_date,
                liver_diseases.ascites,
                liver_diseases.ascites_date,
                liver_diseases.oesophageal,
                liver_diseases.oesophageal_date,
                liver_diseases.oesophageal_bleeding,
                liver_diseases.oesophageal_bleeding_date,
                liver_diseases.gastric,
                liver_diseases.gastric_date,
                liver_diseases.gastric_bleeding,
                liver_diseases.gastric_bleeding_date,
                liver_diseases.anorectal,
                liver_diseases.anorectal_date,
                liver_diseases.anorectal_bleeding,
                liver_diseases.anorectal_bleeding_date,
                liver_diseases.cholangitis_acute,
                liver_diseases.cholangitis_acute_date,
                liver_diseases.cholangitis_recurrent,
                liver_diseases.cholangitis_recurrent_date,
                liver_diseases.spleen_palpable,
                liver_diseases.spleen_palpable_date
            FROM public.liver_diseases
            ORDER BY liver_diseases.patient_id, liver_diseases.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "has_portal_hypertension": d1(row["portal_hypertension"]),
            "portal_hypertension_date": row["portal_hypertension_date"],
            "has_ascites": d1(row["ascites"]),
            "ascites_date": row["ascites_date"],
            "has_oesophageal": d1(row["oesophageal"]),
            "oesophageal_date": row["oesophageal_date"],
            "has_oesophageal_bleeding": d1(row["oesophageal_bleeding"]),
            "oesophageal_bleeding_date": row["oesophageal_bleeding_date"],
            "has_gastric": d1(row["gastric"]),
            "gastric_date": row["gastric_date"],
            "has_gastric_bleeding": d1(row["gastric_bleeding"]),
            "gastric_bleeding_date": row["gastric_bleeding_date"],
            "has_anorectal": d1(row["anorectal"]),
            "anorectal_date": row["anorectal_date"],
            "has_anorectal_bleeding": d1(row["anorectal_bleeding"]),
            "anorectal_bleeding_date": row["anorectal_bleeding_date"],
            "has_cholangitis_acute": d1(row["cholangitis_acute"]),
            "cholangitis_acute_date": row["cholangitis_acute_date"],
            "has_cholangitis_recurrent": d1(row["cholangitis_recurrent"]),
            "cholangitis_recurrent_date": row["cholangitis_recurrent_date"],
            "is_spleen_palpable": d1(row["spleen_palpable"]),
            "spleen_palpable_date": row["spleen_palpable_date"],
        }
        for row in radar2_rows
    ]

    liver_diseases = [LiverDisease.model_validate(row) for row in rows]
    session.add_all(liver_diseases)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, liver_diseases, strict=True)
    }


def copy_liver_imaging(session: Session) -> dict[Any, int]:
    """Copies liver_imaging and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                liver_imaging.id,
                liver_imaging.patient_id,
                liver_imaging.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = liver_imaging.source_type
                ) AS data_source_id,
                liver_imaging.date,
                liver_imaging.imaging_type,
                liver_imaging.size,
                liver_imaging.hepatic_fibrosis,
                liver_imaging.hepatic_cysts,
                liver_imaging.bile_duct_cysts,
                liver_imaging.dilated_bile_ducts,
                liver_imaging.cholangitis
            FROM public.liver_imaging
            JOIN public.groups ON groups.id = liver_imaging.source_group_id
            ORDER BY liver_imaging.patient_id, liver_imaging.date, liver_imaging.id
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
            "imaging_date": uk_date(row["date"]),
            "imaging_type": row["imaging_type"],
            "liver_size": row["size"],
            "has_hepatic_fibrosis": d1(row["hepatic_fibrosis"]),
            "has_hepatic_cysts": d1(row["hepatic_cysts"]),
            "has_bile_duct_cysts": d1(row["bile_duct_cysts"]),
            "has_dilated_bile_ducts": d1(row["dilated_bile_ducts"]),
            "has_cholangitis": d1(row["cholangitis"]),
        }
        for row in radar2_rows
    ]

    liver_imaging = [LiverImaging.model_validate(row) for row in rows]
    session.add_all(liver_imaging)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, liver_imaging, strict=True)
    }


def copy_liver_transplant(session: Session) -> dict[Any, int]:
    """Copies liver_transplants and returns the new ids by radar 2 UUID, for
    liver_transplant_indicator."""
    # indications go to liver_transplant_indicator
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                liver_transplants.id,
                liver_transplants.patient_id,
                liver_transplants.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name
                        = liver_transplants.source_type
                ) AS data_source_id,
                liver_transplants.transplant_group_id,
                liver_transplants.registration_date,
                liver_transplants.transplant_date,
                liver_transplants.other_indications,
                liver_transplants.first_graft_source,
                liver_transplants.loss_reason,
                liver_transplants.other_loss_reason
            FROM public.liver_transplants
            JOIN public.groups ON groups.id = liver_transplants.source_group_id
            ORDER BY
                liver_transplants.patient_id,
                liver_transplants.transplant_date,
                liver_transplants.id
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
            # hospital kept the group ids
            "transplant_hospital_id": row["transplant_group_id"],
            "registration_date": row["registration_date"],
            "transplant_date": row["transplant_date"],
            "other_indications": row["other_indications"],
            "first_graft_source": row["first_graft_source"],
            "loss_reason": row["loss_reason"],
            "other_loss_reason": row["other_loss_reason"],
        }
        for row in radar2_rows
    ]

    liver_transplants = [LiverTransplant.model_validate(row) for row in rows]
    session.add_all(liver_transplants)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, liver_transplants, strict=True)
    }


def copy_liver_transplant_indicator(
    session: Session, liver_transplant_ids: dict[Any, int]
) -> None:
    """One row per indication in each radar 2 liver_transplants.indications."""
    # indicator_id: the indicator with that label, NULL if none, which the
    # model rejects; step 0 made one per label used, so every label has one
    radar2_rows = session.execute(
        text("""
        SELECT
            liver_transplants.id,
            (
                SELECT indicator.id
                FROM radar3.indicator
                WHERE indicator.indicator_label = indication.label
            ) AS indicator_id
        FROM public.liver_transplants
        CROSS JOIN LATERAL unnest(liver_transplants.indications)
            WITH ORDINALITY AS indication (label, position)
        ORDER BY
            liver_transplants.patient_id,
            liver_transplants.transplant_date,
            liver_transplants.id,
            indication.position
    """)
    ).mappings()

    rows = [
        {
            # every liver_transplants row was copied, so each UUID has a new id
            "liver_transplant_id": liver_transplant_ids[row["id"]],
            "indicator_id": row["indicator_id"],
        }
        for row in radar2_rows
    ]

    session.add_all([LiverTransplantIndicator.model_validate(row) for row in rows])
    session.flush()


def copy_nephrectomy(session: Session) -> dict[Any, int]:
    """Copies nephrectomies and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                nephrectomies.id,
                nephrectomies.patient_id,
                nephrectomies.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = nephrectomies.source_type
                ) AS data_source_id,
                nephrectomies.date,
                nephrectomies.kidney_side,
                nephrectomies.kidney_type,
                nephrectomies.entry_type
            FROM public.nephrectomies
            JOIN public.groups ON groups.id = nephrectomies.source_group_id
            ORDER BY nephrectomies.patient_id, nephrectomies.date, nephrectomies.id
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
            "assessment_date": row["date"],
            "kidney_side": row["kidney_side"],
            "kidney_type": row["kidney_type"],
            "entry_type": row["entry_type"],
        }
        for row in radar2_rows
    ]

    nephrectomies = [Nephrectomy.model_validate(row) for row in rows]
    session.add_all(nephrectomies)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, nephrectomies, strict=True)
    }


def copy_nutrition(session: Session) -> dict[Any, int]:
    """Copies nutrition and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                nutrition.id,
                nutrition.patient_id,
                nutrition.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = nutrition.source_type
                ) AS data_source_id,
                nutrition.feeding_type,
                nutrition.from_date,
                nutrition.to_date
            FROM public.nutrition
            JOIN public.groups ON groups.id = nutrition.source_group_id
            ORDER BY nutrition.patient_id, nutrition.from_date, nutrition.id
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
            "feeding_type": row["feeding_type"],
            "from_date": row["from_date"],
            "to_date": row["to_date"],
        }
        for row in radar2_rows
    ]

    nutrition = [Nutrition.model_validate(row) for row in rows]
    session.add_all(nutrition)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id for row, record in zip(radar2_rows, nutrition, strict=True)
    }


def copy_pathology(session: Session) -> dict[Any, int]:
    """Copies pathology and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                pathology.id,
                pathology.patient_id,
                pathology.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = pathology.source_type
                ) AS data_source_id,
                pathology.date,
                pathology.kidney_type,
                pathology.kidney_side,
                pathology.reference_number,
                pathology.image_url,
                pathology.histological_summary,
                pathology.em_findings,
                pathology.report_cleaned
            FROM public.pathology
            JOIN public.groups ON groups.id = pathology.source_group_id
            ORDER BY pathology.patient_id, pathology.date, pathology.id
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
            "report_date": row["date"],
            "kidney_type": row["kidney_type"],
            "kidney_side": row["kidney_side"],
            "reference_number": row["reference_number"],
            "image_url": row["image_url"],
            "histological_summary": row["histological_summary"],
            "em_findings": row["em_findings"],
            "report_cleaned_date": row["report_cleaned"],
        }
        for row in radar2_rows
    ]

    pathology = [Pathology.model_validate(row) for row in rows]
    session.add_all(pathology)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id for row, record in zip(radar2_rows, pathology, strict=True)
    }


def copy_plasmapheresis(session: Session) -> dict[Any, int]:
    """Copies plasmapheresis and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                plasmapheresis.id,
                plasmapheresis.patient_id,
                plasmapheresis.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = plasmapheresis.source_type
                ) AS data_source_id,
                plasmapheresis.from_date,
                plasmapheresis.to_date,
                plasmapheresis.no_of_exchanges,
                plasmapheresis.response
            FROM public.plasmapheresis
            JOIN public.groups ON groups.id = plasmapheresis.source_group_id
            ORDER BY
                plasmapheresis.patient_id,
                plasmapheresis.from_date,
                plasmapheresis.id
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
            "from_date": row["from_date"],
            "to_date": row["to_date"],
            "plasmapheresis_schedule": row["no_of_exchanges"],
            "plasmapheresis_response": row["response"],
        }
        for row in radar2_rows
    ]

    plasmapheresis = [Plasmapheresis.model_validate(row) for row in rows]
    session.add_all(plasmapheresis)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, plasmapheresis, strict=True)
    }


def copy_pregnancy(session: Session) -> dict[Any, int]:
    """Copies pregnancies and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                pregnancies.id,
                pregnancies.patient_id,
                pregnancies.pregnancy_number,
                pregnancies.date_of_lmp,
                pregnancies.gravidity,
                pregnancies.parity1,
                pregnancies.parity2,
                pregnancies.outcome,
                pregnancies.weight,
                pregnancies.weight_centile,
                pregnancies.gestational_age,
                pregnancies.delivery_method,
                pregnancies.neonatal_intensive_care,
                pregnancies.pre_eclampsia
            FROM public.pregnancies
            ORDER BY
                pregnancies.patient_id,
                pregnancies.pregnancy_number,
                pregnancies.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "pregnancy_number": row["pregnancy_number"],
            "date_of_lmp": row["date_of_lmp"],
            "gravidity": row["gravidity"],
            "parity1": row["parity1"],
            "parity2": row["parity2"],
            "pregnancy_outcome": row["outcome"],
            "birth_weight": row["weight"],
            "centile_weight": row["weight_centile"],
            "gestational_age": row["gestational_age"],
            "delivery_method": row["delivery_method"],
            "has_neonatal_intensive_care": d1(row["neonatal_intensive_care"]),
            "pre_eclampsia": row["pre_eclampsia"],
        }
        for row in radar2_rows
    ]

    pregnancies = [Pregnancy.model_validate(row) for row in rows]
    session.add_all(pregnancies)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, pregnancies, strict=True)
    }


def copy_renal_imaging(session: Session) -> dict[Any, int]:
    """Copies renal_imaging and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                renal_imaging.id,
                renal_imaging.patient_id,
                renal_imaging.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = renal_imaging.source_type
                ) AS data_source_id,
                renal_imaging.date,
                renal_imaging.imaging_type,
                renal_imaging.right_present,
                renal_imaging.right_type,
                renal_imaging.right_length,
                renal_imaging.right_volume,
                renal_imaging.right_cysts,
                renal_imaging.right_stones,
                renal_imaging.right_calcification,
                renal_imaging.right_nephrocalcinosis,
                renal_imaging.right_nephrolithiasis,
                renal_imaging.right_other_malformation,
                renal_imaging.left_present,
                renal_imaging.left_type,
                renal_imaging.left_length,
                renal_imaging.left_volume,
                renal_imaging.left_cysts,
                renal_imaging.left_stones,
                renal_imaging.left_calcification,
                renal_imaging.left_nephrocalcinosis,
                renal_imaging.left_nephrolithiasis,
                renal_imaging.left_other_malformation
            FROM public.renal_imaging
            JOIN public.groups ON groups.id = renal_imaging.source_group_id
            ORDER BY renal_imaging.patient_id, renal_imaging.date, renal_imaging.id
        """)
        )
        .mappings()
        .all()
    )

    assessment_date = RenalImaging.__table__.c.assessment_date
    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "hospital_id": hospital_id(row),  # [D3]
            "data_source_id": row["data_source_id"],  # [D4]
            "assessment_date": utc(row["date"], assessment_date),
            "imaging_type": row["imaging_type"],
            "is_right_present": d1(row["right_present"]),
            "right_type": row["right_type"],
            "right_length": row["right_length"],
            "right_volume": row["right_volume"],
            "has_right_cysts": d1(row["right_cysts"]),
            "has_right_stones": d1(row["right_stones"]),
            "has_right_calcification": d1(row["right_calcification"]),
            "has_right_nephrocalcinosis": d1(row["right_nephrocalcinosis"]),
            "has_right_nephrolithiasis": d1(row["right_nephrolithiasis"]),
            "right_other_malformation": row["right_other_malformation"],
            "is_left_present": d1(row["left_present"]),
            "left_type": row["left_type"],
            "left_length": row["left_length"],
            "left_volume": row["left_volume"],
            "has_left_cysts": d1(row["left_cysts"]),
            "has_left_stones": d1(row["left_stones"]),
            "has_left_calcification": d1(row["left_calcification"]),
            "has_left_nephrocalcinosis": d1(row["left_nephrocalcinosis"]),
            "has_left_nephrolithiasis": d1(row["left_nephrolithiasis"]),
            "left_other_malformation": row["left_other_malformation"],
        }
        for row in radar2_rows
    ]

    renal_imaging = [RenalImaging.model_validate(row) for row in rows]
    session.add_all(renal_imaging)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, renal_imaging, strict=True)
    }


def copy_renal_progression(session: Session) -> dict[Any, int]:
    """Copies renal_progressions and returns the new ids by radar 2 UUID."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                renal_progressions.id,
                renal_progressions.patient_id,
                renal_progressions.onset_date,
                renal_progressions.esrf_date,
                renal_progressions.ckd5_date,
                renal_progressions.ckd4_date,
                renal_progressions.ckd3a_date,
                renal_progressions.ckd3b_date
            FROM public.renal_progressions
            ORDER BY renal_progressions.patient_id, renal_progressions.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "onset_date": row["onset_date"],
            "esrf_date": row["esrf_date"],
            "ckd5_date": row["ckd5_date"],
            "ckd4_date": row["ckd4_date"],
            "ckd3a_date": row["ckd3a_date"],
            "ckd3b_date": row["ckd3b_date"],
        }
        for row in radar2_rows
    ]

    renal_progressions = [RenalProgression.model_validate(row) for row in rows]
    session.add_all(renal_progressions)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, renal_progressions, strict=True)
    }


def copy_transplant(session: Session) -> dict[Any, int]:
    """Copies transplants and returns the new ids by radar 2 UUID, for
    transplant_biopsy and transplant_rejection."""
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                transplants.id,
                transplants.patient_id,
                transplants.source_group_id,
                groups.type,
                (
                    SELECT data_source.id
                    FROM radar3.data_source
                    WHERE data_source.data_source_name = transplants.source_type
                ) AS data_source_id,
                transplants.transplant_group_id,
                transplants.date,
                transplants.modality,
                transplants.date_of_recurrence,
                transplants.date_of_failure,
                transplants.recurrence,
                transplants.date_of_cmv_infection,
                transplants.donor_hla,
                transplants.recipient_hla,
                transplants.mismatch_hla,
                transplants.graft_loss_cause
            FROM public.transplants
            JOIN public.groups ON groups.id = transplants.source_group_id
            ORDER BY transplants.patient_id, transplants.date, transplants.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],  # patient kept its ids
            "hospital_id": hospital_id(row),  # [D3]
            # hospital kept the group ids
            "transplant_hospital_id": row["transplant_group_id"],
            "data_source_id": row["data_source_id"],  # [D4]
            "transplant_date": row["date"],
            "transplant_modality_index": row["modality"],
            "date_of_recurrence": row["date_of_recurrence"],
            "date_of_failure": row["date_of_failure"],
            "has_recurrence": d1(row["recurrence"]),
            "date_of_cmv_infection": row["date_of_cmv_infection"],
            "donor_hla": row["donor_hla"],
            "recipient_hla": row["recipient_hla"],
            "mismatch_hla": row["mismatch_hla"],
            "graft_loss_cause": row["graft_loss_cause"],
        }
        for row in radar2_rows
    ]

    transplants = [Transplant.model_validate(row) for row in rows]
    session.add_all(transplants)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: record.id
        for row, record in zip(radar2_rows, transplants, strict=True)
    }


def copy_transplant_biopsy(session: Session, transplant_ids: dict[Any, int]) -> None:
    """Copies transplant_biopsies, keeping their ids."""
    radar2_rows = session.execute(
        text("""
        SELECT
            transplant_biopsies.id,
            transplant_biopsies.transplant_id,
            transplant_biopsies.date_of_biopsy,
            transplant_biopsies.recurrence
        FROM public.transplant_biopsies
        ORDER BY transplant_biopsies.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            # every transplants row was copied, so each UUID has a new id
            "transplant_id": transplant_ids[row["transplant_id"]],
            "biopsy_date": row["date_of_biopsy"],
            "has_biopsy_recurrence": d1(row["recurrence"]),
        }
        for row in radar2_rows
    ]

    session.add_all([TransplantBiopsy.model_validate(row) for row in rows])
    session.flush()
    reset_sequence(session, "transplant_biopsy")


def copy_transplant_rejection(session: Session, transplant_ids: dict[Any, int]) -> None:
    """Copies transplant_rejections, keeping their ids."""
    radar2_rows = session.execute(
        text("""
        SELECT
            transplant_rejections.id,
            transplant_rejections.transplant_id,
            transplant_rejections.date_of_rejection
        FROM public.transplant_rejections
        ORDER BY transplant_rejections.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            # every transplants row was copied, so each UUID has a new id
            "transplant_id": transplant_ids[row["transplant_id"]],
            "rejection_date": row["date_of_rejection"],
        }
        for row in radar2_rows
    ]

    session.add_all([TransplantRejection.model_validate(row) for row in rows])
    session.flush()
    reset_sequence(session, "transplant_rejection")


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
            # the UUID -> new id maps the copies return are kept only where a
            # table here points at the copied rows
            copy_dialysis(session)
            copy_fetal_anomaly_scan(session)
            copy_fetal_ultrasound(session)
            copy_genetics(session)
            copy_hospitalisation(session)
            copy_liver_disease(session)
            copy_liver_imaging(session)
            liver_transplant_ids = copy_liver_transplant(session)
            copy_liver_transplant_indicator(session, liver_transplant_ids)
            copy_nephrectomy(session)
            copy_nutrition(session)
            copy_pathology(session)
            copy_plasmapheresis(session)
            copy_pregnancy(session)
            copy_renal_imaging(session)
            copy_renal_progression(session)
            transplant_ids = copy_transplant(session)
            copy_transplant_biopsy(session, transplant_ids)
            copy_transplant_rejection(session, transplant_ids)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
