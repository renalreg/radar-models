from datetime import date, datetime

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel
# TODO check that the bools are either true or false and how nulls are related
# as is a null false or is a null a lack of answer so could be true - philospophical


# --- Shared mixins --- #


class BigIntPK(SQLModel):
    """bigint auto-incrementing primary key for every table."""

    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)


class HasId(SQLModel):
    """For Read models: the id is always present once a row exists."""

    id: int


# --- AdultEQ5D5L --- #


class AdultEQ5D5LBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    age: int
    gender_index: int
    mobility_index: int
    self_care_index: int
    usual_activities_index: int
    pain_discomfort_index: int
    anxiety_depression_index: int
    health: int


class AdultEQ5D5L(AdultEQ5D5LBase, BigIntPK, table=True):
    __tablename__ = "adult_eq5d5l"


class AdultEQ5D5LRead(AdultEQ5D5LBase, HasId):
    pass


# --- AdverseEvents --- #


class AdverseEventBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    review_date: date
    has_hospitalisation: bool
    has_adverse_event: bool
    new_onset_cancer: date
    is_cancer_cause: bool
    thromboembolism: date
    caused_venous_thrombo_embolism_index: int
    myocardial_infarction: date
    caused_acute_myocardial_infarction_index: int
    stroke: date
    caused_stroke_index: int
    ischaemic_attack: date
    caused_ischaemic_attack_index: int
    other_adverse_event: date
    other_toxicity: str
    caused_other_index: int
    date_of_death: date
    cause_of_death: str


class AdverseEvent(AdverseEventBase, BigIntPK, table=True):
    __tablename__ = "adverse_event"


class AdverseEventRead(AdverseEventBase, HasId):
    pass


# --- AlportAssessment --- #


class AlportAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    deafness_index: int
    deafness_date: date | None = None
    hearing_aid_date: date | None = None


class AlportAssessment(AlportAssessmentBase, BigIntPK, table=True):
    __tablename__ = "alport_assessment"


class AlportAssessmentRead(AlportAssessmentBase, HasId):
    pass


# --- Anthropometric --- #


class AnthropometricBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
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
    karnofsky_index: int
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


# --- Antibody --- #


class AntibodyBase(SQLModel):
    # unique=True makes this 1-to-1: at most one antibody row per patient_diagnosis
    patient_diagnosis_id: int = Field(
        foreign_key="patient_diagnosis.id", unique=True, sa_type=BigInteger
    )
    antibody_option_id: int = Field(
        foreign_key="antibody_option.id", sa_type=BigInteger
    )


class Antibody(AntibodyBase, BigIntPK, table=True):
    __tablename__ = "antibody"


class AntibodyRead(AntibodyBase, HasId):
    pass


# --- AntibodyOption --- #


class AntibodyOptionBase(SQLModel):
    antibody_label: str = Field(unique=True)
    is_official: bool = Field(default=False)


class AntibodyOption(AntibodyOptionBase, BigIntPK, table=True):
    __tablename__ = "antibody_option"


class AntibodyOptionRead(AntibodyOptionBase, HasId):
    pass


# --- Biomarker --- #


class BiomarkerBase(SQLModel):
    biomarker_name: str
    biomarker_type: str | None = None


class Biomarker(BiomarkerBase, BigIntPK, table=True):
    __tablename__ = "biomarker"


class BiomarkerRead(BiomarkerBase, HasId):
    pass


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


# --- CalciphylaxisAssessment --- #


class CalciphylaxisAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_lesion: bool
    lesion_location: str
    has_infection: bool
    infection_location: str


class CalciphylaxisAssessment(CalciphylaxisAssessmentBase, BigIntPK, table=True):
    __tablename__ = "calciphylaxis_assessment"


class CalciphylaxisAssessmentRead(CalciphylaxisAssessmentBase, HasId):
    pass


# --- CalciphylaxisAssessmentOption --- #


class CalciphylaxisAssessmentOptionBase(SQLModel):
    calciphylaxis_assessment_id: int = Field(
        foreign_key="calciphylaxis_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class CalciphylaxisAssessmentOption(
    CalciphylaxisAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "calciphylaxis_assessment_option"


class CalciphylaxisAssessmentOptionRead(CalciphylaxisAssessmentOptionBase, HasId):
    pass


# --- CancerTumours --- #


class CancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    preterm_birth: str
    low_birth_weight: str
    malnutrition: str
    hospital_malnutrition: str


class CKDAfricaRiskFactor(CKDAfricaRiskFactorBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_risk_factor"


class CKDAfricaRiskFactorRead(CKDAfricaRiskFactorBase, HasId):
    pass


# --- ClinicalLetter --- #


class ClinicalLetterBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    letter_date: date
    letter_comments: str


class ClinicalLetter(ClinicalLetterBase, BigIntPK, table=True):
    __tablename__ = "clinical_letter"


class ClinicalLetterRead(ClinicalLetterBase, HasId):
    pass


# --- Code --- #


class CodeBase(SQLModel):
    coding_system: str
    code_describes: str | None = None
    code_value: str
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
    cohort_id: int = Field(foreign_key="cohort.id", sa_type=BigInteger)
    diagnosis_id: int = Field(foreign_key="diagnosis.id", sa_type=BigInteger)
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class CohortDiagnosis(CohortDiagnosisBase, BigIntPK, table=True):
    __tablename__ = "cohort_diagnosis"


class CohortDiagnosisRead(CohortDiagnosisBase, HasId):
    pass


# --- CohortObservation --- #


class CohortObservationBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id", sa_type=BigInteger)
    observation_id: int = Field(foreign_key="observation.id", sa_type=BigInteger)
    observation_weight: int | None = None


class CohortObservation(CohortObservationBase, BigIntPK, table=True):
    __tablename__ = "cohort_observation"


class CohortObservationRead(CohortObservationBase, HasId):
    pass


# --- CohortPatient --- #


class CohortPatientBase(SQLModel):
    cohort_id: int = Field(foreign_key="cohort.id", sa_type=BigInteger)
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    recruited_date: date
    removed_date: date | None = None


class CohortPatient(CohortPatientBase, BigIntPK, table=True):
    __tablename__ = "cohort_patient"


class CohortPatientRead(CohortPatientBase, HasId):
    pass


# --- Consent --- #


class ConsentBase(SQLModel):
    consent_code: str
    consent_label: str | None = None
    is_paediatric: bool = Field(default=False)
    release_date: date
    consent_url: str | None = None
    is_retired: bool = Field(default=False)


class Consent(ConsentBase, BigIntPK, table=True):
    __tablename__ = "consent"


class ConsentRead(ConsentBase, HasId):
    pass


# --- Consultant --- #


class ConsultantBase(SQLModel):
    specialty_id: int = Field(foreign_key="specialty.id", sa_type=BigInteger)
    first_name: str
    last_name: str
    email: str | None = None
    telephone_number: str | None = None
    gmc_number: int | None = None


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
    ethnicity_id: int | None = Field(
        default=None, foreign_key="ethnicity.id", sa_type=BigInteger
    )
    country_id: int | None = Field(
        default=None, foreign_key="country.id", sa_type=BigInteger
    )


class CountryEthnicity(CountryEthnicityBase, BigIntPK, table=True):
    __tablename__ = "country_ethnicity"


class CountryEthnicityRead(CountryEthnicityBase, HasId):
    pass


# --- CountryNationality --- #


class CountryNationalityBase(SQLModel):
    nationality_id: int | None = Field(
        default=None, foreign_key="nationality.id", sa_type=BigInteger
    )
    country_id: int | None = Field(
        default=None, foreign_key="country.id", sa_type=BigInteger
    )


class CountryNationality(CountryNationalityBase, BigIntPK, table=True):
    __tablename__ = "country_nationality"


class CountryNationalityRead(CountryNationalityBase, HasId):
    pass


# --- CystinosisAdultVisit --- #


class CystinosisAdultVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    cystinosis_adult_visit_number: int
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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    cystinosis_paed_visit_number: int
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
    cystinosis_paed_visit_id: int = Field(
        foreign_key="cystinosis_paed_visit.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_death: date
    cause_of_death: str | None = None


class Death(DeathBase, BigIntPK, table=True):
    __tablename__ = "death"


class DeathRead(DeathBase, HasId):
    pass


# --- DentAndLoweAssessment --- #


class DentAndLoweAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
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
    dent_and_lowe_assessment_id: int = Field(
        foreign_key="dent_and_lowe_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class DentAndLoweAssessmentOption(
    DentAndLoweAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "dent_and_lowe_assessment_option"


class DentAndLoweAssessmentOptionRead(DentAndLoweAssessmentOptionBase, HasId):
    pass


# --- DiabeticComplication --- #


class DiabeticComplicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    retinopathy_index: int
    has_laser_treatment: bool
    has_peripheral_neuropathy: bool
    has_foot_ulcer: bool


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
    diagnosis_id: int = Field(foreign_key="diagnosis.id", sa_type=BigInteger)
    code_id: int = Field(foreign_key="code.id", sa_type=BigInteger)


class DiagnosisCode(DiagnosisCodeBase, BigIntPK, table=True):
    __tablename__ = "diagnosis_code"


class DiagnosisCodeRead(DiagnosisCodeBase, HasId):
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


# --- Drug --- #


class DrugBase(SQLModel):
    drug_name: str
    drug_group_id: int | None = Field(
        default=None, foreign_key="drug_group.id", sa_type=BigInteger
    )


class Drug(DrugBase, BigIntPK, table=True):
    __tablename__ = "drug"


class DrugRead(DrugBase, HasId):
    pass


# --- DrugGroup --- #


class DrugGroupBase(SQLModel):
    drug_group_name: str | None = Field(default=None, unique=True)
    parent_drug_group_id: int | None = Field(
        default=None, foreign_key="drug_group.id", sa_type=BigInteger
    )


class DrugGroup(DrugGroupBase, BigIntPK, table=True):
    __tablename__ = "drug_group"


class DrugGroupRead(DrugGroupBase, HasId):
    pass


# --- EQ5DY --- #


class EQ5DYBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    age: int
    gender_index: int
    mobility_index: int
    self_care_index: int
    usual_activities_index: int
    pain_discomfort_index: int
    anxiety_depression_index: int
    health: int


class EQ5DY(EQ5DYBase, BigIntPK, table=True):
    __tablename__ = "eq5dy"


class EQ5DYRead(EQ5DYBase, HasId):
    pass


# --- EthnicOrigin --- #


class EthnicOriginBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
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
    ethnicity_code: str | None = None
    ethnicity_label: str | None = None


class Ethnicity(EthnicityBase, BigIntPK, table=True):
    __tablename__ = "ethnicity"


class EthnicityRead(EthnicityBase, HasId):
    pass


# --- FamilyHistory --- #


class FamilyHistoryBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    diagnosis_id: int | None = Field(
        default=None, foreign_key="diagnosis.id", sa_type=BigInteger
    )
    relation_patient_id: int | None = Field(
        default=None, foreign_key="patient.id", sa_type=BigInteger
    )
    has_condition: bool


class FamilyHistory(FamilyHistoryBase, BigIntPK, table=True):
    __tablename__ = "family_history"


class FamilyHistoryRead(FamilyHistoryBase, HasId):
    pass


# --- FamilyHistoryRelation --- #


class FamilyHistoryRelationBase(SQLModel):
    family_history_id: int = Field(foreign_key="family_history.id", sa_type=BigInteger)
    relation_id: int = Field(foreign_key="relation.id", sa_type=BigInteger)


class FamilyHistoryRelation(FamilyHistoryRelationBase, BigIntPK, table=True):
    __tablename__ = "family_history_relation"


class FamilyHistoryRelationRead(FamilyHistoryRelationBase, HasId):
    pass


# --- FamilyHistoryRelationPatient --- #


class FamilyHistoryRelationPatientBase(SQLModel):
    family_history_relation_id: int = Field(
        foreign_key="family_history_relation.id", sa_type=BigInteger
    )
    patient_id: int | None = Field(
        default=None, foreign_key="patient.id", sa_type=BigInteger
    )


class FamilyHistoryRelationPatient(
    FamilyHistoryRelationPatientBase, BigIntPK, table=True
):
    __tablename__ = "family_history_relation_patient"


class FamilyHistoryRelationPatientRead(FamilyHistoryRelationPatientBase, HasId):
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


# --- FrontPageStat --- #


class FrontPageStatBase(SQLModel):
    stat_label: str
    stat_value: str


class FrontPageStat(FrontPageStatBase, BigIntPK, table=True):
    __tablename__ = "front_page_stat"


class FrontPageStatRead(FrontPageStatBase, HasId):
    pass


# --- FuanAssessment --- #


class FuanAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    picture_date: date
    has_gout: bool
    gout_date: date | None = None
    has_family_gout: bool
    thp: str | None = None
    has_uti: bool
    fuan_comments: str | None = None


class FuanAssessment(FuanAssessmentBase, BigIntPK, table=True):
    __tablename__ = "fuan_assessment"


class FuanAssessmentRead(FuanAssessmentBase, HasId):
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


# --- HADS --- #


class HADSBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    a1_index: int
    d1_index: int
    a2_index: int
    d2_index: int
    a3_index: int
    d3_index: int
    a4_index: int
    d4_index: int
    a5_index: int
    d5_index: int
    a6_index: int
    d6_index: int
    a7_index: int
    d7_index: int
    anxiety_score: int


class HADS(HADSBase, BigIntPK, table=True):
    __tablename__ = "hads"


class HADSRead(HADSBase, HasId):
    pass


# --- Hnf1bAssessment --- #


class Hnf1bAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_single_kidney: bool
    has_hyperuricemia_gout: bool
    has_genital_malformation: bool
    genital_malformation_details: str
    has_familial_cystic_disease: bool
    has_hypertension: bool


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
    hospital_id: int = Field(foreign_key="hospital.id", sa_type=BigInteger)
    consultant_id: int = Field(foreign_key="consultant.id", sa_type=BigInteger)


class HospitalConsultant(HospitalConsultantBase, BigIntPK, table=True):
    __tablename__ = "hospital_consultant"


class HospitalConsultantRead(HospitalConsultantBase, HasId):
    pass


# --- HospitalPatient --- #


class HospitalPatientBase(SQLModel):
    hospital_id: int = Field(foreign_key="hospital.id", sa_type=BigInteger)
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    first_seen_date: date
    discharged_date: date | None = None


class HospitalPatient(HospitalPatientBase, BigIntPK, table=True):
    __tablename__ = "hospital_patient"


class HospitalPatientRead(HospitalPatientBase, HasId):
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


# --- HSPAssessment --- #


class HSPAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_haematuria: bool
    is_nephrotic: bool
    mest_c_m: str
    mest_c_e: str
    mest_c_s: str
    mest_c_t: str
    mest_c_c: str


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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date


class IGAResearch(IGAResearchBase, BigIntPK, table=True):
    __tablename__ = "iga_research"


class IGAResearchRead(IGAResearchBase, HasId):
    pass


# --- IGAResearchOption --- #


class IGAResearchOptionBase(SQLModel):
    iga_research_id: int = Field(foreign_key="iga_research.id", sa_type=BigInteger)
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class IGAResearchOption(IGAResearchOptionBase, BigIntPK, table=True):
    __tablename__ = "iga_research_option"


class IGAResearchOptionRead(IGAResearchOptionBase, HasId):
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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_oedema: bool
    has_hypovoloemia: bool
    has_fever: bool
    has_thrombosis: bool
    has_peritonitis: bool
    has_pulmonary_oedema: bool
    has_hypertension: bool
    has_rash: bool
    rash_details: str | None = None
    has_infection: bool
    infection_details: str | None = None
    has_ophthalmoscopy: bool
    ophthalmoscopy_details: str | None = None
    ins_comments: str | None = None


class InsAssessment(InsAssessmentBase, BigIntPK, table=True):
    __tablename__ = "ins_assessment"


class InsAssessmentRead(InsAssessmentBase, HasId):
    pass


# --- InsRelapse --- #


class InsRelapseBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_relapse: date
    kidney_type: str | None = None
    viral_trigger: str | None = None
    immunisation_trigger: str | None = None
    other_trigger: str | None = None
    has_high_dose_oral_prednisolone: bool
    has_iv_methyl_prednisolone: bool
    date_of_remission: date | None = None
    remission_type: str | None = None
    peak_acr: float | None = None
    peak_pcr: float | None = None
    remission_acr: float | None = None
    remission_pcr: float | None = None
    peak_protein_dipstick: str | None = None
    remission_protein_dipstick: str | None = None
    is_relapse_sample_taken: bool


class InsRelapse(InsRelapseBase, BigIntPK, table=True):
    __tablename__ = "ins_relapse"


class InsRelapseRead(InsRelapseBase, HasId):
    pass


# --- IPOS --- #


class IPOSBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    score_1_index: int
    score_2_index: int
    score_3_index: int
    score_4_index: int
    score_5_index: int
    score_6_index: int
    score_7_index: int
    score_8_index: int
    score_9_index: int
    score_10_index: int
    score_11_index: int
    score_12_index: int
    score_13_index: int
    score_14_index: int
    score_15_index: int
    score_16_index: int
    score_17_index: int
    question_1: str
    score_18_index: int
    question_2: str
    score_19_index: int
    question_3: str
    score_20_index: int
    question_4: str
    question_5: str
    ipos_score: int


class IPOS(IPOSBase, BigIntPK, table=True):
    __tablename__ = "ipos"


class IPOSRead(IPOSBase, HasId):
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


# --- MpgnAssessment --- #


class MpgnAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_oedema: bool
    has_hypertension: bool
    has_urticaria: bool
    has_partial_lipodystrophy: bool
    has_infection: bool
    infection_details: str | None = None
    has_ophthalmoscopy: bool
    ophthalmoscopy_details: str | None = None
    mpgn_comments: str | None = None


class MpgnAssessment(MpgnAssessmentBase, BigIntPK, table=True):
    __tablename__ = "mpgn_assessment"


class MpgnAssessmentRead(MpgnAssessmentBase, HasId):
    pass


# --- Nationality --- #


class NationalityBase(SQLModel):
    nationality_label: str | None = None


class Nationality(NationalityBase, BigIntPK, table=True):
    __tablename__ = "nationality"


class NationalityRead(NationalityBase, HasId):
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


# --- Observation --- #


class ObservationBase(SQLModel):
    sample_type_id: int = Field(foreign_key="sample_type.id", sa_type=BigInteger)
    observation_name: str
    observation_short_name: str
    min_value: float | None = None
    max_value: float | None = None
    observation_units: str | None = None


class Observation(ObservationBase, BigIntPK, table=True):
    __tablename__ = "observation"


class ObservationRead(ObservationBase, HasId):
    pass


# --- ObservationCode --- #


class ObservationCodeBase(SQLModel):
    observation_id: int = Field(foreign_key="observation.id", sa_type=BigInteger)
    code_id: int = Field(foreign_key="code.id", sa_type=BigInteger)


class ObservationCode(ObservationCodeBase, BigIntPK, table=True):
    __tablename__ = "observation_code"


class ObservationCodeRead(ObservationCodeBase, HasId):
    pass


# --- ObservationOptions --- #


class ObservationOptionsBase(SQLModel):
    observation_id: int = Field(foreign_key="observation.id", sa_type=BigInteger)
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    worried_index: int
    sad_index: int
    pain_index: int
    tired_index: int
    annoyed_index: int
    school_index: int
    sleep_index: int
    routine_index: int
    activities_index: int


class PaedsCHU9D(PaedsCHU9DBase, BigIntPK, table=True):
    __tablename__ = "paeds_chu9d"


class PaedsCHU9DRead(PaedsCHU9DBase, HasId):
    pass


# --- PAM --- #


class PAMBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    pam_q1_index: int
    pam_q2_index: int
    pam_q3_index: int
    pam_q4_index: int
    pam_q5_index: int
    pam_q6_index: int
    pam_q7_index: int
    pam_q8_index: int
    pam_q9_index: int
    pam_q10_index: int
    pam_q11_index: int
    pam_q12_index: int
    pam_q13_index: int


class PAM(PAMBase, BigIntPK, table=True):
    __tablename__ = "pam"


class PAMRead(PAMBase, HasId):
    pass


# --- ParentalConsanguinity --- #


class ParentalConsanguinityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    has_consanguinity: bool
    consanguinity_details: str | None = None


class ParentalConsanguinity(ParentalConsanguinityBase, BigIntPK, table=True):
    __tablename__ = "parental_consanguinity"


class ParentalConsanguinityRead(ParentalConsanguinityBase, HasId):
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


# --- Patient --- #


class PatientBase(SQLModel):
    patient_comment: str | None = None
    is_test: bool = Field(default=False)
    is_control: bool = Field(default=False)


class Patient(PatientBase, BigIntPK, table=True):
    __tablename__ = "patient"


class PatientRead(PatientBase, HasId):
    pass


# --- PatientAddress --- #


class PatientAddressBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    country_id: int | None = Field(
        default=None, foreign_key="country.id", sa_type=BigInteger
    )
    from_date: date | None = None
    to_date: date | None = None
    address1: str | None = None
    address2: str | None = None
    address3: str | None = None
    address4: str | None = None
    postcode: str | None = None


class PatientAddress(PatientAddressBase, BigIntPK, table=True):
    __tablename__ = "patient_address"


class PatientAddressRead(PatientAddressBase, HasId):
    pass


# --- PatientAlias --- #


class PatientAliasBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    first_name: str | None = None
    last_name: str | None = None


class PatientAlias(PatientAliasBase, BigIntPK, table=True):
    __tablename__ = "patient_alias"


class PatientAliasRead(PatientAliasBase, HasId):
    pass


# --- PatientConsent --- #


class PatientConsentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    consent_id: int | None = Field(
        default=None, foreign_key="consent.id", sa_type=BigInteger
    )
    signed_on_date: date
    withdrawn_on_date: date | None = None


class PatientConsent(PatientConsentBase, BigIntPK, table=True):
    __tablename__ = "patient_consent"


class PatientConsentRead(PatientConsentBase, HasId):
    pass


# --- PatientConsultant --- #


class PatientConsultantBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    consultant_id: int = Field(foreign_key="consultant.id", sa_type=BigInteger)
    from_date: date
    to_date: date | None = None


class PatientConsultant(PatientConsultantBase, BigIntPK, table=True):
    __tablename__ = "patient_consultant"


class PatientConsultantRead(PatientConsultantBase, HasId):
    pass


# --- PatientDemographic --- #


class PatientDemographicBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    ethnicity_id: int | None = Field(
        default=None, foreign_key="ethnicity.id", sa_type=BigInteger
    )
    country_id: int | None = Field(
        default=None, foreign_key="country.id", sa_type=BigInteger
    )
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender_index: int | None = None
    mobile_number: str | None = None
    email_address: str | None = None


class PatientDemographic(PatientDemographicBase, BigIntPK, table=True):
    __tablename__ = "patient_demographic"


class PatientDemographicRead(PatientDemographicBase, HasId):
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


# --- PatientIdentifier --- #


class PatientIdentifierBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    identifier_id: int = Field(foreign_key="identifier.id", sa_type=BigInteger)
    identifier_value: str


class PatientIdentifier(PatientIdentifierBase, BigIntPK, table=True):
    __tablename__ = "patient_identifier"


class PatientIdentifierRead(PatientIdentifierBase, HasId):
    pass


# --- PatientNationality --- #


class PatientNationalityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    nationality_id: int = Field(foreign_key="nationality.id", sa_type=BigInteger)


class PatientNationality(PatientNationalityBase, BigIntPK, table=True):
    __tablename__ = "patient_nationality"


class PatientNationalityRead(PatientNationalityBase, HasId):
    pass


# --- PatientReconsent --- #


class PatientReconsentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    sent_date: date | None = None
    response_date: date | None = None


class PatientReconsent(PatientReconsentBase, BigIntPK, table=True):
    __tablename__ = "patient_reconsent"


class PatientReconsentRead(PatientReconsentBase, HasId):
    pass


class PatientReconsentCreate(PatientReconsentBase):
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


# --- Post --- #


class PostBase(SQLModel):
    post_title: str
    published_date: datetime
    post_body: str


class Post(PostBase, BigIntPK, table=True):
    __tablename__ = "post"


class PostRead(PostBase, HasId):
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


# --- Relation --- #


class RelationBase(SQLModel):
    relation_label: str


class Relation(RelationBase, BigIntPK, table=True):
    __tablename__ = "relation"


class RelationRead(RelationBase, HasId):
    pass


# --- RenalCancerGenetics --- #


class RenalCancerGeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_bap1_test: bool
    bap1_variant: str
    bap1_variant_status: str
    has_fh_test: bool
    fh_variant: str
    fh_variant_status: str
    has_flcn_test: bool
    flcn_variant: str
    flcn_variant_status: str
    has_met_test: bool
    met_variant: str
    met_variant_status: str
    has_mitf_test: bool
    mitf_variant: str
    mitf_variant_status: str
    has_pten_test: bool
    pten_variant: str
    pten_variant_status: str
    has_sdha_test: bool
    sdha_variant: str
    sdha_variant_status: str
    has_sdhb_test: bool
    sdhb_variant: str
    sdhb_variant_status: str
    has_sdhc_test: bool
    sdhc_variant: str
    sdhc_variant_status: str
    has_sdhd_test: bool
    sdhd_variant: str
    sdhd_variant_status: str
    has_vhl_test: bool
    vhl_variant: str
    vhl_variant_status: str
    has_other_test: bool
    other_test_name: str
    other_variant: str
    other_variant_status: str


class RenalCancerGenetics(RenalCancerGeneticsBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics"


class RenalCancerGeneticsRead(RenalCancerGeneticsBase, HasId):
    pass


# --- RenalCancerGeneticsOption --- #


class RenalCancerGeneticsOptionBase(SQLModel):
    renal_cancer_genetics_id: int = Field(
        foreign_key="renal_cancer_genetics.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RenalCancerGeneticsOption(RenalCancerGeneticsOptionBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics_option"


class RenalCancerGeneticsOptionRead(RenalCancerGeneticsOptionBase, HasId):
    pass


# --- RenalCancerTumour --- #


class RenalCancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    tumor_type: str
    assessment_date: date
    cns_imaging_method: str
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


# --- RituximabBaselineAssessment --- #


class RituximabBaselineAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    assessment_date: date
    nephropathy: str | None = None
    has_steroids: bool
    other_previous_treatment: str | None = None
    has_past_remission: bool
    performance_status_index: int | None = None
    has_comorbidities: bool


class RituximabBaselineAssessment(
    RituximabBaselineAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_assessment"


class RituximabBaselineAssessmentRead(RituximabBaselineAssessmentBase, HasId):
    pass


# --- RituximabBaselineAssessmentOption --- #


class RituximabBaselineAssessmentOptionBase(SQLModel):
    rituximab_baseline_assessment_id: int = Field(
        foreign_key="rituximab_baseline_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


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
    rituximab_baseline_assessment_id: int = Field(
        foreign_key="rituximab_baseline_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)
    treatment_start_date: date
    treatment_end_date: date | None = None


class RituximabBaselinePreviousTreatment(
    RituximabBaselinePreviousTreatmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_previous_treatment"


class RituximabBaselinePreviousTreatmentCreate(RituximabBaselinePreviousTreatmentBase):
    pass


class RituximabBaselinePreviousTreatmentRead(
    RituximabBaselinePreviousTreatmentBase, HasId
):
    pass


# --- RituximabCriterion --- #


class RituximabCriteriaBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_criterion_1: bool
    has_criterion_2: bool
    has_criterion_3: bool
    has_criterion_4: bool
    has_criterion_5: bool
    has_criterion_6: bool
    has_criterion_7: bool
    has_alkylating_complication: bool
    has_alkylating_failure_monitoring_requirements: bool
    has_cancer: bool
    has_cni_failure_monitoring_requirements: bool
    has_cni_therapy_complication: bool
    has_diabetes: bool
    has_drug_associated_toxicity: bool
    has_fall_in_egfr: bool
    has_hypersensitivity: bool
    has_risk_factors: bool
    has_ongoing_severe_disease: bool
    has_threatened_fertility: bool
    has_mood_disturbance: bool
    has_osteoporosis_osteopenia: bool
    has_previous_hospitalization: bool


class RituximabCriteria(RituximabCriteriaBase, BigIntPK, table=True):
    __tablename__ = "rituximab_criteria"


class RituximabCriteriaRead(RituximabCriteriaBase, HasId):
    pass


# --- RituximabFollowUpAssessment --- #


class RituximabFollowUpAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    visit_date: date
    rituximab_follow_up_visit: str
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
        foreign_key="rituximab_follow_up_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    drug_name: str
    other_drug: str
    dose: float | None = None
    retreatment: str
    toxicity: str | None = None
    other_toxicity: str | None = None


class RituximabToxicity(RituximabToxicityBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity"


class RituximabToxicityRead(RituximabToxicityBase, HasId):
    pass


# --- RituximabToxicityOption --- #


class RituximabToxicityOptionBase(SQLModel):
    rituximab_toxicity_id: int = Field(
        foreign_key="rituximab_toxicity.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RituximabToxicityOption(RituximabToxicityOptionBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity_option"


class RituximabToxicityOptionRead(RituximabToxicityOptionBase, HasId):
    pass


# --- SaltWastingClinicalFeature --- #


class SaltWastingClinicalFeatureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    is_normal_pregnancy: bool
    abnormal_pregnancy_text: str | None = None
    has_neurological_problems: bool
    has_seizures: bool
    has_abnormal_gait: bool
    has_deafness: bool
    has_other_neurological_problem: bool
    other_neurological_problem_text: str | None = None
    has_joint_problems: bool
    joint_problems_age: int | None = None
    has_x_ray_abnormalities: bool
    has_chondrocalcinosis: bool
    has_other_x_ray_abnormality: bool
    other_x_ray_abnormality_text: str | None = None


class SaltWastingClinicalFeature(SaltWastingClinicalFeatureBase, BigIntPK, table=True):
    __tablename__ = "salt_wasting_clinical_feature"


class SaltWastingClinicalFeatureRead(SaltWastingClinicalFeatureBase, HasId):
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


# --- SampleType --- #


class SampleTypeBase(SQLModel):
    sample_type_label: str = Field(unique=True)


class SampleType(SampleTypeBase, BigIntPK, table=True):
    __tablename__ = "sample_type"


class SampleTypeRead(SampleTypeBase, HasId):
    pass


# --- sixCIT --- #


class SixCITBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    completed_date: date
    six_cit_q1_index: int
    six_cit_q2_index: int
    six_cit_q3_index: int
    six_cit_q4_index: int
    six_cit_q5_index: int
    six_cit_q6_index: int
    six_cit_q7_index: int
    six_cit_score: int


class SixCIT(SixCITBase, BigIntPK, table=True):
    __tablename__ = "six_cit"


class SixCITRead(SixCITBase, HasId):
    pass


# --- SocioEconomic --- #


class SocioEconomicBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    education_index: int
    employment_status_index: int
    first_language: str
    martial_status: str
    smoking_index: int
    cigarettes_per_day: int
    has_alcohol_intake: bool
    beer_pints: int
    cider_pints: int
    red_wine: int
    white_wine: int
    spirits: int
    cocktails: int
    units_per_week: int
    literacy_index: int
    literacy_help: str
    diet_index: int
    other_diet: str


class SocioEconomic(SocioEconomicBase, BigIntPK, table=True):
    __tablename__ = "socioeconomic"


class SocioEconomicRead(SocioEconomicBase, HasId):
    pass


# --- Specialty --- #


class SpecialtyBase(SQLModel):
    specialty_name: str = Field(unique=True)


class Specialty(SpecialtyBase, BigIntPK, table=True):
    __tablename__ = "specialty"


class SpecialtyRead(SpecialtyBase, HasId):
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
    mismatch_hla: str | None = None
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