from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

# TODO check that the bools are either true or false and how nulls are related
# as is a null false or is a null a lack of answer so could be true - philospophical


class BigIntPK(SQLModel):
    """bigint auto-incrementing primary key for every table."""

    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)


class HasId(SQLModel):
    """For Read models: the id is always present once a row exists."""

    id: int
