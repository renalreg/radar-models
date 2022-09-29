import enum
from datetime import datetime, date
from msilib import sequence
from multiprocessing.dummy import Array
from token import OP
from typing import Optional
from uuid import UUID, uuid4
import uuid

from sqlalchemy import ARRAY, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

# --- AlportClinicalPicture --- #


class AlportClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id", index=True)
    date_of_picture: datetime
    deafness: int
    deafness_date: Optional[date]
    hearing_aid_date: Optional[date]


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
    sample_date: datetime


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
    proc_date: datetime
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
    date_recorded: date
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
    from_date: date
    to_date: Optional[date]
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
    patient_id: int = Field(foreign_key="patients.id")
    group_id: int = Field(foreign_key="groups.id")
    parental_consanguinity: bool
    family_history: bool
    other_family_history: str


class FamilyHistory(FamilyHistoryBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class FamilyHistoryCreate(FamilyHistoryBase):
    pass


class FamilyHistoryRead(FamilyHistoryBase):
    id: UUID


# --- FamilyHistoryRelative --- #


class FamilyHistoryRelativeBase(SQLModel):
    family_history_id: UUID = Field(foreign_key="family_histories.id")
    relationship: int
    # TODO: This seems poorly named, although it is trying to point at a patient
    patient_id: int = Field(foreign_key="patients.id")


class FamilyHistoryRelative(FamilyHistoryRelativeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FamilyHistoryRelativeCreate(FamilyHistoryRelativeBase):
    pass


class FamilyHistoryRelativeRead(FamilyHistoryRelativeBase):
    id: int


# --- FetalAnomalyScan --- #


class FetalAnomalyScanBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
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
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class FetalAnomalyScanCreate(FetalAnomalyScanBase):
    pass


class FetalAnomalyScanRead(FetalAnomalyScanBase):
    id: UUID


# --- FetalUltrasound --- #


class FetalUltrasoundBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date_of_scan: date
    fetal_identifier: Optional[str]
    gestational_age: int
    head_centile: Optional[int]
    abdomen_centile: Optional[int]
    uterine_artery_notched: Optional[bool]
    liquor_volume: Optional[str]
    comments: Optional[str]


class FetalUltrasound(FetalUltrasoundBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class FetalUltrasoundCreate(FetalUltrasoundBase):
    pass


class FetalUltrasoundRead(FetalUltrasoundBase):
    id: UUID


# --- Form --- #


class FormBase(SQLModel):
    name: str
    slug: str = Field(unique=True)
    # TODO: No idea if dict will convert json
    data: dict


class Form(FormBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FormCreate(FormBase):
    pass


class FormRead(FormBase):
    id: int


# --- FuanClinicalPicture --- #


class FuanClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    picture_date: date
    gout: bool
    gout_date: Optional[date]
    family_gout: Optional[bool]
    # TODO: This is the devils work. Should be using family_history_relatives table
    family_gout_relatives: dict = Field(sa_column=Column(ARRAY(int)))
    thp: Optional[str]
    uti: Optional[bool]
    comments: Optional[str]


class FuanClinicalPicture(FuanClinicalPictureBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class FuanClinicalPictureCreate(FuanClinicalPictureBase):
    pass


class FuanClinicalPictureRead(FuanClinicalPictureBase):
    id: UUID


# --- Genetics --- #


class GeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    group_id: int = Field(foreign_key="groups.id")
    date_sent: datetime
    laboratory: str
    reference_number: Optional[str]
    karyotype: Optional[int]
    results: Optional[str]
    summary: Optional[str]


class Genetics(GeneticsBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class GeneticsCreate(GeneticsBase):
    pass


class GeneticsRead(GeneticsBase):
    id: UUID


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
    group_id: int = Field(foreign_key="groups.id")
    consultant_id: int = Field(foreign_key="consultants.id")


class GroupConsultant(GroupConsultantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupConsultantCreate(GroupConsultantBase):
    pass


class GroupConsultantRead(GroupConsultantBase):
    id: int


# --- GroupDiagnose --- #


class GroupDiagnoseTypeEnum(str, enum.Enum):
    primary = "PRIMARY"
    secondary = "SECONDARY"


class GroupDiagnoseBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    diagnosis_id: int = Field(foreign_key="diagnosis.id")
    type: GroupDiagnoseTypeEnum = Field(sa_column=Column(Enum(GroupDiagnoseTypeEnum)))
    weight: int


class GroupDiagnose(GroupDiagnoseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupDiagnoseCreate(GroupDiagnoseBase):
    pass


class GroupDiagnoseRead(GroupDiagnoseBase):
    id: int


# --- GroupForm --- #


class GroupFormBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    form_id: int = Field(foreign_key="forms.id")
    weight: int


class GroupForm(GroupFormBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupFormCreate(GroupFormBase):
    pass


class GroupFormRead(GroupFormBase):
    id: int


# --- GroupObservation --- #


class GroupObservationBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    observation_id: int = Field(foreign_key="observations.id")
    weight: int


class GroupObservation(GroupObservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupObservationCreate(GroupObservationBase):
    pass


class GroupObservationRead(GroupObservationBase):
    id: int


# --- GroupPage --- #


class GroupPageBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    page: str
    weight: int


class GroupPage(GroupPageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupPageCreate(GroupPageBase):
    pass


class GroupPageRead(GroupPageBase):
    id: int


# --- GroupPatient --- #


class GroupPatientBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    patient_id: int = Field(foreign_key="patients.id")
    from_date: datetime
    to_date: Optional[datetime]
    discharged_date: date


class GroupPatient(GroupPatientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupPatientCreate(GroupPatientBase):
    pass


class GroupPatientRead(GroupPatientBase):
    id: int


# --- GroupQuestionnaire --- #


class GroupQuestionnaireBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    form_id: int = Field(foreign_key="forms.id")
    weight: Optional[int]


class GroupQuestionnaire(GroupQuestionnaireBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupQuestionnaireCreate(GroupQuestionnaireBase):
    pass


class GroupQuestionnaireRead(GroupQuestionnaireBase):
    id: int


# --- GroupUser --- #

# TODO: Another enum that should be in a table
class UserRoleEnum(str, enum.Enum):
    admin = "ADMIN"
    clinicain = "CLINICIAN"
    it = "IT"
    researcher = "RESEARCHER"
    senior_clinician = "SENIOR_CLINICIAN"
    senior_researcher = "SENIOR_RESEARCHER"


class GroupUserBase(SQLModel):
    group_id: int = Field(foreign_key="groups.id")
    user_id: int = Field(foreign_key="users.id")
    role: UserRoleEnum = Field(sa_column=Column(Enum(UserRoleEnum)))


class GroupUser(GroupUserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GroupUserCreate(GroupUserBase):
    pass


class GroupUserRead(GroupUserBase):
    id: int


# --- Hnf1bClinicalPicture --- #


class Hnf1bClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    date_of_picture: date
    single_kidney: bool
    hyperuricemia_gout: bool
    genital_malformation: bool
    genital_malformation_details: str
    familial_cystic_disease: bool
    hypertension: bool


class Hnf1bClinicalPicture(Hnf1bClinicalPictureBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class Hnf1bClinicalPictureCreate(Hnf1bClinicalPictureBase):
    pass


class Hnf1bClinicalPictureRead(Hnf1bClinicalPictureBase):
    id: UUID


# --- Hospitalisation --- #


class HospitalisationBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date_of_admission: datetime
    date_of_discharge: datetime
    reason_of_admission: str


class Hospitalisation(HospitalisationBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class HospitalisationCreate(HospitalisationBase):
    pass


class HospitalisationRead(HospitalisationBase):
    id: UUID


# --- IndiaEthnicity --- #


class IndiaEthnicityBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    father_ancestral_state: str
    father_language: str
    mother_ancestral_state: str
    mother_language: str


class IndiaEthnicity(IndiaEthnicityBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class IndiaEthnicityCreate(IndiaEthnicityBase):
    pass


class IndiaEthnicityRead(IndiaEthnicityBase):
    id: UUID


# --- InsClinicalPicture --- #


class InsClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    date_of_picture: date
    oedema: bool
    hypovalaemia: bool
    fever: bool
    thrombosis: bool
    peritonitis: bool
    pulmonary_odemea: bool
    hypertension: bool
    rash: bool
    rash_details: str
    infection: bool
    infection_details: str
    ophthalmoscopy: bool
    ophthalmoscopy_details: str
    comments: str


class InsClinicalPicture(InsClinicalPictureBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class InsClinicalPictureCreate(InsClinicalPictureBase):
    pass


class InsClinicalPictureRead(InsClinicalPictureBase):
    id: UUID


# --- InsRelapse --- #


class InsRelapseBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    date_of_relapse: date
    kidney_type: str
    viral_trigger: str
    immunisation_trigger: str
    other_trigger: str
    high_dose_oral_prednisolone: bool
    iv_methyl_prednisolone: bool
    date_of_remission: date
    remission_type: str
    peak_acr: float
    peak_pcr: float
    remission_acr: float
    remission_pcr: float
    peak_protein_dipstick: str
    remission_protein_dipstick: str
    relapse_sample_taken: bool


class InsRelapse(InsRelapseBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class InsRelapseCreate(InsRelapseBase):
    pass


class InsRelapseRead(InsRelapseBase):
    id: UUID


# --- LiverDisease --- #


class LiverDiseaseBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    portal_hypertension: bool
    portal_hypertension_date: date
    ascites: bool
    ascites_date: date
    oesophageal: bool
    oesophageal_date: date
    oesophageal_bleeding: bool
    oesophageal_bleeding_date: date
    gastric: bool
    gastric_date: date
    gastric_bleeding: bool
    gastric_bleeding_date: date
    anorectal: bool
    anorectal_date: date
    anorectal_bleeding: bool
    anorectal_bleeding_date: date
    cholangitis_acute: bool
    cholangitis_acute_date: date
    cholangitis_recurrent: bool
    cholangitis_recurrent_date: date
    spleen_palpable: bool
    spleen_palpable_date: date


class LiverDisease(LiverDiseaseBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class LiverDiseaseCreate(LiverDiseaseBase):
    pass


class LiverDiseaseRead(LiverDiseaseBase):
    id: UUID


# --- LiverImaging --- #


class LiverImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: datetime
    imaging_type: str
    size: float
    hepatic_fibrosis: bool
    hepatic_cysts: bool
    bile_duct_cysts: bool
    dilated_bile_ducts: bool
    cholangitis: bool


class LiverImaging(LiverImagingBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class LiverImagingCreate(LiverImagingBase):
    pass


class LiverImagingRead(LiverImagingBase):
    id: UUID


# --- LiverTransplant --- #


class LiverTransplantBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    transplant_group_id: int = Field(foreign_key="groups.id")
    registration_date: date
    transplant_date: date
    # TODO: More arrays!!!
    indications: dict = Field(sa_column=Column(ARRAY(str)))
    other_indications: str
    first_graft_source: str
    loss_reason: str
    other_loss_reason: str


class LiverTransplant(LiverTransplantBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class LiverTransplantCreate(LiverTransplantBase):
    pass


class LiverTransplantRead(LiverTransplantBase):
    id: UUID


# --- Log --- #

# TODO: Remove this table and come up with a better solution
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
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    from_date: date
    to_date: date
    drug_id: int = Field(foreign_key="drugs.id")
    dose_quantity: float
    dose_unit: str
    frequency: str
    route: str
    drug_text: str
    dose_text: str


class Medication(MedicationBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    id: UUID


# --- MpgnClinicalPicture --- #


class MpgnClinicalPictureBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
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
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class MpgnClinicalPictureCreate(MpgnClinicalPictureBase):
    pass


class MpgnClinicalPictureRead(MpgnClinicalPictureBase):
    id: UUID


# --- Nationality --- #


class NationalityBase(SQLModel):
    label: str


class Nationality(NationalityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class NationalityCreate(NationalityBase):
    pass


class NationalityRead(NationalityBase):
    id: int


# --- Nephrectomy --- #


class NephrectomyBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: date
    kidney_side: str
    kidney_type: str
    entry_type: str


class Nephrectomy(NephrectomyBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class NephrectomyCreate(NephrectomyBase):
    pass


class NephrectomyRead(NephrectomyBase):
    id: UUID


# --- NurtureDatum --- #


class NurtureDatumBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    signed_off_state: int
    follow_up_refused_date: date
    blood_tests: bool
    blood_refused_date: date
    interviews: bool
    interviews_refused_date: date


class NurtureDatum(NurtureDatumBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class NurtureDatumCreate(NurtureDatumBase):
    pass


class NurtureDatumRead(NurtureDatumBase):
    id: int


# --- NurtureSample --- #


class NurtureSampleBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    taken_on: date
    barcode: int
    epa: int
    epb: int
    lpa: int
    lpb: int
    uc: int
    ub: int
    ud: int
    fub: int
    sc: int
    sa: int
    sb: int
    rna: int
    wb: int


class NurtureSample(NurtureSampleBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class NurtureSampleCreate(NurtureSampleBase):
    pass


class NurtureSampleRead(NurtureSampleBase):
    id: UUID


# --- NurtureSamplesBlood --- #


class NurtureSamplesBloodBase(SQLModel):
    sample_id: str = Field(primary_key=True)
    sample_date: datetime
    radar_id: str
    bnp: str
    creat: str
    crp: str
    cyst: str
    gdf15: str
    trop: str
    ins_state: int
    comments_label: str
    comments_sample: str


class NurtureSamplesBlood(NurtureSamplesBloodBase, table=True):
    pass


class NurtureSamplesBloodCreate(NurtureSamplesBloodBase):
    pass


class NurtureSamplesBloodRead(NurtureSamplesBloodBase):
    pass


# --- NurtureSamplesOption --- #

# TODO: Figure out if and where this table is being used


class NurtureSampleOptionEnum(str, enum.Enum):
    adult_ns = "ADULT_NS"
    adult_ckd = "ADULT_CKD"
    children_15_2nd = "CHILDREN15_2ND"
    children_15_b = "CHILDREN15_B"
    children_less_15_2nd = "CHILDREN_LESS_15_2ND"
    children_less_15_b = "CHILDREN_LESS_15_B"
    children_30_2nd = "CHILDREN30_2ND"
    children_30_b = "CHILDREN30_B"


class NurtureSamplesOptionBase(SQLModel):
    id: NurtureSampleOptionEnum = Field(
        sa_column=Column(Enum(NurtureSampleOptionEnum)), primary_key=True
    )
    label: str
    epa: int
    epb: int
    lpa: int
    lpb: int
    uc: int
    ub: int
    ud: int
    fub: int
    sc: int
    sa: int
    sb: int
    rna: int
    wb: int


class NurtureSamplesOption(NurtureSamplesOptionBase, table=True):
    pass


class NurtureSamplesOptionCreate(NurtureSamplesOptionBase):
    pass


class NurtureSamplesOptionRead(NurtureSamplesOptionBase):
    pass


# --- NurtureSamplesUrine --- #


class NurtureSamplesUrineBase(SQLModel):
    sample_id: str = Field(primary_key=True)
    sample_date: datetime
    radar_id: str
    albumin: str
    creatinin: str
    ins_state: int
    comments_label: str
    comments_sample: str


class NurtureSamplesUrine(NurtureSamplesUrineBase, table=True):
    pass


class NurtureSamplesUrineCreate(NurtureSamplesUrineBase):
    pass


class NurtureSamplesUrineRead(NurtureSamplesUrineBase):
    pass


# --- Nutrition --- #


class NutritionBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    feeding_type: str
    from_date: date
    to_date: date


class Nutrition(NutritionBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class NutritionCreate(NutritionBase):
    pass


class NutritionRead(NutritionBase):
    id: UUID


# --- Observation --- #

# TODO: This table has a load of check constraints that need to be extracted into the API code


class ObservationValueType(str, enum.Enum):
    enum_type = "ENUM"
    int_type = "INTEGER"
    real_type = "REAL"
    str_type = "STRING"


class ObservationSampleType(str, enum.Enum):
    blood = "BLOOD"
    observation = "OBSERVATION"
    urine = "URINE"
    urine_dipstick = "URINE_DIPSTICK"


class ObservationBase(SQLModel):
    name: str
    short_name: str
    value_type: ObservationValueType = Field(
        sa_column=Column(Enum(ObservationValueType))
    )
    sample_type: ObservationSampleType = Field(
        sa_column=Column(Enum(ObservationSampleType))
    )
    pv_code: str
    min_value: int
    max_value: int
    min_length: int
    max_length: int
    units: str
    options: dict = Field(sa_column=Column(ARRAY(str)))


class Observation(ObservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ObservationCreate(ObservationBase):
    pass


class ObservationRead(ObservationBase):
    id: int


# --- Pathology --- #


class PathologyBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: date
    kidney_type: str
    kidney_side: str
    reference_number: str
    image_url: str
    histological_summary: str
    em_findings: str


class Pathology(PathologyBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PathologyCreate(PathologyBase):
    pass


class PathologyRead(PathologyBase):
    id: UUID


# --- Patient --- #


class PatientBase(SQLModel):
    comments: Optional[str]
    test: bool = Field(default=False)
    control: bool = Field(default=False)


class Patients(PatientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int


# --- PatientAddress --- #


class PatientAddressBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    from_date: date
    to_date: date
    address1: str
    address2: str
    address3: str
    address4: str
    postcode: str
    country: str


class PatientAddress(PatientAddressBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientAddressCreate(PatientAddressBase):
    pass


class PatientAddressRead(PatientAddressBase):
    id: UUID


# --- PatientAliase --- #


class PatientAliaseBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    first_name: str
    last_name: str


class PatientAliase(PatientAliaseBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientAliaseCreate(PatientAliaseBase):
    pass


class PatientAliaseRead(PatientAliaseBase):
    id: UUID


# --- PatientConsent --- #


class PatientConsentBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    consent_id: int = Field(foreign_key="consents.id")
    signed_on_date: date
    withdrawn_on_date: Optional[date]
    reconsent_letter_returned_date: date
    reconsent_letter_sent_date: date


class PatientConsent(PatientConsentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PatientConsentCreate(PatientConsentBase):
    pass


class PatientConsentRead(PatientConsentBase):
    id: int


# --- PatientConsultant --- #


class PatientConsultantBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    consultant_id: int = Field(foreign_key="consultants.id")
    from_date: date
    to_date: Optional[date]


class PatientConsultant(PatientConsultantBase, table=True):
    id: int = Field(default=None, primary_key=True)


class PatientConsultantCreate(PatientConsultantBase):
    pass


class PatientConsultantRead(PatientConsultantBase):
    id: int


# --- PatientDemographic --- #


class PatientDemographicBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    ethnicity_id: int = Field(foreign_key="ethnicities.id")
    nationality_id: Field(foreign_key="nationalities.id")
    source_type: str
    first_name: str
    last_name: str
    date_of_birth: date
    date_of_death: date
    gender: int
    home_number: str
    work_number: str
    mobile_number: str
    email_address: str
    cause_of_death: str


class PatientDemographic(PatientDemographicBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientDemographicCreate(PatientDemographicBase):
    pass


class PatientDemographicRead(PatientDemographicBase):
    id: UUID


# --- PatientDiagnose --- #


class PatientDiagnoseBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    diagnosis_id: int = Field(foreign_key="diagnoses.id")
    source_type: str
    diagnosis_text: str
    symptoms_date: date
    from_date: date
    to_date: date
    gene_test: bool
    biochemistry: bool
    clinical_picture: bool
    biopsy: bool
    biopsy_diagnosis: int
    comments: str
    prenatal: bool


class PatientDiagnose(PatientDiagnoseBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientDiagnoseCreate(PatientDiagnoseBase):
    pass


class PatientDiagnoseRead(PatientDiagnoseBase):
    id: UUID


# --- PatientLock --- #


class PatientLockBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    sequence_number: int


class PatientLock(PatientLockBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PatientLockCreate(PatientLockBase):
    pass


class PatientLockRead(PatientLockBase):
    id: int


# --- PatientNumber --- #


class PatientNumberBase(SQLModel):

    patient_id: int = Field(foreign_key="patients.id", index=True)
    source_group_id: int = Field(foreign_key="groups.id", index=True)
    source_type: str
    number_group_id: int = Field(foreign_key="groups.id", index=True)
    number: str


class PatientNumber(PatientNumberBase):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PatientNumberCreate(PatientBase):
    pass


class PatientNumberRead(PatientBase):
    id: UUID


# --- Plasmapheresi --- #


class PlasmapheresiBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    from_date: date
    to_date: date
    # TODO: rename to just exchanges
    no_of_exchanges: str
    response: str


class Plasmapheresi(PlasmapheresiBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PlasmapheresiCreate(PlasmapheresiBase):
    pass


class PlasmapheresiRead(PlasmapheresiBase):
    id: UUID


# --- Post --- #


class PostBase(SQLModel):
    title: str
    published_date: datetime
    body: str


class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int


# --- Pregnancy --- #


class PregnancyBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    pregnancy_number: int
    date_of_lmp: date
    gravidity: int
    parity1: int
    parity2: int
    outcome: str
    weight: int
    weight_centile: int
    gestational_age: int
    delivery_method: str
    neonatal_intensive_care: bool
    pre_eclampsia: str


class Pregnancy(PregnancyBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class PregnancyCreate(PregnancyBase):
    pass


class PregnancyRead(PregnancyBase):
    id: UUID


# --- RenalImaging --- #


class RenalImagingBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: datetime
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


class RenalImaging(RenalImagingBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class RenalImagingCreate(RenalImagingBase):
    pass


class RenalImagingRead(RenalImagingBase):
    id: UUID


# --- RenalProgression --- #


class RenalProgressionBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    onset_date: date
    esrf_date: date
    ckd5_date: date
    ckd4_date: date
    ckd3a_date: date
    ckd3b_date: date


class RenalProgression(RenalProgressionBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class RenalProgressionCreate(RenalProgressionBase):
    pass


class RenalProgressionRead(RenalProgressionBase):
    id: UUID


# --- Result --- #


class ResultBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: datetime
    value: str


class Result(ResultBase):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    id: UUID


# --- RituximabBaselineAssessment --- #


class RituximabBaselineAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    source_group_id: int = Field(foreign_key="groups.id")
    source_type: str
    date: date
    nephropathy: str
    # TODO: More array madness
    supportive_medication: set = Field(sa_column=Column(Array(str)))
    # TODO: More json
    previous_treatment: dict = Field(sa_column=Column(Array(str)))
    steroids: bool
    other_previous_treatment: str
    past_remission: bool
    performance_status: int
    comorbidities: bool


class RituximabBaselineAssessment(RituximabBaselineAssessmentBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class RituximabBaselineAssessmentCreate(RituximabBaselineAssessmentBase):
    pass


class RituximabBaselineAssessmentRead(RituximabBaselineAssessmentBase):
    id: UUID


# --- RituximabCriterion --- #


class RituximabCriterionBase(SQLModel):
    patient_id: int = Field(foreign_key="patients.id")
    date: date
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


class RituximabCriterion(RituximabCriterionBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)


class RituximabCriterionCreate(RituximabCriterionBase):
    pass


class RituximabCriterionRead(RituximabCriterionBase):
    id: UUID


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
