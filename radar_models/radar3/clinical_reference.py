"""Codes, diagnoses, drugs, biomarkers and observations."""

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- Biomarker --- #


class BiomarkerBase(SQLModel):
    biomarker_name: str
    biomarker_type: str | None = None


class Biomarker(BiomarkerBase, BigIntPK, table=True):
    __tablename__ = "biomarker"


class BiomarkerRead(BiomarkerBase, HasId):
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
