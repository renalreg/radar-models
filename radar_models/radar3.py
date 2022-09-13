import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, Enum
from sqlalchemy import Column

# --- Biomarkers --- #
class BiomarkerBase(SQLModel):
    name: str
    type: str


class Biomarker(BiomarkerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BiomarkerCreate(BiomarkerBase):
    pass


class BiomarkerRead(BiomarkerBase):
    id: int


# --- Codes --- #
# TODO: check current indexes and check constraints
class CodeBase(SQLModel):
    system: str
    code: str
    display: str


class Code(CodeBase, table=True):
    pass


class CodeCreate(CodeBase):
    id: Optional[int] = Field(default=None, primary_key=True)


class CodeRead:
    id: int


# --- Countries --- #
# TODO: This table seems to only be used by groups and almost all of them
# are GB. Is this used by anything else? Can we remove this?
class CountryBase(SQLModel):
    code: str = Field(primary_key=True)
    label: str


class Countries(CountryBase, table=True):
    pass


class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    pass


# --- Consents --- #


class ConsentTypeEnum(str, enum.Enum):
    form = "FORM"
    information_sheet = "INFORMATION_SHEET"


class ConsentBase(SQLModel):
    code: str
    label: Optional[str]
    paediatric: bool = Field(default=False)
    from_date: datetime
    link_url: str
    retired: bool = Field(default=False)
    consent_type: ConsentTypeEnum = Field(sa_column=Column(Enum(ConsentTypeEnum)))
    weight: int


class Consents(ConsentBase, table=True):
    pass


class ConsentsCreate(ConsentBase):
    pass


class ConsentRead(ConsentBase):
    pass


# --- Groups --- #

# TODO: This should be a new table
class GroupTypeEnum(str, enum.Enum):
    cohort = "COHORT"
    hospital = "HOSPITAL"
    other = "OTHER"
    system = "SYSTEM"


# TODO: DB has a composite index [code, type] which seems overkill for a table with less than
# 200 rows. Figure out if you need it, speak to George.
class GroupBase(SQLModel):
    type: GroupTypeEnum = Field(sa_column=Column(Enum(GroupTypeEnum)), index=True)
    code: str = Field(index=True)
    name: str
    short_name: str
    instructions: Optional[str]
    multiple_diagnoses: bool = False
    is_recruitment_number_group: bool = False
    parent_group_id: Optional[int] = Field(foreign_key="groups.id")
    is_transplant_centre: bool = False
    country_code: Optional[str] = Field(foreign_key="countries.code")


class Groups(GroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: int


# --- Patient --- #


class PatientBase(SQLModel):
    comments: Optional[str]
    created_user_id: int = Field(foreign_key="users.id")
    created_date: datetime = Field(default=datetime.now())
    modified_user_id: int = Field(foreign_key="users.id")
    modified_date: datetime = Field(default=datetime.now())
    test: bool = Field(default=False)
    control: bool = Field(default=False)

    created_user: Users = Relationship(back_populates="users")
    modified_user: Users = Relationship(back_populates="users")


class Patients(PatientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int


# --- Patient Number --- #


class PatientNumberBase(SQLModel):

    patient_id: int = Field(foreign_key="patients.id", index=True)
    source_group_id: int = Field(foreign_key="groups.id", index=True)
    source_type: str
    number_group_id: int = Field(foreign_key="groups.id", index=True)
    number: str
    created_user_id: int = Field(foreign_key="users.id")
    created_date: datetime = Field(default=datetime.now())
    modified_user_id: int = Field(foreign_key="users.id")
    modified_date: datetime = Field(default=datetime.now())

    created_user: Users = Relationship(back_populates="users")
    modified_user: Users = Relationship(back_populates="users")
    number_group: Groups = Relationship(back_populates="groups")
    patient: Patients = Relationship(back_populates="patients")
    source_group = Relationship(back_populates="Groups")


class PatientNumber(PatientNumberBase):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)


class PatientNumberCreate(PatientBase):
    pass


class PatientNumberRead(PatientBase):
    id: int


# --- User --- #


class UserBase(SQLModel):
    username: str = Field(index=True)
    password: str
    email: str
    first_name: str
    last_name: str
    telephone_number: Optional[str]
    is_admin: bool = Field(default=False)
    is_bot: bool = Field(default=False)
    is_enabled: bool = Field(default=True)
    reset_password_token: str
    reset_password_date: datetime
    force_password_change: bool = Field(default=False)
    created_user_id: int = Field(foreign_key="users.id")
    created_date: datetime = Field(default=datetime.now())
    modified_user_id: int = Field(foreign_key="users.id")
    modified_date: datetime = Field(default=datetime.now())

    # Wonder if required
    created_patients: Patients = Relationship(back_populates="patients")
    created_patient_numbers: PatientNumber = Relationship(
        back_populates="patient_numbers"
    )


class Users(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


# --- AlportClinicalPicture --- #
class AlportClinicalPictureBase(SQLModel):
    pass


class AlportClinicalPicture(AlportClinicalPictureBase, table=True):
    pass


class AlportClinicalPictureCreate(AlportClinicalPictureBase):
    pass


class AlportClinicalPictureRead(AlportClinicalPictureBase):
    pass


Biomarker
BiomarkerBarcode
BiomarkerResult
BiomarkerSample
Code
Consent
Consultant
Country
CountryEthnicity
CountryNationality
CurrentMedication
Diagnose
DiagnosisCode
Dialysi
Drug
DrugGroup
Entry
Ethnicity
FamilyHistory
FamilyHistoryRelative
FetalAnomalyScan
FetalUltrasound
Form
FuanClinicalPicture
Genetic
Group
GroupConsultant
GroupDiagnose
GroupForm
GroupObservation
GroupPage
GroupPatient
GroupQuestionnaire
GroupUser
Hnf1bClinicalPicture
Hospitalisation
IndiaEthnicity
InsClinicalPicture
InsRelapse
LiverDisease
LiverImaging
LiverTransplant
Log
Medication
MpgnClinicalPicture
Nationality
Nephrectomy
NurtureDatum
NurtureSample
NurtureSamplesBlood
NurtureSamplesOption
NurtureSamplesUrine
Nutrition
Observation
Pathology
Patient
PatientAddress
PatientAliase
PatientConsent
PatientConsultant
PatientDemographic
PatientDiagnose
PatientLock
PatientNumber
Plasmapheresi
Post
Pregnancy
RenalImaging
RenalProgression
Result
RituximabBaselineAsse
RituximabCriterion
SaltWastingClinicalFe
Specialty
Transplant
TransplantBiopsy
TransplantRejection
User
UserSession
