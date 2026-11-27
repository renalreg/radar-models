"""radar 2 -> radar 3: biomarkers and codes

Revision ID: d1aa40c7d72c
Revises: 809d34638caf
Create Date: 2026-11-27 15:08:15.674152

"""

import logging
from datetime import UTC, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    Biomarker,
    BiomarkerBarcode,
    BiomarkerResult,
    BiomarkerSample,
    Code,
)

# revision identifiers, used by Alembic.
revision: str = "d1aa40c7d72c"
down_revision: Union[str, Sequence[str], None] = "809d34638caf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

log = logging.getLogger("alembic.runtime.migration")


def as_utc(timestamp: datetime | None, column: sa.Column) -> datetime | None:
    """A radar 2 timestamp, which has no zone, kept as UTC."""
    if timestamp is None or not column.type.timezone:
        return timestamp
    return timestamp.replace(tzinfo=UTC)


def add_copies(session: Session, model: type[SQLModel], copies: list) -> None:
    """Adds copies with their radar 2 ids and moves the id sequence past them."""
    session.add_all(copies)
    session.flush()
    table = model.__tablename__
    session.execute(
        sa.text(f"""
        SELECT setval(
            pg_get_serial_sequence('radar3.{table}', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.{table}),
            false
        )
    """)
    )
    log.info("%s: %s rows copied", table, f"{len(copies):,}")


def copy_code(session: Session) -> None:
    """Copies codes."""
    rows = session.execute(
        sa.text("""
        SELECT codes.id, codes.system, codes.code, codes.display
        FROM public.codes
        ORDER BY codes.id
    """)
    ).mappings()
    add_copies(
        session,
        Code,
        [
            Code.model_validate(
                {
                    "id": row["id"],
                    "coding_system": row["system"],
                    "code_describes": None,  # new in radar 3
                    "code_value": row["code"],
                    "code_label": row["display"],
                }
            )
            for row in rows
        ],
    )


def copy_biomarker(session: Session) -> None:
    """Copies biomarkers."""
    rows = session.execute(
        sa.text("""
        SELECT biomarkers.id, biomarkers.name, biomarkers.type
        FROM public.biomarkers
        ORDER BY biomarkers.id
    """)
    ).mappings()
    add_copies(
        session,
        Biomarker,
        [
            Biomarker.model_validate(
                {
                    "id": row["id"],
                    "biomarker_name": row["name"],
                    "biomarker_type": row["type"],
                }
            )
            for row in rows
        ],
    )


def copy_biomarker_barcode(session: Session) -> None:
    """Copies biomarker barcodes."""
    rows = session.execute(
        sa.text("""
        SELECT
            biomarker_barcodes.id,
            biomarker_barcodes.pat_id,
            biomarker_barcodes.barcode,
            biomarker_barcodes.sample_date
        FROM public.biomarker_barcodes
        ORDER BY biomarker_barcodes.id
    """)
    ).mappings()
    sample_date = BiomarkerBarcode.__table__.c.sample_date
    add_copies(
        session,
        BiomarkerBarcode,
        [
            BiomarkerBarcode.model_validate(
                {
                    "id": row["id"],
                    "patient_id": row["pat_id"],  # patient kept its ids
                    "barcode": row["barcode"],
                    "sample_date": as_utc(row["sample_date"], sample_date),
                }
            )
            for row in rows
        ],
    )


def copy_biomarker_sample(session: Session) -> None:
    """Copies biomarker samples."""
    rows = session.execute(
        sa.text("""
        SELECT biomarker_samples.id, biomarker_samples.barcode_id, biomarker_samples.label
        FROM public.biomarker_samples
        ORDER BY biomarker_samples.id
    """)
    ).mappings()
    add_copies(
        session,
        BiomarkerSample,
        [
            BiomarkerSample.model_validate(
                {
                    "id": row["id"],
                    "biomarker_barcode_id": row["barcode_id"],  # barcode kept its ids
                    "biomarker_sample_label": row["label"],
                }
            )
            for row in rows
        ],
    )


def copy_biomarker_result(session: Session) -> None:
    """Copies biomarker results."""
    rows = session.execute(
        sa.text("""
        SELECT
            biomarker_results.id,
            biomarker_results.bio_id,
            biomarker_results.sample_id,
            biomarker_results.value,
            biomarker_results.unit_measure
        FROM public.biomarker_results
        ORDER BY biomarker_results.id
    """)
    ).mappings()
    add_copies(
        session,
        BiomarkerResult,
        [
            BiomarkerResult.model_validate(
                {
                    "id": row["id"],
                    "biomarker_id": row["bio_id"],  # biomarker kept its ids
                    "biomarker_sample_id": row["sample_id"],  # sample kept its ids
                    "biomarker_result_value": row["value"],
                    "measure_unit": row["unit_measure"],
                }
            )
            for row in rows
        ],
    )


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # model tables go to radar3; raw SQL names public.<table> itself
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in (
            Code,
            Biomarker,
            BiomarkerBarcode,
            BiomarkerSample,
            BiomarkerResult,
        ):
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_code(session)
            copy_biomarker(session)
            copy_biomarker_barcode(session)
            copy_biomarker_sample(session)
            copy_biomarker_result(session)
    finally:
        # Alembic records the version on this connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    """Downgrade schema."""
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
