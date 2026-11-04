"""Countries, ethnicities and nationalities."""

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

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


# --- Ethnicity --- #


class EthnicityBase(SQLModel):
    ethnicity_code: str | None = None
    ethnicity_label: str | None = None


class Ethnicity(EthnicityBase, BigIntPK, table=True):
    __tablename__ = "ethnicity"


class EthnicityRead(EthnicityBase, HasId):
    pass


# --- Nationality --- #


class NationalityBase(SQLModel):
    nationality_label: str | None = None


class Nationality(NationalityBase, BigIntPK, table=True):
    __tablename__ = "nationality"


class NationalityRead(NationalityBase, HasId):
    pass
