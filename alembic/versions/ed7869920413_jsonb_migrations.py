"""radar 2 -> radar 3: form entries (jsonb) -> one table per form

radar 2 stores every form as JSON: public.forms holds each form's definition
(forms.data["fields"]) and public.entries holds what was entered (entries.data).
radar 3 has a table per form. This step:

    1. read_forms           reads every radar 2 form definition
    2. check_forms_mapped   every form slug must map to a radar 3 model
    3. check_<form>_form    each form's field list must be the one its seed maps
    4. create_form_tables   creates the empty radar 3 form tables in radar3
    5. seed_<form>          reads the form's entries, maps each entry's JSON onto
                            the model, validates every row with model_validate,
                            and adds them with the session

Any entry that does not fit its model stops the migration, with every failing
entry listed, so nothing is half-copied.

Needs radar3.patient to exist (the form tables point at it) and assumes radar 3
kept radar 2's patient ids.

One-way migration.

Revision ID: ed7869920413
Revises: 9aaa2a094682
Create Date: 2026-11-05 17:20:30.173960

"""

from collections.abc import Sequence

from alembic import op
from pydantic import ValidationError
from sqlalchemy import text
from sqlmodel import Session

from radar_models.radar3 import SixCIT

# revision identifiers, used by Alembic.
revision: str = "ed7869920413"
down_revision: str | Sequence[str] | None = "9aaa2a094682"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# radar 2 form slug -> radar 3 model
FORM_MODELS = {
    "6cit": SixCIT,
}

# the field names in radar 2's 6cit form definition (forms.data["fields"])
SIX_CIT_FIELDS = {"date", "q1", "q2", "q4", "q5", "q6", "q7", "score"}


def read_forms(bind) -> dict[str, dict]:
    """Every radar 2 form definition, by slug: {slug: forms.data}."""
    rows = bind.execute(text("SELECT slug, data FROM public.forms ORDER BY slug"))
    return {slug: data for slug, data in rows}


def check_forms_mapped(forms: dict[str, dict]) -> None:
    """Every radar 2 form must have a radar 3 model in FORM_MODELS."""
    unmapped = sorted(set(forms) - set(FORM_MODELS))
    if unmapped:
        raise ValueError(f"radar 2 forms with no radar 3 model: {unmapped}")


def check_six_cit_form(form_data: dict) -> None:
    """radar 2's 6cit form must have exactly the fields seed_six_cit maps."""
    form_fields = {field["name"] for field in form_data["fields"]}
    if form_fields != SIX_CIT_FIELDS:
        raise ValueError(
            f"6cit form fields changed: expected {sorted(SIX_CIT_FIELDS)}, "
            f"radar 2 has {sorted(form_fields)}"
        )


def create_form_tables(bind) -> None:
    """The empty radar 3 form tables."""
    SixCIT.__table__.create(bind)


def seed_six_cit(session: Session) -> None:
    """6cit entries -> radar3.six_cit"""
    entries = session.execute(
        text("""
        SELECT e.id, e.patient_id, e.data
        FROM public.entries AS e
        JOIN public.forms AS f ON f.id = e.form_id
        WHERE f.slug = '6cit'
        ORDER BY e.created_date, e.id
    """)
    ).all()

    six_cits = []
    errors = []
    for entry_id, patient_id, data in entries:
        unexpected = set(data) - SIX_CIT_FIELDS
        if unexpected:
            errors.append(
                f"entry {entry_id}: keys not in the form {sorted(unexpected)}"
            )
            continue
        try:
            six_cits.append(
                SixCIT.model_validate(
                    {
                        "patient_id": patient_id,
                        "completed_date": data.get("date"),
                        "six_cit_q1_index": data.get("q1"),
                        "six_cit_q2_index": data.get("q2"),
                        "six_cit_q3_index": None,  # not in radar 2's form
                        "six_cit_q4_index": data.get("q4"),
                        "six_cit_q5_index": data.get("q5"),
                        "six_cit_q6_index": data.get("q6"),
                        "six_cit_q7_index": data.get("q7"),
                        "six_cit_score": data.get("score"),
                    }
                )
            )
        except ValidationError as error:
            errors.append(f"entry {entry_id}: {error}")

    if errors:
        raise ValueError(
            f"{len(errors)} of {len(entries)} 6cit entries do not fit SixCIT:\n"
            + "\n".join(errors)
        )

    session.add_all(six_cits)
    session.flush()


def upgrade() -> None:
    bind = op.get_bind()

    # checks first, so nothing is created if radar 2 does not match the mapping
    forms = read_forms(bind)
    check_forms_mapped(forms)
    check_six_cit_form(forms["6cit"])

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        create_form_tables(bind)

        with Session(bind=bind) as session:
            seed_six_cit(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")