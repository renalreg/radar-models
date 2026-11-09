"""radar 2 -> radar 3: patient tables

Creates the radar 3 patient tables in the radar3 schema from their models and
copies radar 2's rows into them. Radar 2's tables are left as they are.

    patients                                  -> patient                ids kept
    group_patients (COHORT groups)            -> cohort_patient         ids kept
    group_patients (HOSPITAL groups)          -> hospital_patient       ids kept
    patient_addresses                         -> patient_address        new ids
    patient_aliases                           -> patient_alias          new ids
    patient_consents                          -> patient_consent        ids kept
    patient_consents (a reconsent date set)   -> patient_reconsent      new ids
    patient_consultants                       -> patient_consultant     ids kept
    patient_demographics                      -> patient_demographic    new ids
    patient_demographics (date_of_death set)  -> death                  new ids
    patient_demographics (nationality_id set) -> patient_nationality    new ids
    patient_numbers                           -> patient_identifier     new ids
    family_histories (consanguinity set)      -> parental_consanguinity new ids
    diagnoses                                 -> diagnosis              ids kept
    family_histories (family_history set)     -> family_history         new ids
    family_history_relatives                  -> family_history_relation
                                                                        ids kept
    family_history_relatives (patient_id set) -> family_history_relation_patient
                                                                        new ids

Each radar 3 table has one copy_<table> function, which:
  1. reads radar 2's rows with SQL, under their radar 2 column names;
  2. maps each row to the radar 3 model's fields in a dict;
  3. checks every row with the model and adds them with the session:
         session.add_all([Model.model_validate(dict(row)) for row in rows])
Any error stops the migration and the whole step is rolled back: a row the model
rejects, a radar 2 value with no radar 3 row to look up, a foreign key with no
row to point at, or radar 2 data this step cannot map without guessing. The
last is checked before any of that table's rows are added, and the error lists
every row that needs fixing.

cohort_patient keeps each cohort's own recruited date, separate from the
patient's RaDaR date. The radar 2 data is copied as it is, assumed clean: it is
not checked against the consent dates here. group_patients' timestamps become
the day they fall on in the UK.

Where ids are kept, the id sequences are not moved past them here: that is done
for every table at the end of the migration. cohort_patient and hospital_patient
split group_patients, so the kept ids stay unique. Radar 2's UUID ids become new
bigint ids. The only UUIDs pointed at are
family_histories' (by family_history_relatives), which copy_family_history maps
to their new ids.

Lookups: group ids are kept as cohort and hospital ids (organisation step),
source_type -> data_source by name [D4] (step 0 seeded every name used),
country code -> country (geography step), number_group_id -> identifier, which
kept the group ids [D5], relationship -> relation, whose ids are radar 2's
relationship codes [D11] (seeded by an earlier step).

family_history points at diagnosis [D8], which no earlier step creates, so this
step creates it first. A later diagnosis step adds to diagnosis and must not
create it again.

One-way migration.

Revision ID: f2655dc80a30
Revises: b39e4dc2ac81
Create Date: 2026-11-06 16:01:41.330717
"""

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from alembic import op
from sqlalchemy import text
from sqlmodel import Session, SQLModel, select

from radar_models.radar3 import (
    CohortPatient,
    Country,
    DataSource,
    Death,
    Diagnosis,
    FamilyHistory,
    FamilyHistoryRelation,
    FamilyHistoryRelationPatient,
    HospitalPatient,
    ParentalConsanguinity,
    Patient,
    PatientAddress,
    PatientAlias,
    PatientConsent,
    PatientConsultant,
    PatientDemographic,
    PatientIdentifier,
    PatientNationality,
    PatientReconsent,
)

# revision identifiers, used by Alembic.
revision: str = "f2655dc80a30"
down_revision: str | Sequence[str] | None = "b39e4dc2ac81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# radar 2 stores group_patients' from_date and to_date as UTC timestamps (it sets
# them with datetime.now(pytz.UTC)). The date kept is the day it was in the UK,
# where RaDaR's users are: a plain ::date cast uses the database session's time
# zone, and with UTC puts anything between midnight and 1am BST on the day
# before. (For a non-UK site the day can still be one off.)
UK = ZoneInfo("Europe/London")

# created in this order, parents before children: every table points at patient,
# family_history at diagnosis, and the family_history_relation tables at
# family_history
TABLES: list[type[SQLModel]] = [
    Patient,
    CohortPatient,
    HospitalPatient,
    PatientAddress,
    PatientAlias,
    PatientConsent,
    PatientReconsent,
    PatientConsultant,
    PatientDemographic,
    Death,
    PatientNationality,
    PatientIdentifier,
    ParentalConsanguinity,
    FamilyHistory,
    FamilyHistoryRelation,
    FamilyHistoryRelationPatient,
]


def uk_date(timestamp: datetime | None) -> date | None:
    """The day a radar 2 timestamp falls on in the UK."""
    return timestamp.astimezone(UK).date() if timestamp is not None else None


def load_data_source_ids(session: Session) -> dict[str, int]:
    """data_source ids by name, for radar 2's source_type [D4]."""
    return {
        data_source.data_source_name: data_source.id
        for data_source in session.exec(select(DataSource))
    }


def copy_patient(session: Session) -> None:
    radar2_rows = session.execute(
        text("""
        SELECT id, comments, test, control
        FROM public.patients
        ORDER BY id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            "patient_comment": row["comments"],
            "is_test": row["test"],
            "is_control": row["control"],
        }
        for row in radar2_rows
    ]

    session.add_all([Patient.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_cohort_patient(session: Session) -> None:
    # each cohort's own group_patients row, with to_date kept as removed_date
    radar2_rows = session.execute(
        text("""
        SELECT
            group_patients.id,
            group_patients.group_id,
            group_patients.patient_id,
            group_patients.from_date,
            group_patients.to_date
        FROM public.group_patients
        JOIN public.groups ON groups.id = group_patients.group_id
        WHERE groups.type = 'COHORT'
        ORDER BY group_patients.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            "cohort_id": row["group_id"],  # cohort kept the group ids
            "patient_id": row["patient_id"],
            "recruited_date": uk_date(row["from_date"]),
            "removed_date": uk_date(row["to_date"]),
        }
        for row in radar2_rows
    ]

    session.add_all([CohortPatient.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_hospital_patient(session: Session) -> None:
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                group_patients.id,
                group_patients.group_id,
                group_patients.patient_id,
                group_patients.from_date,
                group_patients.to_date,
                group_patients.discharged_date
            FROM public.group_patients
            JOIN public.groups ON groups.id = group_patients.group_id
            WHERE groups.type = 'HOSPITAL'
            ORDER BY group_patients.id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "hospital_id": row["group_id"],  # hospital kept the group ids
            "patient_id": row["patient_id"],
            "first_seen_date": uk_date(row["from_date"]),
            "discharged_date": row["discharged_date"],
        }
        for row in radar2_rows
    ]

    session.add_all([HospitalPatient.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_address(session: Session) -> None:
    data_source_ids = load_data_source_ids(session)
    country_ids = {
        country.country_code: country.id for country in session.exec(select(Country))
    }

    # [D6] dropped: source_group_id
    radar2_rows = session.execute(
        text("""
        SELECT
            id, patient_id, source_type, country, from_date, to_date,
            address1, address2, address3, address4, postcode
        FROM public.patient_addresses
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": data_source_ids[row["source_type"]],
            "country_id": (
                country_ids[row["country"]] if row["country"] is not None else None
            ),
            "from_date": row["from_date"],
            "to_date": row["to_date"],
            "address1": row["address1"],
            "address2": row["address2"],
            "address3": row["address3"],
            "address4": row["address4"],
            "postcode": row["postcode"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientAddress.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_alias(session: Session) -> None:
    data_source_ids = load_data_source_ids(session)

    # [D6] dropped: source_group_id
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, source_type, first_name, last_name
        FROM public.patient_aliases
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": data_source_ids[row["source_type"]],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientAlias.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_consent(session: Session) -> None:
    # the reconsent letter dates go to patient_reconsent
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, consent_id, signed_on_date, withdrawn_on_date
        FROM public.patient_consents
        ORDER BY id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "consent_id": row["consent_id"],  # consent kept its ids
            "signed_on_date": row["signed_on_date"],
            "withdrawn_on_date": row["withdrawn_on_date"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientConsent.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_reconsent(session: Session) -> None:
    radar2_rows = session.execute(
        text("""
        SELECT
            id, patient_id,
            reconsent_letter_sent_date, reconsent_letter_returned_date
        FROM public.patient_consents
        WHERE reconsent_letter_sent_date IS NOT NULL
           OR reconsent_letter_returned_date IS NOT NULL
        ORDER BY id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "sent_date": row["reconsent_letter_sent_date"],
            "response_date": row["reconsent_letter_returned_date"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientReconsent.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_consultant(session: Session) -> None:
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, consultant_id, from_date, to_date
        FROM public.patient_consultants
        ORDER BY id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            "patient_id": row["patient_id"],
            "consultant_id": row["consultant_id"],  # consultant kept its ids
            "from_date": row["from_date"],
            "to_date": row["to_date"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientConsultant.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_demographic(session: Session) -> None:
    data_source_ids = load_data_source_ids(session)
    radar2_rows = session.execute(
        text("""
        SELECT DISTINCT ON (d.patient_id, d.id)
            d.id,
            d.patient_id,
            d.source_type,
            d.ethnicity_id,
            d.first_name,
            d.last_name,
            d.date_of_birth,
            d.gender,
            d.mobile_number,
            d.email_address,
            a.country
        FROM public.patient_demographics d
        LEFT JOIN public.patient_addresses a
            ON a.patient_id = d.patient_id
        ORDER BY d.patient_id, d.id, a.id DESC
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": data_source_ids[row["source_type"]],
            "ethnicity_id": row["ethnicity_id"],  # ethnicity kept its ids
            "country_id": row["country"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "date_of_birth": row["date_of_birth"],
            "gender_index": row["gender"],
            "mobile_number": row["mobile_number"],
            "email_address": row["email_address"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientDemographic.model_validate(dict(row)) for row in rows])
    session.flush()

def copy_death(session: Session) -> None:
    # [D9] assumed: one death per patient. A patient whose demographics rows give
    # different dates of death stops the migration. When they agree, the
    # cause_of_death comes from the most recently modified row.
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, date_of_death, cause_of_death
        FROM public.patient_demographics
        WHERE date_of_death IS NOT NULL
        ORDER BY patient_id, modified_date DESC NULLS LAST, id
    """)
    ).mappings()

    # the rows are newest first within each patient, so the first is kept
    latest = {}
    dates_of_death = defaultdict(set)
    for row in radar2_rows:
        latest.setdefault(row["patient_id"], row)
        dates_of_death[row["patient_id"]].add(row["date_of_death"])

    conflicting = [
        f"patient {patient_id}: {', '.join(str(day) for day in sorted(dates))}"
        for patient_id, dates in dates_of_death.items()
        if len(dates) > 1
    ]
    if conflicting:
        raise ValueError(
            f"{len(conflicting)} patients have more than one date_of_death in "
            "patient_demographics:\n" + "\n".join(conflicting)
        )

    rows = [
        {
            "patient_id": row["patient_id"],
            "date_of_death": row["date_of_death"],
            "cause_of_death": row["cause_of_death"],
        }
        for row in latest.values()
    ]

    session.add_all([Death.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_nationality(session: Session) -> None:
    # one row per patient and nationality: a patient whose demographics rows
    # give different nationalities gets each of them
    radar2_rows = session.execute(
        text("""
        SELECT DISTINCT patient_id, nationality_id
        FROM public.patient_demographics
        WHERE nationality_id IS NOT NULL
        ORDER BY patient_id, nationality_id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "nationality_id": row["nationality_id"],  # nationality kept its ids
        }
        for row in radar2_rows
    ]

    session.add_all([PatientNationality.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_patient_identifier(session: Session) -> None:
    data_source_ids = load_data_source_ids(session)

    # [D6] dropped: source_group_id
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, source_type, number_group_id, number
        FROM public.patient_numbers
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": data_source_ids[row["source_type"]],
            # [D5] identifier kept the ids of radar 2's OTHER groups (step 0); a
            # number on any other kind of group fails the foreign key
            "identifier_id": row["number_group_id"],
            "identifier_value": row["number"],
        }
        for row in radar2_rows
    ]

    session.add_all([PatientIdentifier.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_parental_consanguinity(session: Session) -> None:
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, parental_consanguinity
        FROM public.family_histories
        WHERE parental_consanguinity IS NOT NULL
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "has_consanguinity": row["parental_consanguinity"],
            "consanguinity_details": None,  # new in radar 3
        }
        for row in radar2_rows
    ]

    session.add_all([ParentalConsanguinity.model_validate(dict(row)) for row in rows])
    session.flush()





def copy_family_history(session: Session) -> dict[Any, int]:
    """Copies family_histories; returns each radar 2 id's new family_history id.

    [D8] assumed: radar 2 records a family history per cohort (group_id), of
    that cohort's condition. In radar 3 it points at the patient's own primary
    diagnosis in that cohort. A patient with none, or more than one, there
    stops the migration.

    A NULL family_history is an unanswered question, so that row is not copied
    (its parental_consanguinity is copied on its own).
    """
    # each patient's primary diagnoses in each cohort, by (patient id, cohort id)
    primary_diagnoses = defaultdict(set)
    patient_diagnoses = session.execute(
        text("""
        SELECT DISTINCT
            patient_diagnoses.patient_id,
            group_diagnoses.group_id,
            patient_diagnoses.diagnosis_id
        FROM public.patient_diagnoses
        JOIN public.group_diagnoses
            ON group_diagnoses.diagnosis_id = patient_diagnoses.diagnosis_id
        WHERE group_diagnoses.type = 'PRIMARY'
    """)
    )
    for patient_id, cohort_id, diagnosis_id in patient_diagnoses:
        primary_diagnoses[patient_id, cohort_id].add(diagnosis_id)

    # [D6] dropped: group_id (once it has found the diagnosis),
    # other_family_history
    radar2_rows = (
        session.execute(
            text("""
            SELECT id, patient_id, group_id, family_history
            FROM public.family_histories
            WHERE family_history IS NOT NULL
            ORDER BY patient_id, id
        """)
        )
        .mappings()
        .all()
    )

    not_one_diagnosis = []
    for row in radar2_rows:
        diagnoses = primary_diagnoses.get((row["patient_id"], row["group_id"]), set())
        if len(diagnoses) != 1:
            not_one_diagnosis.append(
                f"family_histories id {row['id']}: patient {row['patient_id']} has "
                f"{len(diagnoses)} primary diagnoses in cohort {row['group_id']} "
                f"{sorted(diagnoses)}"
            )
    if not_one_diagnosis:
        raise ValueError(
            f"{len(not_one_diagnosis)} family histories whose patient does not "
            "have exactly one primary diagnosis in the family history's cohort:\n"
            + "\n".join(not_one_diagnosis)
        )

    rows = [
        {
            "patient_id": row["patient_id"],
            # the one diagnosis; diagnosis kept its ids
            "diagnosis_id": next(
                iter(primary_diagnoses[row["patient_id"], row["group_id"]])
            ),
            # relatives who are patients go to family_history_relation_patient
            "relation_patient_id": None,
            "has_condition": row["family_history"],
        }
        for row in radar2_rows
    ]

    family_histories = [FamilyHistory.model_validate(dict(row)) for row in rows]
    session.add_all(family_histories)
    session.flush()

    # the new ids exist now the rows are flushed
    return {
        radar2_row["id"]: family_history.id
        for radar2_row, family_history in zip(
            radar2_rows, family_histories, strict=True
        )
    }


def copy_family_history_relation(
    session: Session, family_history_ids: dict[Any, int]
) -> None:
    # patient_id goes to family_history_relation_patient
    radar2_rows = (
        session.execute(
            text("""
            SELECT id, family_history_id, relationship
            FROM public.family_history_relatives
            ORDER BY id
        """)
        )
        .mappings()
        .all()
    )

    # a relative whose family history was not copied (no family_history answer)
    # has nothing to point at
    not_copied = [
        f"family_history_relatives id {row['id']}: family_histories id "
        f"{row['family_history_id']} has no family_history answer"
        for row in radar2_rows
        if row["family_history_id"] not in family_history_ids
    ]
    if not_copied:
        raise ValueError(
            f"{len(not_copied)} relatives whose family history was not copied:\n"
            + "\n".join(not_copied)
        )

    rows = [
        {
            "id": row["id"],
            "family_history_id": family_history_ids[row["family_history_id"]],
            # relation's ids are radar 2's relationship codes [D11]
            "relation_id": row["relationship"],
        }
        for row in radar2_rows
    ]

    session.add_all([FamilyHistoryRelation.model_validate(dict(row)) for row in rows])
    session.flush()


def copy_family_history_relation_patient(session: Session) -> None:
    # family_history_relation kept the relatives' ids, and has every relative
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id
        FROM public.family_history_relatives
        WHERE patient_id IS NOT NULL
        ORDER BY id
    """)
    ).mappings()

    rows = [
        {
            "family_history_relation_id": row["id"],
            "patient_id": row["patient_id"],
        }
        for row in radar2_rows
    ]

    session.add_all(
        [FamilyHistoryRelationPatient.model_validate(dict(row)) for row in rows]
    )
    session.flush()


def upgrade() -> None:
    bind = op.get_bind()

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, selects and foreign keys. Raw text() SQL is not affected, so
    # radar 2 is read with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        for model in TABLES:
            model.__table__.create(bind)

        with Session(bind=bind) as session:
            copy_patient(session)
            copy_patient_consent(session)
            copy_patient_reconsent(session)
            copy_cohort_patient(session)
            copy_hospital_patient(session)

            # left of from the cohort hospital split will be the systems group # TODO: is this intended

            copy_patient_address(session)
            copy_patient_alias(session)
            copy_patient_consultant(session)
            copy_patient_demographic(session)
            copy_death(session)
            copy_patient_nationality(session)
            copy_patient_identifier(session)
            copy_parental_consanguinity(session)
            family_history_ids = copy_family_history(session)
            copy_family_history_relation(session, family_history_ids)
            copy_family_history_relation_patient(session)
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")