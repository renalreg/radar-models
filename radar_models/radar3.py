from datetime import datetime, date
from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

# --- Shared mixins --- #


class BigIntPK(SQLModel):
    """bigint auto-incrementing primary key for every table."""

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=BigInteger)


class HasId(SQLModel):
    """For Read models: the id is always present once a row exists."""

    id: int


# --- AdultEQ5D5L --- #


class AdultEQ5D5LBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    age: int
    gender: int
    mobility: int
    self_care: int
    usual_activities: int
    pain_discomfort: int
    anxiety_depression: int
    health: int


class AdultEQ5D5L(AdultEQ5D5LBase, BigIntPK, table=True):
    __tablename__ = "adult_eq5d5l"


class AdultEQ5D5LRead(AdultEQ5D5LBase, HasId):
    pass


# --- AdverseEvents --- #


class AdverseEventBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    review_date: date
    hospitalisation: bool
    adverse_event: bool
    new_onset_cancer: date
    cancer_cause: bool
    thromboembolism: date
    caused_venous_thrombo_embolism: int
    myocardial_infarction: date
    caused_acute_myocardial_infarction: int
    stroke: date
    caused_stroke: int
    ischaemic_attack: date
    caused_ischaemic_attack: int
    other_adverse_event: date
    other_toxicity: str
    caused_other: int
    date_of_death: date
    cause_of_death: str


class AdverseEvent(AdverseEventBase, BigIntPK, table=True):
    __tablename__ = "adverse_event"


class AdverseEventRead(AdverseEventBase, HasId):
    pass


# --- AlportAssessment --- #


class AlportAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    deafness_index: int
    deafness_date: Optional[date]
    hearing_aid_date: Optional[date]


class AlportAssessment(AlportAssessmentBase, BigIntPK, table=True):
    __tablename__ = "alport_assessment"


class AlportAssessmentRead(AlportAssessmentBase, HasId):
    pass


# --- Anthropometric --- #


class AnthropometricBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    height: int
    weight: float
    bmi: float
    hip: float
    waist: float
    arm: float
    up_and_go: float
    grip_dominant: float
    grip_non_dominant: float
    karnofsky: int
    systolic_one: int
    diastolic_one: int
    systolic_two: int
    diastolic_two: int
    systolic_three: int
    diastolic_three: int
    systolic_mean: int
    diastolic_mean: int


class Anthropometric(AnthropometricBase, BigIntPK, table=True):
    __tablename__ = "anthropometric"


class AnthropometricRead(AnthropometricBase, HasId):
    pass


# --- Biomarker --- #


class BiomarkerBase(SQLModel):
    biomarker_name: str
    biomarker_type: str


class Biomarker(BiomarkerBase, BigIntPK, table=True):
    __tablename__ = "biomarker"


class BiomarkerRead(BiomarkerBase, HasId):
    pass


# --- BiomarkerBarcode --- #


class BiomarkerBarcodeBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    barcode: str
    sample_date: datetime


class BiomarkerBarcode(BiomarkerBarcodeBase, BigIntPK, table=True):
    __tablename__ = "biomarker_barcode"


class BiomarkerBarcodeRead(BiomarkerBarcodeBase, HasId):
    pass


# --- BiomarkerResult --- #


class BiomarkerResultBase(SQLModel):
    biomarker_id: int = Field(foreign_key="biomarker.id")
    biomarker_sample_id: int = Field(foreign_key="biomarker_sample.id")
    biomarker_result_value: float
    measure_unit: str


class BiomarkerResult(BiomarkerResultBase, BigIntPK, table=True):
    __tablename__ = "biomarker_result"


class BiomarkerResultRead(BiomarkerResultBase, HasId):
    pass


# --- BiomarkerSample --- #


class BiomarkerSampleBase(SQLModel):
    barcode_id: int = Field(foreign_key="biomarker_barcode.id")
    biomarker_sample_label: str


class BiomarkerSample(BiomarkerSampleBase, BigIntPK, table=True):
    __tablename__ = "biomarker_sample"


class BiomarkerSampleRead(BiomarkerSampleBase, HasId):
    pass


# --- CalciphylaxisAssessment --- #


class CalciphylaxisAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    lesion: bool
    lesion_location: str
    infection: bool
    infection_location: str


class CalciphylaxisAssessment(CalciphylaxisAssessmentBase, BigIntPK, table=True):
    __tablename__ = "calciphylaxis_assessment"


class CalciphylaxisAssessmentRead(CalciphylaxisAssessmentBase, HasId):
    pass


# --- CalciphylaxisAssessmentOption --- #


class CalciphylaxisAssessmentOptionBase(SQLModel):
    calciphylaxis_assessment_id: int = Field(foreign_key="calciphylaxis_assessment.id")
    option_id: int = Field(foreign_key="option.id")


class CalciphylaxisAssessmentOption(
    CalciphylaxisAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "calciphylaxis_assessment_option"


class CalciphylaxisAssessmentOptionRead(CalciphylaxisAssessmentOptionBase, HasId):
    pass


# --- CancerTumours --- #


class CancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    tumour_type: str
    other_tumour_name: str
    diagnosis_date: date
    tumour_count: int
    cns_image: str
    progression_date: date
    t_cat: str
    n_cat: str
    m_cat: str
    radiologic_tumor_size: str
    pathologic_tumor_size: str
    tumor_location: str


class CancerTumour(CancerTumourBase, BigIntPK, table=True):
    __tablename__ = "cancer_tumour"


class CancerTumourRead(CancerTumourBase, HasId):
    pass


# --- CKDAfricaGenetic --- #


class CKDAfricaGeneticBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    sickle_cell: str
    other_sickle_cell: str
    apol_1: str


class CKDAfricaGenetic(CKDAfricaGeneticBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_genetic"


class CKDAfricaGeneticRead(CKDAfricaGeneticBase, HasId):
    pass


# --- CKDAfricaRiskFactor --- #


class CKDAfricaRiskFactorBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    preterm_birth: str
    low_birth_weight: str
    malnutrition: str
    hospital_malnutrition: str


class CKDAfricaRiskFactor(CKDAfricaRiskFactorBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_risk_factor"


class CKDAfricaRiskFactorRead(CKDAfricaRiskFactorBase, HasId):
    pass


# --- ClinicalLetters --- #


class ClinicalLettersBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    letter_date: date
    comments: str


class ClinicalLetters(ClinicalLettersBase, BigIntPK, table=True):
    __tablename__ = "clinical_letters"


class ClinicalLettersRead(ClinicalLettersBase, HasId):
    pass


# --- Code --- #


class CodeBase(SQLModel):
    coding_system: str
    code_describes: str
    code: str
    code_label: str


class Code(CodeBase, BigIntPK, table=True):
    __tablename__ = "code"


class CodeRead(CodeBase, HasId):
    pass


# --- Cohort --- #


class CohortBase(SQLModel):
    cohort_code: str
    cohort_name: str
    cohort_short_name: str


class Cohort(CohortBase, BigIntPK, table=True):
    __tablename__ = "cohort"


class CohortRead(CohortBase, HasId):
    pass


# --- CohortDiagnose --- #


class CohortDiagnosisBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    diagnosis_type: int = Field(foreign_key="option.id")


class CohortDiagnosis(CohortDiagnosisBase, BigIntPK, table=True):
    __tablename__ = "cohort_diagnosis"


class CohortDiagnosisRead(CohortDiagnosisBase, HasId):
    pass


# --- CohortObservation --- #


class CohortObservationBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    observation_id: int = Field(foreign_key="observation.id")
    weight: int


class CohortObservation(CohortObservationBase, BigIntPK, table=True):
    __tablename__ = "cohort_observation"


class CohortObservationRead(CohortObservationBase, HasId):
    pass


# --- CohortPatient --- #


class CohortPatientBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id")
    patient_id: int = Field(foreign_key="patient.id")
    recruited_date: date
    removed_date: Optional[date]


class CohortPatient(CohortPatientBase, BigIntPK, table=True):
    __tablename__ = "cohort_patient"


class CohortPatientRead(CohortPatientBase, HasId):
    pass


# --- Consent --- #


class ConsentBase(SQLModel):
    consent_code: str
    consent_label: Optional[str]
    is_paediatric: bool = Field(default=False)
    release_date: date
    consent_url: str
    is_retired: bool = Field(default=False)


class Consent(ConsentBase, BigIntPK, table=True):
    __tablename__ = "consent"


class ConsentRead(ConsentBase, HasId):
    pass


# --- Consultant --- #


class ConsultantBase(SQLModel):
    specialty_id: int = Field(foreign_key="specialty.id")
    first_name: str
    last_name: str
    email: Optional[str]
    telephone_number: Optional[str]
    gmc_number: Optional[int]


class Consultant(ConsultantBase, BigIntPK, table=True):
    __tablename__ = "consultant"


class ConsultantRead(ConsultantBase, HasId):
    pass


# --- Country --- #


class CountryBase(SQLModel):
    country_name: str
    country_code: str


class Country(CountryBase, BigIntPK, table=True):
    __tablename__ = "country"


class CountryRead(CountryBase, HasId):
    pass


# --- CountryEthnicity --- #


class CountryEthnicityBase(SQLModel):
    ethnicity_id: int = Field(foreign_key="ethnicity.id")
    country_id: int = Field(foreign_key="country.id")


class CountryEthnicity(CountryEthnicityBase, BigIntPK, table=True):
    __tablename__ = "country_ethnicity"


class CountryEthnicityRead(CountryEthnicityBase, HasId):
    pass


# --- CountryNationality --- #


class CountryNationalityBase(SQLModel):
    nationality_id: int = Field(foreign_key="nationality.id")
    country_id: int = Field(foreign_key="country.id")


class CountryNationality(CountryNationalityBase, BigIntPK, table=True):
    __tablename__ = "country_nationality"


class CountryNationalityRead(CountryNationalityBase, HasId):
    pass


# --- CystinosisAdultVisit --- #


class CystinosisAdultVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    visit: int
    visit_date: date
    urine_measurement: str
    urine_output: float
    voiding_overnight: str
    continent_day: str
    fluid_intake: float
    admission_dehydration: int
    constipation: str
    diarrhea: str
    nausea: str
    vomiting: str
    rickets: str
    kyphoscoliosis: str
    fractures: str
    muscle_strength: str
    ankle_strength: float
    elbow_strength: float
    hand_strength: float
    hip_strength: float
    knee_strength: float
    shoulder_strength: float
    wrist_strength: float
    swallowing_difficulties: str
    swallowing_difficulties_detail: str
    joint_surgery: str
    visual_impairment: str
    photophobia: str
    photophobia_grade: str
    keratoplasty_date: date
    acuity: str
    gahl_score: str
    intraocular_pressure_r: str
    intraocular_pressure_l: str
    fev1: float
    vc: float
    snip: float
    seizure: str
    headache: str
    muscle_weakness: str
    learning_difficulties: str
    cognitive_difficulties: str
    cognitive_difficulties_score: str
    movement_disorder: str
    intracranial_hypertension: str
    diabetes: str
    thyroid: str
    hypothyroidism: str
    tanner_stage: str
    wc_cystine: float
    wc_cystine_date: date
    wc_cystine_time: str
    cysteamine_last_dose: int
    cysteamine_effects: str


class CystinosisAdultVisit(CystinosisAdultVisitBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_adult_visit"


class CystinosisAdultVisitRead(CystinosisAdultVisitBase, HasId):
    pass


# --- CystinosisPaedVisit --- #


class CystinosisPaedVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    visit: int
    visit_date: date
    height: float
    weight: float
    urine_measurement: str
    urine_output: float
    voiding_overnight: str
    continence_day: str
    fluid_intake: float
    admission_dehydration: int
    constipation: str
    diarrhea: str
    nausea: str
    vomiting: str
    failure_to_thrive: str
    enteral_feeding: str
    feeding_start_date_1: date
    feeding_end_date_1: date
    feeding_start_date_2: date
    feeding_end_date_2: date
    feeding_start_date_3: date
    feeding_end_date_3: date
    normal_food_orally: str
    supplements: str
    growth_hormone_treatment: str
    rickets: str
    kyphoscoliosis: str
    fractures: str
    joint_surgery: str
    muscle_strength: str
    swallowing_difficulties: str
    nose_snoring: str
    tonsillectomy_date: date
    sight_impairment: str
    severe_sight_impairment: str
    photophobia: str
    photophobia_grade: str
    keratoplasty_date: date
    acuity: str
    gahl_score: str
    intraocular_pressure_r: str
    intraocular_pressure_l: str
    fev1: float
    vc: float
    snip: float
    seizure: str
    headache: str
    muscle_weakness: str
    learning_difficulties: str
    cognitive_difficulties: str
    movement_disorder: str
    intracranial_hypertension: str
    diabetes: str
    thyroid: str
    hypothyroidism: str
    tanner_stage: str
    wc_cystine: float
    wc_cystine_date: date
    wc_cystine_time: str
    cysteamine_last_dose: int
    cysteamine_effects: str


class CystinosisPaedVisit(CystinosisPaedVisitBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_paed_visit"


class CystinosisPaedVisitRead(CystinosisPaedVisitBase, HasId):
    pass


# --- CystinosisPaedVisitOption --- #


class CystinosisPaedVisitOptionBase(SQLModel):
    cystinosis_paeds_visit_id: int = Field(foreign_key="cystinosis_paed_visit.id")
    option_id: int = Field(foreign_key="option.id")


class CystinosisPaedVisitOption(CystinosisPaedVisitOptionBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_paed_visit_option"


class CystinosisPaedVisitOptionRead(CystinosisPaedVisitOptionBase, HasId):
    pass


# --- DataSource --- #


class DataSourceBase(SQLModel):
    data_source_name: str


class DataSource(DataSourceBase, BigIntPK, table=True):
    __tablename__ = "data_source"


class DataSourceRead(DataSourceBase, HasId):
    pass


# --- Death --- #


class DeathBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_death: date
    cause_of_death: Optional[str]


class Death(DeathBase, BigIntPK, table=True):
    __tablename__ = "death"


class DeathRead(DeathBase, HasId):
    pass


# --- DentAndLoweAssessment --- #


class DentAndLoweAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    aetiology: str
    causative_agent: str
    other_agent: str
    extra_involvement: str
    other_extra_involvement: str


class DentAndLoweAssessment(DentAndLoweAssessmentBase, BigIntPK, table=True):
    __tablename__ = "dent_and_lowe_assessment"


class DentAndLoweAssessmentRead(DentAndLoweAssessmentBase, HasId):
    pass


# --- DentAndLoweAssessmentOption --- #


class DentAndLoweAssessmentOptionBase(SQLModel):
    dent_and_lowe_assessment_id: int = Field(foreign_key="dent_and_lowe_assessment.id")
    option_id: int = Field(foreign_key="option.id")


class DentAndLoweAssessmentOption(
    DentAndLoweAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "dent_and_lowe_assessment_option"


class DentAndLoweAssessmentOptionRead(DentAndLoweAssessmentOptionBase, HasId):
    pass


# --- DiabeticComplication --- #


class DiabeticComplicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    retinopathy: int
    laser_treatment: bool
    peripheral_neuropathy: bool
    foot_ulcer: bool


class DiabeticComplication(DiabeticComplicationBase, BigIntPK, table=True):
    __tablename__ = "diabetic_complication"


class DiabeticComplicationRead(DiabeticComplicationBase, HasId):
    pass


# --- Diagnoses --- #


class DiagnosisBase(SQLModel):
    diagnosis_name: str


class Diagnosis(DiagnosisBase, BigIntPK, table=True):
    __tablename__ = "diagnosis"


class DiagnosisRead(DiagnosisBase, HasId):
    pass


# --- DiagnosisCode --- #


class DiagnosisCodeBase(SQLModel):
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    code_id: int = Field(foreign_key="code.id")


class DiagnosisCode(DiagnosisCodeBase, BigIntPK, table=True):
    __tablename__ = "diagnosis_code"


class DiagnosisCodeRead(DiagnosisCodeBase, HasId):
    pass


# --- Dialysis --- #


class DialysisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    timeline_start: date
    timeline_end: Optional[date]
    modality: int


class Dialysis(DialysisBase, BigIntPK, table=True):
    __tablename__ = "dialysis"


class DialysisRead(DialysisBase, HasId):
    pass


# --- Drug --- #


class DrugBase(SQLModel):
    drug_name: str
    drug_group_id: Optional[int] = Field(foreign_key="drug_group.id")


class Drug(DrugBase, BigIntPK, table=True):
    __tablename__ = "drug"


class DrugRead(DrugBase, HasId):
    pass


# --- DrugGroup --- #


class DrugGroupBase(SQLModel):
    drug_group: Optional[str] = Field(unique=True)
    parent_drug_group_id: Optional[int] = Field(foreign_key="drug_group.id")


class DrugGroup(DrugGroupBase, BigIntPK, table=True):
    __tablename__ = "drug_group"


class DrugGroupRead(DrugGroupBase, HasId):
    pass


# --- EQ5DY --- #


class EQ5DYBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    age: int
    gender: int
    mobility: int
    self_care: int
    usual_activities: int
    pain_discomfort: int
    anxiety_depression: int
    health: int


class EQ5DY(EQ5DYBase, BigIntPK, table=True):
    __tablename__ = "eq_5d_y"


class EQ5DYRead(EQ5DYBase, HasId):
    pass


# --- EthnicOrigin --- #


class EthnicOriginBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    country_of_birth: str
    year_of_emigration: int
    ethnic_origin: str


class EthnicOrigin(EthnicOriginBase, BigIntPK, table=True):
    __tablename__ = "ethnic_origin"


class EthnicOriginRead(EthnicOriginBase, HasId):
    pass


# --- Ethnicity --- #


class EthnicityBase(SQLModel):
    ethnicity_code: str
    ethnicity_label: str


class Ethnicity(EthnicityBase, BigIntPK, table=True):
    __tablename__ = "ethnicity"


class EthnicityRead(EthnicityBase, HasId):
    pass


# --- FamilyHistory --- #


class FamilyHistoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    relation_patient_id: int = Field(foreign_key="patient.id")
    has_condition: bool


class FamilyHistory(FamilyHistoryBase, BigIntPK, table=True):
    __tablename__ = "family_history"


class FamilyHistoryRead(FamilyHistoryBase, HasId):
    pass


# --- FamilyHistoryRelation --- #


class FamilyHistoryRelationBase(SQLModel):
    family_history_id: int = Field(foreign_key="family_history.id")
    relation_id: int = Field(foreign_key="relation.id")


class FamilyHistoryRelation(FamilyHistoryRelationBase, BigIntPK, table=True):
    __tablename__ = "family_history_relation"


class FamilyHistoryRelationRead(FamilyHistoryRelationBase, HasId):
    pass


# --- FamilyHistoryRelationPatient --- #


class FamilyHistoryRelationPatientBase(SQLModel):
    family_history_relation_id: int = Field(foreign_key="family_history_relation.id")
    patient_id: int = Field(foreign_key="patient.id")


class FamilyHistoryRelationPatient(
    FamilyHistoryRelationPatientBase, BigIntPK, table=True
):
    __tablename__ = "family_history_relation_patient"


class FamilyHistoryRelationPatientRead(FamilyHistoryRelationPatientBase, HasId):
    pass


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


class FetalAnomalyScan(FetalAnomalyScanBase, BigIntPK, table=True):
    __tablename__ = "fetal_anomaly_scan"


class FetalAnomalyScanRead(FetalAnomalyScanBase, HasId):
    pass


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


class FetalUltrasound(FetalUltrasoundBase, BigIntPK, table=True):
    __tablename__ = "fetal_ultrasound"


class FetalUltrasoundRead(FetalUltrasoundBase, HasId):
    pass


# --- FrontPageStats --- #


class FrontPageStatBase(SQLModel):
    label: str
    stat: str


class FrontPageStat(FrontPageStatBase, BigIntPK, table=True):
    __tablename__ = "front_page_stats"


class FrontPageStatRead(FrontPageStatBase, HasId):
    pass


# --- FuanAssessment --- #


class FuanAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    picture_date: date
    gout: bool
    gout_date: Optional[date]
    family_gout: Optional[bool]
    thp: Optional[str]
    uti: Optional[bool]
    comments: Optional[str]


class FuanAssessment(FuanAssessmentBase, BigIntPK, table=True):
    __tablename__ = "fuan_assessment"


class FuanAssessmentRead(FuanAssessmentBase, HasId):
    pass


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


class Genetics(GeneticsBase, BigIntPK, table=True):
    __tablename__ = "genetics"


class GeneticsRead(GeneticsBase, HasId):
    pass


# --- HADS --- #


class HADSBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    a1: int
    d1: int
    a2: int
    d2: int
    a3: int
    d3: int
    a4: int
    d4: int
    a5: int
    d5: int
    a6: int
    d6: int
    a7: int
    d7: int
    anxiety_score: int


class HADS(HADSBase, BigIntPK, table=True):
    __tablename__ = "hads"


class HADSRead(HADSBase, HasId):
    pass


# --- Hnf1bAssessment --- #


class Hnf1bAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    single_kidney: bool
    hyperuricemia_gout: bool
    genital_malformation: bool
    genital_malformation_details: str
    familial_cystic_disease: bool
    hypertension: bool


class Hnf1bAssessment(Hnf1bAssessmentBase, BigIntPK, table=True):
    __tablename__ = "hnf1b_assessment"


class Hnf1bAssessmentRead(Hnf1bAssessmentBase, HasId):
    pass


# --- Hospital --- #


class HospitalBase(SQLModel):
    hospital_code: str
    hospital_name: str
    hospital_short_name: str
    is_transplant_centre: bool


class Hospital(HospitalBase, BigIntPK, table=True):
    __tablename__ = "hospital"


class HospitalRead(HospitalBase, HasId):
    pass


# --- HospitalConsultant --- #


class HospitalConsultantBase(SQLModel):
    hospital_id: int = Field(foreign_key="hospital.id")
    consultant_id: int = Field(foreign_key="consultant.id")


class HospitalConsultant(HospitalConsultantBase, BigIntPK, table=True):
    __tablename__ = "hospital_consultant"


class HospitalConsultantRead(HospitalConsultantBase, HasId):
    pass


# --- HospitalPatient --- #


class HospitalPatientBase(SQLModel):
    hospital_id: int = Field(foreign_key="hospital.id")
    patient_id: int = Field(foreign_key="patient.id")
    first_seen_date: date
    discharged_date: Optional[date]


class HospitalPatient(HospitalPatientBase, BigIntPK, table=True):
    __tablename__ = "hospital_patient"


class HospitalPatientRead(HospitalPatientBase, HasId):
    pass


# --- Hospitalisation --- #


class HospitalisationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    date_of_admission: date
    date_of_discharge: Optional[date]
    reason_of_admission: Optional[str]


class Hospitalisation(HospitalisationBase, BigIntPK, table=True):
    __tablename__ = "hospitalisation"


class HospitalisationRead(HospitalisationBase, HasId):
    pass


# --- HSPAssessment --- #


class HSPAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    haematuria: bool
    nephrotic: bool
    m: str
    e: str
    s: str
    t: str
    c: str


class HSPAssessment(HSPAssessmentBase, BigIntPK, table=True):
    __tablename__ = "hsp_assessment"


class HSPAssessmentRead(HSPAssessmentBase, HasId):
    pass


# --- Identifier --- #


class IdentifierBase(SQLModel):
    identifier_label: str


class Identifier(IdentifierBase, BigIntPK, table=True):
    __tablename__ = "identifier"


class IdentifierRead(IdentifierBase, HasId):
    pass


# --- IGAResearch --- #


class IGAResearchBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date


class IGAResearch(IGAResearchBase, BigIntPK, table=True):
    __tablename__ = "iga_research"


class IGAResearchRead(IGAResearchBase, HasId):
    pass


# --- IGAResearchOptions --- #


class IGAResearchOptionsBase(SQLModel):
    IGAResearch_id: int = Field(foreign_key="iga_research.id")
    option_id: int = Field(foreign_key="option.id")


class IGAResearchOptions(IGAResearchOptionsBase, BigIntPK, table=True):
    __tablename__ = "iga_research_options"


class IGAResearchOptionsRead(IGAResearchOptionsBase, HasId):
    pass


# --- Indicator --- #


class IndicatorBase(SQLModel):
    indicator_label: str


class Indicator(IndicatorBase, BigIntPK, table=True):
    __tablename__ = "indicator"


class IndicatorRead(IndicatorBase, HasId):
    pass


# --- InsAssessment --- #


class InsAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date_of_picture: date
    oedema: Optional[bool]
    hypovoloemia: Optional[bool]
    fever: Optional[bool]
    thrombosis: Optional[bool]
    peritonitis: Optional[bool]
    pulmonary_oedema: Optional[bool]
    hypertension: Optional[bool]
    rash: Optional[bool]
    rash_details: Optional[str]
    infection: Optional[bool]
    infection_details: Optional[str]
    ophthalmoscopy: Optional[bool]
    ophthalmoscopy_details: Optional[str]
    comments: Optional[str]


class InsAssessment(InsAssessmentBase, BigIntPK, table=True):
    __tablename__ = "ins_assessment"


class InsAssessmentRead(InsAssessmentBase, HasId):
    pass


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


class InsRelapse(InsRelapseBase, BigIntPK, table=True):
    __tablename__ = "ins_relapse"


class InsRelapseRead(InsRelapseBase, HasId):
    pass


# --- IPOS --- #


class IPOSBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    score_1: int
    score_2: int
    score_3: int
    score_4: int
    score_5: int
    score_6: int
    score_7: int
    score_8: int
    score_9: int
    score_10: int
    score_11: int
    score_12: int
    score_13: int
    score_14: int
    score_15: int
    score_16: int
    score_17: int
    question_1: str
    score_18: int
    question_2: str
    score_19: int
    question_3: str
    score_20: int
    question_4: str
    question_5: str
    score: int


class IPOS(IPOSBase, BigIntPK, table=True):
    __tablename__ = "ipos"


class IPOSRead(IPOSBase, HasId):
    pass


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


class LiverDisease(LiverDiseaseBase, BigIntPK, table=True):
    __tablename__ = "liver_disease"


class LiverDiseaseRead(LiverDiseaseBase, HasId):
    pass


# --- LiverImaging --- #


class LiverImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    imaging_date: date
    imaging_type: str
    liver_size: Optional[float]
    hepatic_fibrosis: Optional[bool]
    hepatic_cysts: Optional[bool]
    bile_duct_cysts: Optional[bool]
    dilated_bile_ducts: Optional[bool]
    cholangitis: Optional[bool]


class LiverImaging(LiverImagingBase, BigIntPK, table=True):
    __tablename__ = "liver_imaging"


class LiverImagingRead(LiverImagingBase, HasId):
    pass


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


class LiverTransplant(LiverTransplantBase, BigIntPK, table=True):
    __tablename__ = "liver_transplant"


class LiverTransplantRead(LiverTransplantBase, HasId):
    pass


# --- LiverTransplantIndicator --- #


class LiverTransplantIndicatorBase(SQLModel):
    liver_transplant_id: int = Field(foreign_key="liver_transplant.id")
    indicator_id: int = Field(foreign_key="indicator.id")


class LiverTransplantIndicator(LiverTransplantIndicatorBase, BigIntPK, table=True):
    __tablename__ = "liver_transplant_indicator"


class LiverTransplantIndicatorRead(LiverTransplantIndicatorBase, HasId):
    pass


# --- Medication --- #


class MedicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    drug_id: int = Field(foreign_key="drug.id")
    snapshot_date: Optional[date]
    start_date: Optional[date]
    finish_date: Optional[date]
    dose_quantity: Optional[float]
    dose_unit: str
    frequency: str
    route: str
    drug_text: str
    dose_text: str


class Medication(MedicationBase, BigIntPK, table=True):
    __tablename__ = "medication"


class MedicationRead(MedicationBase, HasId):
    pass


# --- MpgnAssessment --- #


class MpgnAssessmentBase(SQLModel):
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


class MpgnAssessment(MpgnAssessmentBase, BigIntPK, table=True):
    __tablename__ = "mpgn_assessment"


class MpgnAssessmentRead(MpgnAssessmentBase, HasId):
    pass


# --- Nationality --- #


class NationalityBase(SQLModel):
    nationality_label: str


class Nationality(NationalityBase, BigIntPK, table=True):
    __tablename__ = "nationality"


class NationalityRead(NationalityBase, HasId):
    pass


# --- Nephrectomy --- #


class NephrectomyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    assessment_date: date
    kidney_side: str
    kidney_type: str
    entry_type: str


class Nephrectomy(NephrectomyBase, BigIntPK, table=True):
    __tablename__ = "nephrectomy"


class NephrectomyRead(NephrectomyBase, HasId):
    pass


# --- NurtureFamilyHistory --- #


class NurtureFamilyHistoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    eskd: bool
    eskd_relative_1: int
    eskd_relative_2: int
    eskd_relative_3: int
    chd: bool
    chd_relative_1: int
    chd_relative_2: int
    chd_relative_3: int
    diabetes: bool
    diabetes_relative_1: int
    diabetes_relative_2: int
    diabetes_relative_3: int


class NurtureFamilyHistory(NurtureFamilyHistoryBase, BigIntPK, table=True):
    __tablename__ = "nurture_family_history"


class NurtureFamilyHistoryRead(NurtureFamilyHistoryBase, HasId):
    pass


# --- NurtureMetadata --- #


class NurtureMetadataBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    signed_off_state: int
    follow_up_refused_date: date
    blood_tests: bool
    blood_refused_date: date
    interviews: bool
    interviews_refused_date: date


class NurtureMetadata(NurtureMetadataBase, BigIntPK, table=True):
    __tablename__ = "nurture_metadata"


class NurtureMetadataRead(NurtureMetadataBase, HasId):
    pass


# --- NurtureVisit --- #


class NurtureVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    visit_date: date
    visit: int
    comorbidities: int
    vaccination_flu: bool
    vaccination_pneumococcal: bool
    admission: bool
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


# --- Nutrition --- #


class NutritionBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    feeding_type: str
    from_date: date
    to_date: date


class Nutrition(NutritionBase, BigIntPK, table=True):
    __tablename__ = "nutrition"


class NutritionRead(NutritionBase, HasId):
    pass


# --- Observation --- #


class ObservationBase(SQLModel):
    sample_type_id: int = Field(foreign_key="sample_type.id")
    name: str
    short_name: str
    min_value: int
    max_value: int
    units: str


class Observation(ObservationBase, BigIntPK, table=True):
    __tablename__ = "observation"


class ObservationRead(ObservationBase, HasId):
    pass


# --- ObservationCode --- #


class ObservationCodeBase(SQLModel):
    observation_id: int = Field(foreign_key="observation.id")
    code_id: int = Field(foreign_key="code.id")


class ObservationCode(ObservationCodeBase, BigIntPK, table=True):
    __tablename__ = "observation_code"


class ObservationCodeRead(ObservationCodeBase, HasId):
    pass


# --- ObservationOptions --- #


class ObservationOptionsBase(SQLModel):
    observation_id: int
    option_id: int


class ObservationOption(ObservationOptionsBase, BigIntPK, table=True):
    __tablename__ = "observation_option"


class ObservationOptionRead(ObservationOptionsBase, HasId):
    pass


# --- Option --- #


class OptionBase(SQLModel):
    option_group: str
    display_label: str
    store_value: str


class Option(OptionBase, BigIntPK, table=True):
    __tablename__ = "option"


class OptionRead(OptionBase, HasId):
    pass


# --- PaedsCHU9D --- #


class PaedsCHU9DBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    worried: int
    sad: int
    pain: int
    tired: int
    annoyed: int
    school: int
    sleep: int
    routine: int
    activities: int


class PaedsCHU9D(PaedsCHU9DBase, BigIntPK, table=True):
    __tablename__ = "paeds_chu9d"


class PaedsCHU9DRead(PaedsCHU9DBase, HasId):
    pass


# --- PAM --- #


class PAMBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int
    q10: int
    q11: int
    q12: int
    q13: int


class PAM(PAMBase, BigIntPK, table=True):
    __tablename__ = "pam"


class PAMRead(PAMBase, HasId):
    pass


# --- ParentalConsanguinity --- #


class ParentalConsanguinityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    consanguinity: bool
    consanguinity_details: str


class ParentalConsanguinity(ParentalConsanguinityBase, BigIntPK, table=True):
    __tablename__ = "parental_consanguinity"


class ParentalConsanguinityRead(ParentalConsanguinityBase, HasId):
    pass


# --- Pathology --- #


class PathologyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    report_date: date
    kidney_type: str
    kidney_side: str
    reference_number: str
    image_url: str
    histological_summary: str
    em_findings: str
    report_cleaned_date: date


class Pathology(PathologyBase, BigIntPK, table=True):
    __tablename__ = "pathology"


class PathologyRead(PathologyBase, HasId):
    pass


# --- Patient --- #


class PatientBase(SQLModel):
    patient_comment: Optional[str]
    is_test: bool = Field(default=False)
    is_control: bool = Field(default=False)


class Patient(PatientBase, BigIntPK, table=True):
    __tablename__ = "patient"


class PatientRead(PatientBase, HasId):
    pass


# --- PatientAddress --- #


class PatientAddressBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    country_id: int = Field(foreign_key="country.id")
    from_date: date
    to_date: date
    address1: str
    address2: str
    address3: str
    address4: str
    postcode: str


class PatientAddress(PatientAddressBase, BigIntPK, table=True):
    __tablename__ = "patient_address"


class PatientAddressRead(PatientAddressBase, HasId):
    pass


# --- PatientAlias --- #


class PatientAliasBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    first_name: str
    last_name: str


class PatientAlias(PatientAliasBase, BigIntPK, table=True):
    __tablename__ = "patient_alias"


class PatientAliasRead(PatientAliasBase, HasId):
    pass


# --- PatientConsent --- #


class PatientConsentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    consent_id: int = Field(foreign_key="consent.id")
    signed_on_date: date
    withdrawn_on_date: Optional[date]


class PatientConsent(PatientConsentBase, BigIntPK, table=True):
    __tablename__ = "patient_consent"


class PatientConsentRead(PatientConsentBase, HasId):
    pass


# --- PatientConsultant --- #


class PatientConsultantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    consultant_id: int = Field(foreign_key="consultant.id")
    from_date: date
    to_date: Optional[date]


class PatientConsultant(PatientConsultantBase, BigIntPK, table=True):
    __tablename__ = "patient_consultant"


class PatientConsultantRead(PatientConsultantBase, HasId):
    pass


# --- PatientDemographic --- #


class PatientDemographicBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    ethnicity_id: int = Field(foreign_key="ethnicity.id")
    country_of_birth: int = Field(foreign_key="country.id")
    first_name: str
    last_name: str
    date_of_birth: date
    gender: int
    mobile_number: str
    email_address: str


class PatientDemographic(PatientDemographicBase, BigIntPK, table=True):
    __tablename__ = "patient_demographic"


class PatientDemographicRead(PatientDemographicBase, HasId):
    pass


# --- PatientDiagnosis --- #


class PatientDiagnosisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    diagnosis_text: str
    symptoms_date: date
    from_date: Optional[date]
    to_date: Optional[date]
    snapshot_date: Optional[date]
    gene_test: bool
    biochemistry: bool
    assessment: bool
    biopsy: bool
    biopsy_diagnosis: int
    comments: str
    prenatal: bool


class PatientDiagnosis(PatientDiagnosisBase, BigIntPK, table=True):
    __tablename__ = "patient_diagnosis"


class PatientDiagnosisRead(PatientDiagnosisBase, HasId):
    pass


# --- PatientIdentifier --- #


class PatientIdentifierBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    identifier_id: int = Field(foreign_key="identifier.id")
    identifier: str


class PatientIdentifier(PatientIdentifierBase, BigIntPK, table=True):
    __tablename__ = "patient_identifier"


class PatientIdentifierRead(PatientIdentifierBase, HasId):
    pass


# --- PatientNationality --- #


class PatientNationalityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    nationality_id: int = Field(foreign_key="nationality.id")


class PatientNationality(PatientNationalityBase, table=True):
    __tablename__ = "patient_nationality"
    id: int = Field(default=None, primary_key=True)


class PatientNationalityRead(PatientNationalityBase, HasId):
    pass


# --- PatientReconsent --- #


class PatientReconsentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    sent_date: date
    response_date: date


class PatientReconsent(PatientReconsentBase, BigIntPK, table=True):
    __tablename__ = "patient_reconsent"


class PatientReconsentRead(PatientReconsentBase):
    pass


class PatientReconsentCreate(PatientReconsentBase):
    id: int


# --- Plasmapheresis --- #


class PlasmapheresisBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    from_date: date
    to_date: date
    schedule: str
    response: str


class Plasmapheresis(PlasmapheresisBase, BigIntPK, table=True):
    __tablename__ = "plasmapheresis"


class PlasmapheresisRead(PlasmapheresisBase, HasId):
    pass


# --- Post --- #


class PostBase(SQLModel):
    post_title: str
    published_date: datetime
    body: str


class Post(PostBase, BigIntPK, table=True):
    __tablename__ = "post"


class PostRead(PostBase, HasId):
    pass


# --- Pregnancy --- #


class PregnancyBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    pregnancy_number: int
    date_of_lmp: date
    gravidity: int
    parity1: int
    parity2: int
    outcome: str
    birth_weight: int
    centile_weight: int
    gestational_age: int
    delivery_method: str
    neonatal_intensive_care: bool
    pre_eclampsia: str


class Pregnancy(PregnancyBase, BigIntPK, table=True):
    __tablename__ = "pregnancy"


class PregnancyRead(PregnancyBase, HasId):
    pass


# --- Procedure --- #


class ProcedureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    procedure: str
    other_procedure: str
    date_of_procedure: date


class Procedure(ProcedureBase, BigIntPK, table=True):
    __tablename__ = "procedure"


class ProcedureRead(ProcedureBase, HasId):
    pass


# --- Relation --- #


class RelationBase(SQLModel):
    relationship: str


class Relation(RelationBase, BigIntPK, table=True):
    __tablename__ = "relation"


class RelationRead(RelationBase, HasId):
    pass


# --- RenalCancerGenetics --- #


class RenalCancerGeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    bap1_test: bool
    bap1_variant: str
    bap1_variant_status: str
    fh_test: bool
    fh_variant: str
    fh_variant_status: str
    flcn_test: bool
    flcn_variant: str
    flcn_variant_status: str
    met_test: bool
    met_variant: str
    met_variant_status: str
    mitf_test: bool
    mitf_variant: str
    mitf_variant_status: str
    pten_test: bool
    pten_variant: str
    pten_variant_status: str
    sdha_test: bool
    sdha_variant: str
    sdha_variant_status: str
    sdhb_test: bool
    sdhb_variant: str
    sdhb_variant_status: str
    sdhc_test: bool
    sdhc_variant: str
    sdhc_variant_status: str
    sdhd_test: bool
    sdhd_variant: str
    sdhd_variant_status: str
    vhl_test: bool
    vhl_variant: str
    vhl_variant_status: str
    other_test: bool
    other_test_name: str
    other_variant: str
    other_variant_status: str


class RenalCancerGenetics(RenalCancerGeneticsBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics"


class RenalCancerGeneticsRead(RenalCancerGeneticsBase, HasId):
    pass


# --- RenalCancerGeneticsOption --- #


class RenalCancerGeneticsOptionBase(SQLModel):
    renal_cancer_genetics_id: int = Field(foreign_key="renal_cancer_genetics.id")
    option_id: int = Field(foreign_key="option.id")


class RenalCancerGeneticsOption(RenalCancerGeneticsOptionBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics_option"


class RenalCancerGeneticsOptionRead(RenalCancerGeneticsOptionBase, HasId):
    pass


# --- RenalCancerTumour --- #


class RenalCancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    tumor_type: str
    assessment_date: date
    cns_imaging_method: str  #
    progression_date: date
    t_cat: str
    n_cat: str
    m_cat: str
    rt_size: str
    pt_size: str
    t_loc: str


class RenalCancerTumour(RenalCancerTumourBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_tumour"


class RenalCancerTumourRead(RenalCancerTumourBase, HasId):
    pass


# --- RenalImaging --- #


class RenalImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    assessment_date: datetime
    imaging_type: str
    right_present: bool
    right_type: str
    right_length: int
    right_volume: int
    right_cysts: bool
    right_stones: bool
    right_calcification: bool
    right_nephrocalcinosis: bool
    right_nephrolithiasis: bool
    right_other_malformation: str
    left_present: bool
    left_type: str
    left_length: int
    left_volume: int
    left_cysts: bool
    left_stones: bool
    left_calcification: bool
    left_nephrocalcinosis: bool
    left_nephrolithiasis: bool
    left_other_malformation: str


class RenalImaging(RenalImagingBase, BigIntPK, table=True):
    __tablename__ = "renal_imaging"


class RenalImagingRead(RenalImagingBase, HasId):
    pass


# --- RenalProgression --- #


class RenalProgressionBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    onset_date: date
    esrf_date: date
    ckd5_date: date
    ckd4_date: date
    ckd3a_date: date
    ckd3b_date: date


class RenalProgression(RenalProgressionBase, BigIntPK, table=True):
    __tablename__ = "renal_progression"


class RenalProgressionRead(RenalProgressionBase, HasId):
    pass


# --- Result --- #


class ResultBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    result_date: datetime
    qualifier: str
    result_value: str
    sent_value: str


class Result(ResultBase, BigIntPK, table=True):
    __tablename__ = "result"


class ResultRead(ResultBase, HasId):
    pass


# --- RituximabBaselineAssessment --- #


class RituximabBaselineAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    assessment_date: date
    nephropathy: str
    steroids: bool
    other_previous_treatment: str
    past_remission: bool
    performance_status: int
    comorbidities: bool


class RituximabBaselineAssessment(
    RituximabBaselineAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_assessment"


class RituximabBaselineAssessmentRead(RituximabBaselineAssessmentBase, HasId):
    pass


# --- RituximabBaselineAssessmentOption --- #


class RituximabBaselineAssessmentOptionBase(SQLModel):
    rituximab_baseline_assessment_id: int = Field(
        foreign_key="rituximab_baseline_assessment.id"
    )
    option_id: int = Field(foreign_key="option.id")


class RituximabBaselineAssessmentOption(
    RituximabBaselineAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_assessment_option"


class RituximabBaselineAssessmentOptionRead(
    RituximabBaselineAssessmentOptionBase, HasId
):
    pass


# --- RituximabBaselinePreviousTreatment --- #


class RituximabBaselinePreviousTreatmentBase(SQLModel):
    assessment_id: int = Field(foreign_key="rituximab_baseline_assessment.id")
    option_id: int = Field(foreign_key="option.id")
    treatment_start_date: date
    treatment_end_date: Optional[date]


class RituximabBaselinePreviousTreatment(
    RituximabBaselineAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_previous_treatment"


class RituximabBaselinePreviousTreatmentCreate(RituximabBaselineAssessmentBase):
    pass


class RituximabBaselinePreviousTreatmentRead(RituximabBaselineAssessmentBase, HasId):
    pass


# --- RituximabCriterion --- #


class RituximabCriteriaBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    criteria1: bool
    criteria2: bool
    criteria3: bool
    criteria4: bool
    criteria5: bool
    criteria6: bool
    criteria7: bool
    alkylating_complication: bool
    alkylating_failure_monitoring_requirements: bool
    cancer: bool
    cni_failure_monitoring_requirements: bool
    cni_therapy_complication: bool
    diabetes: bool
    drug_associated_toxicity: bool
    fall_in_egfr: bool
    hypersensitivity: bool
    risk_factors: bool
    ongoing_severe_disease: bool
    threatened_fertility: bool
    mood_disturbance: bool
    osteoporosis_osteopenia: bool
    previous_hospitalization: bool


class RituximabCriteria(RituximabCriteriaBase, BigIntPK, table=True):
    __tablename__ = "rituximab_criteria"


class RituximabCriteriaRead(RituximabCriteriaBase, HasId):
    pass


# --- RituximabFollowUpAssessment --- #


class RituximabFollowUpAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    visit_date: date
    visit: str
    performance: str
    transplant: str
    haemodialysis: str
    peritoneal_dialysis: str
    immunosuppression: str
    ciclosporin_administered: date
    tacrolimus_administered: date
    cyclophosphamide_administered: date
    chlorambucil_administered: date
    prednisolone_administered: date
    rituximab_administered: date
    immunosuppression_comments: str


class RituximabFollowUpAssessment(
    RituximabFollowUpAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_follow_up_assessment"


class RituximabFollowUpAssessmentRead(RituximabFollowUpAssessmentBase, HasId):
    pass


# --- RituximabFollowUpAssessmentOption --- #


class RituximabFollowUpAssessmentOptionBase(SQLModel):
    rituximab_follow_up_assessment_id: int = Field(
        foreign_key="rituximab_follow_up_assessment.id"
    )
    option_id: int = Field(foreign_key="option.id")


class RituximabFollowUpAssessmentOption(
    RituximabFollowUpAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_follow_up_assessment_option"


class RituximabFollowUpAssessmentOptionRead(
    RituximabFollowUpAssessmentOptionBase, HasId
):
    pass


# --- RituximabToxicity --- #


class RituximabToxicityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    drug_name: str
    other_drug: str
    dose: Optional[float]
    retreatment: str
    toxicity: Optional[str]
    other_toxicity: Optional[str]


class RituximabToxicity(RituximabToxicityBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity"


class RituximabToxicityRead(RituximabToxicityBase, HasId):
    pass


# --- RituximabToxicityOption --- #


class RituximabToxicityOptionBase(SQLModel):
    rituximab_toxicity_id: int = Field(foreign_key="rituximab_toxicity.id")
    option_id: int = Field(foreign_key="option.id")


class RituximabToxicityOption(RituximabToxicityOptionBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity_option"


class RituximabToxicityOptionRead(RituximabToxicityOptionBase, HasId):
    pass


# --- SaltWastingClinicalFeature --- #


class SaltWastingClinicalFeatureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    normal_pregnancy: bool
    abnormal_pregnancy_text: str
    neurological_problems: bool
    seizures: bool
    abnormal_gait: bool
    deafness: bool
    other_neurological_problem: bool
    other_neurological_problem_text: str
    joint_problems: bool
    joint_problems_age: int
    x_ray_abnormalities: bool
    chondrocalcinosis: bool
    other_x_ray_abnormality: bool
    other_x_ray_abnormality_text: str


class SaltWastingClinicalFeature(SaltWastingClinicalFeatureBase, BigIntPK, table=True):
    __tablename__ = "salt_wasting_clinical_feature"


class SaltWastingClinicalFeatureRead(SaltWastingClinicalFeatureBase, HasId):
    pass


# --- SampleInventory --- #


class SampleInventoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    sample_date: date
    urine: bool
    urine_date: date
    urine_volume: str
    serum: bool
    serum_date: date
    serum_volume: str
    plasma: bool
    plasma_date: date
    plasma_volume: str
    dna: bool
    dna_date: date
    sputum: bool
    sputum_date: date
    faeces: bool
    faeces_date: date


class SampleInventory(SampleInventoryBase, BigIntPK, table=True):
    __tablename__ = "sample_inventory"


class SampleInventoryRead(SampleInventoryBase, HasId):
    pass


# --- SampleType --- #


class SampleTypeBase(SQLModel):
    sample_type_label: str = Field(unique=True)


class SampleType(SampleTypeBase, BigIntPK, table=True):
    __tablename__ = "sample_type"


class SampleTypeRead(SampleTypeBase, HasId):
    pass


# --- sixCIT --- #


class SixCITBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    completed_date: date
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    score: int


class SixCIT(SixCITBase, BigIntPK, table=True):
    __tablename__ = "six_cit"


class SixCITRead(SixCITBase, HasId):
    pass


# --- SocioEconomic --- #


class SocioEconomicBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    assessment_date: date
    education: int
    employment_status: int
    first_language: str
    martial_status: str
    smoking: int
    cigarettes_per_day: int
    alcohol: bool
    beer_pints: int
    cider_pints: int
    red_wine: int
    white_wine: int
    spirits: int
    cocktails: int
    units_per_week: int
    literacy: int
    literacy_help: str
    diet: int
    other_diet: str


class SocioEconomic(SocioEconomicBase, BigIntPK, table=True):
    __tablename__ = "socioeconomic"


class SocioEconomicRead(SocioEconomicBase, HasId):
    pass


# --- Specialty --- #


class SpecialtyBase(SQLModel):
    specialty: str = Field(unique=True)


class Specialty(SpecialtyBase, BigIntPK, table=True):
    __tablename__ = "specialty"


class SpecialtyRead(SpecialtyBase, HasId):
    pass


# --- Transplant --- #


class TransplantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    hospital_id: int = Field(foreign_key="hospital.id")
    transplant_hospital_id: int = Field(foreign_key="hospital.id")
    data_source_id: int = Field(foreign_key="data_source.id")
    transplant_date: date
    modality: int
    date_of_recurrence: date
    date_of_failure: date
    recurrence: bool
    date_of_cmv_infection: date
    donor_hla: str
    recipient_hla: str
    graft_loss_cause: str


class Transplant(TransplantBase, BigIntPK, table=True):
    __tablename__ = "transplant"


class TransplantRead(TransplantBase, HasId):
    pass


# --- TransplantBiopsy --- #


class TransplantBiopsyBase(SQLModel):
    transplant_id: int = Field(foreign_key="transplant.id")
    biopsy_date: date
    recurrence: bool


class TransplantBiopsy(TransplantBiopsyBase, table=True):
    __tablename__ = "transplant_biopsy"
    id: int = Field(default=None, primary_key=True)


class TransplantBiopsyRead(TransplantBiopsyBase, HasId):
    pass


# --- TransplantRejection --- #


class TransplantRejectionBase(SQLModel):
    transplant_id: int = Field(foreign_key="transplant.id")
    rejection_date: date


class TransplantRejection(TransplantRejectionBase, BigIntPK, table=True):
    __tablename__ = "transplant_rejection"


class TransplantRejectionRead(TransplantRejectionBase, HasId):
    pass


# --- TubeSample --- #


class TubeSampleBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    sample_date: date
    barcode: str
    ins_state: int


class TubeSample(TubeSampleBase, BigIntPK, table=True):
    __tablename__ = "tube_sample"


class TubeSampleRead(TubeSampleBase, HasId):
    pass