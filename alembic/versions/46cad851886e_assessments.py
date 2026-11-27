"""radar 2 -> radar 3: clinical pictures to assessments

Copies alport, fuan, hnf1b, ins and mpgn clinical pictures into their radar 3
assessment tables with new ids, in patient and date order, each row checked
with its model. fuan's family_gout_relatives is not copied: radar 3 has no
column for it. One-way migration.

Revision ID: 46cad851886e
Revises: d1aa40c7d72c
Create Date: 2026-11-27 15:35:00.000000
"""

import logging
from collections.abc import Sequence

from alembic import op
from sqlalchemy import text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    AlportAssessment,
    FuanAssessment,
    Hnf1bAssessment,
    InsAssessment,
    MpgnAssessment,
)

# revision identifiers, used by Alembic.
revision: str = "46cad851886e"
down_revision: str | Sequence[str] | None = "d1aa40c7d72c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")


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


def copy_alport(session: Session) -> None:
    """Copies alport_clinical_pictures to alport_assessment."""
    rows = session.execute(
        text("""
        SELECT
            alport.id,
            alport.patient_id,
            alport.date_of_picture,
            alport.deafness,
            alport.deafness_date,
            alport.hearing_aid_date
        FROM public.alport_clinical_pictures AS alport
        ORDER BY alport.patient_id, alport.date_of_picture, alport.id
    """)
    ).mappings()
    add_copies(
        session,
        AlportAssessment,
        [
            AlportAssessment.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "date_of_picture": row["date_of_picture"],
                    "deafness_index": row["deafness"],
                    "deafness_date": row["deafness_date"],
                    "hearing_aid_date": row["hearing_aid_date"],
                }
            )
            for row in rows
        ],
        "alport_clinical_pictures",
    )


def copy_fuan(session: Session) -> None:
    """Copies fuan_clinical_pictures to fuan_assessment."""
    rows = session.execute(
        text("""
        SELECT
            fuan.id,
            fuan.patient_id,
            fuan.picture_date,
            fuan.gout,
            fuan.gout_date,
            fuan.family_gout,
            fuan.family_gout_relatives,
            fuan.thp,
            fuan.uti,
            fuan.comments
        FROM public.fuan_clinical_pictures AS fuan
        ORDER BY fuan.patient_id, fuan.picture_date, fuan.id
    """)
    ).mappings().all()
    add_copies(
        session,
        FuanAssessment,
        [
            FuanAssessment.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "picture_date": row["picture_date"],
                    "has_gout": row["gout"],
                    "gout_date": row["gout_date"],
                    "has_family_gout": row["family_gout"],
                    "thp": row["thp"],
                    "has_uti": row["uti"],
                    "fuan_comments": row["comments"],
                }
            )
            for row in rows
        ],
        "fuan_clinical_pictures",
    )
    log.info(
        "fuan_assessment: %s rows' family_gout_relatives not copied, no column",
        f"{sum(bool(row['family_gout_relatives']) for row in rows):,}",
    )


def copy_hnf1b(session: Session) -> None:
    """Copies hnf1b_clinical_pictures to hnf1b_assessment."""
    rows = session.execute(
        text("""
        SELECT
            hnf1b.id,
            hnf1b.patient_id,
            hnf1b.date_of_picture,
            hnf1b.single_kidney,
            hnf1b.hyperuricemia_gout,
            hnf1b.genital_malformation,
            hnf1b.genital_malformation_details,
            hnf1b.familial_cystic_disease,
            hnf1b.hypertension
        FROM public.hnf1b_clinical_pictures AS hnf1b
        ORDER BY hnf1b.patient_id, hnf1b.date_of_picture, hnf1b.id
    """)
    ).mappings()
    add_copies(
        session,
        Hnf1bAssessment,
        [
            Hnf1bAssessment.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "date_of_picture": row["date_of_picture"],
                    "has_single_kidney": row["single_kidney"],
                    "has_hyperuricemia_gout": row["hyperuricemia_gout"],
                    "has_genital_malformation": row["genital_malformation"],
                    "genital_malformation_details": row[
                        "genital_malformation_details"
                    ],
                    "has_familial_cystic_disease": row["familial_cystic_disease"],
                    "has_hypertension": row["hypertension"],
                }
            )
            for row in rows
        ],
        "hnf1b_clinical_pictures",
    )


def copy_ins(session: Session) -> None:
    """Copies ins_clinical_pictures to ins_assessment."""
    rows = session.execute(
        text("""
        SELECT
            ins.id,
            ins.patient_id,
            ins.date_of_picture,
            ins.oedema,
            ins.hypovalaemia,
            ins.fever,
            ins.thrombosis,
            ins.peritonitis,
            ins.pulmonary_odemea,
            ins.hypertension,
            ins.rash,
            ins.rash_details,
            ins.infection,
            ins.infection_details,
            ins.ophthalmoscopy,
            ins.ophthalmoscopy_details,
            ins.comments
        FROM public.ins_clinical_pictures AS ins
        ORDER BY ins.patient_id, ins.date_of_picture, ins.id
    """)
    ).mappings()
    add_copies(
        session,
        InsAssessment,
        [
            InsAssessment.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "date_of_picture": row["date_of_picture"],
                    "has_oedema": row["oedema"],
                    "has_hypovoloemia": row["hypovalaemia"],
                    "has_fever": row["fever"],
                    "has_thrombosis": row["thrombosis"],
                    "has_peritonitis": row["peritonitis"],
                    "has_pulmonary_oedema": row["pulmonary_odemea"],
                    "has_hypertension": row["hypertension"],
                    "has_rash": row["rash"],
                    "rash_details": row["rash_details"],
                    "has_infection": row["infection"],
                    "infection_details": row["infection_details"],
                    "has_ophthalmoscopy": row["ophthalmoscopy"],
                    "ophthalmoscopy_details": row["ophthalmoscopy_details"],
                    "ins_comments": row["comments"],
                }
            )
            for row in rows
        ],
        "ins_clinical_pictures",
    )


def copy_mpgn(session: Session) -> None:
    """Copies mpgn_clinical_pictures to mpgn_assessment."""
    rows = session.execute(
        text("""
        SELECT
            mpgn.id,
            mpgn.patient_id,
            mpgn.date_of_picture,
            mpgn.oedema,
            mpgn.hypertension,
            mpgn.urticaria,
            mpgn.partial_lipodystrophy,
            mpgn.infection,
            mpgn.infection_details,
            mpgn.ophthalmoscopy,
            mpgn.ophthalmoscopy_details,
            mpgn.comments
        FROM public.mpgn_clinical_pictures AS mpgn
        ORDER BY mpgn.patient_id, mpgn.date_of_picture, mpgn.id
    """)
    ).mappings()
    add_copies(
        session,
        MpgnAssessment,
        [
            MpgnAssessment.model_validate(
                {
                    "patient_id": row["patient_id"],  # patient kept its ids
                    "date_of_picture": row["date_of_picture"],
                    "has_oedema": row["oedema"],
                    "has_hypertension": row["hypertension"],
                    "has_urticaria": row["urticaria"],
                    "has_partial_lipodystrophy": row["partial_lipodystrophy"],
                    "has_infection": row["infection"],
                    "infection_details": row["infection_details"],
                    "has_ophthalmoscopy": row["ophthalmoscopy"],
                    "ophthalmoscopy_details": row["ophthalmoscopy_details"],
                    "mpgn_comments": row["comments"],
                }
            )
            for row in rows
        ],
        "mpgn_clinical_pictures",
    )


def upgrade() -> None:
    bind = op.get_bind()

    # model tables go to radar3; raw SQL names public.<table> itself
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in (
            AlportAssessment,
            FuanAssessment,
            Hnf1bAssessment,
            InsAssessment,
            MpgnAssessment,
        ):
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_alport(session)
            copy_fuan(session)
            copy_hnf1b(session)
            copy_ins(session)
            copy_mpgn(session)
    finally:
        # Alembic records the version on this connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
