from datetime import datetime, date
from typing import Optional, ClassVar, Union, Callable

from sqlalchemy import Column, BigInteger
from sqlmodel import SQLModel, Field


# --- AlportClinicalPicture --- #


class AlportClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", index=True)
    date_of_picture: date
    deafness_index: int
    deafness_date: Optional[date]
    hearing_aid_date: Optional[date]


class AlportClinicalPicture(AlportClinicalPictureBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "alport_clinical_picture"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class AlportClinicalPictureCreate(AlportClinicalPictureBase):
    pass


class AlportClinicalPictureRead(AlportClinicalPictureBase):
    id: int


# --- Biomarker --- #


class BiomarkerBase(SQLModel):
    biomarker_name: str
    biomarker_type: str


class Biomarker(BiomarkerBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class BiomarkerCreate(BiomarkerBase):
    pass


class BiomarkerRead(BiomarkerBase):
    id: int


# --- BiomarkerBarcode --- #


class BiomarkerBarcodeBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    barcode: str
    sample_date: datetime


class BiomarkerBarcode(BiomarkerBarcodeBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "biomarker_barcode"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class BiomarkerBarcodeCreate(BiomarkerBarcodeBase):
    pass


class BiomarkerBarcodeRead(BiomarkerBarcodeBase):
    id: int


# --- BiomarkerResult --- #


class BiomarkerResultBase(SQLModel):
    biomarker_id: int = Field(foreign_key="biomarker.id")
    biomarker_sample_id: int = Field(foreign_key="biomarker_sample.id")
    biomarker_result_value: float
    # TODO: Create a unit_of_measure table to hold this
    measure_unit: str


class BiomarkerResult(BiomarkerResultBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "biomarker_result"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class BiomarkerResultCreate(BiomarkerResultBase):
    pass


class BiomarkerResultRead(BiomarkerResultBase):
    id: int


# --- BiomarkerSample --- #


class BiomarkerSampleBase(SQLModel):
    barcode_id: int = Field(foreign_key="biomarker_barcode.id")
    biomarker_sample_label: str


class BiomarkerSample(BiomarkerSampleBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "biomarker_sample"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class BiomarkerSampleCreate(BiomarkerSampleBase):
    pass


class BiomarkerSampleRead(BiomarkerSampleBase):
    id: int


# --- Code --- #
# TODO: check current indexes and check constraints


class CodeBase(SQLModel):
    coding_system: str
    code: str
    code_label: str


class Code(CodeBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CodeCreate(CodeBase):
    pass


class CodeRead(CodeBase):
    id: int


# --- Cohort --- #


class CohortBase(SQLModel):
    cohort_code: str
    cohort_name: str
    cohort_short_name: str


class Cohort(CohortBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CohortCreate(CohortBase):
    pass


class CohortRead(CohortBase):
    id: int


# --- CohortDiagnose --- #


class CohortDiagnosisBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    diagnosis_type: int = Field(foreign_key="option.id")


class CohortDiagnosis(CohortDiagnosisBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "cohort_diagnosis"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CohortDiagnosisCreate(CohortDiagnosisBase):
    pass


class CohortDiagnosisRead(CohortDiagnosisBase):
    id: int


# --- CohortPatient --- #


class CohortPatientBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    patient_id: int = Field(foreign_key="patient.id")
    recruited_date: date
    removed_date: Optional[date]


class CohortPatient(CohortPatientBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "cohort_patient"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CohortPatientCreate(CohortPatientBase):
    pass


class CohortPatientRead(CohortPatientBase):
    id: int


# --- CohortObservation --- #


class CohortObservationBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    observation_id: int = Field(foreign_key="observation.id")
    weight: int


class CohortObservation(CohortObservationBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "cohort_observation"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CohortObservationCreate(CohortObservationBase):
    pass


class CohortObservationRead(CohortObservationBase):
    id: int


# --- Consent --- #


class ConsentBase(SQLModel):
    consent_code: str
    consent_label: Optional[str]
    is_paediatric: bool = Field(default=False)
    release_date: date
    consent_url: str
    is_retired: bool = Field(default=False)


class Consent(ConsentBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class ConsentCreate(ConsentBase):
    pass


class ConsentRead(ConsentBase):
    id: int


# --- Consultant --- #
# TODO: Composite index


class ConsultantBase(SQLModel):
    specialty_id: int = Field(foreign_key="specialty.id")
    first_name: str
    last_name: str
    email: Optional[str]
    telephone_number: Optional[str]
    gmc_number: Optional[int]


class Consultant(ConsultantBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class ConsultantCreate(ConsultantBase):
    pass


class ConsultantRead(ConsultantBase):
    id: int


# --- Country --- #


class CountryBase(SQLModel):
    country_name: str
    country_code: str


class Country(CountryBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    id: int


# --- CountryEthnicity --- #


class CountryEthnicityBase(SQLModel):
    ethnicity_id: int = Field(foreign_key="ethnicity.id")
    country_id: int = Field(foreign_key="country.id")


class CountryEthnicity(CountryEthnicityBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "country_ethnicity"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CountryEthnicityCreate(CountryEthnicityBase):
    pass


class CountryEthnicityRead(CountryEthnicityBase):
    id: int


# --- CountryNationality --- #


class CountryNationalityBase(SQLModel):
    nationality_id: int = Field(foreign_key="nationality.id")
    country_id: int = Field(foreign_key="country.id")


class CountryNationality(CountryNationalityBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "country_nationality"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class CountryNationalityCreate(CountryNationalityBase):
    pass


class CountryNationalityRead(CountryNationalityBase):
    id: int


# --- DataSource --- #


class DataSourceBase(SQLModel):
    data_source_name: str


class DataSource(DataSourceBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "data_source"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceRead(DataSourceBase):
    id: int


# --- Diagnoses --- #


class DiagnosisBase(SQLModel):
    diagnosis_name: str
    is_retired: bool = Field(default=False)


class Diagnosis(DiagnosisBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DiagnosisCreate(DiagnosisBase):
    pass


class DiagnosisRead(DiagnosisBase):
    id: int


# --- DiagnosisCode --- #
# TODO: composite index


class DiagnosisCodeBase(SQLModel):
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    code_id: int = Field(foreign_key="code.id")


class DiagnosisCode(DiagnosisCodeBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "diagnosis_code"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DiagnosisCodeCreate(DiagnosisCodeBase):
    pass


class DiagnosisCodeRead(DiagnosisCodeBase):
    id: int


# --- Dialysis --- #


class DialysisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    timeline_start: date
    timeline_end: Optional[date]
    modality: int


class Dialysis(DialysisBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DialysisCreate(DialysisBase):
    pass


class DialysisRead(DialysisBase):
    id: int


# --- Drug --- #


class DrugBase(SQLModel):
    drug_name: str
    drug_group_id: Optional[int] = Field(foreign_key="drug_group.id")


class Drug(DrugBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DrugCreate(DrugBase):
    pass


class DrugRead(DrugBase):
    id: int


# --- DrugGroup --- #


class DrugGroupBase(SQLModel):
    drug_group: Optional[str] = Field(unique=True)
    # TODO: Check that everything in here makes sense
    parent_drug_group_id: Optional[int] = Field(foreign_key="drug_group.id")


class DrugGroup(DrugGroupBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "drug_group"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class DrugGroupCreate(DrugGroupBase):
    pass


class DrugGroupRead(DrugGroupBase):
    id: int


# --- Ethnicity --- #


class EthnicityBase(SQLModel):
    ethnicity_code: str
    ethnicity_label: str


class Ethnicity(EthnicityBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class EthnicityCreate(EthnicityBase):
    pass


class EthnicityRead(EthnicityBase):
    id: int


# --- FamilyHistory --- #


class FamilyHistoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    relation_id: int = Field(foreign_key="relation.id")
    relation_patient_id: int = Field(foreign_key="patient.id")
    has_condition: bool


class FamilyHistory(FamilyHistoryBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "family_history"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class FamilyHistoryCreate(FamilyHistoryBase):
    pass


class FamilyHistoryRead(FamilyHistoryBase):
    id: int


# --- FetalAnomalyScan --- #


class FetalAnomalyScanBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    date_of_scan: date
    gestational_age: int
    oligohydramnios: bool
    right_anomaly_details: Optional[str]
    right_ultrasound_details: Optional[str]
    left_anomaly_details: Optional[str]
    left_ultrasound_details: Optional[str]
    hypoplasia: Optional[bool]
    echogenicity: Optional[bool]
    hepatic_abnormalities: Optional[bool]
    hepatic_abnormality_details: Optional[str]
    lung_abnormalities: Optional[bool]
    lung_abnormality_details: Optional[str]
    amnioinfusion: Optional[bool]
    amnioinfusion_count: Optional[int]


class FetalAnomalyScan(FetalAnomalyScanBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "fetal_anomaly_scan"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class FetalAnomalyScanCreate(FetalAnomalyScanBase):
    pass


class FetalAnomalyScanRead(FetalAnomalyScanBase):
    id: int


# --- FetalUltrasound --- #


class FetalUltrasoundBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    date_of_scan: date
    fetal_identifier: Optional[str]
    gestational_age: int
    head_centile: Optional[int]
    abdomen_centile: Optional[int]
    uterine_artery_notched: Optional[bool]
    liquor_volume: Optional[str]
    fetal_ultrasound_comment: Optional[str]


class FetalUltrasound(FetalUltrasoundBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "fetal_ultrasound"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class FetalUltrasoundCreate(FetalUltrasoundBase):
    pass


class FetalUltrasoundRead(FetalUltrasoundBase):
    id: int


# --- FuanClinicalPicture --- #


class FuanClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    picture_date: date
    gout: bool
    gout_date: Optional[date]
    family_gout: Optional[bool]
    thp: Optional[str]
    uti: Optional[bool]
    comments: Optional[str]


class FuanClinicalPicture(FuanClinicalPictureBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "fuan_clinical_picture"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class FuanClinicalPictureCreate(FuanClinicalPictureBase):
    pass


class FuanClinicalPictureRead(FuanClinicalPictureBase):
    id: int


# --- Genetics --- #


class GeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    cohort_id: int = Field(foreign_key="cohort.id")
    date_sent: datetime
    laboratory: str
    reference_number: Optional[str]
    karyotype: Optional[int]
    results: Optional[str]
    summary: Optional[str]


class Genetics(GeneticsBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class GeneticsCreate(GeneticsBase):
    pass


class GeneticsRead(GeneticsBase):
    id: int


# --- Hnf1bClinicalPicture --- #


class Hnf1bClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    single_kidney: bool
    hyperuricemia_gout: bool
    genital_malformation: bool
    genital_malformation_details: str
    familial_cystic_disease: bool
    hypertension: bool


class Hnf1bClinicalPicture(Hnf1bClinicalPictureBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "hnf1b_clinical_picture"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class Hnf1bClinicalPictureCreate(Hnf1bClinicalPictureBase):
    pass


class Hnf1bClinicalPictureRead(Hnf1bClinicalPictureBase):
    id: int


# --- Hospital --- #


class HospitalBase(SQLModel):
    hospital_code: str
    hospital_name: str
    hospital_short_name: str
    is_transplant_centre: bool


class Hospital(HospitalBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class HospitalCreate(HospitalBase):
    pass


class HospitalRead(HospitalBase):
    id: int


# --- Hospitalisation --- #


# TODO: Discharge and admission are currently datetime. Will need converting
class HospitalisationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    date_of_admission: date
    date_of_discharge: Optional[date]
    reason_of_admission: Optional[str]


class Hospitalisation(HospitalisationBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class HospitalisationCreate(HospitalisationBase):
    pass


class HospitalisationRead(HospitalisationBase):
    id: int


# --- HospitalConsultant --- #


class HospitalConsultantBase(SQLModel):
    hospital_id: int = Field(foreign_key="hospital.id")
    consultant_id: int = Field(foreign_key="consultant.id")


class HospitalConsultant(HospitalConsultantBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "hospital_consultant"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class HospitalConsultantCreate(HospitalConsultantBase):
    pass


class HospitalConsultantRead(HospitalConsultantBase):
    id: int


# --- HospitalPatient --- #


class HospitalPatientBase(SQLModel):
    hospital_id: int = Field(foreign_key="hospital.id")
    patient_id: int = Field(foreign_key="patient.id")
    first_seen_date: date
    discharged_date: Optional[date]


class HospitalPatient(HospitalPatientBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "hospital_patient"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class HospitalPatientCreate(HospitalPatientBase):
    pass


class HospitalPatientRead(HospitalPatientBase):
    id: int


# --- Indicators --- #


class IndicatorBase(SQLModel):
    indicator_label: str


class Indicator(IndicatorBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorRead(IndicatorBase):
    id: int


# --- InsClinicalPicture --- #


class InsClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    oedema: Optional[bool]
    hypovalaemia: Optional[bool]
    fever: Optional[bool]
    thrombosis: Optional[bool]
    peritonitis: Optional[bool]
    pulmonary_odemea: Optional[bool]
    hypertension: Optional[bool]
    rash: Optional[bool]
    rash_details: Optional[str]
    infection: Optional[bool]
    infection_details: Optional[str]
    ophthalmoscopy: Optional[bool]
    ophthalmoscopy_details: Optional[str]
    comments: Optional[str]


class InsClinicalPicture(InsClinicalPictureBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "ins_clinical_picture"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class InsClinicalPictureCreate(InsClinicalPictureBase):
    pass


class InsClinicalPictureRead(InsClinicalPictureBase):
    id: int


# --- InsRelapse --- #


class InsRelapseBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_relapse: date
    kidney_type: Optional[str]
    viral_trigger: Optional[str]
    immunisation_trigger: Optional[str]
    other_trigger: Optional[str]
    high_dose_oral_prednisolone: Optional[bool]
    iv_methyl_prednisolone: Optional[bool]
    date_of_remission: date
    remission_type: Optional[str]
    peak_acr: Optional[float]
    peak_pcr: Optional[float]
    remission_acr: Optional[float]
    remission_pcr: Optional[float]
    peak_protein_dipstick: Optional[str]
    remission_protein_dipstick: Optional[str]
    relapse_sample_taken: Optional[bool]


class InsRelapse(InsRelapseBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "ins_relapse"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class InsRelapseCreate(InsRelapseBase):
    pass


class InsRelapseRead(InsRelapseBase):
    id: int


# --- LiverDisease --- #


class LiverDiseaseBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    portal_hypertension: Optional[bool]
    portal_hypertension_date: Optional[date]
    ascites: Optional[bool]
    ascites_date: Optional[date]
    oesophageal: Optional[bool]
    oesophageal_date: Optional[date]
    oesophageal_bleeding: Optional[bool]
    oesophageal_bleeding_date: Optional[date]
    gastric: Optional[bool]
    gastric_date: Optional[date]
    gastric_bleeding: Optional[bool]
    gastric_bleeding_date: Optional[date]
    anorectal: Optional[bool]
    anorectal_date: Optional[date]
    anorectal_bleeding: Optional[bool]
    anorectal_bleeding_date: Optional[date]
    cholangitis_acute: Optional[bool]
    cholangitis_acute_date: Optional[date]
    cholangitis_recurrent: Optional[bool]
    cholangitis_recurrent_date: Optional[date]
    spleen_palpable: Optional[bool]
    spleen_palpable_date: Optional[date]


class LiverDisease(LiverDiseaseBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "liver_disease"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class LiverDiseaseCreate(LiverDiseaseBase):
    pass


class LiverDiseaseRead(LiverDiseaseBase):
    id: int


# --- LiverImaging --- #


# TODO:
class LiverImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    imaging_date: date
    imaging_type: str
    # TODO: Originally labelled size. Check this is actually referring to liver size.
    liver_size: Optional[float]
    hepatic_fibrosis: Optional[bool]
    hepatic_cysts: Optional[bool]
    bile_duct_cysts: Optional[bool]
    dilated_bile_ducts: Optional[bool]
    cholangitis: Optional[bool]


class LiverImaging(LiverImagingBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "liver_imaging"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class LiverImagingCreate(LiverImagingBase):
    pass


class LiverImagingRead(LiverImagingBase):
    id: int


# --- LiverTransplant --- #


class LiverTransplantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    transplant_group_id: int = Field(foreign_key="hospital.id")
    registration_date: date
    transplant_date: date
    other_indications: str
    first_graft_source: str
    loss_reason: str
    other_loss_reason: str


class LiverTransplant(LiverTransplantBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "liver_transplant"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class LiverTransplantCreate(LiverTransplantBase):
    pass


class LiverTransplantRead(LiverTransplantBase):
    id: int


# --- LiverTransplantIndicator --- #


class LiverTransplantIndicatorBase(SQLModel):
    liver_transplant_id: int = Field(foreign_key="liver_transplant.id")
    indicator_id: int = Field(foreign_key="indicator.id")


class LiverTransplantIndicator(LiverTransplantIndicatorBase, table=True):
    __tablename__: ClassVar[
        Union[str, Callable[..., str]]
    ] = "liver_transplant_indicator"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class LiverTransplantIndicatorCreate(LiverTransplantIndicatorBase):
    pass


class LiverTransplantIndicatorRead(LiverTransplantIndicatorBase):
    id: int


# --- Medication --- #


class MedicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    drug_id: int = Field(foreign_key="drug.id")
    start_date: date
    finish_date: Optional[date]
    dose_quantity: Optional[float]
    dose_unit: str
    frequency: str
    route: str
    drug_text: str
    dose_text: str


class Medication(MedicationBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    id: int


# --- MpgnClinicalPicture --- #


class MpgnClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    oedema: bool
    hypertension: bool
    urticaria: bool
    partial_lipodystrophy: bool
    infection: bool
    infection_details: str
    ophthalmoscopy: bool
    ophthalmoscopy_details: str
    comments: str


class MpgnClinicalPicture(MpgnClinicalPictureBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "mpgn_clinical_picture"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class MpgnClinicalPictureCreate(MpgnClinicalPictureBase):
    pass


class MpgnClinicalPictureRead(MpgnClinicalPictureBase):
    id: int


# --- Nationality --- #


class NationalityBase(SQLModel):
    nationality_label: str


class Nationality(NationalityBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class NationalityCreate(NationalityBase):
    pass


class NationalityRead(NationalityBase):
    id: int


# # # --- Nephrectomy --- #


# # class NephrectomyBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: date
# #     kidney_side: str
# #     kidney_type: str
# #     entry_type: str


# # class Nephrectomy(NephrectomyBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class NephrectomyCreate(NephrectomyBase):
# #     pass


# # class NephrectomyRead(NephrectomyBase):
# #     id: int


# # # --- NurtureDatum --- #


# # class NurtureDatumBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     signed_off_state: int
# #     follow_up_refused_date: date
# #     blood_tests: bool
# #     blood_refused_date: date
# #     interviews: bool
# #     interviews_refused_date: date


# # class NurtureDatum(NurtureDatumBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class NurtureDatumCreate(NurtureDatumBase):
# #     pass


# # class NurtureDatumRead(NurtureDatumBase):
# #     id: int


# # # --- NurtureSample --- #


# # class NurtureSampleBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     taken_on: date
# #     barcode: int
# #     epa: int
# #     epb: int
# #     lpa: int
# #     lpb: int
# #     uc: int
# #     ub: int
# #     ud: int
# #     fub: int
# #     sc: int
# #     sa: int
# #     sb: int
# #     rna: int
# #     wb: int


# # class NurtureSample(NurtureSampleBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class NurtureSampleCreate(NurtureSampleBase):
# #     pass


# # class NurtureSampleRead(NurtureSampleBase):
# #     id: int


# # # --- NurtureSamplesBlood --- #


# # class NurtureSamplesBloodBase(SQLModel):
# #     sample_id: str = Field(primary_key=True)
# #     sample_date: datetime
# #     radar_id: str
# #     bnp: str
# #     creat: str
# #     crp: str
# #     cyst: str
# #     gdf15: str
# #     trop: str
# #     ins_state: int
# #     comments_label: str
# #     comments_sample: str


# # class NurtureSamplesBlood(NurtureSamplesBloodBase, table=True):
# #     pass


# # class NurtureSamplesBloodCreate(NurtureSamplesBloodBase):
# #     pass


# # class NurtureSamplesBloodRead(NurtureSamplesBloodBase):
# #     pass


# # # --- NurtureSamplesOption --- #

# # # TODO: Figure out if and where this table is being used


# # class NurtureSampleOptionEnum(str, enum.Enum):
# #     adult_ns = "ADULT_NS"
# #     adult_ckd = "ADULT_CKD"
# #     children_15_2nd = "CHILDREN15_2ND"
# #     children_15_b = "CHILDREN15_B"
# #     children_less_15_2nd = "CHILDREN_LESS_15_2ND"
# #     children_less_15_b = "CHILDREN_LESS_15_B"
# #     children_30_2nd = "CHILDREN30_2ND"
# #     children_30_b = "CHILDREN30_B"


# # class NurtureSamplesOptionBase(SQLModel):
# #     id: NurtureSampleOptionEnum = Field(
# #         sa_column=Column(Enum(NurtureSampleOptionEnum)), primary_key=True
# #     )
# #     label: str
# #     epa: int
# #     epb: int
# #     lpa: int
# #     lpb: int
# #     uc: int
# #     ub: int
# #     ud: int
# #     fub: int
# #     sc: int
# #     sa: int
# #     sb: int
# #     rna: int
# #     wb: int


# # class NurtureSamplesOption(NurtureSamplesOptionBase, table=True):
# #     pass


# # class NurtureSamplesOptionCreate(NurtureSamplesOptionBase):
# #     pass


# # class NurtureSamplesOptionRead(NurtureSamplesOptionBase):
# #     pass


# # # --- NurtureSamplesUrine --- #


# # class NurtureSamplesUrineBase(SQLModel):
# #     sample_id: str = Field(primary_key=True)
# #     sample_date: datetime
# #     radar_id: str
# #     albumin: str
# #     creatinin: str
# #     ins_state: int
# #     comments_label: str
# #     comments_sample: str


# # class NurtureSamplesUrine(NurtureSamplesUrineBase, table=True):
# #     pass


# # class NurtureSamplesUrineCreate(NurtureSamplesUrineBase):
# #     pass


# # class NurtureSamplesUrineRead(NurtureSamplesUrineBase):
# #     pass


# # # --- Nutrition --- #


# # class NutritionBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     feeding_type: str
# #     from_date: date
# #     to_date: date


# # class Nutrition(NutritionBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class NutritionCreate(NutritionBase):
# #     pass


# # class NutritionRead(NutritionBase):
# #     id: int


# --- Observation --- #


class ObservationBase(SQLModel):
    sample_type_id: int = Field(foreign_key="sample_type.id")
    name: str
    short_name: str
    min_value: int
    max_value: int
    units: str


class Observation(ObservationBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class ObservationCreate(ObservationBase):
    pass


class ObservationRead(ObservationBase):
    id: int


# --- ObservationCode --- #


class ObservationCodeBase(SQLModel):
    observation_id: int = Field(foreign_key="observation.id")
    code_id: int = Field(foreign_key="code.id")


class ObservationCode(ObservationCodeBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "observation_code"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class ObservationCodeCreate(ObservationCodeBase):
    pass


class ObservationCodeRead(ObservationCodeBase):
    id: int


# --- ObservationOptions --- #


class ObservationOptionsBase(SQLModel):
    observation_id: int
    option_id: int


class ObservationOption(ObservationOptionsBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "observation_option"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class ObservationOptionCreate(ObservationOptionsBase):
    pass


class ObservationOptionRead(ObservationOptionsBase):
    id: int


# --- Options --- #


class OptionBase(SQLModel):
    option_label: str


class Option(OptionBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class OptionCreate(OptionBase):
    pass


class OptionRead(OptionBase):
    id: int


# # # --- Pathology --- #


# # class PathologyBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: date
# #     kidney_type: str
# #     kidney_side: str
# #     reference_number: str
# #     image_url: str
# #     histological_summary: str
# #     em_findings: str


# # class Pathology(PathologyBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PathologyCreate(PathologyBase):
# #     pass


# # class PathologyRead(PathologyBase):
# #     id: int


# # --- Patient --- #


class PatientBase(SQLModel):
    patient_comment: Optional[str]
    is_test: bool = Field(default=False)
    is_control: bool = Field(default=False)


class Patient(PatientBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int


# # # --- PatientAddress --- #


# # class PatientAddressBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     from_date: date
# #     to_date: date
# #     address1: str
# #     address2: str
# #     address3: str
# #     address4: str
# #     postcode: str
# #     country: str


# # class PatientAddress(PatientAddressBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientAddressCreate(PatientAddressBase):
# #     pass


# # class PatientAddressRead(PatientAddressBase):
# #     id: int


# # # --- PatientAliase --- #


# # class PatientAliaseBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     first_name: str
# #     last_name: str


# # class PatientAliase(PatientAliaseBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientAliaseCreate(PatientAliaseBase):
# #     pass


# # class PatientAliaseRead(PatientAliaseBase):
# #     id: int


# # # --- PatientConsent --- #


# # class PatientConsentBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     consent_id: int = Field(foreign_key="consents.id")
# #     signed_on_date: date
# #     withdrawn_on_date: Optional[date]
# #     reconsent_letter_returned_date: date
# #     reconsent_letter_sent_date: date


# # class PatientConsent(PatientConsentBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientConsentCreate(PatientConsentBase):
# #     pass


# # class PatientConsentRead(PatientConsentBase):
# #     id: int


# # # --- PatientConsultant --- #


# # class PatientConsultantBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     consultant_id: int = Field(foreign_key="consultants.id")
# #     from_date: date
# #     to_date: Optional[date]


# # class PatientConsultant(PatientConsultantBase, table=True):
# #     id: int = Field(default=None, primary_key=True)


# # class PatientConsultantCreate(PatientConsultantBase):
# #     pass


# # class PatientConsultantRead(PatientConsultantBase):
# #     id: int


# # # --- PatientDemographic --- #


# # class PatientDemographicBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     ethnicity_id: int = Field(foreign_key="ethnicities.id")
# #     nationality_id: Field(foreign_key="nationalities.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     first_name: str
# #     last_name: str
# #     date_of_birth: date
# #     date_of_death: date
# #     gender: int
# #     home_number: str
# #     work_number: str
# #     mobile_number: str
# #     email_address: str
# #     cause_of_death: str


# # class PatientDemographic(PatientDemographicBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientDemographicCreate(PatientDemographicBase):
# #     pass


# # class PatientDemographicRead(PatientDemographicBase):
# #     id: int


# # # --- PatientDiagnose --- #


# # class PatientDiagnoseBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     diagnosis_id: int = Field(foreign_key="diagnoses.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     diagnosis_text: str
# #     symptoms_date: date
# #     from_date: date
# #     to_date: date
# #     gene_test: bool
# #     biochemistry: bool
# #     clinical_picture: bool
# #     biopsy: bool
# #     biopsy_diagnosis: int
# #     comments: str
# #     prenatal: bool


# # class PatientDiagnose(PatientDiagnoseBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientDiagnoseCreate(PatientDiagnoseBase):
# #     pass


# # class PatientDiagnoseRead(PatientDiagnoseBase):
# #     id: int


# # # --- PatientLock --- #


# # class PatientLockBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     sequence_number: int


# # class PatientLock(PatientLockBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientLockCreate(PatientLockBase):
# #     pass


# # class PatientLockRead(PatientLockBase):
# #     id: int


# # # --- PatientNumber --- #


# # class PatientNumberBase(SQLModel):

# #     patient_id: int = Field(foreign_key="patient.id", index=True)
# #     source_group_id: int = Field(foreign_key="groups.id", index=True)
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     number_group_id: int = Field(foreign_key="groups.id", index=True)
# #     number: str


# # class PatientNumber(PatientNumberBase):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PatientNumberCreate(PatientBase):
# #     pass


# # class PatientNumberRead(PatientBase):
# #     id: int


# # # --- Plasmapheresi --- #


# # class PlasmapheresiBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     from_date: date
# #     to_date: date
# #     # TODO: rename to just exchanges
# #     no_of_exchanges: str
# #     response: str


# # class Plasmapheresi(PlasmapheresiBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PlasmapheresiCreate(PlasmapheresiBase):
# #     pass


# # class PlasmapheresiRead(PlasmapheresiBase):
# #     id: int


# # # --- Post --- #


# # class PostBase(SQLModel):
# #     title: str
# #     published_date: datetime
# #     body: str


# # class Post(PostBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PostCreate(PostBase):
# #     pass


# # class PostRead(PostBase):
# #     id: int


# # # --- Pregnancy --- #


# # class PregnancyBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     pregnancy_number: int
# #     date_of_lmp: date
# #     gravidity: int
# #     parity1: int
# #     parity2: int
# #     outcome: str
# #     weight: int
# #     weight_centile: int
# #     gestational_age: int
# #     delivery_method: str
# #     neonatal_intensive_care: bool
# #     pre_eclampsia: str


# # class Pregnancy(PregnancyBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class PregnancyCreate(PregnancyBase):
# #     pass


# # class PregnancyRead(PregnancyBase):
# #     id: int

# --- Relation --- #


class RelationBase(SQLModel):
    relationship: str


class Relation(RelationBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class RelationCreate(RelationBase):
    pass


class RelationRead(RelationBase):
    id: int


# # # --- RenalImaging --- #


# # class RenalImagingBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: datetime
# #     imaging_type: str
# #     right_present: bool
# #     right_type: str
# #     right_length: int
# #     right_volume: int
# #     right_cysts: bool
# #     right_stones: bool
# #     right_calcification: bool
# #     right_nephrocalcinosis: bool
# #     right_nephrolithiasis: bool
# #     right_other_malformation: str
# #     left_present: bool
# #     left_type: str
# #     left_length: int
# #     left_volume: int
# #     left_cysts: bool
# #     left_stones: bool
# #     left_calcification: bool
# #     left_nephrocalcinosis: bool
# #     left_nephrolithiasis: bool
# #     left_other_malformation: str


# # class RenalImaging(RenalImagingBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class RenalImagingCreate(RenalImagingBase):
# #     pass


# # class RenalImagingRead(RenalImagingBase):
# #     id: int


# # # --- RenalProgression --- #


# # class RenalProgressionBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     onset_date: date
# #     esrf_date: date
# #     ckd5_date: date
# #     ckd4_date: date
# #     ckd3a_date: date
# #     ckd3b_date: date


# # class RenalProgression(RenalProgressionBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class RenalProgressionCreate(RenalProgressionBase):
# #     pass


# # class RenalProgressionRead(RenalProgressionBase):
# #     id: int


# # # --- Result --- #


# # class ResultBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: datetime
# #     value: str


# # class Result(ResultBase):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class ResultCreate(ResultBase):
# #     pass


# # class ResultRead(ResultBase):
# #     id: int


# # # --- RituximabBaselineAssessment --- #


# # class RituximabBaselineAssessmentBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: date
# #     nephropathy: str
# #     # TODO: More array madness
# #     supportive_medication: set = Field(sa_column=Column(Array(str)))
# #     # TODO: More json
# #     previous_treatment: dict = Field(sa_column=Column(Array(str)))
# #     steroids: bool
# #     other_previous_treatment: str
# #     past_remission: bool
# #     performance_status: int
# #     comorbidities: bool


# # class RituximabBaselineAssessment(RituximabBaselineAssessmentBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class RituximabBaselineAssessmentCreate(RituximabBaselineAssessmentBase):
# #     pass


# # class RituximabBaselineAssessmentRead(RituximabBaselineAssessmentBase):
# #     id: int


# # # --- RituximabCriterion --- #


# # class RituximabCriterionBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     date: date
# #     criteria1: bool
# #     criteria2: bool
# #     criteria3: bool
# #     criteria4: bool
# #     criteria5: bool
# #     criteria6: bool
# #     criteria7: bool
# #     alkylating_complication: bool
# #     alkylating_failure_monitoring_requirements: bool
# #     cancer: bool
# #     cni_failure_monitoring_requirements: bool
# #     cni_therapy_complication: bool
# #     diabetes: bool
# #     drug_associated_toxicity: bool
# #     fall_in_egfr: bool
# #     hypersensitivity: bool
# #     risk_factors: bool
# #     ongoing_severe_disease: bool
# #     threatened_fertility: bool
# #     mood_disturbance: bool
# #     osteoporosis_osteopenia: bool
# #     previous_hospitalization: bool


# # class RituximabCriterion(RituximabCriterionBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class RituximabCriterionCreate(RituximabCriterionBase):
# #     pass


# # class RituximabCriterionRead(RituximabCriterionBase):
# #     id: int


# # # --- SaltWastingClinicalFeature --- #


# # class SaltWastingClinicalFeatureBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     normal_pregnancy: bool
# #     abnormal_pregnancy_text: str
# #     neurological_problems: bool
# #     seizures: bool
# #     abnormal_gait: bool
# #     deafness: bool
# #     other_neurological_problem: bool
# #     other_neurological_problem_text: str
# #     joint_problems: bool
# #     joint_problems_age: int
# #     x_ray_abnormalities: bool
# #     chondrocalcinosis: bool
# #     other_x_ray_abnormality: bool
# #     other_x_ray_abnormality_text: str


# # class SaltWastingClinicalFeature(SaltWastingClinicalFeatureBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class SaltWastingClinicalFeatureCreate(SaltWastingClinicalFeatureBase):
# #     pass


# # class SaltWastingClinicalFeatureRead(SaltWastingClinicalFeatureBase):
# #     id: int


# --- SampleType --- #


class SampleTypeBase(SQLModel):
    sample_type_label: str = Field(unique=True)


class SampleType(SampleTypeBase, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "sample_type"
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class SampleTypeCreate(SampleTypeBase):
    pass


class SampleTypeRead(SampleTypeBase):
    id: int


# --- Specialty --- #


class SpecialtyBase(SQLModel):
    specialty: str = Field(unique=True)


class Specialty(SpecialtyBase, table=True):
    id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyRead(SpecialtyBase):
    id: int


# # # --- Transplant --- #


# # class TransplantBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     transplant_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     date: date
# #     modality: int
# #     date_of_recurrence: date
# #     date_of_failure: date
# #     recurrence: bool
# #     date_of_cmv_infection: date
# #     donor_hla: str
# #     recipient_hla: str
# #     graft_loss_cause: str


# # class Transplant(TransplantBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class TransplantCreate(TransplantBase):
# #     pass


# # class TransplantRead(TransplantBase):
# #     id: int


# # # --- TransplantBiopsy --- #


# # class TransplantBiopsyBase(SQLModel):
# #     transplant_id: int = Field(foreign_key="transplants.id")
# #     date_of_biopsy: date
# #     recurrence: bool


# # class TransplantBiopsy(TransplantBiopsyBase, table=True):
# #     id: int = Field(default=None, primary_key=True)


# # class TransplantBiopsyCreate(TransplantBiopsyBase):
# #     pass


# # class TransplantBiopsyRead(TransplantBiopsyBase):
# #     id: int


# # # --- TransplantRejection --- #


# # class TransplantRejectionBase(SQLModel):
# #     transplant_id: int = Field(foreign_key="transplants.id")
# #     # TODO: Rename rejection date
# #     date_of_rejection: date


# # class TransplantRejection(TransplantRejectionBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class TransplantRejectionCreate(TransplantRejectionBase):
# #     pass


# # class TransplantRejectionRead(TransplantRejectionBase):
# #     id: int


# # # --- User --- #


# # class UserBase(SQLModel):
# #     username: str = Field(index=True)
# #     password: str
# #     email: str
# #     first_name: str
# #     last_name: str
# #     telephone_number: Optional[str]
# #     is_admin: bool = Field(default=False)
# #     is_bot: bool = Field(default=False)
# #     is_enabled: bool = Field(default=True)
# #     reset_password_token: str
# #     reset_password_date: datetime
# #     force_password_change: bool = Field(default=False)
# #     created_user_id: int = Field(foreign_key="users.id")
# #     created_date: datetime = Field(default=datetime.now())
# #     modified_user_id: int = Field(foreign_key="users.id")
# #     modified_date: datetime = Field(default=datetime.now())

# #     # Wonder if required
# #     created_patients: Patients = Relationship(back_populates="patients")
# #     created_patient_numbers: PatientNumber = Relationship(
# #         back_populates="patient_numbers"
# #     )


# # class Users(UserBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class UserCreate(UserBase):
# #     pass


# # class UserRead(UserBase):
# #     id: int


# # # --- UserSession --- #


# # class UserSessionBase(SQLModel):
# #     user_id: int = Field(foreign_key="users.id")
# #     date: datetime
# #     ip_address: INET


# # class UserSession(UserSessionBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class UserSessionCreate(UserSessionBase):
# #     pass


# # class UserSessionRead(UserSessionBase):
# #     id: int

# # # --- GroupForm --- # #

# # TODO: Decide if this should be removed and instead handle it with permissions

# # class GroupFormBase(SQLModel):
# #     group_id: int = Field(foreign_key="groups.id")
# #     form_id: int = Field(foreign_key="forms.id")
# #     weight: int


# # class GroupForm(GroupFormBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class GroupFormCreate(GroupFormBase):
# #     pass


# # class GroupFormRead(GroupFormBase):
# #     id: int


# # # --- GroupPage --- #

# # TODO: Decide if this should be removed and instead handle it with permissions

# # class GroupPageBase(SQLModel):
# #     group_id: int = Field(foreign_key="groups.id")
# #     page: str
# #     weight: int


# # class GroupPage(GroupPageBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class GroupPageCreate(GroupPageBase):
# #     pass


# # class GroupPageRead(GroupPageBase):
# #     id: int


# # --- GroupQuestionnaire --- #
# # Assigns questionnaires to groups, I assume to control viewing in the UI.
# # TODO: Decide if this should be removed and instead handle it with permissions


# # class GroupQuestionnaireBase(SQLModel):
# #     group_id: int = Field(foreign_key="groups.id")
# #     form_id: int = Field(foreign_key="forms.id")
# #     weight: Optional[int]


# # class GroupQuestionnaire(GroupQuestionnaireBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class GroupQuestionnaireCreate(GroupQuestionnaireBase):
# #     pass


# # class GroupQuestionnaireRead(GroupQuestionnaireBase):
# #     id: int

# # # --- IndiaEthnicity --- #


# # # TODO: Empty table, can probably be removed
# # class IndiaEthnicityBase(SQLModel):
# #     patient_id: int = Field(foreign_key="patient.id")
# #     source_group_id: int = Field(foreign_key="groups.id")
# #     data_source_id: int = Field(foreign_key="data_source.id")
# #     father_ancestral_state: str
# #     father_language: str
# #     mother_ancestral_state: str
# #     mother_language: str


# # class IndiaEthnicity(IndiaEthnicityBase, table=True):
# #     id: Optional[int] = Field(sa_column=Column(BigInteger(), primary_key=True))


# # class IndiaEthnicityCreate(IndiaEthnicityBase):
# #     pass


# # class IndiaEthnicityRead(IndiaEthnicityBase):
# #     id: int
