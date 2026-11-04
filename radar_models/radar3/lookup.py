"""Small reference lists other tables point at."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- DataSource --- #


class DataSourceBase(SQLModel):
    data_source_name: str


class DataSource(DataSourceBase, BigIntPK, table=True):
    __tablename__ = "data_source"


class DataSourceRead(DataSourceBase, HasId):
    pass


# --- FrontPageStat --- #


class FrontPageStatBase(SQLModel):
    stat_label: str
    stat_value: str


class FrontPageStat(FrontPageStatBase, BigIntPK, table=True):
    __tablename__ = "front_page_stat"


class FrontPageStatRead(FrontPageStatBase, HasId):
    pass


# --- Identifier --- #


class IdentifierBase(SQLModel):
    identifier_label: str


class Identifier(IdentifierBase, BigIntPK, table=True):
    __tablename__ = "identifier"


class IdentifierRead(IdentifierBase, HasId):
    pass


# --- Indicator --- #


class IndicatorBase(SQLModel):
    indicator_label: str


class Indicator(IndicatorBase, BigIntPK, table=True):
    __tablename__ = "indicator"


class IndicatorRead(IndicatorBase, HasId):
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


# --- Relation --- #


class RelationBase(SQLModel):
    relation_label: str


class Relation(RelationBase, BigIntPK, table=True):
    __tablename__ = "relation"


class RelationRead(RelationBase, HasId):
    pass


# --- SampleType --- #


class SampleTypeBase(SQLModel):
    sample_type_label: str = Field(unique=True)


class SampleType(SampleTypeBase, BigIntPK, table=True):
    __tablename__ = "sample_type"


class SampleTypeRead(SampleTypeBase, HasId):
    pass
