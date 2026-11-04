"""Biomarker samples and NURTuRE."""

from datetime import date, datetime

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- BiomarkerBarcode --- #


class BiomarkerBarcodeBase(SQLModel):
    patient_id: int | None = Field(
        default=None, foreign_key="patient.id", sa_type=BigInteger
    )
    barcode: str | None = None
    sample_date: datetime | None = None


class BiomarkerBarcode(BiomarkerBarcodeBase, BigIntPK, table=True):
    __tablename__ = "biomarker_barcode"


class BiomarkerBarcodeRead(BiomarkerBarcodeBase, HasId):
    pass


# --- BiomarkerResult --- #


class BiomarkerResultBase(SQLModel):
    biomarker_id: int | None = Field(
        default=None, foreign_key="biomarker.id", sa_type=BigInteger
    )
    biomarker_sample_id: int | None = Field(
        default=None, foreign_key="biomarker_sample.id", sa_type=BigInteger
    )
    biomarker_result_value: float | None = None
    measure_unit: str | None = None


class BiomarkerResult(BiomarkerResultBase, BigIntPK, table=True):
    __tablename__ = "biomarker_result"


class BiomarkerResultRead(BiomarkerResultBase, HasId):
    pass


# --- BiomarkerSample --- #


class BiomarkerSampleBase(SQLModel):
    biomarker_barcode_id: int | None = Field(
        default=None, foreign_key="biomarker_barcode.id", sa_type=BigInteger
    )
    biomarker_sample_label: str


class BiomarkerSample(BiomarkerSampleBase, BigIntPK, table=True):
    __tablename__ = "biomarker_sample"


class BiomarkerSampleRead(BiomarkerSampleBase, HasId):
    pass


# --- NurtureFamilyHistory --- #


class NurtureFamilyHistoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    has_eskd: bool
    eskd_relative_1_index: int
    eskd_relative_2_index: int
    eskd_relative_3_index: int
    has_chd: bool
    chd_relative_1_index: int
    chd_relative_2_index: int
    chd_relative_3_index: int
    has_diabetes: bool
    diabetes_relative_1_index: int
    diabetes_relative_2_index: int
    diabetes_relative_3_index: int


class NurtureFamilyHistory(NurtureFamilyHistoryBase, BigIntPK, table=True):
    __tablename__ = "nurture_family_history"


class NurtureFamilyHistoryRead(NurtureFamilyHistoryBase, HasId):
    pass


# --- NurtureMetadata --- #


class NurtureMetadataBase(SQLModel):
    patient_id: int | None = Field(
        default=None, foreign_key="patient.id", sa_type=BigInteger
    )
    signed_off_state_index: int | None = None
    follow_up_refused_date: date | None = None
    has_blood_tests: bool
    blood_refused_date: date | None = None
    has_interviews: bool
    interviews_refused_date: date | None = None


class NurtureMetadata(NurtureMetadataBase, BigIntPK, table=True):
    __tablename__ = "nurture_metadata"


class NurtureMetadataRead(NurtureMetadataBase, HasId):
    pass


# --- NurtureVisit --- #


class NurtureVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    visit_date: date
    nurture_visit_number: int
    comorbidities: int
    has_flu_vaccination: bool
    has_pneumococcal_vaccination: bool
    has_admission: bool
    admission_number: int
    admission_emergency: int
    admission_planned: int
    admission_days: int
    admission_antibiotics: int
    paracetamol_tablets: int
    paracetamol_years: int
    cocodamol_tablets: int
    cocodamol_years: int
    ibuprofen_tablets: int
    ibuprofen_years: int


class NurtureVisit(NurtureVisitBase, BigIntPK, table=True):
    __tablename__ = "nurture_visit"


class NurtureVisitRead(NurtureVisitBase, HasId):
    pass


# --- SampleInventory --- #


class SampleInventoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    sample_date: date
    has_urine_sample: bool
    urine_date: date
    urine_volume: str
    has_serum_sample: bool
    serum_date: date
    serum_volume: str
    has_plasma_sample: bool
    plasma_date: date
    plasma_volume: str
    has_dna_sample: bool
    dna_date: date
    has_sputum_sample: bool
    sputum_date: date
    has_faeces_sample: bool
    faeces_date: date


class SampleInventory(SampleInventoryBase, BigIntPK, table=True):
    __tablename__ = "sample_inventory"


class SampleInventoryRead(SampleInventoryBase, HasId):
    pass


# --- TubeSample --- #


class TubeSampleBase(SQLModel):
    patient_id: int | None = Field(
        default=None, foreign_key="patient.id", sa_type=BigInteger
    )
    sample_date: date
    barcode: str
    ins_state_index: int | None = None


class TubeSample(TubeSampleBase, BigIntPK, table=True):
    __tablename__ = "tube_sample"


class TubeSampleRead(TubeSampleBase, HasId):
    pass
