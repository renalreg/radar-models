"""The patient and what hangs directly off them."""

from datetime import date

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

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


# --- Death --- #


class DeathBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_death: date
    cause_of_death: str | None = None


class Death(DeathBase, BigIntPK, table=True):
    __tablename__ = "death"


class DeathRead(DeathBase, HasId):
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


# --- ParentalConsanguinity --- #


class ParentalConsanguinityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    has_consanguinity: bool
    consanguinity_details: str | None = None


class ParentalConsanguinity(ParentalConsanguinityBase, BigIntPK, table=True):
    __tablename__ = "parental_consanguinity"


class ParentalConsanguinityRead(ParentalConsanguinityBase, HasId):
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
