"""Hospitals, cohorts, consultants and consents."""

from datetime import date

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- Cohort --- #


class CohortBase(SQLModel):
    cohort_code: str
    cohort_name: str
    cohort_short_name: str


class Cohort(CohortBase, BigIntPK, table=True):
    __tablename__ = "cohort"


class CohortRead(CohortBase, HasId):
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


# --- Specialty --- #


class SpecialtyBase(SQLModel):
    specialty_name: str = Field(unique=True)


class Specialty(SpecialtyBase, BigIntPK, table=True):
    __tablename__ = "specialty"


class SpecialtyRead(SpecialtyBase, HasId):
    pass
