"""radar 2 -> radar 3: form entries kept as JSONB

Creates radar 3 tables for the radar 2 forms whose answers are kept in
entries.data, a JSONB column, and copies each entry into its own row, with each
of the form's fields in its own column. Radar 2's tables are left as they are.

    entries (form 18)               -> adverse_event               new ids

FORMS says where each form's entries go, which key in entries.data goes to
which of the model's fields, and which keys' values are cast before they go to
the model. Each entry is read with SQL, joined to public.forms for its form's
slug, its data cast and spread into those fields in a dict, checked with the
model and added with the session.

An entry whose data has a key that is not mapped stops the migration, naming
the entry and the key, so no answer is dropped without anyone deciding to drop
it. A key that is mapped but missing from an entry, as when a question was not
answered, gives NULL.

A key mapped to a field its form's model does not have stops the migration
before any table is made, naming the form, the key and the field, as the model
would otherwise drop that answer without a word. So does a cast for a key that
is not mapped, as it would never be used.

Values go to the model as radar 2 stored them, unless FORMS gives a cast for
the key or the field is an option index: dates as text, which the model parses;
yes / no / Unknown answers as that text. otherTox, a list of text, is joined
into one string, its items split by ", ". A cast is not given a missing or null
value; that stays NULL. A value a cast or the model rejects stops the
migration, naming the entry.

A field whose name ends in _index holds the id of a radar 3 option. Its radar 2
value, after any cast, is looked up in the option table by the value and the
option group, which is the entry's form slug and the key joined by a dot
(rituximab-adverse-events.causedOther), as seed_form_options made them, and
the option's id goes to the model. A value
with no option stops the migration, naming the entry, the key, the value and
the group. A missing or null value is not looked up; it stays NULL.

Entries get new ids, in patient and date order; no UUID -> new id map is kept,
as no radar 2 table points at entries.

Dropped: entries.id and form_id (the form decides the table), created_user_id,
created_date, modified_user_id, modified_date.

Any error stops the migration and the whole step is rolled back.

One-way migration.

Revision ID: 7e8597a03a37
Revises: b1fc3e475c02
Create Date: 2026-11-19 13:05:00.000000
"""

import json
import logging
from collections.abc import Callable, Sequence
from typing import Any

from alembic import op
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import AdverseEvent, Option

revision: str = "7e8597a03a37"
down_revision: str | Sequence[str] | None = "b1fc3e475c02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

ADVERSE_EVENT_FIELDS = {
    "date": "review_date",
    "hospitalisation": "has_hospitalisation",
    "adverseEvents": "has_adverse_event",
    "newOnsetCancer": "new_onset_cancer",
    "causedCancer": "caused_cancer_index",
    "thromboembolism": "thromboembolism",
    "causedVenousThromboEmbolism": "caused_venous_thrombo_embolism_index",
    "myocardialInfarction": "myocardial_infarction",
    "causedAcuteMyocardialInfarction": "caused_acute_myocardial_infarction_index",
    "stroke": "stroke",
    "causedStroke": "caused_stroke_index",
    "ischaemicAttack": "ischaemic_attack",
    "causedIschaemicAttack": "caused_ischaemic_attack_index",
    "otherAdverseEvent": "other_adverse_event",
    "otherTox": "other_toxicity",
    "causedOther": "caused_other_index",
    "dod": "date_of_death",
    "dodCause": "date_of_death",
}

def join_text(value: Any) -> str:
    """Joins a list of text into one string, its items split by ", "."""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        raise TypeError(f"expected a list, got {type(value).__name__}")
    return ", ".join(str(item) for item in value)


ADVERSE_EVENT_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "otherTox": join_text,
}

TABLES = [
    AdverseEvent,
]

FORMS = {
    18: (AdverseEvent, ADVERSE_EVENT_FIELDS, ADVERSE_EVENT_FIELDS_CAST),
}

OPTION_INDEX_SUFFIX = "_index"


def load_options(session: Session) -> dict[tuple[str, str], int]:
    """Returns every radar 3 option's id, by its option group and store
    value."""
    return {
        (option_group, store_value): option_id
        for option_group, store_value, option_id in session.execute(
            select(Option.option_group, Option.store_value, Option.id)
        )
    }


def as_store_value(value: Any) -> str:
    """Returns value as text the way PostgreSQL's ->> gives it, which is how
    seed_form_options read each option's store value: text as it is, anything
    else as JSON (1, 1.5, true)."""
    return value if isinstance(value, str) else json.dumps(value)


def check_forms() -> None:
    """Checks that every field FORMS maps a key to is a field of that form's
    model, as model_validate ignores a field the model does not have, and that
    every key FORMS gives a cast for is a key it maps."""
    for form_id, (model, fields, casts) in FORMS.items():
        unknown = {
            key: field
            for key, field in fields.items()
            if field not in model.model_fields
        }
        if unknown:
            raise ValueError(
                f"form {form_id} maps keys to fields {model.__name__} does not "
                "have: "
                + ", ".join(f"{key} -> {field}" for key, field in unknown.items())
            )

        unused = casts.keys() - fields.keys()
        if unused:
            raise ValueError(
                f"form {form_id} has casts for keys it does not map: "
                f"{', '.join(sorted(unused))}"
            )


def copy_form(
    session: Session,
    form_id: int,
    model: type[SQLModel],
    fields: dict[str, str],
    casts: dict[str, Callable[[Any], Any]],
    options: dict[tuple[str, str], int],
) -> int:
    """Copies form form_id's entries into model's table, one row per entry,
    with each key in the entry's data in the model field fields maps it to,
    cast first if casts has a cast for the key, and looked up in options if
    the field is an option index. Returns how many rows it copied."""
    entries = session.execute(
        text("""
        SELECT
            entries.id,
            entries.patient_id,
            forms.slug,
            entries.data
        FROM public.entries
        JOIN public.forms ON forms.id = entries.form_id
        WHERE entries.form_id = :form_id
        ORDER BY entries.patient_id, entries.data->>'date', entries.id
    """),
        {"form_id": form_id},
    ).mappings()

    rows = []
    for entry in entries:
        data = entry["data"] or {}

        unmapped = data.keys() - fields.keys()
        if unmapped:
            raise ValueError(
                f"radar 2 entry {entry['id']} ({entry['slug']}, form {form_id}) has "
                f"fields with no {model.__tablename__} column: "
                f"{', '.join(sorted(unmapped))}"
            )

        row = {"patient_id": entry["patient_id"]}
        for key, field in fields.items():
            value = data.get(key)
            if value is not None and key in casts:
                try:
                    value = casts[key](value)
                except Exception as e:
                    raise ValueError(
                        f"radar 2 entry {entry['id']} ({entry['slug']}, form "
                        f"{form_id}): {key} could not be cast: {e}"
                    ) from e
            if value is not None and field.endswith(OPTION_INDEX_SUFFIX):
                option_group = f"{entry['slug']}.{key}"
                try:
                    value = options[option_group, as_store_value(value)]
                except KeyError:
                    raise ValueError(
                        f"radar 2 entry {entry['id']} ({entry['slug']}, form "
                        f"{form_id}): {key} is {value!r}, which is not an option "
                        f"in group {option_group!r}"
                    ) from None
            row[field] = value

        try:
            rows.append(model.model_validate(row))
        except ValidationError as e:
            raise ValueError(
                f"radar 2 entry {entry['id']} ({entry['slug']}, form {form_id}) "
                f"was rejected by {model.__name__}: {e}"
            ) from e

    session.add_all(rows)
    session.flush()
    return len(rows)


def upgrade() -> None:
    check_forms()

    bind = op.get_bind()
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in TABLES:
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            options = load_options(session)
            for form_id, (model, fields, casts) in FORMS.items():
                count = copy_form(session, form_id, model, fields, casts, options)
                log.info(
                    "%s: %s rows copied from form %d's entries",
                    model.__tablename__,
                    f"{count:,}",
                    form_id,
                )
    finally:
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")