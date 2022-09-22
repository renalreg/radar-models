import enum
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

from sqlmodel import Date, DateTime, Field, Relationship, SQLModel, Enum
from sqlalchemy import Column


# --- AlportClinicalPicture --- #


class AlportClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id", index=True)
    date_of_picture: DateTime
    deafness: int
    deafness_date: Optional[Date]
    hearing_aid_date: Optional[Date]


class AlportClinicalPicture(AlportClinicalPictureBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class AlportClinicalPictureCreate(AlportClinicalPictureBase):
    pass


class AlportClinicalPictureRead(AlportClinicalPictureBase):
    id: UUID


# --- Biomarker --- #


class BiomarkerBase(SQLModel):
    name: str
    type: str


class Biomarker(BiomarkerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BiomarkerCreate(BiomarkerBase):
    pass


class BiomarkerRead(BiomarkerBase):
    id: int


# --- BiomarkerBarcode --- #


class BiomarkerBarcodeBase(SQLModel):
    # TODO: choose either pat_id or patient_id and make consistent across DB
    pat_id: int = Field(foreign_key="patients.id")
    barcode: str
    sample_date: DateTime


class BiomarkerBarcode(BiomarkerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BiomarkerBarcodeCreate(BiomarkerBase):
    pass


class BiomarkerBarcodeRead(BiomarkerBase):
    id: int


# --- BiomarkerResult --- #


class BiomarkerResultBase(SQLModel):
    bio_id: int = Field(foreign_key="biomarkers.id")
    sample_id: int = Field(foreign_key="biomarker_samples.id")
    value: float
    unit_measure: str
    proc_date: DateTime
    hospital: str


class BiomarkerResult(BiomarkerResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BiomarkerResultCreate(BiomarkerResultBase):
    pass


class BiomarkerResultRead(BiomarkerResultBase):
    id: int


# --- BiomarkerSample --- #


class BiomarkerSampleBase(SQLModel):
    barcode_id: int = Field(foreign_key="biomarker_barcodes.id")
    label: str


class BiomarkerSample(BiomarkerSampleBase):
    id: Optional[int] = Field(default=None, primary_key=True)


class BiomarkerSampleCreate(BiomarkerSampleBase):
    pass


class BiomarkerSampleRead(BiomarkerSampleBase):
    id: int


# --- Code --- #
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


# --- Consent --- #
# TODO: SHould be a table


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
    id: Optional[int] = Field(default=None, primary_key=True)


class ConsentsCreate(ConsentBase):
    pass


class ConsentRead(ConsentBase):
    id: int


# --- Consultant --- #
# TODO: Composite index
# TODO: Question the need for consultants data


class ConsultantBase(SQLModel):
    first_name: str
    last_name: str
    email: Optional[str]
    telephone_number: Optional[str]
    # TODO:
    gmc_number: Optional[int]
    specialty_id: int = Field(foreign_key="groups.id")

    specialty: Specialty = Relationship(back_populates="specialty")


class Consultant(ConsultantBase, table=True):
    pass


class ConsultantCreate(ConsultantBase):
    pass


class ConsultantRead(ConsultantBase):
    pass


# --- Country --- #
# TODO: This table seems to only be used by groups and almost all of them
# are GB. Is this used by anything else? Can we remove this?

# TODO: Check handling of primary key


class CountryBase(SQLModel):
    label: str


class Countries(CountryBase, table=True):
    code: str = Field(primary_key=True)


class CountryCreate(CountryBase):
    code: str


class CountryRead(CountryBase):
    code: str


# --- CountryEthnicity --- #


class CountryEthnicityBase(SQLModel):
    ethnicity_id: int = Field(foreign_key="ethnicities.id")
    country_code: str = Field(foreign_key="countries.code")


class CountryEthnicity(CountryEthnicityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CountryEthnicityCreate(CountryEthnicityBase):
    pass


class CountryEthnicityRead(CountryEthnicityBase):
    id: int


# --- CountryNationality --- #


class CountryNationalityBase(SQLModel):
    nationality_id: int = Field(foreign_key="nationalities.id")
    country_code: int = Field(foreign_key="countries.code")


class CountryNationality(CountryNationalityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CountryNationalityCreate(CountryNationalityBase):
    pass


class CountryNationalityRead(CountryNationalityBase):
    id: int


# --- CurrentMedication --- #


class CurrentMedicationBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date_recorded: Date
    drug_id: int = Field(foreign_key="drugs.id")
    dose_quantity: Optional[float]
    dose_unit: Optional[str]
    frequency: Optional[str]
    route: Optional[str]
    drug_text: Optional[str]
    dose_text: Optional[str]


class CurrentMedication(CurrentMedicationBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class CurrentMedicationCreate(CurrentMedicationBase):
    pass


class CurrentMedicationRead(CurrentMedicationBase):
    id: UUID


# --- Diagnoses --- #


class DiagnosesBase(SQLModel):
    name: str
    retired: bool = Field(default=False)


class Diagnoses(DiagnosesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DiagnosesCreate(DiagnosesBase):
    pass


class DiagnosesRead(DiagnosesBase):
    id: int


# --- DiagnosisCode --- #
# TODO: composite index


class DiagnosisCodeBase(SQLModel):
    diagnosis_id: int = Field(foreign_key="diagnoses.id")
    code_id: int = Field(foreign_key="codes.id")


class DiagnosisCode(DiagnosisCodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DiagnosisCodeCreate(DiagnosisCodeBase):
    pass


class DiagnosisCodeRead(DiagnosisCodeBase):
    id: int


# --- Dialysis --- #


class DialysisBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    from_date: Date
    to_date: Optional[Date]
    modality: int


class Dialysis(DialysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DialysisCreate(DialysisBase):
    pass


class DialysisRead(DialysisBase):
    id: int


# --- Drug --- #


class DrugBase(SQLModel):
    name: str
    drug_group_id: Optional[int] = Field(foreign_key="drug_groups.id")


class Drug(DrugBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DrugCreate(DrugBase):
    pass


class DrugRead(DrugBase):
    id: int


# --- DrugGroup --- #


class DrugGroupBase(SQLModel):
    name: Optional[str] = Field(unique=True)
    # TODO: Check that everything in here makes sense
    parent_drug_group_id: Optional[int] = Field(foreign_key="drug_groups.id")


class DrugGroup(DrugGroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DrugGroupCreate(DrugGroupBase):
    pass


class DrugGroupRead(DrugGroupBase):
    id: int


# --- Entry --- #
# TODO: This table needs to be burnt in the fires of hell


class EntryBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    form_id: int = Field(foreign_key="forms.id")
    # TODO: No idea if dict will convert json
    data: dict


class Entry(EntryBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class EntryCreate(EntryBase):
    pass


class EntryRead(EntryBase):
    id: UUID


# --- Ethnicity --- #


class EthnicityBase(SQLModel):
    code: str
    label: str


class Ethnicity(EthnicityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EthnicityCreate(EthnicityBase):
    pass


class EthnicityRead(EthnicityBase):
    id: int


# --- FamilyHistory --- #


class FamilyHistoryBase(SQLModel):
    pass


class FamilyHistory(FamilyHistoryBase, table=True):
    pass


class FamilyHistoryCreate(FamilyHistoryBase):
    pass


class FamilyHistoryRead(FamilyHistoryBase):
    pass


# --- FamilyHistoryRelative --- #


class FamilyHistoryRelativeBase(SQLModel):
    pass


class FamilyHistoryRelative(FamilyHistoryRelativeBase, table=True):
    pass


class FamilyHistoryRelativeCreate(FamilyHistoryRelativeBase):
    pass


class FamilyHistoryRelativeRead(FamilyHistoryRelativeBase):
    pass


# --- FetalAnomalyScan --- #


class FetalAnomalyScanBase(SQLModel):
    pass


class FetalAnomalyScan(FetalAnomalyScanBase, table=True):
    pass


class FetalAnomalyScanCreate(FetalAnomalyScanBase):
    pass


class FetalAnomalyScanRead(FetalAnomalyScanBase):
    pass


# --- FetalUltrasound --- #


class FetalUltrasoundBase(SQLModel):
    pass


class FetalUltrasound(FetalUltrasoundBase, table=True):
    pass


class FetalUltrasoundCreate(FetalUltrasoundBase):
    pass


class FetalUltrasoundRead(FetalUltrasoundBase):
    pass


# --- Form --- #


class FormBase(SQLModel):
    pass


class Form(FormBase, table=True):
    pass


class FormCreate(FormBase):
    pass


class FormRead(FormBase):
    pass


# --- FuanClinicalPicture --- #


class FuanClinicalPictureBase(SQLModel):
    pass


class FuanClinicalPicture(FuanClinicalPictureBase, table=True):
    pass


class FuanClinicalPictureCreate(FuanClinicalPictureBase):
    pass


class FuanClinicalPictureRead(FuanClinicalPictureBase):
    pass


# --- Genetics --- #


class GeneticsBase(SQLModel):
    pass


class Genetics(GeneticsBase, table=True):
    pass


class GeneticsCreate(GeneticsBase):
    pass


class GeneticsRead(GeneticsBase):
    pass


# --- Group --- #
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


# --- GroupConsultant --- #


class GroupConsultantBase(SQLModel):
    pass


class GroupConsultant(GroupConsultantBase, table=True):
    pass


class GroupConsultantCreate(GroupConsultantBase):
    pass


class GroupConsultantRead(GroupConsultantBase):
    pass


# --- GroupDiagnose --- #


class GroupDiagnoseBase(SQLModel):
    pass


class GroupDiagnose(GroupDiagnoseBase, table=True):
    pass


class GroupDiagnoseCreate(GroupDiagnoseBase):
    pass


class GroupDiagnoseRead(GroupDiagnoseBase):
    pass


# --- GroupForm --- #


class GroupFormBase(SQLModel):
    pass


class GroupForm(GroupFormBase, table=True):
    pass


class GroupFormCreate(GroupFormBase):
    pass


class GroupFormRead(GroupFormBase):
    pass


# --- GroupObservation --- #


class GroupObservationBase(SQLModel):
    pass


class GroupObservation(GroupObservationBase, table=True):
    pass


class GroupObservationCreate(GroupObservationBase):
    pass


class GroupObservationRead(GroupObservationBase):
    pass


# --- GroupPage --- #


class GroupPageBase(SQLModel):
    pass


class GroupPage(GroupPageBase, table=True):
    pass


class GroupPageCreate(GroupPageBase):
    pass


class GroupPageRead(GroupPageBase):
    pass


# --- GroupPatient --- #


class GroupPatientBase(SQLModel):
    pass


class GroupPatient(GroupPatientBase, table=True):
    pass


class GroupPatientCreate(GroupPatientBase):
    pass


class GroupPatientRead(GroupPatientBase):
    pass


# --- GroupQuestionnaire --- #


class GroupQuestionnaireBase(SQLModel):
    pass


class GroupQuestionnaire(GroupQuestionnaireBase, table=True):
    pass


class GroupQuestionnaireCreate(GroupQuestionnaireBase):
    pass


class GroupQuestionnaireRead(GroupQuestionnaireBase):
    pass


# --- GroupUser --- #


class GroupUserBase(SQLModel):
    pass


class GroupUser(GroupUserBase, table=True):
    pass


class GroupUserCreate(GroupUserBase):
    pass


class GroupUserRead(GroupUserBase):
    pass


# --- Hnf1bClinicalPicture --- #


class Hnf1bClinicalPictureBase(SQLModel):
    pass


class Hnf1bClinicalPicture(Hnf1bClinicalPictureBase, table=True):
    pass


class Hnf1bClinicalPictureCreate(Hnf1bClinicalPictureBase):
    pass


class Hnf1bClinicalPictureRead(Hnf1bClinicalPictureBase):
    pass


# --- Hospitalisation --- #


class HospitalisationBase(SQLModel):
    pass


class Hospitalisation(HospitalisationBase, table=True):
    pass


class HospitalisationCreate(HospitalisationBase):
    pass


class HospitalisationRead(HospitalisationBase):
    pass


# --- IndiaEthnicity --- #


class IndiaEthnicityBase(SQLModel):
    pass


class IndiaEthnicity(IndiaEthnicityBase, table=True):
    pass


class IndiaEthnicityCreate(IndiaEthnicityBase):
    pass


class IndiaEthnicityRead(IndiaEthnicityBase):
    pass


# --- InsClinicalPicture --- #


class InsClinicalPictureBase(SQLModel):
    pass


class InsClinicalPicture(InsClinicalPictureBase, table=True):
    pass


class InsClinicalPictureCreate(InsClinicalPictureBase):
    pass


class InsClinicalPictureRead(InsClinicalPictureBase):
    pass


# --- InsRelapse --- #


class InsRelapseBase(SQLModel):
    pass


class InsRelapse(InsRelapseBase, table=True):
    pass


class InsRelapseCreate(InsRelapseBase):
    pass


class InsRelapseRead(InsRelapseBase):
    pass


# --- LiverDisease --- #


class LiverDiseaseBase(SQLModel):
    pass


class LiverDisease(LiverDiseaseBase, table=True):
    pass


class LiverDiseaseCreate(LiverDiseaseBase):
    pass


class LiverDiseaseRead(LiverDiseaseBase):
    pass


# --- LiverImaging --- #


class LiverImagingBase(SQLModel):
    pass


class LiverImaging(LiverImagingBase, table=True):
    pass


class LiverImagingCreate(LiverImagingBase):
    pass


class LiverImagingRead(LiverImagingBase):
    pass


# --- LiverTransplant --- #


class LiverTransplantBase(SQLModel):
    pass


class LiverTransplant(LiverTransplantBase, table=True):
    pass


class LiverTransplantCreate(LiverTransplantBase):
    pass


class LiverTransplantRead(LiverTransplantBase):
    pass


# --- Log --- #


class LogBase(SQLModel):
    pass


class Log(LogBase, table=True):
    pass


class LogCreate(LogBase):
    pass


class LogRead(LogBase):
    pass


# --- Medication --- #


class MedicationBase(SQLModel):
    pass


class Medication(MedicationBase, table=True):
    pass


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    pass


# --- MpgnClinicalPicture --- #


class MpgnClinicalPictureBase(SQLModel):
    pass


class MpgnClinicalPicture(MpgnClinicalPictureBase, table=True):
    pass


class MpgnClinicalPictureCreate(MpgnClinicalPictureBase):
    pass


class MpgnClinicalPictureRead(MpgnClinicalPictureBase):
    pass


# --- Nationality --- #


class NationalityBase(SQLModel):
    pass


class Nationality(NationalityBase, table=True):
    pass


class NationalityCreate(NationalityBase):
    pass


class NationalityRead(NationalityBase):
    pass


# --- Nephrectomy --- #


class NephrectomyBase(SQLModel):
    pass


class Nephrectomy(NephrectomyBase, table=True):
    pass


class NephrectomyCreate(NephrectomyBase):
    pass


class NephrectomyRead(NephrectomyBase):
    pass


# --- NurtureDatum --- #


class NurtureDatumBase(SQLModel):
    pass


class NurtureDatum(NurtureDatumBase, table=True):
    pass


class NurtureDatumCreate(NurtureDatumBase):
    pass


class NurtureDatumRead(NurtureDatumBase):
    pass


# --- NurtureSample --- #


class NurtureSampleBase(SQLModel):
    pass


class NurtureSample(NurtureSampleBase, table=True):
    pass


class NurtureSampleCreate(NurtureSampleBase):
    pass


class NurtureSampleRead(NurtureSampleBase):
    pass


# --- NurtureSamplesBlood --- #


class NurtureSamplesBloodBase(SQLModel):
    pass


class NurtureSamplesBlood(NurtureSamplesBloodBase, table=True):
    pass


class NurtureSamplesBloodCreate(NurtureSamplesBloodBase):
    pass


class NurtureSamplesBloodRead(NurtureSamplesBloodBase):
    pass


# --- NurtureSamplesOption --- #


class NurtureSamplesOptionBase(SQLModel):
    pass


class NurtureSamplesOption(NurtureSamplesOptionBase, table=True):
    pass


class NurtureSamplesOptionCreate(NurtureSamplesOptionBase):
    pass


class NurtureSamplesOptionRead(NurtureSamplesOptionBase):
    pass


# --- NurtureSamplesUrine --- #


class NurtureSamplesUrineBase(SQLModel):
    pass


class NurtureSamplesUrine(NurtureSamplesUrineBase, table=True):
    pass


class NurtureSamplesUrineCreate(NurtureSamplesUrineBase):
    pass


class NurtureSamplesUrineRead(NurtureSamplesUrineBase):
    pass


# --- Nutrition --- #


class NutritionBase(SQLModel):
    pass


class Nutrition(NutritionBase, table=True):
    pass


class NutritionCreate(NutritionBase):
    pass


class NutritionRead(NutritionBase):
    pass


# --- Observation --- #


class ObservationBase(SQLModel):
    pass


class Observation(ObservationBase, table=True):
    pass


class ObservationCreate(ObservationBase):
    pass


class ObservationRead(ObservationBase):
    pass


# --- Pathology --- #


class PathologyBase(SQLModel):
    pass


class Pathology(PathologyBase, table=True):
    pass


class PathologyCreate(PathologyBase):
    pass


class PathologyRead(PathologyBase):
    pass


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


# --- PatientAddress --- #


class PatientAddressBase(SQLModel):
    pass


class PatientAddress(PatientAddressBase, table=True):
    pass


class PatientAddressCreate(PatientAddressBase):
    pass


class PatientAddressRead(PatientAddressBase):
    pass


# --- PatientAliase --- #


class PatientAliaseBase(SQLModel):
    pass


class PatientAliase(PatientAliaseBase, table=True):
    pass


class PatientAliaseCreate(PatientAliaseBase):
    pass


class PatientAliaseRead(PatientAliaseBase):
    pass


# --- PatientConsent --- #


class PatientConsentBase(SQLModel):
    pass


class PatientConsent(PatientConsentBase, table=True):
    pass


class PatientConsentCreate(PatientConsentBase):
    pass


class PatientConsentRead(PatientConsentBase):
    pass


# --- PatientConsultant --- #


class PatientConsultantBase(SQLModel):
    pass


class PatientConsultant(PatientConsultantBase, table=True):
    pass


class PatientConsultantCreate(PatientConsultantBase):
    pass


class PatientConsultantRead(PatientConsultantBase):
    pass


# --- PatientDemographic --- #


class PatientDemographicBase(SQLModel):
    pass


class PatientDemographic(PatientDemographicBase, table=True):
    pass


class PatientDemographicCreate(PatientDemographicBase):
    pass


class PatientDemographicRead(PatientDemographicBase):
    pass


# --- PatientDiagnose --- #


class PatientDiagnoseBase(SQLModel):
    pass


class PatientDiagnose(PatientDiagnoseBase, table=True):
    pass


class PatientDiagnoseCreate(PatientDiagnoseBase):
    pass


class PatientDiagnoseRead(PatientDiagnoseBase):
    pass


# --- PatientLock --- #


class PatientLockBase(SQLModel):
    pass


class PatientLock(PatientLockBase, table=True):
    pass


class PatientLockCreate(PatientLockBase):
    pass


class PatientLockRead(PatientLockBase):
    pass


# --- PatientNumber --- #


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
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientNumberCreate(PatientBase):
    pass


class PatientNumberRead(PatientBase):
    id: UUID


# --- Plasmapheresi --- #


class PlasmapheresiBase(SQLModel):
    pass


class Plasmapheresi(PlasmapheresiBase, table=True):
    pass


class PlasmapheresiCreate(PlasmapheresiBase):
    pass


class PlasmapheresiRead(PlasmapheresiBase):
    pass


# --- Post --- #


class PostBase(SQLModel):
    pass


class Post(PostBase, table=True):
    pass


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    pass


# --- Pregnancy --- #


class PregnancyBase(SQLModel):
    pass


class Pregnancy(PregnancyBase, table=True):
    pass


class PregnancyCreate(PregnancyBase):
    pass


class PregnancyRead(PregnancyBase):
    pass


# --- RenalImaging --- #


class RenalImagingBase(SQLModel):
    pass


class RenalImaging(RenalImagingBase, table=True):
    pass


class RenalImagingCreate(RenalImagingBase):
    pass


class RenalImagingRead(RenalImagingBase):
    pass


# --- RenalProgression --- #


class RenalProgressionBase(SQLModel):
    pass


class RenalProgression(RenalProgressionBase, table=True):
    pass


class RenalProgressionCreate(RenalProgressionBase):
    pass


class RenalProgressionRead(RenalProgressionBase):
    pass


# --- Result --- #


class ResultBase(SQLModel):
    pass


class Result(ResultBase):
    pass


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    pass


# --- RituximabBaselineAsse --- #


class RituximabBaselineAsseBase(SQLModel):
    pass


class RituximabBaselineAsse(RituximabBaselineAsseBase, table=True):
    pass


class RituximabBaselineAsseCreate(RituximabBaselineAsseBase):
    pass


class RituximabBaselineAsseRead(RituximabBaselineAsseBase):
    pass


# --- RituximabCriterion --- #


class RituximabCriterionBase(SQLModel):
    pass


class RituximabCriterion(RituximabCriterionBase, table=True):
    pass


class RituximabCriterionCreate(RituximabCriterionBase):
    pass


class RituximabCriterionRead(RituximabCriterionBase):
    pass


# --- SaltWastingClinicalFe --- #


class SaltWastingClinicalFeBase(SQLModel):
    pass


class SaltWastingClinicalFe(SaltWastingClinicalFeBase, table=True):
    pass


class SaltWastingClinicalFeCreate(SaltWastingClinicalFeBase):
    pass


class SaltWastingClinicalFeRead(SaltWastingClinicalFeBase):
    pass


# --- Specialty --- #


class SpecialtyBase(SQLModel):
    pass


class Specialty(SpecialtyBase, table=True):
    pass


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyRead(SpecialtyBase):
    pass


# --- Transplant --- #


class TransplantBase(SQLModel):
    pass


class Transplant(TransplantBase, table=True):
    pass


class TransplantCreate(TransplantBase):
    pass


class TransplantRead(TransplantBase):
    pass


# --- TransplantBiopsy --- #


class TransplantBiopsyBase(SQLModel):
    pass


class TransplantBiopsy(TransplantBiopsyBase, table=True):
    pass


class TransplantBiopsyCreate(TransplantBiopsyBase):
    pass


class TransplantBiopsyRead(TransplantBiopsyBase):
    pass


# --- TransplantRejection --- #


class TransplantRejectionBase(SQLModel):
    pass


class TransplantRejection(TransplantRejectionBase, table=True):
    pass


class TransplantRejectionCreate(TransplantRejectionBase):
    pass


class TransplantRejectionRead(TransplantRejectionBase):
    pass


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


# --- UserSession --- #


class UserSessionBase(SQLModel):
    pass


class UserSession(UserSessionBase, table=True):
    pass


class UserSessionCreate(UserSessionBase):
    pass


class UserSessionRead(UserSessionBase):
    pass
