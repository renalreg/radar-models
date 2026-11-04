"""Patient questionnaires and forms."""

from datetime import date

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

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
