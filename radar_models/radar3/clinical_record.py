"""Treatments, diagnoses, results and imaging."""

from datetime import date, datetime

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- ClinicalLetter --- #


class ClinicalLetterBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    letter_date: date
    letter_comments: str


class ClinicalLetter(ClinicalLetterBase, BigIntPK, table=True):
    __tablename__ = "clinical_letter"


class ClinicalLetterRead(ClinicalLetterBase, HasId):
    pass


# --- Dialysis --- #


class DialysisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    timeline_start: date
    timeline_end: date | None = None
    dialysis_modality_index: int


class Dialysis(DialysisBase, BigIntPK, table=True):
    __tablename__ = "dialysis"


class DialysisRead(DialysisBase, HasId):
    pass


# --- FetalAnomalyScan --- #


class FetalAnomalyScanBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    date_of_scan: date
    gestational_age: int
    has_oligohydramnios: bool
    right_anomaly_details: str | None = None
    right_ultrasound_details: str | None = None
    left_anomaly_details: str | None = None
    left_ultrasound_details: str | None = None
    has_hypoplasia: bool
    has_echogenicity: bool
    has_hepatic_abnormalities: bool
    hepatic_abnormality_details: str | None = None
    has_lung_abnormalities: bool
    lung_abnormality_details: str | None = None
    has_amnioinfusion: bool
    amnioinfusion_count: int | None = None


class FetalAnomalyScan(FetalAnomalyScanBase, BigIntPK, table=True):
    __tablename__ = "fetal_anomaly_scan"


class FetalAnomalyScanRead(FetalAnomalyScanBase, HasId):
    pass


# --- FetalUltrasound --- #


class FetalUltrasoundBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    date_of_scan: date
    fetal_identifier: str | None = None
    gestational_age: int | None = None
    head_centile: int | None = None
    abdomen_centile: int | None = None
    is_uterine_artery_notched: bool
    liquor_volume: str | None = None
    fetal_ultrasound_comment: str | None = None


class FetalUltrasound(FetalUltrasoundBase, BigIntPK, table=True):
    __tablename__ = "fetal_ultrasound"


class FetalUltrasoundRead(FetalUltrasoundBase, HasId):
    pass


# --- Genetics --- #


class GeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    cohort_id: int = Field(foreign_key="cohort.id", sa_type=BigInteger)
    date_sent: datetime
    laboratory: str | None = None
    reference_number: str | None = None
    karyotype_index: int | None = None
    results: str | None = None
    summary: str | None = None


class Genetics(GeneticsBase, BigIntPK, table=True):
    __tablename__ = "genetics"


class GeneticsRead(GeneticsBase, HasId):
    pass


# --- Hospitalisation --- #


class HospitalisationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    date_of_admission: date
    date_of_discharge: date | None = None
    reason_of_admission: str | None = None


class Hospitalisation(HospitalisationBase, BigIntPK, table=True):
    __tablename__ = "hospitalisation"


class HospitalisationRead(HospitalisationBase, HasId):
    pass


# --- LiverDisease --- #


class LiverDiseaseBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    has_portal_hypertension: bool
    portal_hypertension_date: date | None = None
    has_ascites: bool
    ascites_date: date | None = None
    has_oesophageal: bool
    oesophageal_date: date | None = None
    has_oesophageal_bleeding: bool
    oesophageal_bleeding_date: date | None = None
    has_gastric: bool
    gastric_date: date | None = None
    has_gastric_bleeding: bool
    gastric_bleeding_date: date | None = None
    has_anorectal: bool
    anorectal_date: date | None = None
    has_anorectal_bleeding: bool
    anorectal_bleeding_date: date | None = None
    has_cholangitis_acute: bool
    cholangitis_acute_date: date | None = None
    has_cholangitis_recurrent: bool
    cholangitis_recurrent_date: date | None = None
    is_spleen_palpable: bool
    spleen_palpable_date: date | None = None


class LiverDisease(LiverDiseaseBase, BigIntPK, table=True):
    __tablename__ = "liver_disease"


class LiverDiseaseRead(LiverDiseaseBase, HasId):
    pass


# --- LiverImaging --- #


class LiverImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    imaging_date: date
    imaging_type: str
    liver_size: float | None = None
    has_hepatic_fibrosis: bool
    has_hepatic_cysts: bool
    has_bile_duct_cysts: bool
    has_dilated_bile_ducts: bool
    has_cholangitis: bool


class LiverImaging(LiverImagingBase, BigIntPK, table=True):
    __tablename__ = "liver_imaging"


class LiverImagingRead(LiverImagingBase, HasId):
    pass


# --- LiverTransplant --- #


class LiverTransplantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    transplant_hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    registration_date: date | None = None
    transplant_date: date
    other_indications: str | None = None
    first_graft_source: str | None = None
    loss_reason: str | None = None
    other_loss_reason: str | None = None


class LiverTransplant(LiverTransplantBase, BigIntPK, table=True):
    __tablename__ = "liver_transplant"


class LiverTransplantRead(LiverTransplantBase, HasId):
    pass


# --- LiverTransplantIndicator --- #


class LiverTransplantIndicatorBase(SQLModel):
    liver_transplant_id: int = Field(
        foreign_key="liver_transplant.id", sa_type=BigInteger
    )
    indicator_id: int = Field(foreign_key="indicator.id", sa_type=BigInteger)


class LiverTransplantIndicator(LiverTransplantIndicatorBase, BigIntPK, table=True):
    __tablename__ = "liver_transplant_indicator"


class LiverTransplantIndicatorRead(LiverTransplantIndicatorBase, HasId):
    pass


# --- Medication --- #


class MedicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    drug_id: int | None = Field(default=None, foreign_key="drug.id", sa_type=BigInteger)
    snapshot_date: date | None = None
    start_date: date | None = None
    finish_date: date | None = None
    dose_quantity: float | None = None
    dose_unit: str | None = None
    medication_frequency: str | None = None
    medication_route: str | None = None
    drug_text: str | None = None
    dose_text: str | None = None


class Medication(MedicationBase, BigIntPK, table=True):
    __tablename__ = "medication"


class MedicationRead(MedicationBase, HasId):
    pass


# --- Nephrectomy --- #


class NephrectomyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    assessment_date: date
    kidney_side: str
    kidney_type: str
    entry_type: str


class Nephrectomy(NephrectomyBase, BigIntPK, table=True):
    __tablename__ = "nephrectomy"


class NephrectomyRead(NephrectomyBase, HasId):
    pass


# --- Nutrition --- #


class NutritionBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    feeding_type: str
    from_date: date
    to_date: date | None = None


class Nutrition(NutritionBase, BigIntPK, table=True):
    __tablename__ = "nutrition"


class NutritionRead(NutritionBase, HasId):
    pass


# --- Pathology --- #


class PathologyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    report_date: date
    kidney_type: str | None = None
    kidney_side: str | None = None
    reference_number: str | None = None
    image_url: str | None = None
    histological_summary: str | None = None
    em_findings: str | None = None
    report_cleaned_date: date | None = None


class Pathology(PathologyBase, BigIntPK, table=True):
    __tablename__ = "pathology"


class PathologyRead(PathologyBase, HasId):
    pass


# --- PatientDiagnosis --- #


class PatientDiagnosisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    diagnosis_id: int | None = Field(
        default=None, foreign_key="diagnosis.id", sa_type=BigInteger
    )
    diagnosis_text: str | None = None
    symptoms_date: date | None = None
    from_date: date | None = None
    to_date: date | None = None
    snapshot_date: date | None = None
    has_gene_test: bool
    has_biochemistry: bool
    has_assessment: bool
    has_biopsy: bool
    biopsy_diagnosis_index: int | None = None
    diagnosis_comments: str | None = None
    is_prenatal: bool


class PatientDiagnosis(PatientDiagnosisBase, BigIntPK, table=True):
    __tablename__ = "patient_diagnosis"


class PatientDiagnosisRead(PatientDiagnosisBase, HasId):
    pass


# --- Plasmapheresis --- #


class PlasmapheresisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    from_date: date
    to_date: date | None = None
    plasmapheresis_schedule: str | None = None
    plasmapheresis_response: str | None = None


class Plasmapheresis(PlasmapheresisBase, BigIntPK, table=True):
    __tablename__ = "plasmapheresis"


class PlasmapheresisRead(PlasmapheresisBase, HasId):
    pass


# --- Pregnancy --- #


class PregnancyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    pregnancy_number: int
    date_of_lmp: date
    gravidity: int | None = None
    parity1: int | None = None
    parity2: int | None = None
    pregnancy_outcome: str | None = None
    birth_weight: int | None = None
    centile_weight: int | None = None
    gestational_age: int | None = None
    delivery_method: str | None = None
    has_neonatal_intensive_care: bool
    pre_eclampsia: str | None = None


class Pregnancy(PregnancyBase, BigIntPK, table=True):
    __tablename__ = "pregnancy"


class PregnancyRead(PregnancyBase, HasId):
    pass


# --- Procedure --- #


class ProcedureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    procedure_name: str
    other_procedure: str
    date_of_procedure: date


class Procedure(ProcedureBase, BigIntPK, table=True):
    __tablename__ = "procedure"


class ProcedureRead(ProcedureBase, HasId):
    pass


# --- RenalImaging --- #


class RenalImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    assessment_date: datetime | None = None
    imaging_type: str | None = None
    is_right_present: bool
    right_type: str | None = None
    right_length: float | None = None
    right_volume: float | None = None
    has_right_cysts: bool
    has_right_stones: bool
    has_right_calcification: bool
    has_right_nephrocalcinosis: bool
    has_right_nephrolithiasis: bool
    right_other_malformation: str | None = None
    is_left_present: bool
    left_type: str | None = None
    left_length: float | None = None
    left_volume: float | None = None
    has_left_cysts: bool
    has_left_stones: bool
    has_left_calcification: bool
    has_left_nephrocalcinosis: bool
    has_left_nephrolithiasis: bool
    left_other_malformation: str | None = None


class RenalImaging(RenalImagingBase, BigIntPK, table=True):
    __tablename__ = "renal_imaging"


class RenalImagingRead(RenalImagingBase, HasId):
    pass


# --- RenalProgression --- #


class RenalProgressionBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    onset_date: date | None = None
    esrf_date: date | None = None
    ckd5_date: date | None = None
    ckd4_date: date | None = None
    ckd3a_date: date | None = None
    ckd3b_date: date | None = None


class RenalProgression(RenalProgressionBase, BigIntPK, table=True):
    __tablename__ = "renal_progression"


class RenalProgressionRead(RenalProgressionBase, HasId):
    pass


# --- Result --- #


class ResultBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    observation_id: int = Field(foreign_key="observation.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    result_date: datetime
    qualifier: str | None = None
    result_value: str | None = None
    sent_value: str


class Result(ResultBase, BigIntPK, table=True):
    __tablename__ = "result"


class ResultRead(ResultBase, HasId):
    pass


# --- Transplant --- #


class TransplantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    transplant_hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    transplant_date: date
    transplant_modality_index: int
    date_of_recurrence: date | None = None
    date_of_failure: date | None = None
    has_recurrence: bool
    date_of_cmv_infection: date | None = None
    donor_hla: str | None = None
    recipient_hla: str | None = None
    graft_loss_cause: str | None = None


class Transplant(TransplantBase, BigIntPK, table=True):
    __tablename__ = "transplant"


class TransplantRead(TransplantBase, HasId):
    pass


# --- TransplantBiopsy --- #


class TransplantBiopsyBase(SQLModel):
    transplant_id: int = Field(foreign_key="transplant.id", sa_type=BigInteger)
    biopsy_date: date
    has_biopsy_recurrence: bool


class TransplantBiopsy(TransplantBiopsyBase, BigIntPK, table=True):
    __tablename__ = "transplant_biopsy"


class TransplantBiopsyRead(TransplantBiopsyBase, HasId):
    pass


# --- TransplantRejection --- #


class TransplantRejectionBase(SQLModel):
    transplant_id: int = Field(foreign_key="transplant.id", sa_type=BigInteger)
    rejection_date: date


class TransplantRejection(TransplantRejectionBase, BigIntPK, table=True):
    __tablename__ = "transplant_rejection"


class TransplantRejectionRead(TransplantRejectionBase, HasId):
    pass
