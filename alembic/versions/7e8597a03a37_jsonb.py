"""radar 2 -> radar 3: form entries kept as JSONB
One-way migration.

Revision ID: 7e8597a03a37
Revises: b1fc3e475c02
Create Date: 2026-11-19 13:05:00.000000
"""

import json
import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from alembic import op
from sqlalchemy import select, text
from sqlmodel import Session, SQLModel

from form_fields.jsonb_form_fields import FORMS, SKIP, Skip
from radar_models.radar3 import Option

revision: str = "7e8597a03a37"
down_revision: str | Sequence[str] | None = "b1fc3e475c02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

FormFields = dict[str, str | type[SQLModel] | Skip]
FormCasts = dict[str, Callable[[Any], Any]]
OPTION_ID = f"{Option.__tablename__}.id"

TABLES = list(
    dict.fromkeys(
        table
        for model, fields, _ in FORMS.values()
        for table in (model, *(f for f in fields.values() if isinstance(f, type)))
    )
)


def option_fields(model: type[SQLModel]) -> set[str]:
    """The model's fields with a foreign key to option.id."""
    return {
        column.name
        for column in model.__table__.columns
        if any(key.target_fullname == OPTION_ID for key in column.foreign_keys)
    }


def parent_field(option_table: type[SQLModel], model: type[SQLModel]) -> str | None:
    """The option table's field pointing at the model's table."""
    for key in option_table.__table__.foreign_keys:
        if key.target_fullname == f"{model.__tablename__}.id":
            return key.parent.name
    return None


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
    model, as model_validate ignores a field the model does not have; that
    every option table it maps a key to points at the form's table and has an
    option_id; and that every key FORMS gives a cast for is a key it maps and
    does not skip."""
    for form_id, (model, fields, casts) in FORMS.items():
        unknown = {
            key: field
            for key, field in fields.items()
            if isinstance(field, str) and field not in model.model_fields
        }
        if unknown:
            raise ValueError(
                f"form {form_id} maps keys to fields {model.__name__} does not "
                "have: "
                + ", ".join(f"{key} -> {field}" for key, field in unknown.items())
            )

        unlinked = {
            key: table.__name__
            for key, table in fields.items()
            if isinstance(table, type)
            and (
                parent_field(table, model) is None
                or "option_id" not in table.model_fields
            )
        }
        if unlinked:
            raise ValueError(
                f"form {form_id} maps keys to option tables with no key to "
                f"{model.__tablename__} or no option_id: "
                + ", ".join(f"{key} -> {table}" for key, table in unlinked.items())
            )

        copied = {key for key, field in fields.items() if field is not SKIP}
        unused = casts.keys() - copied
        if unused:
            raise ValueError(
                f"form {form_id} has casts for keys it does not map or skips: "
                f"{', '.join(sorted(unused))}"
            )


def option_id(
    entry: Mapping[str, Any],
    key: str,
    value: Any,
    options: dict[tuple[str, str], int],
) -> int:
    """The id of the option value is in key's option group."""
    return options[f"{entry['slug']}.{key}", as_store_value(value)]


def copy_form(
    session: Session,
    form_id: int,
    model: type[SQLModel],
    fields: FormFields,
    casts: FormCasts,
    options: dict[tuple[str, str], int],
) -> int:
    """Copies form form_id's entries into model's table, one row per entry,
    with each key in the entry's data in the model field fields maps it to,
    other than keys it maps to SKIP, which are left out, cast first if casts has a cast for the key, and looked up in options if
    the field holds an option; then adds a row to the option table a key is
    mapped to for each of its answers. Returns how many entries it copied."""
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

    holds_option = option_fields(model)
    rows: list[tuple[SQLModel, list[tuple[type[SQLModel], int]]]] = []
    for entry in entries:
        data = entry["data"] or {}

        unmapped = data.keys() - fields.keys()
        if unmapped:
            raise ValueError(
                f"radar 2 entry {entry['id']} ({entry['slug']}, form {form_id}) has "
                f"fields with no {model.__tablename__} column: "
                f"{', '.join(sorted(unmapped))}"
            )

        row: dict[str, Any] = {"patient_id": entry["patient_id"]}
        answers: list[tuple[type[SQLModel], int]] = []
        for key, field in fields.items():
            if field is SKIP:
                continue
            value = data.get(key)
            if value is not None and key in casts:
                value = casts[key](value)
            if not isinstance(field, str):
                answers += [
                    (field, option_id(entry, key, answer, options))
                    for answer in (value if isinstance(value, list) else [value])
                    if answer is not None
                ]
                continue
            if value is not None and field in holds_option:
                value = option_id(entry, key, value, options)
            row[field] = value

        rows.append((model.model_validate(row), answers))

    session.add_all([copy for copy, _ in rows])
    session.flush()

    session.add_all(
        [
            table.model_validate(
                {parent_field(table, model): copy.id, "option_id": answer_id}
            )
            for copy, answers in rows
            for table, answer_id in answers
        ]
    )
    session.flush()
    return len(rows)


def log_forms_not_copied(session: Session) -> None:
    """Logs each radar 2 form FORMS does not cover, with its count of
    entries."""
    rows = session.execute(
        text("""
        SELECT forms.id, forms.slug, count(entries.id)
        FROM public.forms
        LEFT JOIN public.entries ON entries.form_id = forms.id
        WHERE NOT forms.id = ANY(:copied)
        GROUP BY forms.id, forms.slug
        ORDER BY forms.id
    """),
        {"copied": list(FORMS)},
    ).all()
    for form_id, slug, count in rows:
        log.info(
            "form %d (%s): %s %s not copied, no radar 3 model",
            form_id,
            slug,
            f"{count:,}",
            "entry" if count == 1 else "entries",
        )


def upgrade() -> None:
    check_forms()

    bind = op.get_bind()
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in TABLES:
            if model.__table__.name != "clinical_letter":
                model.__table__.create(bind)

        with Session(bind=bind) as session:
            options = load_options(session)
            for form_id, (model, fields, casts) in reversed(FORMS.items()):
                count = copy_form(session, form_id, model, fields, casts, options)
                log.info(
                    "%s: %s rows copied from form %d's entries",
                    model.__tablename__,
                    f"{count:,}",
                    form_id,
                )
            log_forms_not_copied(session)
    finally:
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")
