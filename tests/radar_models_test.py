from sqlalchemy import create_mock_engine
from sqlalchemy.sql.type_api import TypeEngine
from sqlmodel import SQLModel

from tests.test_lists import tables, enums
from radar_models.radar3 import *


def pg_dump(sql: TypeEngine, *args, **kwargs):
    dialect = sql.compile(dialect=postgres_engine.dialect)
    if sql_str := str(dialect).rstrip():
        print(f"{sql_str};")


postgres_engine = create_mock_engine("postgresql://", pg_dump)


def test_create_tables(capsys):
    SQLModel.metadata.create_all(bind=postgres_engine, checkfirst=False)
    captured = capsys.readouterr()
    for table in tables:
        assert f"CREATE TABLE {table}" in captured.out


def test_create_enum(capsys):
    SQLModel.metadata.create_all(bind=postgres_engine, checkfirst=False)
    captured = capsys.readouterr()
    for enum in enums:
        assert f"CREATE TYPE {enum} AS ENUM {enums[enum]};" in captured.out
