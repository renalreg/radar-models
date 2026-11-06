"""radar 2 -> radar 3: form entries (jsonb) -> one table per form

radar 2 stores every form as JSON: public.forms holds each form's definition
(forms.data["fields"]) and public.entries holds what was entered (entries.data).
radar 3 has a table per form. This step:

    1. read_forms           reads every radar 2 form definition
    2. check_forms_mapped   every form slug must be in FORMS or TODO_FORMS
    3. check_form_fields    each mapped form's field list must be the one its
                            mapping expects
    4. warn_todo_forms      logs the forms not migrated yet, with entry counts
    5. create_form_tables   creates the empty radar 3 form tables in radar3
    6. seed_form            for each mapped form: reads its entries, builds each
                            row with its <form>_row function, validates every row
                            against the model, and adds them with the session

Each <form>_row function is the explicit field-by-field mapping from that form's
JSON keys to its model's fields. TODO comments there mark form fields with no
column (not migrated), columns with no form field, and values whose type does
not fit the column.

Any entry that does not fit its model stops the migration, with every failing
entry from every form listed, so nothing is half-copied.

Needs radar3.patient to exist (the form tables point at it) and assumes radar 3
kept radar 2's patient ids.

One-way migration.

Revision ID: ed7869920413
Revises: 9aaa2a094682
Create Date: 2026-11-05 17:20:30.173960

"""

import logging
from collections.abc import Callable, Sequence
from typing import NamedTuple

from alembic import op
from pydantic import ValidationError
from sqlalchemy import text
from sqlmodel import Session, SQLModel

from radar_models.radar3 import (
    EQ5DY,
    HADS,
    IPOS,
    PAM,
    AdultEQ5D5L,
    AdultEQ5D5LBase,
    AdverseEvent,
    AdverseEventBase,
    Anthropometric,
    AnthropometricBase,
    CalciphylaxisAssessment,
    CalciphylaxisAssessmentBase,
    CancerTumour,
    CancerTumourBase,
    CKDAfricaGenetic,
    CKDAfricaGeneticBase,
    CKDAfricaRiskFactor,
    CKDAfricaRiskFactorBase,
    ClinicalLetter,
    ClinicalLetterBase,
    CystinosisAdultVisit,
    CystinosisAdultVisitBase,
    CystinosisPaedVisit,
    CystinosisPaedVisitBase,
    DentAndLoweAssessment,
    DentAndLoweAssessmentBase,
    DiabeticComplication,
    DiabeticComplicationBase,
    EQ5DYBase,
    EthnicOrigin,
    EthnicOriginBase,
    HADSBase,
    HSPAssessment,
    HSPAssessmentBase,
    IGAResearch,
    IGAResearchBase,
    IPOSBase,
    NurtureFamilyHistory,
    NurtureFamilyHistoryBase,
    NurtureVisit,
    NurtureVisitBase,
    PaedsCHU9D,
    PaedsCHU9DBase,
    PAMBase,
    Procedure,
    ProcedureBase,
    RenalCancerGenetics,
    RenalCancerGeneticsBase,
    RenalCancerTumour,
    RenalCancerTumourBase,
    RituximabFollowUpAssessment,
    RituximabFollowUpAssessmentBase,
    RituximabToxicity,
    RituximabToxicityBase,
    SampleInventory,
    SampleInventoryBase,
    SixCIT,
    SixCITBase,
    SocioEconomic,
    SocioEconomicBase,
    TubeSample,
    TubeSampleBase,
)

# revision identifiers, used by Alembic.
revision: str = "ed7869920413"
down_revision: str | Sequence[str] | None = "9aaa2a094682"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

log = logging.getLogger("alembic.runtime.migration")

# Each <form>_row function below builds the row with the model's Base class:
# the Base validates on creation (the table model does not) and its keyword
# arguments are the model's own fields. The table model is then built from it.


# --- 6cit -> six_cit --- #

SIX_CIT_FIELDS = {"date", "q1", "q2", "q4", "q5", "q6", "q7", "score"}


def six_cit_row(patient_id: int, data: dict) -> SixCIT:
    six_cit = SixCITBase(
        patient_id=patient_id,
        completed_date=data.get("date"),
        six_cit_q1_index=data.get("q1"),
        six_cit_q2_index=data.get("q2"),
        six_cit_q4_index=data.get("q4"),
        six_cit_q5_index=data.get("q5"),
        six_cit_q6_index=data.get("q6"),
        six_cit_q7_index=data.get("q7"),
        six_cit_score=data.get("score"),
    )
    return SixCIT.model_validate(six_cit)


# --- hads -> hads --- #

HADS_FIELDS = {
    "date",
    "a1", "d1", "a2", "d2", "a3", "d3", "a4", "d4",
    "a5", "d5", "a6", "d6", "a7", "d7",
    "anxietyScore", "depressionScore",
}  # fmt: skip


def hads_row(patient_id: int, data: dict) -> HADS:
    hads = HADSBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        a1_index=data.get("a1"),
        d1_index=data.get("d1"),
        a2_index=data.get("a2"),
        d2_index=data.get("d2"),
        a3_index=data.get("a3"),
        d3_index=data.get("d3"),
        a4_index=data.get("a4"),
        d4_index=data.get("d4"),
        a5_index=data.get("a5"),
        d5_index=data.get("d5"),
        a6_index=data.get("a6"),
        d6_index=data.get("d6"),
        a7_index=data.get("a7"),
        d7_index=data.get("d7"),
        anxiety_score=data.get("anxietyScore"),
        depression_score=data.get("depressionScore"),
    )
    return HADS.model_validate(hads)


# --- diabetic-complications -> diabetic_complication --- #

DIABETIC_COMPLICATION_FIELDS = {
    "retinopathy",
    "laser",
    "peripheralNeuropathy",
    "footUlcers",
}


def diabetic_complication_row(patient_id: int, data: dict) -> DiabeticComplication:
    diabetic_complication = DiabeticComplicationBase(
        patient_id=patient_id,
        retinopathy_index=data.get("retinopathy"),
        has_laser_treatment=data.get("laser"),
        has_peripheral_neuropathy=data.get("peripheralNeuropathy"),
        has_foot_ulcer=data.get("footUlcers"),
    )
    return DiabeticComplication.model_validate(diabetic_complication)


# --- pam -> pam --- #

PAM_FIELDS = {
    "date",
    "q1", "q2", "q3", "q4", "q5", "q6", "q7",
    "q8", "q9", "q10", "q11", "q12", "q13",
}  # fmt: skip


def pam_row(patient_id: int, data: dict) -> PAM:
    pam = PAMBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        pam_q1_index=data.get("q1"),
        pam_q2_index=data.get("q2"),
        pam_q3_index=data.get("q3"),
        pam_q4_index=data.get("q4"),
        pam_q5_index=data.get("q5"),
        pam_q6_index=data.get("q6"),
        pam_q7_index=data.get("q7"),
        pam_q8_index=data.get("q8"),
        pam_q9_index=data.get("q9"),
        pam_q10_index=data.get("q10"),
        pam_q11_index=data.get("q11"),
        pam_q12_index=data.get("q12"),
        pam_q13_index=data.get("q13"),
    )
    return PAM.model_validate(pam)


# --- chu9d -> paeds_chu9d --- #

PAEDS_CHU9D_FIELDS = {
    "date",
    "worried", "sad", "pain", "tired", "annoyed",
    "work", "sleep", "routine", "activities",
}  # fmt: skip


def paeds_chu9d_row(patient_id: int, data: dict) -> PaedsCHU9D:
    paeds_chu9d = PaedsCHU9DBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        worried_index=data.get("worried"),
        sad_index=data.get("sad"),
        pain_index=data.get("pain"),
        tired_index=data.get("tired"),
        annoyed_index=data.get("annoyed"),
        school_index=data.get("work"),
        sleep_index=data.get("sleep"),
        routine_index=data.get("routine"),
        activities_index=data.get("activities"),
    )
    return PaedsCHU9D.model_validate(paeds_chu9d)


# --- origin -> ethnic_origin --- #

ETHNIC_ORIGIN_FIELDS = {
    "date",
    "countryofbirthpatient",
    "patientyearuk",
    "ethnicoriginpatient",
    "ethnicoriginmother",
    "ethnicoriginfather",
}


def ethnic_origin_row(patient_id: int, data: dict) -> EthnicOrigin:
    def to_int(value):
        """Return value as an int, or None if it can't be converted."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    ethnic_origin = EthnicOrigin(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        country_of_birth=to_int(data.get("countryofbirth")),
        year_of_emigration=to_int(data.get("patientyearuk")),
        ethnic_origin=to_int(data.get("ethnicorigin")),
        ethnic_origin_father=to_int(data.get("ethnicoriginfather")),
        ethnic_origin_mother=to_int(data.get("ethnicoriginmother")),
    )
    return EthnicOrigin.model_validate(ethnic_origin)


# --- family-history -> nurture_family_history --- #

NURTURE_FAMILY_HISTORY_FIELDS = {
    "eskd", "eskdRelative1", "eskdRelative2", "eskdRelative3",
    "chd", "chdRelative1", "chdRelative2", "chdRelative3",
    "diabetes", "diabetesRelative1", "diabetesRelative2", "diabetesRelative3",
}  # fmt: skip


def nurture_family_history_row(patient_id: int, data: dict) -> NurtureFamilyHistory:
    nurture_family_history = NurtureFamilyHistoryBase(
        patient_id=patient_id,
        has_eskd=data.get("eskd"),
        eskd_relative_1_index=data.get("eskdRelative1"),
        eskd_relative_2_index=data.get("eskdRelative2"),
        eskd_relative_3_index=data.get("eskdRelative3"),
        has_chd=data.get("chd"),
        chd_relative_1_index=data.get("chdRelative1"),
        chd_relative_2_index=data.get("chdRelative2"),
        chd_relative_3_index=data.get("chdRelative3"),
        has_diabetes=data.get("diabetes"),
        diabetes_relative_1_index=data.get("diabetesRelative1"),
        diabetes_relative_2_index=data.get("diabetesRelative2"),
        diabetes_relative_3_index=data.get("diabetesRelative3"),
    )
    return NurtureFamilyHistory.model_validate(nurture_family_history)


# --- ddls -> dent_and_lowe_assessment --- #

DENT_AND_LOWE_FIELDS = {
    "date",
    "aetiology",
    "agent",
    "otherAgent",
    "extraInvolvement",
    "otherExtraInvolvement",
}


def dent_and_lowe_row(patient_id: int, data: dict) -> DentAndLoweAssessment:
    dent_and_lowe = DentAndLoweAssessmentBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        aetiology=data.get("aetiology"),
        causative_agent=data.get("agent"),
        other_agent=data.get("otherAgent"),
        # TODO extraInvolvement is a multi-select array; it belongs in
        # dent_and_lowe_assessment_option rows, so a list will not fit this str
        extra_involvement=data.get("extraInvolvement"),
        other_extra_involvement=data.get("otherExtraInvolvement"),
    )
    return DentAndLoweAssessment.model_validate(dent_and_lowe)


# --- calciphylaxis -> calciphylaxis_assessment --- #

CALCIPHYLAXIS_FIELDS = {"date", "lesion", "lesionIn", "infection", "infectionIn"}


def calciphylaxis_row(patient_id: int, data: dict) -> CalciphylaxisAssessment:
    calciphylaxis = CalciphylaxisAssessmentBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        has_lesion=data.get("lesion"),
        # TODO lesionIn is a multi-select array; it belongs in
        # calciphylaxis_assessment_option rows, so a list will not fit this str
        lesion_location=data.get("lesionIn"),
        has_infection=data.get("infection"),
        # TODO infectionIn: multi-select array, as above
        infection_location=data.get("infectionIn"),
    )
    return CalciphylaxisAssessment.model_validate(calciphylaxis)


# --- eq-5d-y -> eq5dy --- #

EQ5DY_FIELDS = {
    "date",
    "age",
    "gender",
    "mobility",
    "selfCare",
    "usualActivities",
    "painDiscomfort",
    "anxietyDepression",
    "health",
}


def eq5dy_row(patient_id: int, data: dict) -> EQ5DY:
    # TODO not migrated: date (EQ5DY has no assessment_date column, AdultEQ5D5L does)
    eq5dy = EQ5DYBase(
        patient_id=patient_id,
        age=data.get("age"),
        gender_index=data.get("gender"),
        mobility_index=data.get("mobility"),
        self_care_index=data.get("selfCare"),
        usual_activities_index=data.get("usualActivities"),
        pain_discomfort_index=data.get("painDiscomfort"),
        anxiety_depression_index=data.get("anxietyDepression"),
        health=data.get("health"),
    )
    return EQ5DY.model_validate(eq5dy)


# --- eq-5d-5l -> adult_eq5d5l --- #

ADULT_EQ5D5L_FIELDS = {
    "date",
    "age",
    "gender",
    "mobility",
    "selfCare",
    "usualActivities",
    "painDiscomfort",
    "anxietyDepression",
    "health",
}


def adult_eq5d5l_row(patient_id: int, data: dict) -> AdultEQ5D5L:
    adult_eq5d5l = AdultEQ5D5LBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        age=data.get("age"),
        gender_index=data.get("gender"),
        mobility_index=data.get("mobility"),
        self_care_index=data.get("selfCare"),
        usual_activities_index=data.get("usualActivities"),
        pain_discomfort_index=data.get("painDiscomfort"),
        anxiety_depression_index=data.get("anxietyDepression"),
        health=data.get("health"),
    )
    return AdultEQ5D5L.model_validate(adult_eq5d5l)


# --- socio-economic -> socioeconomic --- #

SOCIO_ECONOMIC_FIELDS = {
    "date", "education", "employmentStatus", "firstLanguage", "maritalStatus",
    "smoking", "cigarettesPerDay", "alcohol",
    "beerPints", "ciderPints", "redWine", "whiteWine", "spirits", "cocktails",
    "unitsPerWeek", "literacy", "literacyHelp", "diet", "otherDiet",
}  # fmt: skip


def socio_economic_row(patient_id: int, data: dict) -> SocioEconomic:
    socio_economic = SocioEconomicBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        education_index=data.get("education"),
        employment_status_index=data.get("employmentStatus"),
        first_language=data.get("firstLanguage"),
        martial_status=data.get("maritalStatus"),
        smoking_index=data.get("smoking"),
        cigarettes_per_day=data.get("cigarettesPerDay"),
        has_alcohol_intake=data.get("alcohol"),
        beer_pints=data.get("beerPints"),
        cider_pints=data.get("ciderPints"),
        red_wine=data.get("redWine"),
        white_wine=data.get("whiteWine"),
        spirits=data.get("spirits"),
        cocktails=data.get("cocktails"),
        units_per_week=data.get("unitsPerWeek"),
        literacy_index=data.get("literacy"),
        # TODO literacyHelp is an int option (1 = Never ... 5 = Always) but the
        # column is str; should it be literacy_help_index: int?
        literacy_help=data.get("literacyHelp"),
        diet_index=data.get("diet"),
        other_diet=data.get("otherDiet"),
    )
    return SocioEconomic.model_validate(socio_economic)


# --- ipos -> ipos --- #

IPOS_FIELDS = {
    "date",
    "score1", "score2", "score3", "score4", "score5", "score6", "score7",
    "score8", "score9", "score10", "score11", "score12", "score13", "score14",
    "score15", "score16", "score17",
    "question1", "score18", "question2", "score19", "question3", "score20",
    "question4", "question5", "score",
}  # fmt: skip


def ipos_row(patient_id: int, data: dict) -> IPOS:
    ipos = IPOSBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        score_1_index=data.get("score1"),
        score_2_index=data.get("score2"),
        score_3_index=data.get("score3"),
        score_4_index=data.get("score4"),
        score_5_index=data.get("score5"),
        score_6_index=data.get("score6"),
        score_7_index=data.get("score7"),
        score_8_index=data.get("score8"),
        score_9_index=data.get("score9"),
        score_10_index=data.get("score10"),
        score_11_index=data.get("score11"),
        score_12_index=data.get("score12"),
        score_13_index=data.get("score13"),
        score_14_index=data.get("score14"),
        score_15_index=data.get("score15"),
        score_16_index=data.get("score16"),
        score_17_index=data.get("score17"),
        question_1=data.get("question1"),
        score_18_index=data.get("score18"),
        question_2=data.get("question2"),
        score_19_index=data.get("score19"),
        question_3=data.get("question3"),
        score_20_index=data.get("score20"),
        # TODO question4 and question5 are int options (0 = No Answer, 1 = Pain,
        # ...) but the columns are str; should they be question_4_index: int?
        question_4=data.get("question4"),
        question_5=data.get("question5"),
        ipos_score=data.get("score"),
    )
    return IPOS.model_validate(ipos)


# --- rituximab-administration -> rituximab_toxicity --- #

RITUXIMAB_TOXICITY_FIELDS = {
    "date",
    "drugName",
    "otherDrug",
    "dose",
    "retreatment",
    "toxicity",
    "otherToxicity",
}


def rituximab_toxicity_row(patient_id: int, data: dict) -> RituximabToxicity:
    rituximab_toxicity = RituximabToxicityBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        drug_name=data.get("drugName"),
        other_drug=data.get("otherDrug"),
        dose=data.get("dose"),
        retreatment=data.get("retreatment"),
        # TODO toxicity is a multi-select array; it belongs in
        # rituximab_toxicity_option rows, so a list will not fit this str
        toxicity=data.get("toxicity"),
        other_toxicity=data.get("otherToxicity"),
    )
    return RituximabToxicity.model_validate(rituximab_toxicity)


# --- specgenetics -> ckd_africa_genetic --- #

CKD_AFRICA_GENETIC_FIELDS = {"date", "sickle", "sickleother", "apol"}


def ckd_africa_genetic_row(patient_id: int, data: dict) -> CKDAfricaGenetic:
    ckd_africa_genetic = CKDAfricaGeneticBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        sickle_cell=data.get("sickle"),
        other_sickle_cell=data.get("sickleother"),
        apol_1=data.get("apol"),
    )
    return CKDAfricaGenetic.model_validate(ckd_africa_genetic)


# --- rituximab-assessment -> rituximab_follow_up_assessment --- #

RITUXIMAB_FOLLOW_UP_FIELDS = {
    "date", "visit", "performance",
    "transplant", "haemodialysis", "peritonealDialysis", "medication",
    "immunos",
    "immunosCicl", "ciclDate", "immunosTacr", "TacrDate",
    "immunosCyclo", "cycloDate", "immunosChlor", "chlorDate",
    "immunosPred", "predDate", "immunosRitux", "rituxDate",
    "rituxRetreat", "immunosComment",
}  # fmt: skip


def rituximab_follow_up_row(patient_id: int, data: dict) -> RituximabFollowUpAssessment:
    # TODO not migrated: medication, immunosCicl, immunosTacr, immunosCyclo,
    # immunosChlor, immunosPred, immunosRitux (multi-select arrays; they belong
    # in rituximab_follow_up_assessment_option rows) and rituxRetreat (no column)
    rituximab_follow_up = RituximabFollowUpAssessmentBase(
        patient_id=patient_id,
        visit_date=data.get("date"),
        rituximab_follow_up_visit=data.get("visit"),
        # TODO performance is an int option (0-4) but the column is str
        performance=data.get("performance"),
        # TODO transplant, haemodialysis, peritonealDialysis and immunos are
        # True/False in the form but the columns are str; should they be bool?
        transplant=data.get("transplant"),
        haemodialysis=data.get("haemodialysis"),
        peritoneal_dialysis=data.get("peritonealDialysis"),
        immunosuppression=data.get("immunos"),
        # TODO the *_administered dates are only filled when that drug was
        # given, but the columns are required
        ciclosporin_administered=data.get("ciclDate"),
        tacrolimus_administered=data.get("TacrDate"),
        cyclophosphamide_administered=data.get("cycloDate"),
        chlorambucil_administered=data.get("chlorDate"),
        prednisolone_administered=data.get("predDate"),
        rituximab_administered=data.get("rituxDate"),
        # TODO immunosComment is an array in the form but the column is str
        immunosuppression_comments=data.get("immunosComment"),
    )
    return RituximabFollowUpAssessment.model_validate(rituximab_follow_up)


# --- igan-inventory -> sample_inventory --- #

SAMPLE_INVENTORY_FIELDS = {
    "date",
    "urine", "urineDate", "urineVolume",
    "serum", "serumDate", "serumVolume",
    "plasma", "plasmaDate", "plasmaVolume",
    "dna", "dnaDate",
    "sputum", "sputumDate",
    "faeces", "faecesDate",
}  # fmt: skip


def sample_inventory_row(patient_id: int, data: dict) -> SampleInventory:
    sample_inventory = SampleInventoryBase(
        patient_id=patient_id,
        sample_date=data.get("date"),
        has_urine_sample=data.get("urine"),
        urine_date=data.get("urineDate"),
        urine_volume=data.get("urineVolume"),
        has_serum_sample=data.get("serum"),
        serum_date=data.get("serumDate"),
        serum_volume=data.get("serumVolume"),
        has_plasma_sample=data.get("plasma"),
        plasma_date=data.get("plasmaDate"),
        plasma_volume=data.get("plasmaVolume"),
        has_dna_sample=data.get("dna"),
        dna_date=data.get("dnaDate"),
        has_sputum_sample=data.get("sputum"),
        sputum_date=data.get("sputumDate"),
        has_faeces_sample=data.get("faeces"),
        faeces_date=data.get("faecesDate"),
    )
    return SampleInventory.model_validate(sample_inventory)


# --- anthropometrics -> anthropometric --- #

ANTHROPOMETRIC_FIELDS = {
    "date", "height", "weight", "bmi", "hip", "waist", "arm", "up",
    "gripDominant", "gripNonDominant", "karnofsky",
    "systolic1", "diastolic1", "systolic2", "diastolic2", "systolic3", "diastolic3",
    "systolic", "diastolic",
}  # fmt: skip


def anthropometric_row(patient_id: int, data: dict) -> Anthropometric:
    anthropometric = AnthropometricBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        height=data.get("height"),
        weight=data.get("weight"),
        bmi=data.get("bmi"),
        hip=data.get("hip"),
        waist=data.get("waist"),
        arm=data.get("arm"),
        up_and_go=data.get("up"),
        grip_dominant=data.get("gripDominant"),
        grip_non_dominant=data.get("gripNonDominant"),
        karnofsky_index=data.get("karnofsky"),
        systolic_one=data.get("systolic1"),
        diastolic_one=data.get("diastolic1"),
        systolic_two=data.get("systolic2"),
        diastolic_two=data.get("diastolic2"),
        systolic_three=data.get("systolic3"),
        diastolic_three=data.get("diastolic3"),
        systolic_mean=data.get("systolic"),
        diastolic_mean=data.get("diastolic"),
    )
    return Anthropometric.model_validate(anthropometric)


# --- igan-research -> iga_research --- #

IGA_RESEARCH_FIELDS = {"date", "registeredOn"}


def iga_research_row(patient_id: int, data: dict) -> IGAResearch:
    # TODO not migrated: registeredOn (multi-select array; it belongs in
    # iga_research_option rows)
    iga_research = IGAResearchBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
    )
    return IGAResearch.model_validate(iga_research)


# --- rituximab-adverse-events -> adverse_event --- #

ADVERSE_EVENT_FIELDS = {
    "date", "hospitalisation", "adverseEvents",
    "newOnsetCancer", "causedCancer",
    "thromboembolism", "causedVenousThromboEmbolism",
    "myocardialInfarction", "causedAcuteMyocardialInfarction",
    "stroke", "causedStroke",
    "ischaemicAttack", "causedIschaemicAttack",
    "otherAdverseEvent", "otherTox", "causedOther",
    "dod", "dodCause",
}  # fmt: skip


def adverse_event_row(patient_id: int, data: dict) -> AdverseEvent:
    # TODO the event dates (newOnsetCancer, thromboembolism, ..., dod) are only
    # filled when that event happened, but the columns are required
    adverse_event = AdverseEventBase(
        patient_id=patient_id,
        review_date=data.get("date"),
        has_hospitalisation=data.get("hospitalisation"),  # "yes"/"no" -> bool
        has_adverse_event=data.get("adverseEvents"),  # "yes"/"no" -> bool
        new_onset_cancer=data.get("newOnsetCancer"),
        # TODO causedCancer is "yes"/"no"/"Unknown"; "Unknown" will not fit bool
        is_cancer_cause=data.get("causedCancer"),
        thromboembolism=data.get("thromboembolism"),
        # TODO the caused* answers are "yes"/"no"/"Unknown" but the *_index
        # columns are int; decide the codes, or make them str
        caused_venous_thrombo_embolism_index=data.get("causedVenousThromboEmbolism"),
        myocardial_infarction=data.get("myocardialInfarction"),
        caused_acute_myocardial_infarction_index=data.get(
            "causedAcuteMyocardialInfarction"
        ),
        stroke=data.get("stroke"),
        caused_stroke_index=data.get("causedStroke"),
        ischaemic_attack=data.get("ischaemicAttack"),
        caused_ischaemic_attack_index=data.get("causedIschaemicAttack"),
        other_adverse_event=data.get("otherAdverseEvent"),
        # TODO otherTox is an array in the form but the column is str
        other_toxicity=data.get("otherTox"),
        caused_other_index=data.get("causedOther"),
        date_of_death=data.get("dod"),
        cause_of_death=data.get("dodCause"),
    )
    return AdverseEvent.model_validate(adverse_event)


# --- nurtureckd -> nurture_visit --- #

NURTURE_VISIT_FIELDS = {
    "date", "visit", "comorbities", "vaccinationFlu", "vaccinationPneumonia",
    "admission", "admissionNumber", "admissionEmergency", "admissionPlanned",
    "admissionDays", "admissionAntibiotics",
    "medicine1", "tabletsParacetamol", "yearsParacetamol",
    "medicine2", "tabletsCocodamol", "yearsCocodamol",
    "medicine3", "tabletsIbuprofen", "yearsIbuprofen",
}  # fmt: skip


def nurture_visit_row(patient_id: int, data: dict) -> NurtureVisit:
    # TODO not migrated: medicine1, medicine2, medicine3 (each has a single option,
    # paracetamol / cocodamol / ibuprofen, already implied by the columns below)
    nurture_visit = NurtureVisitBase(
        patient_id=patient_id,
        visit_date=data.get("date"),
        nurture_visit_number=data.get("visit"),
        comorbidities=data.get("comorbities"),
        has_flu_vaccination=data.get("vaccinationFlu"),
        has_pneumococcal_vaccination=data.get("vaccinationPneumonia"),
        has_admission=data.get("admission"),
        admission_number=data.get("admissionNumber"),
        admission_emergency=data.get("admissionEmergency"),
        admission_planned=data.get("admissionPlanned"),
        admission_days=data.get("admissionDays"),
        admission_antibiotics=data.get("admissionAntibiotics"),
        paracetamol_tablets=data.get("tabletsParacetamol"),
        paracetamol_years=data.get("yearsParacetamol"),
        cocodamol_tablets=data.get("tabletsCocodamol"),
        cocodamol_years=data.get("yearsCocodamol"),
        ibuprofen_tablets=data.get("tabletsIbuprofen"),
        ibuprofen_years=data.get("yearsIbuprofen"),
    )
    return NurtureVisit.model_validate(nurture_visit)


# --- samples -> tube_sample --- #

TUBE_SAMPLE_FIELDS = {"date", "barcode", "insstate"}


def tube_sample_row(patient_id: int, data: dict) -> TubeSample:
    tube_sample = TubeSampleBase(
        patient_id=patient_id,
        sample_date=data.get("date"),
        barcode=data.get("barcode"),
        ins_state_index=data.get("insstate"),
    )
    return TubeSample.model_validate(tube_sample)


# --- renaltumour -> renal_cancer_tumour --- #

RENAL_CANCER_TUMOUR_FIELDS = {
    "tumourtype",
    "date",
    "cnsimaging",
    "progone",
    "cnsimaging2",  # appears twice in the form: once for T, once for N
    "cnsimaging3",
    "rtsize",
    "ptsize",
    "tloc",
}


def renal_cancer_tumour_row(patient_id: int, data: dict) -> RenalCancerTumour:
    # TODO the form names both its T and N category fields "cnsimaging2", so each
    # entry holds only one of them and the other is lost in radar 2. The option
    # values were also copied from cnsimaging ("mri" = Ta/N0/M0, "ct" = T0/N1/M1,
    # ... and "other" = T2, T3, T4 or Tx), so the stored values need decoding,
    # and "other" cannot be decoded.
    renal_cancer_tumour = RenalCancerTumourBase(
        patient_id=patient_id,
        tumor_type=data.get("tumourtype"),
        assessment_date=data.get("date"),
        cns_imaging_method=data.get("cnsimaging"),
        progression_date=data.get("progone"),  # free text: only ISO dates fit
        t_cat=None,  # TODO lost: see above
        n_cat=data.get("cnsimaging2"),  # TODO T or N: see above
        m_cat=data.get("cnsimaging3"),
        rt_size=data.get("rtsize"),
        pt_size=data.get("ptsize"),
        t_loc=data.get("tloc"),
    )
    return RenalCancerTumour.model_validate(renal_cancer_tumour)


# --- riskckd -> ckd_africa_risk_factor --- #

CKD_AFRICA_RISK_FACTOR_FIELDS = {
    "date",
    "histpretermbirth",
    "histlowbirthweight",
    "histmalnutrition",
    "histhospitalmalnutrition",
}


def ckd_africa_risk_factor_row(patient_id: int, data: dict) -> CKDAfricaRiskFactor:
    ckd_africa_risk_factor = CKDAfricaRiskFactorBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        preterm_birth=data.get("histpretermbirth"),
        low_birth_weight=data.get("histlowbirthweight"),
        malnutrition=data.get("histmalnutrition"),
        hospital_malnutrition=data.get("histhospitalmalnutrition"),
    )
    return CKDAfricaRiskFactor.model_validate(ckd_africa_risk_factor)


# --- paedcyst -> cystinosis_paed_visit --- #

CYSTINOSIS_PAED_VISIT_FIELDS = {
    "visit", "date", "height", "weight",
    "urinemeasurement", "urineoutput", "voidingovernight", "continentday",
    "fluidintake", "admdehydrate",
    "constipation", "diarrhoea", "nausea", "vomiting",
    "failuretothrive", "enteralfeeding",
    "feedingstartdate1", "feedingendtdate1",
    "feedingstartdate2", "feedingendtdate2",
    "feedingstartdate3", "feedingendtdate3",
    "usedtoadminister", "normalfoodorally", "supplements", "growthhormonetreatment",
    "rickets", "kyphoscoliosis", "fractures", "jointsurgery", "musclestrength",
    "swallowing difficulty", "nosesnoring", "tonsilectomydate", "adenoidectomydate",
    "sightimpair", "severesightimpair", "photophobia", "photophobiagrading",
    "kdate", "acuity", "gahl", "intrar", "intral", "fev", "vc", "snip",
    "seizures", "headaches", "muscleweakness", "learningdifficulties",
    "cognitivedefect", "movementdisorder", "intracranialhypertension",
    "diabetes", "thyroidstate", "hyperparathyroidism", "tannerstage",
    "wccystine", "wccystinedate", "wccystinetime", "cystlastdosehrs",
    "cystsideeffects",
}  # fmt: skip


def cystinosis_paed_visit_row(patient_id: int, data: dict) -> CystinosisPaedVisit:
    # TODO not migrated: usedtoadminister (multi-select array; it belongs in
    # cystinosis_paed_visit_option rows) and adenoidectomydate (no column)
    cystinosis_paed_visit = CystinosisPaedVisitBase(
        patient_id=patient_id,
        cystinosis_paed_visit_number=data.get("visit"),
        visit_date=data.get("date"),
        height=data.get("height"),
        weight=data.get("weight"),
        urine_measurement=data.get("urinemeasurement"),
        urine_output=data.get("urineoutput"),
        voiding_overnight=data.get("voidingovernight"),
        continence_day=data.get("continentday"),
        fluid_intake=data.get("fluidintake"),
        # TODO admdehydrate is a float in the form but the column is int
        admission_dehydration=data.get("admdehydrate"),
        constipation=data.get("constipation"),
        diarrhea=data.get("diarrhoea"),
        nausea=data.get("nausea"),
        vomiting=data.get("vomiting"),
        failure_to_thrive=data.get("failuretothrive"),
        enteral_feeding=data.get("enteralfeeding"),
        feeding_start_date_1=data.get("feedingstartdate1"),
        feeding_end_date_1=data.get("feedingendtdate1"),
        feeding_start_date_2=data.get("feedingstartdate2"),
        feeding_end_date_2=data.get("feedingendtdate2"),
        feeding_start_date_3=data.get("feedingstartdate3"),
        feeding_end_date_3=data.get("feedingendtdate3"),
        normal_food_orally=data.get("normalfoodorally"),
        supplements=data.get("supplements"),
        growth_hormone_treatment=data.get("growthhormonetreatment"),
        rickets=data.get("rickets"),
        kyphoscoliosis=data.get("kyphoscoliosis"),
        fractures=data.get("fractures"),
        joint_surgery=data.get("jointsurgery"),
        muscle_strength=data.get("musclestrength"),
        swallowing_difficulties=data.get("swallowing difficulty"),
        nose_snoring=data.get("nosesnoring"),
        tonsillectomy_date=data.get("tonsilectomydate"),
        sight_impairment=data.get("sightimpair"),
        severe_sight_impairment=data.get("severesightimpair"),
        photophobia=data.get("photophobia"),
        photophobia_grade=data.get("photophobiagrading"),
        keratoplasty_date=data.get("kdate"),
        acuity=data.get("acuity"),
        gahl_score=data.get("gahl"),
        # TODO intrar and intral are floats in this form (strings in the adult
        # form) but the columns are str
        intraocular_pressure_r=data.get("intrar"),
        intraocular_pressure_l=data.get("intral"),
        fev1=data.get("fev"),
        vc=data.get("vc"),
        snip=data.get("snip"),
        seizure=data.get("seizures"),
        headache=data.get("headaches"),
        muscle_weakness=data.get("muscleweakness"),
        learning_difficulties=data.get("learningdifficulties"),
        cognitive_difficulties=data.get("cognitivedefect"),
        movement_disorder=data.get("movementdisorder"),
        intracranial_hypertension=data.get("intracranialhypertension"),
        diabetes=data.get("diabetes"),
        thyroid=data.get("thyroidstate"),
        # TODO the form field is hyperparathyroidism; check this column should
        # not be named hyperparathyroidism too
        hypothyroidism=data.get("hyperparathyroidism"),
        tanner_stage=data.get("tannerstage"),
        wc_cystine=data.get("wccystine"),
        wc_cystine_date=data.get("wccystinedate"),
        wc_cystine_time=data.get("wccystinetime"),
        cysteamine_last_dose=data.get(
            "cystlastdosehrs"
        ),  # free text: only "12"-style fits
        cysteamine_effects=data.get("cystsideeffects"),
    )
    return CystinosisPaedVisit.model_validate(cystinosis_paed_visit)


# --- cystadult -> cystinosis_adult_visit --- #

CYSTINOSIS_ADULT_VISIT_FIELDS = {
    "visit", "date",
    "urinemeasurement", "urineoutput", "voidingovernight", "continentday",
    "fluidintake", "admdehydrate",
    "constipation", "diarrhoea", "nausea", "vomiting",
    "rickets", "kyphoscoliosis", "fractures", "musclestrength",
    "musclestrengthankle", "musclestrengthelbow", "musclestrengthhand",
    "musclestrengthhip", "musclestrengthknee", "musclestrengthshoulder",
    "musclestrengthwrist",
    "swallowingdifficulty", "swallowingdifficultydetail", "jointsurgery",
    "visualimpair", "photophobia", "photophobiagrading",
    "kdate", "acuity", "gahl", "intrar", "intral", "fev", "vc", "snip",
    "seizures", "headaches", "muscleweakness", "learningdifficulties",
    "cognitivedefect", "cognitivedefectmmsescore", "movementdisorder",
    "intracranialhypertension", "diabetes", "thyroidstate", "hyperparathyroidism",
    "tannerstage", "wccystine", "wccystinedate", "wccystinetime",
    "cystlastdosehrs", "cystsideeffects",
}  # fmt: skip


def cystinosis_adult_visit_row(patient_id: int, data: dict) -> CystinosisAdultVisit:
    cystinosis_adult_visit = CystinosisAdultVisitBase(
        patient_id=patient_id,
        cystinosis_adult_visit_number=data.get("visit"),
        visit_date=data.get("date"),
        urine_measurement=data.get("urinemeasurement"),
        urine_output=data.get("urineoutput"),
        voiding_overnight=data.get("voidingovernight"),
        continent_day=data.get("continentday"),
        fluid_intake=data.get("fluidintake"),
        # TODO admdehydrate is a float in the form but the column is int
        admission_dehydration=data.get("admdehydrate"),
        constipation=data.get("constipation"),
        diarrhea=data.get("diarrhoea"),
        nausea=data.get("nausea"),
        vomiting=data.get("vomiting"),
        rickets=data.get("rickets"),
        kyphoscoliosis=data.get("kyphoscoliosis"),
        fractures=data.get("fractures"),
        muscle_strength=data.get("musclestrength"),
        ankle_strength=data.get("musclestrengthankle"),
        elbow_strength=data.get("musclestrengthelbow"),
        hand_strength=data.get("musclestrengthhand"),
        hip_strength=data.get("musclestrengthhip"),
        knee_strength=data.get("musclestrengthknee"),
        shoulder_strength=data.get("musclestrengthshoulder"),
        wrist_strength=data.get("musclestrengthwrist"),
        swallowing_difficulties=data.get("swallowingdifficulty"),
        swallowing_difficulties_detail=data.get("swallowingdifficultydetail"),
        joint_surgery=data.get("jointsurgery"),
        visual_impairment=data.get("visualimpair"),
        photophobia=data.get("photophobia"),
        photophobia_grade=data.get("photophobiagrading"),
        keratoplasty_date=data.get("kdate"),
        acuity=data.get("acuity"),
        gahl_score=data.get("gahl"),
        intraocular_pressure_r=data.get("intrar"),
        intraocular_pressure_l=data.get("intral"),
        fev1=data.get("fev"),
        vc=data.get("vc"),
        snip=data.get("snip"),
        seizure=data.get("seizures"),
        headache=data.get("headaches"),
        muscle_weakness=data.get("muscleweakness"),
        learning_difficulties=data.get("learningdifficulties"),
        cognitive_difficulties=data.get("cognitivedefect"),
        cognitive_difficulties_score=data.get("cognitivedefectmmsescore"),
        movement_disorder=data.get("movementdisorder"),
        intracranial_hypertension=data.get("intracranialhypertension"),
        diabetes=data.get("diabetes"),
        thyroid=data.get("thyroidstate"),
        # TODO the form field is hyperparathyroidism; check this column should
        # not be named hyperparathyroidism too
        hypothyroidism=data.get("hyperparathyroidism"),
        tanner_stage=data.get("tannerstage"),
        wc_cystine=data.get("wccystine"),
        wc_cystine_date=data.get("wccystinedate"),
        wc_cystine_time=data.get("wccystinetime"),
        cysteamine_last_dose=data.get(
            "cystlastdosehrs"
        ),  # free text: only "12"-style fits
        cysteamine_effects=data.get("cystsideeffects"),
    )
    return CystinosisAdultVisit.model_validate(cystinosis_adult_visit)


# --- renalgenetics -> renal_cancer_genetics --- #

RENAL_CANCER_GENETICS_FIELDS = {
    "date",
    "bap1test", "bap1action", "bap1variant", "bap1variantstatus",
    "fhtest", "fhaction", "fhvariant", "fhvariantstatus",
    "flcntest", "flcnaction", "flcnvariant", "flcnvariantstatus",
    "mettest", "metaction", "metvariant", "metvariantstatus",
    "mitftest", "mitfaction", "mitfvariant", "mitfvariantstatus",
    "ptentest", "ptenaction", "ptenvariant", "ptenvariantstatus",
    "sdhatest", "sdhaaction", "sdhavariant", "sdhavariantstatus",
    "sdhbtest", "sdhbaction", "sdhbvariant", "sdhbvariantstatus",
    "sdhctest", "sdhcaction", "sdhcvariant", "sdhcvariantstatus",
    "sdhdtest", "sdhdaction", "sdhdvariant", "sdhdvariantstatus",
    "vhltest", "vhlaction", "vhlvariant", "vhlvariantstatus",
    "othertest", "othertestname", "otheraction", "othervariant", "othervariantstatus",
}  # fmt: skip


def renal_cancer_genetics_row(patient_id: int, data: dict) -> RenalCancerGenetics:
    # TODO not migrated: bap1action, fhaction, flcnaction, metaction, mitfaction,
    # ptenaction, sdhaaction, sdhbaction, sdhcaction, sdhdaction, vhlaction,
    # otheraction (multi-select arrays; they belong in
    # renal_cancer_genetics_option rows)
    renal_cancer_genetics = RenalCancerGeneticsBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        has_bap1_test=data.get("bap1test"),
        bap1_variant=data.get("bap1variant"),
        bap1_variant_status=data.get("bap1variantstatus"),
        has_fh_test=data.get("fhtest"),
        fh_variant=data.get("fhvariant"),
        fh_variant_status=data.get("fhvariantstatus"),
        has_flcn_test=data.get("flcntest"),
        flcn_variant=data.get("flcnvariant"),
        flcn_variant_status=data.get("flcnvariantstatus"),
        has_met_test=data.get("mettest"),
        met_variant=data.get("metvariant"),
        met_variant_status=data.get("metvariantstatus"),
        has_mitf_test=data.get("mitftest"),
        mitf_variant=data.get("mitfvariant"),
        mitf_variant_status=data.get("mitfvariantstatus"),
        has_pten_test=data.get("ptentest"),
        pten_variant=data.get("ptenvariant"),
        pten_variant_status=data.get("ptenvariantstatus"),
        has_sdha_test=data.get("sdhatest"),
        sdha_variant=data.get("sdhavariant"),
        sdha_variant_status=data.get("sdhavariantstatus"),
        has_sdhb_test=data.get("sdhbtest"),
        sdhb_variant=data.get("sdhbvariant"),
        sdhb_variant_status=data.get("sdhbvariantstatus"),
        has_sdhc_test=data.get("sdhctest"),
        sdhc_variant=data.get("sdhcvariant"),
        sdhc_variant_status=data.get("sdhcvariantstatus"),
        has_sdhd_test=data.get("sdhdtest"),
        sdhd_variant=data.get("sdhdvariant"),
        sdhd_variant_status=data.get("sdhdvariantstatus"),
        has_vhl_test=data.get("vhltest"),
        vhl_variant=data.get("vhlvariant"),
        vhl_variant_status=data.get("vhlvariantstatus"),
        has_other_test=data.get("othertest"),
        other_test_name=data.get("othertestname"),
        other_variant=data.get("othervariant"),
        other_variant_status=data.get("othervariantstatus"),
    )
    return RenalCancerGenetics.model_validate(renal_cancer_genetics)


# --- letters -> clinical_letter --- #

CLINICAL_LETTER_FIELDS = {"date", "comments"}


def clinical_letter_row(patient_id: int, data: dict) -> ClinicalLetter:
    clinical_letter = ClinicalLetterBase(
        patient_id=patient_id,
        letter_date=data.get("date"),
        letter_comments=data.get("comments"),
    )
    return ClinicalLetter.model_validate(clinical_letter)


# --- cancertumours -> cancer_tumour --- #

CANCER_TUMOUR_FIELDS = {
    "tumourtype", "othertumourname", "date", "tumournumber", "cnsimaging",
    "progdate", "tcat", "ncat", "mcat", "rtsize", "ptsize", "tloc", "comments",
}  # fmt: skip


def cancer_tumour_row(patient_id: int, data: dict) -> CancerTumour:
    # TODO not migrated: comments (no column)
    # TODO tcat, ncat and mcat reuse cnsimaging's option values ("mri" = Ta/N0/M0,
    # "ct" = T0/N1/M1, ... and "other" = T2, T3, T4 or Tx), so the stored values
    # need decoding, and "other" cannot be decoded
    cancer_tumour = CancerTumourBase(
        patient_id=patient_id,
        tumour_type=data.get("tumourtype"),
        other_tumour_name=data.get("othertumourname"),
        diagnosis_date=data.get("date"),
        tumour_count=data.get("tumournumber"),  # free text: only "2"-style fits
        cns_image=data.get("cnsimaging"),
        progression_date=data.get("progdate"),
        t_cat=data.get("tcat"),
        n_cat=data.get("ncat"),
        m_cat=data.get("mcat"),
        radiologic_tumor_size=data.get("rtsize"),
        pathologic_tumor_size=data.get("ptsize"),
        tumor_location=data.get("tloc"),
    )
    return CancerTumour.model_validate(cancer_tumour)


# --- igan -> hsp_assessment --- #

HSP_ASSESSMENT_FIELDS = {"date", "haematuria", "nephrotic", "m", "e", "s", "t", "c"}


def hsp_assessment_row(patient_id: int, data: dict) -> HSPAssessment:
    hsp_assessment = HSPAssessmentBase(
        patient_id=patient_id,
        assessment_date=data.get("date"),
        has_haematuria=data.get("haematuria"),
        is_nephrotic=data.get("nephrotic"),
        mest_c_m=data.get("m"),
        mest_c_e=data.get("e"),
        mest_c_s=data.get("s"),
        mest_c_t=data.get("t"),
        mest_c_c=data.get("c"),
    )
    return HSPAssessment.model_validate(hsp_assessment)


# --- procedures -> procedure --- #

PROCEDURE_FIELDS = {"procedure", "otherprocedure", "date", "comments"}


def procedure_row(patient_id: int, data: dict) -> Procedure:
    # TODO not migrated: comments (no column)
    procedure = ProcedureBase(
        patient_id=patient_id,
        procedure_name=data.get("procedure"),
        other_procedure=data.get("otherprocedure"),
        date_of_procedure=data.get("date"),
    )
    return Procedure.model_validate(procedure)


# --- the mapping --- #


class FormMapping(NamedTuple):
    fields: set[str]  # the field names in the radar 2 form (forms.data["fields"])
    model: type[SQLModel]  # the radar 3 table
    row: Callable[[int, dict], SQLModel]  # builds one row from (patient_id, data)


# radar 2 form slug -> its radar 3 mapping
FORMS = {
    "6cit": FormMapping(SIX_CIT_FIELDS, SixCIT, six_cit_row),
    "hads": FormMapping(HADS_FIELDS, HADS, hads_row),
    "diabetic-complications": FormMapping(
        DIABETIC_COMPLICATION_FIELDS, DiabeticComplication, diabetic_complication_row
    ),
    "pam": FormMapping(PAM_FIELDS, PAM, pam_row),
    "chu9d": FormMapping(PAEDS_CHU9D_FIELDS, PaedsCHU9D, paeds_chu9d_row),
    "origin": FormMapping(ETHNIC_ORIGIN_FIELDS, EthnicOrigin, ethnic_origin_row),
    "family-history": FormMapping(
        NURTURE_FAMILY_HISTORY_FIELDS, NurtureFamilyHistory, nurture_family_history_row
    ),
    "ddls": FormMapping(DENT_AND_LOWE_FIELDS, DentAndLoweAssessment, dent_and_lowe_row),
    "calciphylaxis": FormMapping(
        CALCIPHYLAXIS_FIELDS, CalciphylaxisAssessment, calciphylaxis_row
    ),
    "eq-5d-y": FormMapping(EQ5DY_FIELDS, EQ5DY, eq5dy_row),
    "eq-5d-5l": FormMapping(ADULT_EQ5D5L_FIELDS, AdultEQ5D5L, adult_eq5d5l_row),
    "socio-economic": FormMapping(
        SOCIO_ECONOMIC_FIELDS, SocioEconomic, socio_economic_row
    ),
    "ipos": FormMapping(IPOS_FIELDS, IPOS, ipos_row),
    "rituximab-administration": FormMapping(
        RITUXIMAB_TOXICITY_FIELDS, RituximabToxicity, rituximab_toxicity_row
    ),
    "specgenetics": FormMapping(
        CKD_AFRICA_GENETIC_FIELDS, CKDAfricaGenetic, ckd_africa_genetic_row
    ),
    "rituximab-assessment": FormMapping(
        RITUXIMAB_FOLLOW_UP_FIELDS,
        RituximabFollowUpAssessment,
        rituximab_follow_up_row,
    ),
    "igan-inventory": FormMapping(
        SAMPLE_INVENTORY_FIELDS, SampleInventory, sample_inventory_row
    ),
    "anthropometrics": FormMapping(
        ANTHROPOMETRIC_FIELDS, Anthropometric, anthropometric_row
    ),
    "igan-research": FormMapping(IGA_RESEARCH_FIELDS, IGAResearch, iga_research_row),
    "rituximab-adverse-events": FormMapping(
        ADVERSE_EVENT_FIELDS, AdverseEvent, adverse_event_row
    ),
    "nurtureckd": FormMapping(NURTURE_VISIT_FIELDS, NurtureVisit, nurture_visit_row),
    "samples": FormMapping(TUBE_SAMPLE_FIELDS, TubeSample, tube_sample_row),
    "renaltumour": FormMapping(
        RENAL_CANCER_TUMOUR_FIELDS, RenalCancerTumour, renal_cancer_tumour_row
    ),
    "riskckd": FormMapping(
        CKD_AFRICA_RISK_FACTOR_FIELDS, CKDAfricaRiskFactor, ckd_africa_risk_factor_row
    ),
    "paedcyst": FormMapping(
        CYSTINOSIS_PAED_VISIT_FIELDS, CystinosisPaedVisit, cystinosis_paed_visit_row
    ),
    "cystadult": FormMapping(
        CYSTINOSIS_ADULT_VISIT_FIELDS, CystinosisAdultVisit, cystinosis_adult_visit_row
    ),
    "renalgenetics": FormMapping(
        RENAL_CANCER_GENETICS_FIELDS, RenalCancerGenetics, renal_cancer_genetics_row
    ),
    "letters": FormMapping(CLINICAL_LETTER_FIELDS, ClinicalLetter, clinical_letter_row),
    "cancertumours": FormMapping(CANCER_TUMOUR_FIELDS, CancerTumour, cancer_tumour_row),
    "igan": FormMapping(HSP_ASSESSMENT_FIELDS, HSPAssessment, hsp_assessment_row),
    "procedures": FormMapping(PROCEDURE_FIELDS, Procedure, procedure_row),
}

# radar 2 forms not migrated yet: no radar 3 model matches them. Every radar 2
# form must be in FORMS or here, so a new form in radar 2 still stops the
# migration. Their entry counts are logged as a warning on every run.
TODO_FORMS = {
    # TODO no model: Rituximab Visits (date, visit)
    "rituximab-visits",
    # TODO no model: Clinical Picture - Nurture CKD (date, comments)
    "ckd-clinical-pictures",
    # TODO no model: CMV Summary
    "cmvstatus",
    # TODO no model: CMV Antiviral Resistance
    "cmvantiviralresistance",
    # TODO no model: CMV Episodes
    "cmvepisodes",
    # TODO no model: Secondary diagnosis of hypertension
    "secdiaght",
    # TODO no model: Baseline clinic BP measurements
    "baselinebp",
    # TODO no model: Hypertension History
    "hthistory",
    # TODO no model: Additional Investigations (hypertension)
    "htadditional",
    # TODO no model: Vasculitis Meds (137 fields)
    "vasmeds",
    # TODO no model: Vasculitis Detail
    "vasdetail",
    # TODO no model: Avacopan
    "avacopan",
    # TODO no model: Lupus Nephritis Review (238 fields)
    "lupusreview",
    # TODO no model: Status Change
    "statuschange",
    # TODO no model: CAKUT Clinical Picture
    "cakutclinicalpicture",
    # TODO no model: CAKUT Surgical Intervention
    "cakutsurginter",
    # TODO no model: Core Data Check
    "datacheck",
    # TODO no model: Non Renal Pathology
    "nonrenalpath",
    # TODO no model, looks like a test form: test2 (copy of Renal Cancer Genetics)
    "test2",
    # TODO no model, looks like a test form: Cystinosis*Test (copy of renaltumour)
    "cysttest",
    # TODO no model, looks like a test form: cystinosis *test2 measures
    # (copy of Anthropometrics)
    "cyst2",
    # TODO no model, looks like a test form: Cyst3 (copy of renaltumour)
    "cyst3",
}


# --- the steps --- #


def read_forms(bind) -> dict[str, dict]:
    """Every radar 2 form definition, by slug: {slug: forms.data}."""
    rows = bind.execute(text("SELECT slug, data FROM public.forms ORDER BY slug"))
    return {slug: data for slug, data in rows}


def check_forms_mapped(forms: dict[str, dict]) -> None:
    """Every radar 2 form must be mapped in FORMS or listed in TODO_FORMS."""
    unknown = sorted(set(forms) - set(FORMS) - TODO_FORMS)
    if unknown:
        raise ValueError(f"radar 2 forms in neither FORMS nor TODO_FORMS: {unknown}")


def check_form_fields(forms: dict[str, dict]) -> None:
    """Each mapped form's fields in radar 2 must be the fields its mapping expects."""
    errors = []
    for slug, mapping in FORMS.items():
        if slug not in forms:
            errors.append(f"{slug}: mapped, but radar 2 has no such form")
            continue
        form_fields = {field["name"] for field in forms[slug]["fields"]}
        if form_fields != mapping.fields:
            errors.append(
                f"{slug}: radar 2 has {sorted(form_fields - mapping.fields)} that "
                f"the mapping does not, and is missing "
                f"{sorted(mapping.fields - form_fields)}"
            )
    if errors:
        raise ValueError(
            "form fields do not match their mapping:\n" + "\n".join(errors)
        )





def create_form_tables(bind) -> None:
    """The empty radar 3 form tables."""
    for mapping in FORMS.values():
        mapping.model.__table__.create(bind)


def seed_form(session: Session, slug: str, mapping: FormMapping) -> list[str]:
    """One form's entries -> its radar 3 table. Returns an error per bad entry."""
    entries = session.execute(
        text("""
        SELECT e.id, e.patient_id, e.data
        FROM public.entries AS e
        JOIN public.forms AS f ON f.id = e.form_id
        WHERE f.slug = :slug
        ORDER BY e.created_date, e.id
    """),
        {"slug": slug},
    ).all()

    rows = []
    errors = []
    for entry_id, patient_id, data in entries:
        unexpected = set(data) - mapping.fields
        if unexpected:
            errors.append(
                f"{slug} entry {entry_id}: keys not in the form {sorted(unexpected)}"
            )
            continue
        try:
            rows.append(mapping.row(patient_id, data))
        except ValidationError as error:
            errors.append(f"{slug} entry {entry_id}: {error}")

    session.add_all(rows)
    session.flush()
    log.info("%s: %d of %d entries copied", slug, len(rows), len(entries))
    return errors


def upgrade() -> None:
    bind = op.get_bind()

    # checks first, so nothing is created if radar 2 does not match the mapping
    forms = read_forms(bind)
    check_forms_mapped(forms)
    check_form_fields(forms)

    # From here on every model table on this connection lives in radar3: creates,
    # inserts, and foreign keys. Raw text() SQL is not affected, so radar 2 is read
    # with explicit public.<table> names.
    bind.execution_options(schema_translate_map={None: "radar3"})
    try:
        create_form_tables(bind)

        errors = []
        with Session(bind=bind) as session:
            for slug, mapping in FORMS.items():
                errors += seed_form(session, slug, mapping)

        # every form is tried first, so one run lists every bad entry
        if errors:
            raise ValueError(
                f"{len(errors)} entries do not fit their radar 3 model:\n"
                + "\n".join(errors)
            )
    finally:
        # Alembic records the version on this same connection, in public
        bind.execution_options(schema_translate_map=None)


def downgrade() -> None:
    raise NotImplementedError("One-way migration: RaDaR2 -> RaDaR3.")