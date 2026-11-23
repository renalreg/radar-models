from datetime import date, datetime
from typing import Optional, Any

from sqlalchemy import BigInteger, UniqueConstraint, CheckConstraint
from sqlmodel import Field, Relationship, SQLModel
# TODO check that the bools are either true or false and how nulls are related
# as is a null false or is a null a lack of answer so could be true - philospophical

# helpers


def options_in_group(option_table: str, group: str) -> Any:
    """Read-only relationship to the options in group that option_table holds
    for the row."""
    return Relationship(
        sa_relationship_kwargs={
            "secondary": option_table,
            "secondaryjoin": f"and_(Option.id == {option_table}.c.option_id,"
            f" Option.option_group == '{group}')",
            "viewonly": True,
        }
    )


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
    has_hospitalisation: bool | None = None
    has_adverse_event: bool | None = None
    new_onset_cancer: date | None = None
    caused_cancer_index: int | None = Field(default=None, foreign_key="option.id")
    thromboembolism: date | None = None
    caused_venous_thrombo_embolism_index: int | None = Field(
        default=None, foreign_key="option.id"
    )
    myocardial_infarction: date | None = None
    caused_acute_myocardial_infarction_index: int | None = Field(
        default=None, foreign_key="option.id"
    )
    stroke: date | None = None
    caused_stroke_index: int | None = Field(default=None, foreign_key="option.id")
    ischaemic_attack: date | None = None
    caused_ischaemic_attack_index: int | None = Field(
        default=None, foreign_key="option.id"
    )
    other_adverse_event: date | None = None
    other_toxicity: str | None = None
    caused_other_index: int | None = Field(default=None, foreign_key="option.id")
    date_of_death: date | None = None
    cause_of_death: str | None = None


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
    height: int | None = None
    weight: float | None = None
    bmi: float | None = None
    hip: float | None = None
    waist: float | None = None
    arm: float | None = None
    up_and_go: float | None = None
    grip_dominant: float | None = None
    grip_non_dominant: float | None = None
    karnofsky_index: int | None = None
    systolic_one: int | None = None
    diastolic_one: int | None = None
    systolic_two: int | None = None
    diastolic_two: int | None = None
    systolic_three: int | None = None
    diastolic_three: int | None = None
    systolic_mean: int | None = None
    diastolic_mean: int | None = None


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
    # the antibody is an option row in option_group "antibody"
    antibody_option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class Antibody(AntibodyBase, BigIntPK, table=True):
    __tablename__ = "antibody"


class AntibodyRead(AntibodyBase, HasId):
    pass


class AvacopanBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    course_type_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    indication_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    start_date: date
    diagnosis_relapse_date: date | None = None
    baseline1weeklabel: date
    baseline1wkdose: float | None = None
    baseline2wkdose: float | None = None
    baseline3wkdose: float | None = None
    baseline4wkdose: float | None = None
    baseline3mthdose: float | None = None
    baseline6mthdose: float | None = None
    baseline9mthdose: float | None = None
    baseline12mthdose: float | None = None


class Avacopan(AvacopanBase, BigIntPK, table=True):
    __tablename__ = "avacopan"
    other_conditions: list["AvacopanOption"] = Relationship(sa_relationship_kwargs={})


class AvacopanOptionBase(SQLModel):
    avacopan_id: int = Field(foreign_key="avacopan.id", sa_type=BigInteger)
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class AvacopanOption(AvacopanOptionBase, BigIntPK, table=True):
    __tablename__ = "avacopan_option"


class AvacopanOptionRead(AvacopanOptionBase, HasId):
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


class CakutClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    clinical_picture_date: date | None = None
    incontinent_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    voiding_difficulties_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    bladder_catheterisation_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    recurrent_uti_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    medication_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    dmsa_scan_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    dmsadate: date | None = None
    dmsafunctionright: int | None = None
    dmsafunctionleft: int | None = None
    dmsarep: str | None = None
    mcug_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mcug_date: date | None = None
    vur_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    vur_right_grade_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    vur_left_grade_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    bladder_normal_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    urethralappearancenormal_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    bladderrep: str | None = None
    mag3_renogram_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mag3_date: date | None = None
    mag3_obstruction_left_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mag3_obstruction_right_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mag3_differential_function_left: float | None = None
    mag3_differential_function_right: float | None = None
    mag3_reflux_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mag3_renogram_rep: str | None = None
    videourodynamics_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    videourodynamics_rep: str | None = None
    uroflowmetry_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    uroflowmetry_rep: str | None = None


class CakutClinicalPicture(CakutClinicalPictureBase, BigIntPK, table=True):
    __tablename__ = "cakut_clinical_picture"

    incontinent_time: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "cakut_clinical_picture_option",
            "primaryjoin": "CakutClinicalPicture.id"
            " == CakutClinicalPictureOption.cakut_clinical_picture_id",
            "secondaryjoin": "and_(Option.id == CakutClinicalPictureOption.option_id,"
            " Option.option_group == 'cakut-clinical-picture.incontinent-time')",
            "viewonly": True,
        }
    )
    bladder_catheterisation_type: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "cakut_clinical_picture_option",
            "primaryjoin": "CakutClinicalPicture.id"
            " == CakutClinicalPictureOption.cakut_clinical_picture_id",
            "secondaryjoin": "and_(Option.id == CakutClinicalPictureOption.option_id,"
            " Option.option_group == 'cakut-clinical-picture.bladder-catheterisation-type')",
            "viewonly": True,
        }
    )
    medlist: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "cakut_clinical_picture_option",
            "primaryjoin": "CakutClinicalPicture.id"
            " == CakutClinicalPictureOption.cakut_clinical_picture_id",
            "secondaryjoin": "and_(Option.id == CakutClinicalPictureOption.option_id,"
            " Option.option_group == 'cakut-clinical-picture.medication')",
            "viewonly": True,
        }
    )


class CakutClinicalPictureOptionBase(SQLModel):
    cakut_clinical_picture_id: int = Field(
        foreign_key="cakut_clinical_picture.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class CakutClinicalPictureOption(CakutClinicalPictureOptionBase, BigIntPK, table=True):
    __tablename__ = "cakut_clinical_picture_option"


class CakutSurginterBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    procedure_type_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    procedure_date: date | None = None
    fi_procedure: str | None = None
    kidney_procedure_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    ureter_procedure_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    bladder_procedure_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    procedure_details: str | None = None


class CakutSurginter(CakutSurginterBase, BigIntPK, table=True):
    __tablename__ = "cakut_surginter"


class CakutSurginterRead(CakutSurginterBase, HasId):
    pass


# --- CalciphylaxisAssessment --- #


class CalciphylaxisAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_lesion: bool
    has_infection: bool


class CalciphylaxisAssessment(CalciphylaxisAssessmentBase, BigIntPK, table=True):
    __tablename__ = "calciphylaxis_assessment"

    lesion_locations: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "calciphylaxis_assessment_option",
            "primaryjoin": "CalciphylaxisAssessment.id"
            " == CalciphylaxisAssessmentOption.calciphylaxis_assessment_id",
            "secondaryjoin": "and_(Option.id == CalciphylaxisAssessmentOption.option_id,"
            " Option.option_group == 'calciphylaxis.lesionIn')",
            "viewonly": True,
        }
    )
    infection_locations: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "calciphylaxis_assessment_option",
            "primaryjoin": "CalciphylaxisAssessment.id"
            " == CalciphylaxisAssessmentOption.calciphylaxis_assessment_id",
            "secondaryjoin": "and_(Option.id == CalciphylaxisAssessmentOption.option_id,"
            " Option.option_group == 'calciphylaxis.infectionIn')",
            "viewonly": True,
        }
    )


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
    tumour_type_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    other_tumour_name: str | None = None
    diagnosis_date: date
    tumour_count: int | None = None
    cns_image_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    progression_date: date | None = None
    t_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    n_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    m_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    radiologic_tumour_size: str | None = None
    pathologic_tumour_size: str | None = None
    tumour_location_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    comments: str | None = None


class CancerTumour(CancerTumourBase, BigIntPK, table=True):
    __tablename__ = "cancer_tumour"


class CancerTumourRead(CancerTumourBase, HasId):
    pass


# --- CKDAfricaGenetic --- #


class CKDAfricaGeneticBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    sickle_cell_index: int | None = Field(foreign_key="option.id", sa_type=BigInteger)
    other_sickle_cell_index: int | None = Field(
        foreign_key="option.id", sa_type=BigInteger
    )
    apol_1_index: int | None = Field(foreign_key="option.id", sa_type=BigInteger)


class CKDAfricaGenetic(CKDAfricaGeneticBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_genetic"


class CKDAfricaGeneticRead(CKDAfricaGeneticBase, HasId):
    pass


# --- CKDAfricaRiskFactor --- #


class CKDAfricaRiskFactorBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    preterm_birth_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    low_birth_weight_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    malnutrition_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    hospital_malnutrition_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )


class CKDAfricaRiskFactor(CKDAfricaRiskFactorBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_risk_factor"


class CKDAfricaRiskFactorRead(CKDAfricaRiskFactorBase, HasId):
    pass


class CKDClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id")
    date: date
    comments: str | None = None


class CKDClinicalPicture(CKDClinicalPictureBase, BigIntPK, table=True):
    __tablename__ = "ckd_clinical_picture"


class CKDClinicalPictureRead(CKDClinicalPictureBase, HasId):
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
    country_code: str = Field(primary_key=True)
    country_name: str


class Country(CountryBase, table=True):
    __tablename__ = "country"


class CountryRead(CountryBase):
    pass


# --- CountryEthnicity --- #


class CountryEthnicityBase(SQLModel):
    ethnicity_id: int | None = Field(
        default=None, foreign_key="ethnicity.id", sa_type=BigInteger
    )
    country_code: str | None = Field(default=None, foreign_key="country.country_code")


# TODO do we need a bigintpk if we say a composite key of ethnicity id and country code
class CountryEthnicity(CountryEthnicityBase, BigIntPK, table=True):
    __tablename__ = "country_ethnicity"


class CountryEthnicityRead(CountryEthnicityBase, HasId):
    pass


# --- CountryNationality --- #


# TODO do we need a bigintpk if we say a composite key of nationality id and country code
class CountryNationalityBase(SQLModel):
    nationality_id: int | None = Field(
        default=None, foreign_key="nationality.id", sa_type=BigInteger
    )
    country_code: str | None = Field(default=None, foreign_key="country.country_code")


class CountryNationality(CountryNationalityBase, BigIntPK, table=True):
    __tablename__ = "country_nationality"


class CountryNationalityRead(CountryNationalityBase, HasId):
    pass


class CystinosisVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    visit_date: date
    urine_measurement_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    urine_output: float | None = None
    voiding_overnight_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    continence_day_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    fluid_intake: float | None = None
    admission_dehydration: int | None = None
    constipation_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    diarrhea_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    nausea_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    vomiting_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    rickets_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    kyphoscoliosis_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    fractures_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    joint_surgery_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    muscle_strength_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    swallowing_difficulties_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    sight_impairment_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    photophobia_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    photophobia_grade_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    keratoplasty_date: date | None = None
    acuity: str | None = None
    gahl_score: str | None = None
    intraocular_pressure_r: str | None = None
    intraocular_pressure_l: str | None = None
    fev1: float | None = None
    vc: float | None = None
    snip: float | None = None
    seizure_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    headache_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    muscle_weakness_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    learning_difficulties_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    cognitive_difficulties_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    movement_disorder_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    intracranial_hypertension_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    diabetes_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    thyroid_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    hypothyroidism_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    tanner_stage_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    wc_cystine: float | None = None
    wc_cystine_date: date | None = None
    wc_cystine_time: str | None = None
    cysteamine_effects: str | None = None
    cysteamine_hrs_since_last_dose: str | None = None


# --- CystinosisAdultVisit --- #


class CystinosisAdultVisitBase(CystinosisVisitBase):
    cystinosis_adult_visit_number_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    ankle_strength: float | None = None
    elbow_strength: float | None = None
    hand_strength: float | None = None
    hip_strength: float | None = None
    knee_strength: float | None = None
    shoulder_strength: float | None = None
    wrist_strength: float | None = None
    swallowing_difficulties_detail: str | None = None
    cognitive_difficulties_score: str | None = None


class CystinosisAdultVisit(CystinosisAdultVisitBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_adult_visit"


class CystinosisAdultVisitRead(CystinosisAdultVisitBase, HasId):
    pass


# --- CystinosisPaedVisit --- #


class CystinosisPaedVisitBase(CystinosisVisitBase):
    cystinosis_paed_visit_number_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    height: float | None = None
    weight: float | None = None
    failure_to_thrive_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    growth_hormone_treatment_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    enteral_feeding_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    feeding_start_date_1: date | None = None
    feeding_end_date_1: date | None = None
    feeding_start_date_2: date | None = None
    feeding_end_date_2: date | None = None
    feeding_start_date_3: date | None = None
    feeding_end_date_3: date | None = None
    normal_food_orally_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    supplements_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    nose_snoring_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    tonsillectomy_date: date | None = None
    adenoidectomy_date: date | None = None
    severe_sight_impairment_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )


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
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    date_of_death: date
    cause_of_death: str | None = None


class Death(DeathBase, BigIntPK, table=True):
    __tablename__ = "death"


class DeathRead(DeathBase, HasId):
    pass


class DentAndLoweAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    aetiology_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    causative_agent_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    other_agent: str | None = None
    other_extra_involvement: str | None = None


class DentAndLoweAssessment(DentAndLoweAssessmentBase, BigIntPK, table=True):
    __tablename__ = "dent_and_lowe_assessment"

    extra_involvements: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "dent_and_lowe_assessment_option",
            "primaryjoin": "DentAndLoweAssessment.id"
            " == DentAndLoweAssessmentOption.dent_and_lowe_assessment_id",
            "secondaryjoin": "and_("
            "Option.id == DentAndLoweAssessmentOption.option_id,"
            " Option.option_group == 'dent-and-lowe-assessment.extra-involvement')",
            "viewonly": True,
        }
    )


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
    has_laser_treatment: bool | None = None
    has_peripheral_neuropathy: bool | None = None
    has_foot_ulcer: bool | None = None


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


class Drug(DrugBase, BigIntPK, table=True):
    __tablename__ = "drug"


class DrugRead(DrugBase, HasId):
    pass


# --- DrugGroup --- #
# a drug can belong to many drug groups, and a group can contain many drugs
class DrugGroupBase(SQLModel):
    drug_group_name: str | None = Field(default=None, unique=True)


class DrugGroup(DrugGroupBase, BigIntPK, table=True):
    __tablename__ = "drug_group"


class DrugGroupRead(DrugGroupBase, HasId):
    pass


# --- Drug <-> DrugGroup link --- #
class DrugToGroupLink(SQLModel, table=True):
    __tablename__ = "drug_to_group"

    drug_id: int = Field(
        foreign_key="drug.id",
        primary_key=True,
        sa_type=BigInteger,
        ondelete="CASCADE",
    )
    drug_group_id: int = Field(
        foreign_key="drug_group.id",
        primary_key=True,
        sa_type=BigInteger,
        ondelete="CASCADE",
    )


# --- EQ5DY --- #


class EQ5DYBase(SQLModel):
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


class EQ5DY(EQ5DYBase, BigIntPK, table=True):
    __tablename__ = "eq5dy"


class EQ5DYRead(EQ5DYBase, HasId):
    pass


# --- EthnicOrigin --- #


class EthnicOriginBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    country_of_birth: int | None = None
    year_of_emigration: int | None = Field(default=None, nullable=True)
    ethnic_origin: int | None = None
    ethnic_origin_father: int | None = None
    ethnic_origin_mother: int | None = None


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
    has_condition: bool


class FamilyHistory(FamilyHistoryBase, BigIntPK, table=True):
    __tablename__ = "family_history"


class FamilyHistoryRead(FamilyHistoryBase, HasId):
    pass


# --- FamilyHistoryRelation --- #


class FamilyHistoryRelationBase(SQLModel):
    family_history_id: int = Field(foreign_key="family_history.id", sa_type=BigInteger)
    relation_id: int = Field(foreign_key="relation.id", sa_type=BigInteger)
    # set when the relative is a patient on Radar: the patient_relation from the
    # family history's patient to them. Its relation_id should match this one;
    # the database does not check that.
    patient_relation_id: int | None = Field(
        default=None, foreign_key="patient_relation.id", sa_type=BigInteger
    )


class FamilyHistoryRelation(FamilyHistoryRelationBase, BigIntPK, table=True):
    __tablename__ = "family_history_relation"


class FamilyHistoryRelationRead(FamilyHistoryRelationBase, HasId):
    pass


# --- PatientRelation --- #


# Two patients on Radar who are family: related_patient_id is patient_id's
# relation_id, e.g. patient 12 is patient 1's Aunt. Each row is stated from
# patient_id's side, and a patient's relatives on Radar are the rows with their
# id in either column. The reverse row (patient 1 is patient 12's niece) is its
# own row, stored only when it is recorded: it cannot be worked out, as relation
# has no reverse for every relation (Aunt -> Niece or Nephew) and a cousin's side
# depends on the other patient's parents.
class PatientRelationBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    related_patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    relation_id: int = Field(foreign_key="relation.id", sa_type=BigInteger)


class PatientRelation(PatientRelationBase, BigIntPK, table=True):
    __tablename__ = "patient_relation"
    __table_args__ = (
        # one relation per pair and direction; the reverse direction is its own row
        UniqueConstraint("patient_id", "related_patient_id"),
        CheckConstraint("patient_id <> related_patient_id"),
    )


class PatientRelationRead(PatientRelationBase, HasId):
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
    a1_index: int | None = None
    d1_index: int | None = None
    a2_index: int | None = None
    d2_index: int | None = None
    a3_index: int | None = None
    d3_index: int | None = None
    a4_index: int | None = None
    d4_index: int | None = None
    a5_index: int | None = None
    d5_index: int | None = None
    a6_index: int | None = None
    d6_index: int | None = None
    a7_index: int | None = None
    d7_index: int | None = None
    anxiety_score: int
    depression_score: int


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
    mest_c_m: str | None = None
    mest_c_e: str | None = None
    mest_c_s: str | None = None
    mest_c_t: str | None = None
    mest_c_c: str | None = None


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
    score_1_index: int | None = None
    score_2_index: int | None = None
    score_3_index: int | None = None
    score_4_index: int | None = None
    score_5_index: int | None = None
    score_6_index: int | None = None
    score_7_index: int | None = None
    score_8_index: int | None = None
    score_9_index: int | None = None
    score_10_index: int | None = None
    score_11_index: int | None = None
    score_12_index: int | None = None
    score_13_index: int | None = None
    score_14_index: int | None = None
    score_15_index: int | None = None
    score_16_index: int | None = None
    score_17_index: int | None = None
    question_1: str | None = None
    score_18_index: int | None = None
    question_2: str | None = None
    score_19_index: int | None = None
    question_3: str | None = None
    score_20_index: int | None = None
    question_4: str | None = None
    question_5: str | None = None
    ipos_score: int | None = None


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
    has_eskd: bool | None = None
    eskd_relative_1_index: int | None = None
    eskd_relative_2_index: int | None = None
    eskd_relative_3_index: int | None = None
    has_chd: bool | None = None
    chd_relative_1_index: int | None = None
    chd_relative_2_index: int | None = None
    chd_relative_3_index: int | None = None
    has_diabetes: bool | None = None
    diabetes_relative_1_index: int | None = None
    diabetes_relative_2_index: int | None = None
    diabetes_relative_3_index: int | None = None


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
    nurture_visit_number: int | None = None
    comorbidities: int | None = None
    has_flu_vaccination: bool
    has_pneumococcal_vaccination: bool
    has_admission: bool | None = None
    admission_number: int | None = None
    admission_emergency: int | None = None
    admission_planned: int | None = None
    admission_days: int | None = None
    admission_antibiotics: int | None = None
    paracetamol_tablets: int | None = None
    paracetamol_years: int | None = None
    cocodamol_tablets: int | None = None
    cocodamol_years: int | None = None
    ibuprofen_tablets: int | None = None
    ibuprofen_years: int | None = None


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
    country_code: str | None = Field(default=None, foreign_key="country.country_code")
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
    country_code: str | None = Field(default=None, foreign_key="country.country_code")
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
    date_of_lmp: date | None = None
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
    procedure_name_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    other_procedure: str | None = None
    date_of_procedure: date
    comments: str | None = None


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
    has_bap1_test: bool | None = None
    bap1_variant: str | None = None
    bap1_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_fh_test: bool | None = None
    fh_variant: str | None = None
    fh_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_flcn_test: bool | None = None
    flcn_variant: str | None = None
    flcn_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_met_test: bool | None = None
    met_variant: str | None = None
    met_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_mitf_test: bool | None = None
    mitf_variant: str | None = None
    mitf_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_pten_test: bool | None = None
    pten_variant: str | None = None
    pten_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_sdha_test: bool | None = None
    sdha_variant: str | None = None
    sdha_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_sdhb_test: bool | None = None
    sdhb_variant: str | None = None
    sdhb_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_sdhc_test: bool | None = None
    sdhc_variant: str | None = None
    sdhc_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_sdhd_test: bool | None = None
    sdhd_variant: str | None = None
    sdhd_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_vhl_test: bool | None = None
    vhl_variant: str | None = None
    vhl_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    has_other_test: bool | None = None
    other_test_name: str | None = None
    other_variant: str | None = None
    other_variant_status_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )


class RenalCancerGenetics(RenalCancerGeneticsBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics"

    bap1_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.bap1action"
    )
    fh_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.fhaction"
    )
    flcn_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.flcnaction"
    )
    met_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.metaction"
    )
    mitf_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.mitfaction"
    )
    pten_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.ptenaction"
    )
    sdha_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.sdhaaction"
    )
    sdhb_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.sdhbaction"
    )
    sdhc_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.sdhcaction"
    )
    sdhd_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.sdhdaction"
    )
    vhl_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.vhlaction"
    )
    other_actions: list["Option"] = options_in_group(
        "renal_cancer_genetics_option", "renalgenetics.otheraction"
    )


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
    tumour_type_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    assessment_date: date
    cns_imaging_method_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    progression_date: date
    t_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    n_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    m_cat_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    rt_size: str
    pt_size: str
    t_loc_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )


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
    visit_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    performance_status_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    transplant_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    haemodialysis_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    peritoneal_dialysis_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    immunosuppression_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    ciclosporin_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    ciclosporin_administered: date | None = None
    tacrolimus_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    tacrolimus_administered: date | None = None
    cyclophosphamide_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    cyclophosphamide_administered: date | None = None
    chlorambucil_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    chlorambucil_administered: date | None = None
    prednisolone_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    prednisolone_administered: date | None = None
    rituximab_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    rituximab_administered: date | None = None
    met_retreatment_criteria_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    immunosuppression_comments: str | None = None


class RituximabFollowUpAssessment(
    RituximabFollowUpAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_follow_up_assessment"

    medications: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "rituximab_follow_up_assessment_option",
            "primaryjoin": "RituximabFollowUpAssessment.id"
            " == RituximabFollowUpAssessmentOption.rituximab_follow_up_assessment_id",
            "secondaryjoin": "and_("
            "Option.id == RituximabFollowUpAssessmentOption.option_id,"
            " Option.option_group == 'rituximab-assessment.medication')",
            "viewonly": True,
        }
    )


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
    # option in group rituximab-administration.drugName: truxima, rixathon, other
    drug_name_index: int = Field(foreign_key="option.id", sa_type=BigInteger)
    # only filled in when drug_name_index is the "other" option
    other_drug: str | None = None
    dose: float | None = None  # mg
    is_retreatment: bool
    other_toxicity: str | None = None


class RituximabToxicity(RituximabToxicityBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity"

    # every toxicity ticked, one rituximab_toxicity_option row each
    toxicities: list["Option"] = Relationship(
        sa_relationship_kwargs={
            "secondary": "rituximab_toxicity_option",
            "primaryjoin": "RituximabToxicity.id"
            " == RituximabToxicityOption.rituximab_toxicity_id",
            "secondaryjoin": "and_(Option.id == RituximabToxicityOption.option_id,"
            " Option.option_group == 'rituximab-administration.toxicity')",
            "viewonly": True,
        }
    )


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
    has_urine_sample: bool | None = None
    urine_date: date | None = None
    urine_volume: str | None = None
    has_serum_sample: bool | None = None
    serum_date: date | None = None
    serum_volume: str | None = None
    has_plasma_sample: bool | None = None
    plasma_date: date | None = None
    plasma_volume: str | None = None
    has_dna_sample: bool | None = None
    dna_date: date | None = None
    has_sputum_sample: bool | None = None
    sputum_date: date | None = None
    has_faeces_sample: bool | None = None
    faeces_date: date | None = None


class SampleInventory(SampleInventoryBase, BigIntPK, table=True):
    __tablename__ = "sample_inventory"


class SampleInventoryRead(SampleInventoryBase, HasId):
    pass


# --- SampleType --- #


# TODO could move into the option table?
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
    six_cit_q4_index: int
    six_cit_q5_index: int
    six_cit_q6_index: int
    six_cit_q7_index: int  # q3 is the question q7 is the answer to q3 hence the sixcit
    six_cit_score: int


class SixCIT(SixCITBase, BigIntPK, table=True):
    __tablename__ = "six_cit"


class SixCITRead(SixCITBase, HasId):
    pass


# --- SocioEconomic --- #


class SocioEconomicBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    education_index: int | None = None
    employment_status_index: int | None = None
    first_language: str | None = None
    martial_status: str | None = None
    smoking_index: int | None = None
    cigarettes_per_day: int | None = None
    has_alcohol_intake: bool | None = None
    beer_pints: int | None = None
    cider_pints: int | None = None
    red_wine: int | None = None
    white_wine: int | None = None
    spirits: int | None = None
    cocktails: int | None = None
    units_per_week: int | None = None
    literacy_index: int | None = None
    literacy_help: str | None = None
    diet_index: int | None = None
    other_diet: str | None = None


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
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    sample_date: date
    barcode: str
    ins_state_index: int | None = None


class TubeSample(TubeSampleBase, BigIntPK, table=True):
    __tablename__ = "tube_sample"


class TubeSampleRead(TubeSampleBase, HasId):
    pass


class VasculitisDetailBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_renalflare: date | None = None
    more_than_one_renalflare_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )


class VasculitisDetail(VasculitisDetailBase, BigIntPK, table=True):
    __tablename__ = "vasculitis_detail"


class VasculitisRead(VasculitisDetailBase, HasId):
    pass


class VasculitisMedsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    review_date: date
    avacopan_infsel_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    avacopan_start_date_1: date | None = None
    avacopan_end_date_1: date | None = None
    avacopan_dose_1: float | None = None
    avacopan_start_date_2: date | None = None
    avacopan_end_date_2: date | None = None
    avacopan_dose_2: float | None = None
    avacopan_start_date_3: date | None = None
    avacopan_end_date_3: date | None = None
    avacopan_dose_3: float | None = None
    azathioprine_infsel_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    azathioprine_start_date_1: date | None = None
    azathioprine_end_date_1: date | None = None
    azathioprine_dose_1: float | None = None
    azathioprine_start_date_2: date | None = None
    azathioprine_end_date_2: date | None = None
    azathioprine_dose_2: float | None = None
    azathioprine_start_date_3: date | None = None
    azathioprine_end_date_3: date | None = None
    azathioprine_dose_3: float | None = None
    cyclophosphamidetab_sel_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    cyclophosphamidetab_start_date_1: date | None = None
    cyclophosphamidetab_end_date_1: date | None = None
    cyclophosphamidetab_dose_1: float | None = None
    cyclophosphamidetab_start_date_2: date | None = None
    cyclophosphamidetab_end_date_2: date | None = None
    cyclophosphamidetab_dose_2: float | None = None
    cyclophosphamidetab_start_date_3: date | None = None
    cyclophosphamidetab_end_date_3: date | None = None
    cyclophosphamidetab_dose_3: float | None = None
    mycophenolate_inf_sel_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    mycophenolate_start_date_1: date | None = None
    mycophenolate_end_date_1: date | None = None
    mycophenolate_dose_1: float | None = None
    mycophenolate_start_date_2: date | None = None
    mycophenolate_end_date_2: date | None = None
    mycophenolate_dose_2: float | None = None
    mycophenolate_start_date_3: date | None = None
    mycophenolate_end_date_3: date | None = None
    mycophenolate_dose_3: float | None = None
    prednisolone_inf_sel_index: int | None = Field(
        default=None, foreign_key="option.id", sa_type=BigInteger
    )
    prednisolone_start_date_1: date | None = None
    prednisolone_end_date_1: date | None = None
    prednisolone_dose_1: float | None = None
    prednisolone_start_date_2: date | None = None
    prednisolone_end_date_2: date | None = None
    prednisolone_dose_2: float | None = None
    prednisolone_start_date_3: date | None = None
    prednisolone_end_date_3: date | None = None
    prednisolone_dose_3: float | None = None
    prednisolone_start_date_4: date | None = None
    prednisolone_end_date_4: date | None = None
    prednisolone_dose_4: float | None = None
    prednisolone_start_date_5: date | None = None
    prednisolone_end_date_5: date | None = None
    prednisolone_dose_5: float | None = None
    prednisolone_start_date_6: date | None = None
    prednisolone_end_date_6: date | None = None
    prednisolone_dose_6: float | None = None
    prednisolone_start_date_7: date | None = None
    prednisolone_end_date_7: date | None = None
    prednisolone_dose_7: float | None = None
    prednisolone_start_date_8: date | None = None
    prednisolone_end_date_8:date| None = None
    prednisolone_dose_8:float | None = None
    dummy_title: date| None = None
    ivig_date: date| None = None
    ivig_inf_number: int | None = None
    rituximab_inf_sel_index: int | None = Field(default=None,foreign_key="option.id", sa_type=BigInteger)
    rituximab_date_1:date|None=None
    rituximab_dose_1:float|None=None
    rituximab_date_2:date|None=None
    rituximab_dose_2:float|None=None
    rituximab_date_3:date|None=None
    rituximab_dose_3:float|None=None
    rituximab_date_4:date|None=None
    rituximab_dose_4:float|None=None
    rituximab_date_5:date|None=None
    rituximab_dose_5:float|None=None
    rituximab_date_6:date|None=None
    rituximab_dose_6:float|None=None
    rituximab_date_7:date|None=None
    rituximab_dose_7:float|None=None
    rituximab_date_8:date|None=None
    rituximab_dose_8:float|None=None
    obinutuzumab_inf_sel_index: int | None = Field(default=None,foreign_key="option.id", sa_type=BigInteger)
    obinutuzumab_date_1:date|None=None
    obinutuzumab_dose_1:float|None=None
    obinutuzumab_date_2:date|None=None
    obinutuzumab_dose_2:float|None=None
    obinutuzumab_date_3:date|None=None
    obinutuzumab_dose_3:float|None=None
    obinutuzumab_date_4:date|None=None
    obinutuzumab_dose_4:float|None=None
    obinutuzumab_date_5:date|None=None
    obinutuzumab_dose_5:float|None=None
    obinutuzumab_date_6:date|None=None
    obinutuzumab_dose_6:float|None=None
    obinutuzumab_date_7:date|None=None
    obinutuzumab_dose_7:float|None=None
    obinutuzumab_date_8:date|None=None
    obinutuzumab_dose_8:float|None=None
    cyclophosphamide_inf_sel_index: int | None = Field(default=None,foreign_key="option.id", sa_type=BigInteger)
    cyclophosphamide_date_1:date|None=None
    cyclophosphamide_dose_1:float|None=None
    cyclophosphamide_date_2:date|None=None
    cyclophosphamide_dose_2:float|None=None
    cyclophosphamide_date_3:date|None=None
    cyclophosphamide_dose_3:float|None=None
    cyclophosphamide_date_4:date|None=None
    cyclophosphamide_dose_4:float|None=None
    cyclophosphamide_date_5:date|None=None
    cyclophosphamide_dose_5:float|None=None
    cyclophosphamide_date_6:date|None=None
    cyclophosphamide_dose_6:float|None=None
    cyclophosphamide_date_7:date|None=None
    cyclophosphamide_dose_7:float|None=None
    cyclophosphamide_date_8:date|None=None
    cyclophosphamide_dose_8:float|None=None
    methylprednisolone_inf_sel_index: int | None = Field(default=None,foreign_key="option.id", sa_type=BigInteger)
    methylprednisolone_date_1:date|None=None
    methylprednisolone_dose_1:float|None=None
    methylprednisolone_date_2:date|None=None
    methylprednisolone_dose_2:float|None=None
    methylprednisolone_date_3:date|None=None
    methylprednisolone_dose_3:float|None=None
    methylprednisolone_date_4:date|None=None
    methylprednisolone_dose_4:float|None=None
    methylprednisolone_date_5:date|None=None
    methylprednisolone_dose_5:float|None=None
    methylprednisolone_date_6:date|None=None
    methylprednisolone_dose_6:float|None=None
    methylprednisolone_date_7:date|None=None
    methylprednisolone_dose_7:float|None=None
    methylprednisolone_date_8:date|None=None
    methylprednisolone_dose_8:float|None=None


class VasculitisMeds(VasculitisMedsBase, BigIntPK, table=True):
    __tablename__ = "vasculitis_meds"