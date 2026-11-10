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
    family_histories (family_history true)    -> family_history         new ids
    family_history_relatives (patient_id set) -> patient_relation       new ids
    family_history_relatives                  -> family_history_relation
                                                                        ids kept

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
source_group_id copied as data_source_id, as data_source kept radar 2's group
ids (step 0; source_type is dropped), country codes copied as they are, as
country is keyed by its code (geography step), number_group_id -> identifier,
which kept the group ids [D5] (step 0), relationship -> relation, whose ids are
radar 2's relationship codes [D11] (step 0).

A family_history records a condition the patient's relatives have, and whether
the patient has it too. Radar 2's family_history flag says whether the family
has a history, so a radar 2 row is copied when the flag is true (in radar 2's
data, the only rows that list relatives); has_condition is whether the patient
has the diagnosis in patient_diagnoses. diagnosis_id is the cohort's PRIMARY
diagnosis in group_diagnoses [D8], as diagnosis kept radar 2's ids (step 0). A
cohort with none, or several, gives NULL: a radar 2 data quality issue, not
checked here.

patient_relation links two patients on Radar who are family, stated from the
first patient's side. A radar 2 relative who is a patient gives one row per
patient and relative, however many of the patient's family histories list them,
and their family_history_relation points at it. A relative listed with
different relationships, or a patient listed as their own relative, cannot be
mapped without guessing and stops the migration.

Comments marked "could change:" are where open decisions or model changes would
change the copy.

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
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    CohortPatient,
    Death,
    FamilyHistory,
    FamilyHistoryRelation,
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
    PatientRelation,
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
# and family_history_relation at family_history and patient_relation
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
    PatientRelation,
    FamilyHistoryRelation,
]


def uk_date(timestamp: datetime | None) -> date | None:
    """The day a radar 2 timestamp falls on in the UK."""
    return timestamp.astimezone(UK).date() if timestamp is not None else None


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
            "id": row["id"],
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
    # dropped: source_type
    radar2_rows = session.execute(
        text("""
        SELECT
            id, patient_id, source_group_id, country, from_date, to_date,
            address1, address2, address3, address4, postcode
        FROM public.patient_addresses
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": row["source_group_id"],  # data_source kept group ids
            "country_code": row["country"],  # country is keyed by its code
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
    # dropped: source_type
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, source_group_id, first_name, last_name
        FROM public.patient_aliases
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": row["source_group_id"],  # data_source kept group ids
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
            "id": row["id"],
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
    # dropped: source_type
    radar2_rows = session.execute(
        text("""
        SELECT DISTINCT ON (d.patient_id, d.id)
            d.id,
            d.patient_id,
            d.source_group_id,
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
            "data_source_id": row["source_group_id"],  # data_source kept group ids
            "ethnicity_id": row["ethnicity_id"],  # ethnicity kept its ids
            "country_code": row["country"],  # country is keyed by its code
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
        SELECT id, patient_id, source_group_id, date_of_death, cause_of_death
        FROM public.patient_demographics
        WHERE date_of_death IS NOT NULL
        ORDER BY patient_id, modified_date DESC NULLS LAST, id
    """)
    ).mappings()

    # # the rows are newest first within each patient, so the first is kept
    # latest = {}
    # dates_of_death = defaultdict(set)
    # for row in radar2_rows:
    #     latest.setdefault(row["patient_id"], row)
    #     dates_of_death[row["patient_id"]].add(row["date_of_death"])
    #
    # conflicting = [
    #     f"patient {patient_id}: {', '.join(str(day) for day in sorted(dates))}"
    #     for patient_id, dates in dates_of_death.items()
    #     if len(dates) > 1
    # ]
    # if conflicting:
    #     raise ValueError(
    #         f"{len(conflicting)} patients have more than one date_of_death in "
    #         "patient_demographics:\n" + "\n".join(conflicting)
    #     )
    #
    # rows = [
    #     {
    #         "patient_id": row["patient_id"],
    #         "date_of_death": row["date_of_death"],
    #         "cause_of_death": row["cause_of_death"],
    #     }
    #     for row in latest.values()
    # ]

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": row["source_group_id"],  # data_source kept group ids
            "date_of_death": row["date_of_death"],
            "cause_of_death": row["cause_of_death"],
        }
        for row in radar2_rows
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
    # dropped: source_type
    radar2_rows = session.execute(
        text("""
        SELECT id, patient_id, source_group_id, number_group_id, number
        FROM public.patient_numbers
        ORDER BY patient_id, id
    """)
    ).mappings()

    rows = [
        {
            "patient_id": row["patient_id"],
            "data_source_id": row["source_group_id"],  # data_source kept group ids
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
    """Copies family_histories and returns their new ids by radar 2 UUID, for
    family_history_relation.

    A radar 3 family_history records a condition the patient's relatives have
    (diagnosis_id) and whether the patient has it too (has_condition). Radar 2's
    family_history flag says whether the family has a history, not the patient,
    so it decides which rows are copied rather than filling has_condition.
    """
    # Rows copied: family_history is true. A false or NULL [D1] one records no
    # condition in the family, so there is nothing to copy; in radar 2's data
    # none of them lists a relative (copy_family_history_relation relies on it)
    # could change: a true family_history with no relatives is copied as a
    # family_history with no relations, so radar 2's "yes" is kept
    #
    # diagnosis_id [D8]: the cohort's PRIMARY diagnosis, NULL when the cohort
    # has none or several (a radar 2 data quality issue, not checked here).
    # could change: the design links every family_history to a diagnosis; if
    # the model makes diagnosis_id required, those rows need a rule
    #
    # has_condition: whether the patient has that diagnosis in patient_diagnoses.
    # could change: a NULL diagnosis_id gives false, as nothing can match it
    #
    # parental_consanguinity went to parental_consanguinity
    # [D6] dropped: other_family_history
    radar2_rows = (
        session.execute(
            text("""
            SELECT
                family_histories.id,
                family_histories.patient_id,
                primary_diagnosis.diagnosis_id,
                EXISTS (
                    SELECT 1
                    FROM public.patient_diagnoses
                    WHERE patient_diagnoses.patient_id = family_histories.patient_id
                      AND patient_diagnoses.diagnosis_id
                          = primary_diagnosis.diagnosis_id
                ) AS has_condition
            FROM public.family_histories
            LEFT JOIN (
                SELECT group_id, min(diagnosis_id) AS diagnosis_id
                FROM public.group_diagnoses
                WHERE type = 'PRIMARY'
                GROUP BY group_id
                HAVING count(*) = 1
            ) AS primary_diagnosis
                ON primary_diagnosis.group_id = family_histories.group_id
            WHERE family_histories.family_history
            ORDER BY family_histories.patient_id, family_histories.group_id
        """)
        )
        .mappings()
        .all()
    )

    rows = [
        {
            "patient_id": row["patient_id"],
            "diagnosis_id": row["diagnosis_id"],
            "has_condition": row["has_condition"],
        }
        for row in radar2_rows
    ]

    family_histories = [FamilyHistory.model_validate(dict(row)) for row in rows]
    session.add_all(family_histories)
    session.flush()

    # the flush gave each row its new id
    return {
        row["id"]: family_history.id
        for row, family_history in zip(radar2_rows, family_histories, strict=True)
    }


def copy_patient_relation(session: Session) -> dict[tuple[int, int], int]:
    """Copies the relatives who are patients on Radar to patient_relation, and
    returns their new ids by (patient_id, related_patient_id), for
    family_history_relation."""
    # one row per patient and relative, however many of the patient's family
    # histories list them; stated from the patient's side, as radar 2 recorded it
    # could change: the reverse row (the relative's relation to the patient) is
    # not made up here; it exists only if the relative's own family history
    # lists the patient
    radar2_rows = (
        session.execute(
            text("""
            SELECT DISTINCT
                family_histories.patient_id,
                family_history_relatives.patient_id AS related_patient_id,
                family_history_relatives.relationship
            FROM public.family_history_relatives
            JOIN public.family_histories
                ON family_histories.id = family_history_relatives.family_history_id
            WHERE family_history_relatives.patient_id IS NOT NULL
            ORDER BY patient_id, related_patient_id, relationship
        """)
        )
        .mappings()
        .all()
    )

    # checked before any row is added: a pair with more than one relationship
    # (one per pair and direction) or a patient listed as their own relative
    # could change: if this fires and should not stop the migration, decide which
    # relationship wins, or skip the pair
    relationships = defaultdict(set)
    for row in radar2_rows:
        pair = (row["patient_id"], row["related_patient_id"])
        relationships[pair].add(row["relationship"])
    unmappable = [
        f"patient {patient_id} -> patient {related_patient_id}: "
        + (
            "listed as their own relative"
            if patient_id == related_patient_id
            else "relationships " + ", ".join(str(code) for code in sorted(codes))
        )
        for (patient_id, related_patient_id), codes in relationships.items()
        if patient_id == related_patient_id or len(codes) > 1
    ]
    if unmappable:
        raise ValueError(
            f"{len(unmappable)} relatives in family_history_relatives cannot be "
            "copied to patient_relation:\n" + "\n".join(unmappable)
        )

    rows = [
        {
            "patient_id": row["patient_id"],
            "related_patient_id": row["related_patient_id"],
            # [D11] relation kept radar 2's relationship codes as ids (step 0)
            "relation_id": row["relationship"],
        }
        for row in radar2_rows
    ]

    patient_relations = [PatientRelation.model_validate(dict(row)) for row in rows]
    session.add_all(patient_relations)
    session.flush()

    # the flush gave each row its new id
    return {
        (patient_relation.patient_id, patient_relation.related_patient_id): (
            patient_relation.id
        )
        for patient_relation in patient_relations
    }


def copy_family_history_relation(
    session: Session,
    family_history_ids: dict[Any, int],
    patient_relation_ids: dict[tuple[int, int], int],
) -> None:
    radar2_rows = session.execute(
        text("""
        SELECT
            family_history_relatives.id,
            family_history_relatives.family_history_id,
            family_history_relatives.relationship,
            family_histories.patient_id,
            family_history_relatives.patient_id AS related_patient_id
        FROM public.family_history_relatives
        JOIN public.family_histories
            ON family_histories.id = family_history_relatives.family_history_id
        ORDER BY family_history_relatives.id
    """)
    ).mappings()

    rows = [
        {
            "id": row["id"],
            # only true family_histories were copied, and in radar 2's data only
            # those list relatives, so each UUID here has a new id
            # could change: a relative of a false or NULL family_history would
            # have no new id, and this lookup would stop the migration
            # (KeyError); skip those relatives here if that ever happens
            "family_history_id": family_history_ids[row["family_history_id"]],
            # [D11] relation kept radar 2's relationship codes as ids (step 0)
            # could change: if relation gets new ids, look them up by label
            "relation_id": row["relationship"],
            # a relative who is a patient on Radar: the patient_relation copied
            # for this patient and relative, which has the same relation_id
            "patient_relation_id": (
                patient_relation_ids[(row["patient_id"], row["related_patient_id"])]
                if row["related_patient_id"] is not None
                else None
            ),
        }
        for row in radar2_rows
    ]

    session.add_all([FamilyHistoryRelation.model_validate(dict(row)) for row in rows])
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
            patient_relation_ids = copy_patient_relation(session)
            copy_family_history_relation(
                session, family_history_ids, patient_relation_ids
            )
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")