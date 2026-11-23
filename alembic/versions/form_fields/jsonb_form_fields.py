"""Where each radar 2 form's entries go in radar 3, for migration 7e8597a03a37.

FORMS maps a radar 2 form id to (model, fields, casts):

    fields   each key in entries.data -> the model field its answer goes to,
             or an option table: each of the key's answers becomes a row in
             it, pointing at the copied entry and the answer's option,
             or SKIP: the key's answer is not copied
    casts   key -> a function its value goes through before the model
             checks it (only for keys whose value the model's field cannot
             take as radar 2 stored it)

A field with a foreign key to option.id gets the id of the answer's option,
not the answer.

Forms copied:

     1  6cit                       -> six_cit
     2  anthropometrics            -> anthropometric
     3  chu9d                      -> paeds_chu9d
     4  diabetic-complications     -> diabetic_complication
     5  eq-5d-5l                   -> adult_eq5d5l
     6  eq-5d-y                    -> eq5dy
     7  family-history             -> nurture_family_history
     8  hads                       -> hads
     9  ipos                       -> ipos
    10  pam                        -> pam
    11  samples                    -> tube_sample
    12  socio-economic             -> socioeconomic
    13  nurtureckd                 -> nurture_visit
    15  igan                       -> hsp_assessment
    16  calciphylaxis              -> calciphylaxis_assessment
    17  rituximab-administration   -> rituximab_toxicity
    18  rituximab-adverse-events   -> adverse_event
    19  rituximab-assessment       -> rituximab_follow_up_assessment
    22  igan-inventory             -> sample_inventory
    23  igan-research              -> iga_research
    24  origin                     -> ethnic_origin
    25  specgenetics               -> ckd_africa_genetic
    26  renalgenetics              -> renal_cancer_genetics
    27  renaltumour                -> renal_cancer_tumour
    29  riskckd                    -> ckd_africa_risk_factor
    33  paedcyst                   -> cystinosis_paed_visit
    34  cystadult                  -> cystinosis_adult_visit
    35  procedures                 -> procedure
    36  cancertumours              -> cancer_tumour
    37  letters                    -> clinical_letter

Lives in versions/form_fields/, not versions/ itself, as Alembic loads every
.py file in versions/ as a migration.
"""

from collections.abc import Callable
from typing import Any

from radar_models.radar3 import (
    EQ5DY,
    HADS,
    IPOS,
    PAM,
    AdultEQ5D5L,
    AdverseEvent,
    Anthropometric,
    CalciphylaxisAssessment,
    CalciphylaxisAssessmentOption,
    CancerTumour,
    CKDAfricaGenetic,
    CKDAfricaRiskFactor,
    ClinicalLetter,
    CystinosisAdultVisit,
    CystinosisPaedVisit,
    CystinosisPaedVisitOption,
    DiabeticComplication,
    EthnicOrigin,
    HSPAssessment,
    IGAResearch,
    IGAResearchOption,
    NurtureFamilyHistory,
    NurtureVisit,
    PaedsCHU9D,
    Procedure,
    RenalCancerGenetics,
    RenalCancerGeneticsOption,
    RenalCancerTumour,
    RituximabFollowUpAssessment,
    RituximabFollowUpAssessmentOption,
    RituximabToxicity,
    RituximabToxicityOption,
    SampleInventory,
    SixCIT,
    SocioEconomic,
    TubeSample,
    DentAndLoweAssessment,
    DentAndLoweAssessmentBase,
    DentAndLoweAssessmentOption,
    CKDClinicalPicture,
    Avacopan,
    AvacopanOption,
)


class Skip:
    """Marks a key in entries.data whose answer is not copied to radar 3."""

    def __repr__(self) -> str:
        return "SKIP"


SKIP = Skip()


def is_ticked(value: Any) -> bool:
    """Whether a checkbox list with one box is ticked: ["x"] is True, [] is
    False. A missing box is not given to a cast, so its field takes the model's
    default, False."""
    if isinstance(value, str):
        return True
    if not isinstance(value, list):
        raise TypeError(f"expected a list, got {type(value).__name__}")
    if len(value) > 1:
        raise ValueError(f"expected at most one answer, got {value!r}")
    return bool(value)


def single_answer(value: Any) -> Any:
    """The answer of a checkbox list with one box, so it can be looked up as a
    single option: ["x"] is "x", [] is None (not ticked)."""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        raise TypeError(f"expected a list, got {type(value).__name__}")
    if len(value) > 1:
        raise ValueError(f"expected at most one answer, got {value!r}")
    return value[0] if value else None


def join_text(value: Any) -> str:
    """Joins a list of text into one string, its items split by ", "."""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        raise TypeError(f"expected a list, got {type(value).__name__}")
    return ", ".join(str(item) for item in value)


def to_text(value: Any) -> str:
    """A number as text, for a text field."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"expected a number, got {type(value).__name__}")
    return str(value)


def to_float(value: Any) -> str:
    if isinstance(value, str):
        if value.strip() == "":
            return None
    return float(value)


def year_of_emigration(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        if value == "NOT DISCLOSED":
            return None
    return int(value)


SIX_CIT_FIELDS = {
    "date": "completed_date",
    "q1": "six_cit_q1_index",
    "q2": "six_cit_q2_index",
    "q4": "six_cit_q4_index",
    "q5": "six_cit_q5_index",
    "q6": "six_cit_q6_index",
    "q7": "six_cit_q7_index",
    "score": "six_cit_score",
}

ANTHROPOMETRIC_FIELDS = {
    "date": "assessment_date",
    "height": "height",
    "weight": "weight",
    "bmi": "bmi",
    "hip": "hip",
    "waist": "waist",
    "arm": "arm",
    "up": "up_and_go",
    "gripDominant": "grip_dominant",
    "gripNonDominant": "grip_non_dominant",
    "karnofsky": "karnofsky_index",
    "systolic1": "systolic_one",
    "diastolic1": "diastolic_one",
    "systolic2": "systolic_two",
    "diastolic2": "diastolic_two",
    "systolic3": "systolic_three",
    "diastolic3": "diastolic_three",
    "systolic": "systolic_mean",
    "diastolic": "diastolic_mean",
}

PAEDS_CHU9D_FIELDS = {
    "date": "assessment_date",
    "worried": "worried_index",
    "sad": "sad_index",
    "pain": "pain_index",
    "tired": "tired_index",
    "annoyed": "annoyed_index",
    "work": "school_index",
    "sleep": "sleep_index",
    "routine": "routine_index",
    "activities": "activities_index",
}

DIABETIC_COMPLICATION_FIELDS = {
    "retinopathy": "retinopathy_index",
    "laser": "has_laser_treatment",
    "peripheralNeuropathy": "has_peripheral_neuropathy",
    "footUlcers": "has_foot_ulcer",
}

ADULT_EQ5D5L_FIELDS = {
    "date": "assessment_date",
    "age": "age",
    "gender": "gender_index",
    "mobility": "mobility_index",
    "selfCare": "self_care_index",
    "usualActivities": "usual_activities_index",
    "painDiscomfort": "pain_discomfort_index",
    "anxietyDepression": "anxiety_depression_index",
    "health": "health",
}

EQ5DY_FIELDS = {
    "date": "assessment_date",
    "age": "age",
    "gender": "gender_index",
    "mobility": "mobility_index",
    "selfCare": "self_care_index",
    "usualActivities": "usual_activities_index",
    "painDiscomfort": "pain_discomfort_index",
    "anxietyDepression": "anxiety_depression_index",
    "health": "health",
}

NURTURE_FAMILY_HISTORY_FIELDS = {
    "eskd": "has_eskd",
    "eskdRelative1": "eskd_relative_1_index",
    "eskdRelative2": "eskd_relative_2_index",
    "eskdRelative3": "eskd_relative_3_index",
    "chd": "has_chd",
    "chdRelative1": "chd_relative_1_index",
    "chdRelative2": "chd_relative_2_index",
    "chdRelative3": "chd_relative_3_index",
    "diabetes": "has_diabetes",
    "diabetesRelative1": "diabetes_relative_1_index",
    "diabetesRelative2": "diabetes_relative_2_index",
    "diabetesRelative3": "diabetes_relative_3_index",
}

HADS_FIELDS = {
    "date": "assessment_date",
    "a1": "a1_index",
    "d1": "d1_index",
    "a2": "a2_index",
    "d2": "d2_index",
    "a3": "a3_index",
    "d3": "d3_index",
    "a4": "a4_index",
    "d4": "d4_index",
    "a5": "a5_index",
    "d5": "d5_index",
    "a6": "a6_index",
    "d6": "d6_index",
    "a7": "a7_index",
    "d7": "d7_index",
    "anxietyScore": "anxiety_score",
    "depressionScore": "depression_score",
}

IPOS_FIELDS = {
    "date": "assessment_date",
    "score1": "score_1_index",
    "score2": "score_2_index",
    "score3": "score_3_index",
    "score4": "score_4_index",
    "score5": "score_5_index",
    "score6": "score_6_index",
    "score7": "score_7_index",
    "score8": "score_8_index",
    "score9": "score_9_index",
    "score10": "score_10_index",
    "score11": "score_11_index",
    "score12": "score_12_index",
    "score13": "score_13_index",
    "score14": "score_14_index",
    "score15": "score_15_index",
    "score16": "score_16_index",
    "score17": "score_17_index",
    "question1": "question_1",
    "score18": "score_18_index",
    "question2": "question_2",
    "score19": "score_19_index",
    "question3": "question_3",
    "score20": "score_20_index",
    "question4": "question_4",
    "question5": "question_5",
    "score": "ipos_score",
}

IPOS_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "question4": to_text,
    "question5": to_text,
}

PAM_FIELDS = {
    "date": "assessment_date",
    "q1": "pam_q1_index",
    "q2": "pam_q2_index",
    "q3": "pam_q3_index",
    "q4": "pam_q4_index",
    "q5": "pam_q5_index",
    "q6": "pam_q6_index",
    "q7": "pam_q7_index",
    "q8": "pam_q8_index",
    "q9": "pam_q9_index",
    "q10": "pam_q10_index",
    "q11": "pam_q11_index",
    "q12": "pam_q12_index",
    "q13": "pam_q13_index",
}

TUBE_SAMPLE_FIELDS = {
    "date": "sample_date",
    "barcode": "barcode",
    "insstate": "ins_state_index",
}

SOCIOECONOMIC_FIELDS = {
    "date": "assessment_date",
    "education": "education_index",
    "employmentStatus": "employment_status_index",
    "firstLanguage": "first_language",
    "maritalStatus": "martial_status",
    "smoking": "smoking_index",
    "cigarettesPerDay": "cigarettes_per_day",
    "alcohol": "has_alcohol_intake",
    "beerPints": "beer_pints",
    "ciderPints": "cider_pints",
    "redWine": "red_wine",
    "whiteWine": "white_wine",
    "spirits": "spirits",
    "cocktails": "cocktails",
    "unitsPerWeek": "units_per_week",
    "literacy": "literacy_index",
    "literacyHelp": "literacy_help",
    "diet": "diet_index",
    "otherDiet": "other_diet",
}

SOCIOECONOMIC_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "literacyHelp": to_text,
}

NURTURE_VISIT_FIELDS = {
    "date": "visit_date",
    "visit": "nurture_visit_number",
    "comorbities": "comorbidities",
    "vaccinationFlu": "has_flu_vaccination",
    "vaccinationPneumonia": "has_pneumococcal_vaccination",
    "admission": "has_admission",
    "admissionNumber": "admission_number",
    "admissionEmergency": "admission_emergency",
    "admissionPlanned": "admission_planned",
    "admissionDays": "admission_days",
    "admissionAntibiotics": "admission_antibiotics",
    "tabletsParacetamol": "paracetamol_tablets",
    "yearsParacetamol": "paracetamol_years",
    "tabletsCocodamol": "cocodamol_tablets",
    "yearsCocodamol": "cocodamol_years",
    "tabletsIbuprofen": "ibuprofen_tablets",
    "yearsIbuprofen": "ibuprofen_years",
    "medicine1": SKIP,
    "medicine2": SKIP,
    "medicine3": SKIP,
}

HSP_ASSESSMENT_FIELDS = {
    "date": "assessment_date",
    "haematuria": "has_haematuria",
    "nephrotic": "is_nephrotic",
    "m": "mest_c_m",
    "e": "mest_c_e",
    "s": "mest_c_s",
    "t": "mest_c_t",
    "c": "mest_c_c",
    "aki": SKIP,  # TODO ask Andy if this should be added to model as not in form but in data entry
    "crescents": SKIP,  # TODO ask Andy if this should be added to model as not in form but in data entry
}

DENT_AND_LOWE_FIELDS = {
    "date": "assessment_date",
    "aetiology": "aetiology_index",
    "agent": "causative_agent_index",
    "otherAgent": "other_agent",
    "extraInvolvement": DentAndLoweAssessmentOption,
    "otherExtraInvolvement": "other_extra_involvement",
}

CALCIPHYLAXIS_ASSESSMENT_FIELDS = {
    "date": "assessment_date",
    "lesion": "has_lesion",
    "lesionIn": CalciphylaxisAssessmentOption,
    "infection": "has_infection",
    "infectionIn": CalciphylaxisAssessmentOption,
}

RITUXIMAB_TOXICITY_FIELDS = {
    "date": "assessment_date",
    "drugName": "drug_name_index",
    "otherDrug": "other_drug",
    "dose": "dose",
    "retreatment": "is_retreatment",
    "toxicity": RituximabToxicityOption,
    "otherToxicity": "other_toxicity",
}

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
    "dodCause": "cause_of_death",
}

ADVERSE_EVENT_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "otherTox": join_text,
}

RITUXIMAB_FOLLOW_UP_ASSESSMENT_FIELDS = {
    "date": "visit_date",
    "visit": "visit_index",
    "performance": "performance_status_index",
    "transplant": "transplant_index",
    "haemodialysis": "haemodialysis_index",
    "peritonealDialysis": "peritoneal_dialysis_index",
    "medication": RituximabFollowUpAssessmentOption,
    "immunos": "immunosuppression_index",
    "immunosCicl": "ciclosporin_index",
    "ciclDate": "ciclosporin_administered",
    "immunosTacr": "tacrolimus_index",
    "TacrDate": "tacrolimus_administered",
    "immunosCyclo": "cyclophosphamide_index",
    "cycloDate": "cyclophosphamide_administered",
    "immunosChlor": "chlorambucil_index",
    "chlorDate": "chlorambucil_administered",
    "immunosPred": "prednisolone_index",
    "predDate": "prednisolone_administered",
    "immunosRitux": "rituximab_index",
    "rituxDate": "rituximab_administered",
    "rituxRetreat": "met_retreatment_criteria_index",
    "immunosComment": "immunosuppression_comments",
}

RITUXIMAB_FOLLOW_UP_ASSESSMENT_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "immunosCicl": single_answer,
    "immunosTacr": single_answer,
    "immunosCyclo": single_answer,
    "immunosChlor": single_answer,
    "immunosPred": single_answer,
    "immunosRitux": single_answer,
    "immunosComment": join_text,
}

SAMPLE_INVENTORY_FIELDS = {
    "date": "sample_date",
    "urine": "has_urine_sample",
    "urineDate": "urine_date",
    "urineVolume": "urine_volume",
    "serum": "has_serum_sample",
    "serumDate": "serum_date",
    "serumVolume": "serum_volume",
    "plasma": "has_plasma_sample",
    "plasmaDate": "plasma_date",
    "plasmaVolume": "plasma_volume",
    "dna": "has_dna_sample",
    "dnaDate": "dna_date",
    "sputum": "has_sputum_sample",
    "sputumDate": "sputum_date",
    "faeces": "has_faeces_sample",
    "faecesDate": "faeces_date",
}

IGA_RESEARCH_FIELDS = {
    "date": "assessment_date",
    "registeredOn": IGAResearchOption,
}

ETHNIC_ORIGIN_FIELDS = {
    "date": "assessment_date",
    "countryofbirthpatient": "country_of_birth",
    "patientyearuk": "year_of_emigration",
    "ethnicoriginpatient": "ethnic_origin",
    "ethnicoriginmother": "ethnic_origin_mother",
    "ethnicoriginfather": "ethnic_origin_father",
}
ETHNIC_ORIGIN_CASTS = {
    "patientyearuk": year_of_emigration,
}

CKD_AFRICA_GENETIC_FIELDS = {
    "date": "assessment_date",
    "sickle": "sickle_cell_index",
    "sickleother": "other_sickle_cell_index",
    "apol": "apol_1_index",
}

RENAL_CANCER_GENETICS_FIELDS = {
    "date": "assessment_date",
    "bap1test": "has_bap1_test",
    "bap1action": RenalCancerGeneticsOption,
    "bap1variant": "bap1_variant",
    "bap1variantstatus": "bap1_variant_status_index",
    "fhtest": "has_fh_test",
    "fhaction": RenalCancerGeneticsOption,
    "fhvariant": "fh_variant",
    "fhvariantstatus": "fh_variant_status_index",
    "flcntest": "has_flcn_test",
    "flcnaction": RenalCancerGeneticsOption,
    "flcnvariant": "flcn_variant",
    "flcnvariantstatus": "flcn_variant_status_index",
    "mettest": "has_met_test",
    "metaction": RenalCancerGeneticsOption,
    "metvariant": "met_variant",
    "metvariantstatus": "met_variant_status_index",
    "mitftest": "has_mitf_test",
    "mitfaction": RenalCancerGeneticsOption,
    "mitfvariant": "mitf_variant",
    "mitfvariantstatus": "mitf_variant_status_index",
    "ptentest": "has_pten_test",
    "ptenaction": RenalCancerGeneticsOption,
    "ptenvariant": "pten_variant",
    "ptenvariantstatus": "pten_variant_status_index",
    "sdhatest": "has_sdha_test",
    "sdhaaction": RenalCancerGeneticsOption,
    "sdhavariant": "sdha_variant",
    "sdhavariantstatus": "sdha_variant_status_index",
    "sdhbtest": "has_sdhb_test",
    "sdhbaction": RenalCancerGeneticsOption,
    "sdhbvariant": "sdhb_variant",
    "sdhbvariantstatus": "sdhb_variant_status_index",
    "sdhctest": "has_sdhc_test",
    "sdhcaction": RenalCancerGeneticsOption,
    "sdhcvariant": "sdhc_variant",
    "sdhcvariantstatus": "sdhc_variant_status_index",
    "sdhdtest": "has_sdhd_test",
    "sdhdaction": RenalCancerGeneticsOption,
    "sdhdvariant": "sdhd_variant",
    "sdhdvariantstatus": "sdhd_variant_status_index",
    "vhltest": "has_vhl_test",
    "vhlaction": RenalCancerGeneticsOption,
    "vhlvariant": "vhl_variant",
    "vhlvariantstatus": "vhl_variant_status_index",
    "othertest": "has_other_test",
    "othertestname": "other_test_name",
    "otheraction": RenalCancerGeneticsOption,
    "othervariant": "other_variant",
    "othervariantstatus": "other_variant_status_index",
}

RENAL_CANCER_TUMOUR_FIELDS = {
    "tumourtype": "tumour_type_index",
    "date": "assessment_date",
    "cnsimaging": "cns_imaging_method_index",
    "progone": "progression_date",
    "cnsimaging2": "t_cat_index",
    "cnsimaging2": "n_cat_index",  # TODO form entry duplicate definition
    "cnsimaging3": "m_cat_index",
    "rtsize": "rt_size",
    "ptsize": "pt_size",
    "tloc": "t_loc_index",
}

CKD_AFRICA_RISK_FACTOR_FIELDS = {
    "date": "assessment_date",
    "histpretermbirth": "preterm_birth_index",
    "histlowbirthweight": "low_birth_weight_index",
    "histmalnutrition": "malnutrition_index",
    "histhospitalmalnutrition": "hospital_malnutrition_index",
}
CYSTINOSIS_VISIT_FIELDS = {
    "date": "visit_date",
    "urinemeasurement": "urine_measurement_index",
    "urineoutput": "urine_output",
    "voidingovernight": "voiding_overnight_index",
    "continentday": "continence_day_index",
    "fluidintake": "fluid_intake",
    "admdehydrate": "admission_dehydration",
    "constipation": "constipation_index",
    "diarrhoea": "diarrhea_index",
    "nausea": "nausea_index",
    "vomiting": "vomiting_index",
    "rickets": "rickets_index",
    "kyphoscoliosis": "kyphoscoliosis_index",
    "fractures": "fractures_index",
    "jointsurgery": "joint_surgery_index",
    "musclestrength": "muscle_strength_index",
    "photophobia": "photophobia_index",
    "photophobiagrading": "photophobia_grade_index",
    "kdate": "keratoplasty_date",
    "acuity": "acuity",
    "gahl": "gahl_score",
    "intrar": "intraocular_pressure_r",
    "intral": "intraocular_pressure_l",
    "fev": "fev1",
    "vc": "vc",
    "snip": "snip",
    "seizures": "seizure_index",
    "headaches": "headache_index",
    "muscleweakness": "muscle_weakness_index",
    "learningdifficulties": "learning_difficulties_index",
    "cognitivedefect": "cognitive_difficulties_index",
    "movementdisorder": "movement_disorder_index",
    "intracranialhypertension": "intracranial_hypertension_index",
    "diabetes": "diabetes_index",
    "thyroidstate": "thyroid_index",
    "hyperparathyroidism": "hypothyroidism_index",
    "tannerstage": "tanner_stage_index",
    "wccystine": "wc_cystine",
    "wccystinedate": "wc_cystine_date",
    "wccystinetime": "wc_cystine_time",
    "cystsideeffects": "cysteamine_effects",
    "cystlastdosehrs": "cysteamine_hrs_since_last_dose",
}

CYSTINOSIS_PAED_VISIT_FIELDS = {
    **CYSTINOSIS_VISIT_FIELDS,
    "visit": "cystinosis_paed_visit_number_index",
    "height": "height",
    "weight": "weight",
    "failuretothrive": "failure_to_thrive_index",
    "enteralfeeding": "enteral_feeding_index",
    "feedingstartdate1": "feeding_start_date_1",
    "feedingendtdate1": "feeding_end_date_1",
    "feedingstartdate2": "feeding_start_date_2",
    "feedingendtdate2": "feeding_end_date_2",
    "feedingstartdate3": "feeding_start_date_3",
    "feedingendtdate3": "feeding_end_date_3",
    "usedtoadminister": CystinosisPaedVisitOption,
    "normalfoodorally": "normal_food_orally_index",
    "supplements": "supplements_index",
    "growthhormonetreatment": "growth_hormone_treatment_index",
    "swallowing difficulty": "swallowing_difficulties_index",
    "nosesnoring": "nose_snoring_index",
    "tonsilectomydate": "tonsillectomy_date",
    "adenoidectomydate": "adenoidectomy_date",
    "sightimpair": "sight_impairment_index",
    "severesightimpair": "severe_sight_impairment_index",
}

CYSTINOSIS_PAED_VISIT_FIELDS_CAST: dict[str, Callable[[Any], Any]] = {
    "intrar": to_text,
    "intral": to_text,
}

CYSTINOSIS_ADULT_VISIT_FIELDS = {
    **CYSTINOSIS_VISIT_FIELDS,
    "visit": "cystinosis_adult_visit_number_index",
    "musclestrengthankle": "ankle_strength",
    "musclestrengthelbow": "elbow_strength",
    "musclestrengthhand": "hand_strength",
    "musclestrengthhip": "hip_strength",
    "musclestrengthknee": "knee_strength",
    "musclestrengthshoulder": "shoulder_strength",
    "musclestrengthwrist": "wrist_strength",
    "swallowingdifficulty": "swallowing_difficulties_index",
    "swallowingdifficultydetail": "swallowing_difficulties_detail",
    "visualimpair": "sight_impairment_index",
    "cognitivedefectmmsescore": "cognitive_difficulties_score",
}

PROCEDURE_FIELDS = {
    "procedure": "procedure_name_index",
    "otherprocedure": "other_procedure",
    "date": "date_of_procedure",
    "comments": "comments",
}

CANCER_TUMOUR_FIELDS = {
    "tumourtype": "tumour_type_index",
    "othertumourname": "other_tumour_name",
    "date": "diagnosis_date",
    "tumournumber": "tumour_count",
    "cnsimaging": "cns_image_index",
    "progdate": "progression_date",
    "tcat": "t_cat_index",
    "ncat": "n_cat_index",
    "mcat": "m_cat_index",
    "rtsize": "radiologic_tumour_size",
    "ptsize": "pathologic_tumour_size",
    "tloc": "tumour_location_index",
    "comments": "comments",
}

CLINICAL_LETTER_FIELDS = {
    "date": "letter_date",
    "comments": "letter_comments",
}

CKD_CLINCICAL_PICTURE_FIELDS = {
    "date": "date",
    "comments": "comments",
}

AVACOPAN_FIELDS = {
    "avacopancoursetype": "course_type_index",
    "avacopanindication": "indication_index",
    "avacopanstartdate1": "start_date",
    "diagrelapseaavdate": "diagnosis_relapse_date",
    "avvotherconditions": AvacopanOption,
    "baseline1weeklabel": "baseline1weeklabel",
    "baseline1wkdose": "baseline1wkdose",
    "baseline2wkdose": "baseline2wkdose",
    "baseline3wkdose": "baseline3wkdose",
    "baseline4wkdose": "baseline4wkdose",
    "baseline3mthdose": "baseline3mthdose",
    "baseline6mthdose": "baseline6mthdose",
    "baseline9mthdose": "baseline9mthdose",
    "baseline12mth": "baseline12mthdose",
}

FORMS = {
    1: (SixCIT, SIX_CIT_FIELDS, {}),
    2: (Anthropometric, ANTHROPOMETRIC_FIELDS, {}),
    3: (PaedsCHU9D, PAEDS_CHU9D_FIELDS, {}),
    4: (DiabeticComplication, DIABETIC_COMPLICATION_FIELDS, {}),
    5: (AdultEQ5D5L, ADULT_EQ5D5L_FIELDS, {}),
    6: (EQ5DY, EQ5DY_FIELDS, {}),
    7: (NurtureFamilyHistory, NURTURE_FAMILY_HISTORY_FIELDS, {}),
    8: (HADS, HADS_FIELDS, {}),
    9: (IPOS, IPOS_FIELDS, IPOS_FIELDS_CAST),
    10: (PAM, PAM_FIELDS, {}),
    11: (TubeSample, TUBE_SAMPLE_FIELDS, {}),
    12: (SocioEconomic, SOCIOECONOMIC_FIELDS, SOCIOECONOMIC_FIELDS_CAST),
    13: (NurtureVisit, NURTURE_VISIT_FIELDS, {}),
    15: (HSPAssessment, HSP_ASSESSMENT_FIELDS, {}),
    14: (DentAndLoweAssessment, DENT_AND_LOWE_FIELDS, {}),
    16: (CalciphylaxisAssessment, CALCIPHYLAXIS_ASSESSMENT_FIELDS, {}),
    17: (RituximabToxicity, RITUXIMAB_TOXICITY_FIELDS, {}),
    18: (AdverseEvent, ADVERSE_EVENT_FIELDS, ADVERSE_EVENT_FIELDS_CAST),
    19: (
        RituximabFollowUpAssessment,
        RITUXIMAB_FOLLOW_UP_ASSESSMENT_FIELDS,
        RITUXIMAB_FOLLOW_UP_ASSESSMENT_FIELDS_CAST,
    ),
    21: (CKDClinicalPicture, CKD_CLINCICAL_PICTURE_FIELDS, {}),
    23: (IGAResearch, IGA_RESEARCH_FIELDS, {}),
    24: (EthnicOrigin, ETHNIC_ORIGIN_FIELDS, ETHNIC_ORIGIN_CASTS),
    25: (CKDAfricaGenetic, CKD_AFRICA_GENETIC_FIELDS, {}),
    26: (RenalCancerGenetics, RENAL_CANCER_GENETICS_FIELDS, {}),
    27: (RenalCancerTumour, RENAL_CANCER_TUMOUR_FIELDS, {}),
    29: (CKDAfricaRiskFactor, CKD_AFRICA_RISK_FACTOR_FIELDS, {}),
    33: (
        CystinosisPaedVisit,
        CYSTINOSIS_PAED_VISIT_FIELDS,
        CYSTINOSIS_PAED_VISIT_FIELDS_CAST,
    ),
    34: (CystinosisAdultVisit, CYSTINOSIS_ADULT_VISIT_FIELDS, {}),
    35: (Procedure, PROCEDURE_FIELDS, {}),
    36: (CancerTumour, CANCER_TUMOUR_FIELDS, {}),
    37: (ClinicalLetter, CLINICAL_LETTER_FIELDS, {}),
    38: (Avacopan, AVACOPAN_FIELDS, {}),
}


# dropped form 20 (rituximab-visits): 0 entries not copied, no radar 3 model
# dropped form 28 (test2): 0 entries not copied, no radar 3 model
# dropped form 30 (cysttest): 0 entries not copied, no radar 3 model
# dropped form 31 (cyst2): 0 entries not copied, no radar 3 model
# dropped form 32 (cyst3): 0 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 39 (vasdetail): 207 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 40 (vasmeds): 304 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 41 (cakutclinicalpicture): 1,323 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 42 (cakutsurginter): 428 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 43 (lupusreview): 131 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 44 (nonrenalpath): 353 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 45 (cmvstatus): 625 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 46 (cmvantiviralresistance): 1,131 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 47 (cmvepisodes): 722 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 48 (datacheck): 4 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 49 (statuschange): 7 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 50 (secdiaght): 3 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 51 (hthistory): 2 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 52 (baselinebp): 2 entries not copied, no radar 3 model
# INFO  [alembic.runtime.migration] form 53 (htadditional): 1 entry not copied, no radar 3 model
