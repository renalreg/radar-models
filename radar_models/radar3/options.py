from sqlmodel import SQLModel

from radar_models.radar3.shared import BigIntPK, HasId


class OptionBase(SQLModel):
    option_group: str
    display_label: str
    store_value: str


class Option(OptionBase, BigIntPK, table=True):
    __tablename__ = "option"


class OptionRead(OptionBase, HasId):
    pass
