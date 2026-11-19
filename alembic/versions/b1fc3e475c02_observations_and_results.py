"""radar 2 -> radar 3: observations and results

Creates the radar 3 observation and result tables in the radar3 schema from
their models and copies radar 2's rows into them. Radar 2's tables are left as
they are. results is likely radar 2's biggest table, so it has this step to
itself and is copied in batches (see copy_result).

    observations                    -> observation                 ids kept
    results                         -> result                      new ids

observation is copied as the other steps copy their tables: its rows are read
with SQL under their radar 2 column names, mapped to the model's fields in a
dict, checked with the model and added with the session.

result's rows are checked with the model too, but as radar 2 has about 61
million results they are copied in batches of RESULT_BATCH_SIZE rows, and each
batch is inserted with one execute rather than added with the session (see
copy_result). The model cannot check that every patient, observation, hospital
and data source pointed at exists; the database checks that when result's
foreign keys are added after the copy.

Any error stops the migration and the whole step is rolled back.



Times: results.date, a radar 2 timestamptz, keeps the UTC time, with or without
a zone as the radar 3 column takes it (see utc()).

Dropped from every table: source_group_id and source_type (looked up as above),
created_user_id, created_date, modified_user_id, modified_date.
could change: observations' value_type, pv_code, min_length, max_length and
options, and group_observations, are not copied yet: radar 3's observation has
no columns for them, and observation_code, observation_option and
cohort_observation have no mapping.

One-way migration.

Revision ID: b1fc3e475c02
Revises: ebaa154bbec0
Create Date: 2026-11-18 15:40:00.000000
"""

import logging
import time
from collections.abc import Sequence
from datetime import UTC, datetime

from alembic import op
from pydantic import ValidationError
from sqlalchemy import Column, RowMapping, insert, text
from sqlalchemy.schema import AddConstraint, CreateTable
from sqlmodel import Session

from radar_models.radar3 import Observation, Result

# revision identifiers, used by Alembic.
revision: str = "b1fc3e475c02"
down_revision: str | Sequence[str] | None = "ebaa154bbec0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

# results are read and inserted this many at a time, and progress is logged
# after each batch (see copy_result)
RESULT_BATCH_SIZE = 100_000


def utc(timestamp: datetime | None, column: Column) -> datetime | None:
    """A radar 2 timestamptz as its UTC time, in the form the radar 3 column
    takes: with its zone for a timestamptz column, without one for a timestamp
    column (given a zone, the database would store it in the connection's time
    zone instead).

    SQLModel decides which: a datetime field is timestamptz (UTCDateTime) in
    newer SQLModel, timestamp in older, and a NaiveDatetime field is timestamp.
    """
    if timestamp is None:
        return None
    in_utc = timestamp.astimezone(UTC)
    return in_utc if column.type.timezone else in_utc.replace(tzinfo=None)


def reset_sequence(session: Session, table_name: str) -> None:
    """The ids were copied, so move the table's id sequence past them."""
    session.execute(
        text(f"""
        SELECT setval(
            pg_get_serial_sequence('radar3.{table_name}', 'id'),
            (SELECT COALESCE(MAX(id), 0) + 1 FROM radar3.{table_name}),
            false
        )
    """)
    )


def hospital_id(row: RowMapping) -> int | None:
    """[D3] the row's source group if it is a hospital, else NULL. type is the
    source group's, from the join to public.groups."""
    if row["type"] == "HOSPITAL":
        return row["source_group_id"]  # hospital kept the group ids
    return None


def checked_result(row: RowMapping, result_date: Column) -> dict:
    """A radar 2 result mapped to radar 3's fields and checked with the model,
    returned as the dict to insert. id is left out, as the database gives each
    result a new one. A row the model rejects stops the migration, naming the
    radar 2 result; the model's own error is chained below it."""
    fields = {
        "patient_id": row["patient_id"],  # patient kept its ids
        "observation_id": row["observation_id"],  # observation kept its ids
        "hospital_id": hospital_id(row),  # [D3]
        "data_source_id": row["data_source_id"],  # [D4]
        "result_date": utc(row["date"], result_date),
        "qualifier": None,  # new in radar 3
        "result_value": row["value"],
        "sent_value": row["sent_value"],
    }
    try:
        result = Result.model_validate(fields)
    except ValidationError as error:
        raise ValueError(
            f"radar 2 result {row['id']} does not pass radar 3's Result model"
        ) from error
    # the model object is dropped here, so a batch holds only dicts
    return result.model_dump(exclude={"id"})


def log_progress(copied: int, total: int, seconds: float) -> None:
    """Logs how many of the results are in, and roughly how long the rest will
    take at the rate so far."""
    percent = copied * 100 // total if total else 100
    seconds_left = seconds / copied * (total - copied) if copied else 0
    minutes, seconds_left = divmod(round(seconds_left), 60)
    log.info(
        "result: %s of %s rows copied (%d%%), about %d min %d s left",
        f"{copied:,}",
        f"{total:,}",
        percent,
        minutes,
        seconds_left,
    )


def copy_observation(session: Session) -> None:
    """Copies observations, keeping their ids, so result's observation_id
    copies across."""
    # could change: value_type, pv_code, min_length, max_length and options
    # are not copied (see the module docstring)
    radar2_rows = session.execute(
        text("""
        SELECT
            observations.id,
            (
                SELECT sample_type.id
                FROM radar3.sample_type
                WHERE sample_type.sample_type_label = observations.sample_type::text
            ) AS sample_type_id,
            observations.name,
            observations.short_name,
            observations.min_value,
            observations.max_value,
            observations.units
        FROM public.observations
        ORDER BY observations.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            # NULL when no sample_type has the label, which the model rejects
            "sample_type_id": row["sample_type_id"],
            "observation_name": row["name"],
            "observation_short_name": row["short_name"],
            "min_value": row["min_value"],
            "max_value": row["max_value"],
            "observation_units": row["units"],
        }
        for row in radar2_rows
    ]

    session.add_all([Observation.model_validate(row) for row in rows])
    session.flush()
    reset_sequence(session, "observation")


def copy_result(session: Session) -> int:
    """Copies results RESULT_BATCH_SIZE rows at a time, checking each with the
    model, and returns how many rows it copied.

    radar 2 has about 61 million results. The database streams them, and each
    row is mapped to the radar 3 fields and checked with Result.model_validate,
    as observation's rows are (see checked_result). Each batch is then
    inserted into result with one execute, not added with the session: the
    session would track every object and fetch each new id back, which a copy
    this size cannot afford. Nothing is kept from one batch to the next, so
    memory stays at one batch.

    Progress is logged after each batch, against a count of radar 2's results
    taken first: "result: 3,100,000 of 61,000,000 rows copied (5%), about
    18 min 40 s left". It shows in Alembic's output with its "Running upgrade"
    lines, as it uses Alembic's own logger. The first estimate is high: the
    first batch also waits for the database to sort the rows.

    The model checks each row's types and required fields (patient_id,
    observation_id, result_date, sent_value) before it goes in. It cannot
    check the foreign keys, so the database checks those when upgrade() adds
    them after the copy.
    """
    # the rows the copy below reads, counted first for the progress lines
    total = session.execute(
        text("""
        SELECT count(*)
        FROM public.results
        JOIN public.groups ON groups.id = results.source_group_id
    """)
    ).scalar_one()
    log.info(
        "result: copying %s rows from radar 2's results, %s at a time",
        f"{total:,}",
        f"{RESULT_BATCH_SIZE:,}",
    )

    radar2_rows = session.execute(
        text("""
        SELECT
            results.id,
            results.patient_id,
            results.observation_id,
            results.source_group_id,
            groups.type,
            (
                SELECT data_source.id
                FROM radar3.data_source
                WHERE data_source.data_source_name = results.source_type
            ) AS data_source_id,
            results.date,
            results.value,
            results.sent_value
        FROM public.results
        JOIN public.groups ON groups.id = results.source_group_id
        ORDER BY results.patient_id, results.date, results.id
    """),
        execution_options={"yield_per": RESULT_BATCH_SIZE},
    ).mappings()

    insert_result = insert(Result.__table__)
    result_date = Result.__table__.c.result_date
    copied = 0
    started = time.monotonic()

    # yield_per above makes the database stream the rows; the size is given
    # again here, as .mappings() does not pass it on to partitions()
    for batch in radar2_rows.partitions(RESULT_BATCH_SIZE):
        rows = [checked_result(row, result_date) for row in batch]

        # executed at once, so there is nothing to flush
        session.execute(insert_result, rows)

        copied += len(rows)
        log_progress(copied, total, time.monotonic() - started)

    return copied


def upgrade() -> None:
    bind = op.get_bind()

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        # observation points at sample_type (step 0), and result at observation
        Observation.__table__.create(bind)

        # result is created without its foreign keys or indexes, which are added
        # once its rows are in: checking four keys for each row as it goes in
        # takes far longer than adding a key, which checks every row at once
        bind.execute(CreateTable(Result.__table__, include_foreign_key_constraints=[]))

        with Session(bind=bind) as session:
            copy_observation(session)
            count = copy_result(session)
            log.info("result: %s rows copied from radar 2's results, in all", f"{count:,}")

        # a result with no patient, observation, hospital or data source to
        # point at stops the migration here
        for foreign_key in Result.__table__.foreign_key_constraints:
            bind.execute(AddConstraint(foreign_key))
        for index in Result.__table__.indexes:
            index.create(bind)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")