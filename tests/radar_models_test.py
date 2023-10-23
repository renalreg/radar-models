import ast

from sqlalchemy import create_mock_engine
from sqlalchemy.sql.type_api import TypeEngine
from sqlmodel import SQLModel

from radar_models import radar3
from tests.table_extractor import TableNameExtractor


def pg_dump(sql: TypeEngine, *args, **kwargs):
    dialect = sql.compile(dialect=postgres_engine.dialect)
    if sql_str := str(dialect).rstrip():
        print(f"{sql_str};")


postgres_engine = create_mock_engine("postgresql://", pg_dump)

with open("./radar_models/radar3.py", "r") as file:
    code = file.read()

tree = ast.parse(code)
table_name_extractor = TableNameExtractor()
table_name_extractor.visit(tree)


def test_create_tables(capsys):
    SQLModel.metadata.create_all(bind=postgres_engine, checkfirst=False)
    captured = capsys.readouterr()
    for table in table_name_extractor.table_names:
        assert f"CREATE TABLE {table}" in captured.out
