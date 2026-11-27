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
    VasculitisDetail,
    VasculitisMeds,
    CakutClinicalPicture,
    CakutClinicalPictureOption,
    CakutSurginter,
    LupusReview,
    NonRenalPath,
    CmvSummary,
    CmvSummaryOption,
    CmvAntiviralResistance,
    CmvEpisodesOption,
    CmvEpisodes,
    CoreDataCheck,
    StatusChange,
    SecondaryDiagnosisHypertension,
    BaselineClinicBpMeasurements,
    HypertensionHistoryOption,
    HypertensionHistory,
    AdditionalInvestigations,
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

VAS_DETAIL_FIELDS = {
    "renalflare": "date_of_renalflare",
    "renalflaremorethanone": "more_than_one_renalflare_index",
}
VAS_MEDS_FIELDS = {
    "ivigdate": "ivig_date",
    "dummytitle": "dummy_title",
    "reviewdate": "review_date",
    "avacopandose1": "avacopan_dose_1",
    "avacopandose2": "avacopan_dose_2",
    "avacopandose3": "avacopan_dose_3",
    "iviginfnumber": "ivig_inf_number",
    "avacopaninfsel": "avacopan_infsel_index",
    "rituximabdate1": "rituximab_date_1",
    "rituximabdate2": "rituximab_date_2",
    "rituximabdate3": "rituximab_date_3",
    "rituximabdate4": "rituximab_date_4",
    "rituximabdate5": "rituximab_date_5",
    "rituximabdate6": "rituximab_date_6",
    "rituximabdate7": "rituximab_date_7",
    "rituximabdate8": "rituximab_date_8",
    "rituximabdose1": "rituximab_dose_1",
    "rituximabdose2": "rituximab_dose_2",
    "rituximabdose3": "rituximab_dose_3",
    "rituximabdose4": "rituximab_dose_4",
    "rituximabdose5": "rituximab_dose_5",
    "rituximabdose6": "rituximab_dose_6",
    "rituximabdose7": "rituximab_dose_7",
    "rituximabdose8": "rituximab_dose_8",
    "rituximabinfsel": "rituximab_inf_sel_index",
    "avacopanenddate1": "avacopan_end_date_1",
    "avacopanenddate2": "avacopan_end_date_2",
    "avacopanenddate3": "avacopan_end_date_3",
    "azathioprinedose1": "azathioprine_dose_1",
    "azathioprinedose2": "azathioprine_dose_2",
    "azathioprinedose3": "azathioprine_dose_3",
    "obinutuzumabdate1": "obinutuzumab_date_1",
    "obinutuzumabdate2": "obinutuzumab_date_2",
    "obinutuzumabdate3": "obinutuzumab_date_3",
    "obinutuzumabdate4": "obinutuzumab_date_4",
    "obinutuzumabdate5": "obinutuzumab_date_5",
    "obinutuzumabdate6": "obinutuzumab_date_6",
    "obinutuzumabdate7": "obinutuzumab_date_7",
    "obinutuzumabdate8": "obinutuzumab_date_8",
    "obinutuzumabdose1": "obinutuzumab_dose_1",
    "obinutuzumabdose2": "obinutuzumab_dose_2",
    "obinutuzumabdose3": "obinutuzumab_dose_3",
    "obinutuzumabdose4": "obinutuzumab_dose_4",
    "obinutuzumabdose5": "obinutuzumab_dose_5",
    "obinutuzumabdose6": "obinutuzumab_dose_6",
    "obinutuzumabdose7": "obinutuzumab_dose_7",
    "obinutuzumabdose8": "obinutuzumab_dose_8",
    "prednisolonedose1": "prednisolone_dose_1",
    "prednisolonedose2": "prednisolone_dose_2",
    "prednisolonedose3": "prednisolone_dose_3",
    "prednisolonedose4": "prednisolone_dose_4",
    "prednisolonedose5": "prednisolone_dose_5",
    "prednisolonedose6": "prednisolone_dose_6",
    "prednisolonedose7": "prednisolone_dose_7",
    "prednisolonedose8": "prednisolone_dose_8",
    "avacopanstartdate1": "avacopan_start_date_1",
    "avacopanstartdate2": "avacopan_start_date_2",
    "avacopanstartdate3": "avacopan_start_date_3",
    "azathioprineinfsel": "azathioprine_infsel_index",
    "mycophenolatedose1": "mycophenolate_dose_1",
    "mycophenolatedose2": "mycophenolate_dose_2",
    "mycophenolatedose3": "mycophenolate_dose_3",
    "obinutuzumabinfsel": "obinutuzumab_inf_sel_index",
    "prednisoloneinfsel": "prednisolone_inf_sel_index",
    "mycophenolateinfsel": "mycophenolate_inf_sel_index",
    "azathioprineenddate1": "azathioprine_end_date_1",
    "azathioprineenddate2": "azathioprine_end_date_2",
    "azathioprineenddate3": "azathioprine_end_date_3",
    "prednisoloneenddate1": "prednisolone_end_date_1",
    "prednisoloneenddate2": "prednisolone_end_date_2",
    "prednisoloneenddate3": "prednisolone_end_date_3",
    "prednisoloneenddate4": "prednisolone_end_date_4",
    "prednisoloneenddate5": "prednisolone_end_date_5",
    "prednisoloneenddate6": "prednisolone_end_date_6",
    "prednisoloneenddate7": "prednisolone_end_date_7",
    "prednisoloneenddate8": "prednisolone_end_date_8",
    "cyclophosphamidedate1": "cyclophosphamide_date_1",
    "cyclophosphamidedate2": "cyclophosphamide_date_2",
    "cyclophosphamidedate3": "cyclophosphamide_date_3",
    "cyclophosphamidedate4": "cyclophosphamide_date_4",
    "cyclophosphamidedate5": "cyclophosphamide_date_5",
    "cyclophosphamidedate6": "cyclophosphamide_date_6",
    "cyclophosphamidedate7": "cyclophosphamide_date_7",
    "cyclophosphamidedate8": "cyclophosphamide_date_8",
    "cyclophosphamidedose1": "cyclophosphamide_dose_1",
    "cyclophosphamidedose2": "cyclophosphamide_dose_2",
    "cyclophosphamidedose3": "cyclophosphamide_dose_3",
    "cyclophosphamidedose4": "cyclophosphamide_dose_4",
    "cyclophosphamidedose5": "cyclophosphamide_dose_5",
    "cyclophosphamidedose6": "cyclophosphamide_dose_6",
    "cyclophosphamidedose7": "cyclophosphamide_dose_7",
    "cyclophosphamidedose8": "cyclophosphamide_dose_8",
    "mycophenolateenddate1": "mycophenolate_end_date_1",
    "mycophenolateenddate2": "mycophenolate_end_date_2",
    "mycophenolateenddate3": "mycophenolate_end_date_3",
    "azathioprinestartdate1": "azathioprine_start_date_1",
    "azathioprinestartdate2": "azathioprine_start_date_2",
    "azathioprinestartdate3": "azathioprine_start_date_3",
    "cyclophosphamideinfsel": "cyclophosphamide_inf_sel_index",
    "cyclophosphamidetabsel": "cyclophosphamidetab_sel_index",
    "prednisolonestartdate1": "prednisolone_start_date_1",
    "prednisolonestartdate2": "prednisolone_start_date_2",
    "prednisolonestartdate3": "prednisolone_start_date_3",
    "prednisolonestartdate4": "prednisolone_start_date_4",
    "prednisolonestartdate5": "prednisolone_start_date_5",
    "prednisolonestartdate6": "prednisolone_start_date_6",
    "prednisolonestartdate7": "prednisolone_start_date_7",
    "prednisolonestartdate8": "prednisolone_start_date_8",
    "methylprednisolonedate1": "methylprednisolone_date_1",
    "methylprednisolonedate2": "methylprednisolone_date_2",
    "methylprednisolonedate3": "methylprednisolone_date_3",
    "methylprednisolonedate4": "methylprednisolone_date_4",
    "methylprednisolonedate5": "methylprednisolone_date_5",
    "methylprednisolonedate6": "methylprednisolone_date_6",
    "methylprednisolonedate7": "methylprednisolone_date_7",
    "methylprednisolonedate8": "methylprednisolone_date_8",
    "methylprednisolonedose1": "methylprednisolone_dose_1",
    "methylprednisolonedose2": "methylprednisolone_dose_2",
    "methylprednisolonedose3": "methylprednisolone_dose_3",
    "methylprednisolonedose4": "methylprednisolone_dose_4",
    "methylprednisolonedose5": "methylprednisolone_dose_5",
    "methylprednisolonedose6": "methylprednisolone_dose_6",
    "methylprednisolonedose7": "methylprednisolone_dose_7",
    "methylprednisolonedose8": "methylprednisolone_dose_8",
    "mycophenolatestartdate1": "mycophenolate_start_date_1",
    "mycophenolatestartdate2": "mycophenolate_start_date_2",
    "mycophenolatestartdate3": "mycophenolate_start_date_3",
    "cyclophosphamideenddate1": "cyclophosphamidetab_end_date_1",
    "cyclophosphamideenddate2": "cyclophosphamidetab_end_date_2",
    "cyclophosphamideenddate3": "cyclophosphamidetab_end_date_3",
    "cyclophosphamidetabdose1": "cyclophosphamidetab_dose_1",
    "cyclophosphamidetabdose2": "cyclophosphamidetab_dose_2",
    "cyclophosphamidetabdose3": "cyclophosphamidetab_dose_3",
    "methylprednisoloneinfsel": "methylprednisolone_inf_sel_index",
    "cyclophosphamidestartdate1": "cyclophosphamidetab_start_date_1",
    "cyclophosphamidestartdate2": "cyclophosphamidetab_start_date_2",
    "cyclophosphamidestartdate3": "cyclophosphamidetab_start_date_3",
}

VAS_MEDS_CASTS = {
    "avacopaninfsel": single_answer,
    "rituximabinfsel": single_answer,
    "azathioprineinfsel": single_answer,
    "obinutuzumabinfsel": single_answer,
    "prednisoloneinfsel": single_answer,
    "mycophenolateinfsel": single_answer,
    "cyclophosphamideinfsel": single_answer,
    "cyclophosphamidetabsel": single_answer,
    "methylprednisoloneinfsel": single_answer,
}

CAKUT_FIELDS = {
    "date": "clinical_picture_date",
    "incontinent": "incontinent_index",
    "incontinenttime": CakutClinicalPictureOption,
    "voidingdifficulties ": "voiding_difficulties_index",
    "bladdercatheterisation": "bladder_catheterisation_index",
    "bladdercatheterisationtype": CakutClinicalPictureOption,
    "Recurrentuti": "recurrent_uti_index",
    "medication": "medication_index",
    "medlist": CakutClinicalPictureOption,
    "dmsascan": "dmsa_scan_index",
    "dmsadate": "dmsadate",
    "dmsafunctionright": "dmsafunctionright",
    "dmsafunctionleft": "dmsafunctionleft",
    "dmsarep": "dmsarep",
    "mcug": "mcug_index",
    "mcugdate": "mcug_date",
    "vur": "vur_index",
    "vurrightgrade": "vur_right_grade_index",
    "vurleftgrade": "vur_left_grade_index",
    "bladdernormal": "bladder_normal_index",
    "urethralappearancenormal": "urethralappearancenormal_index",
    "bladderrep": "bladderrep",
    "mag3renogram": "mag3_renogram_index",
    "mag3date": "mag3_date",
    "mag3obstructionleft": "mag3_obstruction_left_index",
    "mag3obstructionright": "mag3_obstruction_right_index",
    "mag3differentialfunctionleft": "mag3_differential_function_left",
    "mag3differentialfunctionright": "mag3_differential_function_right",
    "mag3reflux": "mag3_reflux_index",
    "mag3renogramrep": "mag3_renogram_rep",
    "videourodynamics": "videourodynamics_index",
    "videourodynamicsrep": "videourodynamics_rep",
    "uroflowmetry": "uroflowmetry_index",
    "uroflowmetryrep": "uroflowmetry_rep",
}
CAKUT_SURG_FIELDS = {
    "proceduretype": "procedure_type_index",
    "proceduredate": "procedure_date",
    "fiprocedure": "fi_procedure",
    "kidneyprocedure": "kidney_procedure_index",
    "ureterprocedure": "ureter_procedure_index",
    "bladderprocedure": "bladder_procedure_index",
    "proceduredetails": "procedure_details",
}
CYCLOPHOSPHAMIDE_8_FIELDS = {
    "cyclophosphamideinfsel": "cyclophosphamide_inf_sel_index",
    "cyclophosphamideinfgivendate1": "cyclophosphamide_date_1",
    "cyclophosphamideinfdose1": "cyclophosphamide_dose_1",
    "cyclophosphamideinfgivendate2": "cyclophosphamide_date_2",
    "cyclophosphamideinfdose2": "cyclophosphamide_dose_2",
    "cyclophosphamideinfgivendate3": "cyclophosphamide_date_3",
    "cyclophosphamideinfdose3": "cyclophosphamide_dose_3",
    "cyclophosphamideinfgivendate4": "cyclophosphamide_date_4",
    "cyclophosphamideinfdose4": "cyclophosphamide_dose_4",
    "cyclophosphamideinfgivendate5": "cyclophosphamide_date_5",
    "cyclophosphamideinfdose5": "cyclophosphamide_dose_5",
    "cyclophosphamideinfgivendate6": "cyclophosphamide_date_6",
    "cyclophosphamideinfdose6": "cyclophosphamide_dose_6",
    "cyclophosphamideinfgivendate7": "cyclophosphamide_date_7",
    "cyclophosphamideinfdose7": "cyclophosphamide_dose_7",
    "cyclophosphamideinfgivendate8": "cyclophosphamide_date_8",
    "cyclophosphamideinfdose8": "cyclophosphamide_dose_8",
}

METHYLPREDNISOLONE_8_FIELDS = {
    "methylprednisoloneinfsel": "methylprednisolone_inf_sel_index",
    "methylprednisoloneinfgivendate1": "methylprednisolone_date_1",
    "methylprednisoloneinfdose1": "methylprednisolone_dose_1",
    "methylprednisoloneinfgivendate2": "methylprednisolone_date_2",
    "methylprednisoloneinfdose2": "methylprednisolone_dose_2",
    "methylprednisoloneinfgivendate3": "methylprednisolone_date_3",
    "methylprednisoloneinfdose3": "methylprednisolone_dose_3",
    "methylprednisoloneinfgivendate4": "methylprednisolone_date_4",
    "methylprednisoloneinfdose4": "methylprednisolone_dose_4",
    "methylprednisoloneinfgivendate5": "methylprednisolone_date_5",
    "methylprednisoloneinfdose5": "methylprednisolone_dose_5",
    "methylprednisoloneinfgivendate6": "methylprednisolone_date_6",
    "methylprednisoloneinfdose6": "methylprednisolone_dose_6",
    "methylprednisoloneinfgivendate7": "methylprednisolone_date_7",
    "methylprednisoloneinfdose7": "methylprednisolone_dose_7",
    "methylprednisoloneinfgivendate8": "methylprednisolone_date_8",
    "methylprednisoloneinfdose8": "methylprednisolone_dose_8",
    "methylprednisoloneinfgivendate9": "methylprednisolone_date_9",
    "methylprednisoloneinfdose9": "methylprednisolone_dose_9",
    "methylprednisoloneinfgivendate10": "methylprednisolone_date_10",
    "methylprednisoloneinfdose10": "methylprednisolone_dose_10",
}

RITUXIMAB_8_FIELDS = {
    "rituximabinfsel": "rituximab_inf_sel_index",
    "rituximabinfgivendate1": "rituximab_inf_date_1",
    "rituximabinfdose1": "rituximab_inf_dose_1",
    "rituximabinfgivendate2": "rituximab_inf_date_2",
    "rituximabinfdose2": "rituximab_inf_dose_2",
    "rituximabinfgivendate3": "rituximab_inf_date_3",
    "rituximabinfdose3": "rituximab_inf_dose_3",
    "rituximabinfgivendate4": "rituximab_inf_date_4",
    "rituximabinfdose4": "rituximab_inf_dose_4",
    "rituximabinfgivendate5": "rituximab_inf_date_5",
    "rituximabinfdose5": "rituximab_inf_dose_5",
    "rituximabinfgivendate6": "rituximab_inf_date_6",
    "rituximabinfdose6": "rituximab_inf_dose_6",
    "rituximabinfgivendate7": "rituximab_inf_date_7",
    "rituximabinfdose7": "rituximab_inf_dose_7",
    "rituximabinfgivendate8": "rituximab_inf_date_8",
    "rituximabinfdose8": "rituximab_inf_dose_8",
}

OBINUTUZUMAB_INF_6_FIELDS = {
    "obinutuzumabinfsel": "obinutuzumab_inf_sel_index",
    "obinutuzumabinfgivendate1": "obinutuzumab_inf_date_1",
    "obinutuzumabinfdose1": "obinutuzumab_inf_dose_1",
    "obinutuzumabinfgivendate2": "obinutuzumab_inf_date_2",
    "obinutuzumabinfdose2": "obinutuzumab_inf_dose_2",
    "obinutuzumabinfgivendate3": "obinutuzumab_inf_date_3",
    "obinutuzumabinfdose3": "obinutuzumab_inf_dose_3",
    "obinutuzumabinfgivendate4": "obinutuzumab_inf_date_4",
    "obinutuzumabinfdose4": "obinutuzumab_inf_dose_4",
    "obinutuzumabinfgivendate5": "obinutuzumab_inf_date_5",
    "obinutuzumabinfdose5": "obinutuzumab_inf_dose_5",
    "obinutuzumabinfgivendate6": "obinutuzumab_inf_date_6",
    "obinutuzumabinfdose6": "obinutuzumab_inf_dose_6",
}


PREDNISOLONE_8_FIELDS = {
    "prednisolonenewmed": "prednisolone_newmed_index",
    "prednisoloneindication1": "prednisolone_indication_1_index",
    "prednisolonenewmedstartdate1": "prednisolone_newmed_startdate_1",
    "prednisolonenewmedenddate1": "prednisolone_newmed_enddate_1",
    "prednisolonenewmedstartdate2": "prednisolone_newmed_startdate_2",
    "prednisolonenewmedenddate2": "prednisolone_newmed_enddate_2",
    "prednisolonenewmedstartdate3": "prednisolone_newmed_startdate_3",
    "prednisolonenewmedenddate3": "prednisolone_newmed_enddate_3",
    "prednisolonenewmedstartdate4": "prednisolone_newmed_startdate_4",
    "prednisolonenewmedenddate4": "prednisolone_newmed_enddate_4",
    "prednisolonenewmedstartdate5": "prednisolone_newmed_startdate_5",
    "prednisolonenewmedenddate5": "prednisolone_newmed_enddate_5",
    "prednisolonenewmedstartdate6": "prednisolone_newmed_startdate_6",
    "prednisolonenewmedenddate6": "prednisolone_newmed_enddate_6",
    "prednisolonenewmedstartdate7": "prednisolone_newmed_startdate_7",
    "prednisolonenewmedenddate7": "prednisolone_newmed_enddate_7",
    "prednisolonenewmedstartdate8": "prednisolone_newmed_startdate_8",
    "prednisolonenewmedenddate8": "prednisolone_newmed_enddate_8",
    "prednisolonenewmedstartdate9": "prednisolone_newmed_startdate_9",
    "prednisolonenewmedenddate9": "prednisolone_newmed_enddate_9",
    "prednisolonenewmedstartdate10": "prednisolone_newmed_startdate_10",
    "prednisolonenewmedenddate10": "prednisolone_newmed_enddate_10",
}

LUPUS_REVIEW_FIELDS = {
    **CYCLOPHOSPHAMIDE_8_FIELDS,
    **METHYLPREDNISOLONE_8_FIELDS,
    **RITUXIMAB_8_FIELDS,
    **PREDNISOLONE_8_FIELDS,
    **OBINUTUZUMAB_INF_6_FIELDS,
    "date": "review_date",
    "livebirthsnumber": "number_of_live_births",
    "lnclass": "inclass_index",
    "lnoverlapclass": "overlapclass_index",
    "biopsyconfirmation": "biopsyconfirmation_index",
    "lnflaredate1": "flaredate_1",
    "lnflaredate2": "flaredate_2",
    "lnflaredate3": "flaredate_3",
    "pregnancynumber": "pregancy_number",
    "infusionconfirmation": "infusion_confirmation_index",
    "belimumabinfsel": "belimumab_inf_sel_index",
    "belimumabinfgivendate1": "belimumab_inf_given_date_1",
    "belimumabinfdose1": "belimumab_inf_dose_1",
    "belimumabinfgivendate2": "belimumab_inf_given_date_2",
    "belimumabinfdose2": "belimumab_inf_dose_2",
    "belimumabinfgivendate3": "belimumab_inf_given_date_3",
    "belimumabinfdose3": "belimumab_inf_dose_3",
    "belimumabinfgivendate4": "belimumab_inf_given_date_4",
    "belimumabinfdose4": "belimumab_inf_dose_4",
    "belimumabinfgivendate5": "belimumab_inf_given_date_5",
    "belimumabinfdose5": "belimumab_inf_dose_5",
    "belimumabinfgivendate6": "belimumab_inf_given_date_6",
    "belimumabinfdose6": "belimumab_inf_dose_6",
    "belimumabinfgivendate7": "belimumab_inf_given_date_7",
    "belimumabinfdose7": "belimumab_inf_dose_7",
    "belimumabinfgivendate8": "belimumab_inf_given_date_8",
    "belimumabinfdose8": "belimumab_inf_dose_8",
    "newmedconfirmation": "newmedconfirmation_index",
    "azathioprinenewmed": "azathioprine_newmed_index",
    "azathioprineindication1": "azathioprine_indication_1_index",
    "azathioprinenewmedstartdate1": "azathioprine_newmed_startdate_1",
    "azathioprinenewmedenddate1": "azathioprine_newmed_enddate_1",
    "azathioprinenewmedstartdate2": "azathioprine_newmed_startdate_2",
    "azathioprinenewmedenddate2": "azathioprine_newmed_enddate_2",
    "azathioprinenewmedstartdate3": "azathioprine_newmed_startdate_3",
    "azathioprinenewmedenddate3": "azathioprine_newmed_enddate_3",
    "belimumabnewmed": "belimumab_newmed_index",
    "belimumabindication1": "belimumab_indication_1_index",
    "belimumabnewmedstartdate1": "belimumab_newmed_startdate_1",
    "belimumabnewmedenddate1": "belimumab_newmed_enddate_1",
    "belimumabnewmedstartdate2": "belimumab_newmed_startdate_2",
    "belimumabnewmedenddate2": "belimumab_newmed_enddate_2",
    "belimumabnewmedstartdate3": "belimumab_newmed_startdate_3",
    "belimumabnewmedenddate3": "belimumab_newmed_enddate_3",
    "ciclosporinnewmed": "ciclosporin_newmed_index",
    "ciclosporinindication1": "ciclosporin_indication_1_index",
    "ciclosporinnewmedstartdate1": "ciclosporin_newmed_startdate_1",
    "ciclosporinnewmedenddate1": "ciclosporin_newmed_enddate_1",
    "ciclosporinnewmedstartdate2": "ciclosporin_newmed_startdate_2",
    "ciclosporinnewmedenddate2": "ciclosporin_newmed_enddate_2",
    "ciclosporinnewmedstartdate3": "ciclosporin_newmed_startdate_3",
    "ciclosporinnewmedenddate3": "ciclosporin_newmed_enddate_3",
    "cyclophosphamidenewmed": "cyclophosphamide_newmed_index",
    "cyclophosphamideindication1": "cyclophosphamide_indication_1_index",
    "cyclophosphamidenewmedstartdate1": "cyclophosphamide_newmed_startdate_1",
    "cyclophosphamidenewmedenddate1": "cyclophosphamide_newmed_enddate_1",
    "cyclophosphamidenewmedstartdate2": "cyclophosphamide_newmed_startdate_2",
    "cyclophosphamidenewmedenddate2": "cyclophosphamide_newmed_enddate_2",
    "cyclophosphamidenewmedstartdate3": "cyclophosphamide_newmed_startdate_3",
    "cyclophosphamidenewmedenddate3": "cyclophosphamide_newmed_enddate_3",
    "hydroxychloroquinenewmed": "hydroxychloroquine_newmed_index",
    "hydroxychloroquineindication1": "hydroxychloroquine_indication_1_index",
    "hydroxychloroquinenewmedstartdate1": "hydroxychloroquine_newmed_startdate_1",
    "hydroxychloroquinenewmedenddate1": "hydroxychloroquine_newmed_enddate_1",
    "hydroxychloroquinenewmedstartdate2": "hydroxychloroquine_newmed_startdate_2",
    "hydroxychloroquinenewmedenddate2": "hydroxychloroquine_newmed_enddate_2",
    "hydroxychloroquinenewmedstartdate3": "hydroxychloroquine_newmed_startdate_3",
    "hydroxychloroquinenewmedenddate3": "hydroxychloroquine_newmed_enddate_3",
    "hydroxychloroquinenewmedstartdate4": "hydroxychloroquine_newmed_startdate_4",
    "hydroxychloroquinenewmedenddate4": "hydroxychloroquine_newmed_enddate_4",
    "leflunomidenewmed": "leflunomide_newmed_index",
    "leflunomideindication1": "leflunomide_indication_1_index",
    "leflunomidenewmedstartdate1": "leflunomide_newmed_startdate_1",
    "leflunomidenewmedenddate1": "leflunomide_newmed_enddate_1",
    "leflunomidenewmedstartdate2": "leflunomide_newmed_startdate_2",
    "leflunomidenewmedenddate2": "leflunomide_newmed_enddate_2",
    "leflunomidenewmedstartdate3": "leflunomide_newmed_startdate_3",
    "leflunomidenewmedenddate3": "leflunomide_newmed_enddate_3",
    "methotrexatenewmed": "methotrexate_newmed_index",
    "methotrexateindication1": "methotrexate_indication_1_index",
    "methotrexatenewmedstartdate1": "methotrexate_newmed_startdate_1",
    "methotrexatenewmedenddate1": "methotrexate_newmed_enddate_1",
    "methotrexatenewmedstartdate2": "methotrexate_newmed_startdate_2",
    "methotrexatenewmedenddate2": "methotrexate_newmed_enddate_2",
    "methotrexatenewmedstartdate3": "methotrexate_newmed_startdate_3",
    "methotrexatenewmedenddate3": "methotrexate_newmed_enddate_3",
    "mycophenolatenewmed": "mycophenolate_newmed_index",
    "mycophenolateindication1": "mycophenolate_indication_1_index",
    "mycophenolatenewmedstartdate1": "mycophenolate_newmed_startdate_1",
    "mycophenolatenewmedenddate1": "mycophenolate_newmed_enddate_1",
    "mycophenolatenewmedstartdate2": "mycophenolate_newmed_startdate_2",
    "mycophenolatenewmedenddate2": "mycophenolate_newmed_enddate_2",
    "mycophenolatenewmedstartdate3": "mycophenolate_newmed_startdate_3",
    "mycophenolatenewmedenddate3": "mycophenolate_newmed_enddate_3",
    "mycophenolatenewmedstartdate4": "mycophenolate_newmed_startdate_4",
    "mycophenolatenewmedenddate4": "mycophenolate_newmed_enddate_4",
    "mycophenolicacidnewmed": "mycophenolicacid_newmed_index",
    "mycophenolicacidindication1": "mycophenolicacid_indication_1_index",
    "mycophenolicacidnewmedstartdate1": "mycophenolicacid_newmed_startdate_1",
    "mycophenolicacidnewmedenddate1": "mycophenolicacid_newmed_enddate_1",
    "mycophenolicacidnewmedstartdate2": "mycophenolicacid_newmed_startdate_2",
    "mycophenolicacidnewmedenddate2": "mycophenolicacid_newmed_enddate_2",
    "mycophenolicacidnewmedstartdate3": "mycophenolicacid_newmed_startdate_3",
    "mycophenolicacidnewmedenddate3": "mycophenolicacid_newmed_enddate_3",
    "mycophenolicacidnewmedstartdate4": "mycophenolicacid_newmed_startdate_4",
    "mycophenolicacidnewmedenddate4": "mycophenolicacid_newmed_enddate_4",
    "tacrolimusnewmed": "tacrolimus_newmed_index",
    "tacrolimusindication1": "tacrolimus_indication_1_index",
    "tacrolimusnewmedstartdate1": "tacrolimus_newmed_startdate_1",
    "tacrolimusnewmedenddate1": "tacrolimus_newmed_enddate_1",
    "tacrolimusnewmedstartdate2": "tacrolimus_newmed_startdate_2",
    "tacrolimusnewmedenddate2": "tacrolimus_newmed_enddate_2",
    "tacrolimusnewmedstartdate3": "tacrolimus_newmed_startdate_3",
    "tacrolimusnewmedenddate3": "tacrolimus_newmed_enddate_3",
    "tacrolimusnewmedstartdate4": "tacrolimus_newmed_startdate_4",
    "tacrolimusnewmedenddate4": "tacrolimus_newmed_enddate_4",
    "voclosporinnewmed": "voclosporin_newmed_index",
    "voclosporinindication1": "voclosporin_indication_1_index",
    "voclosporinnewmedstartdate1": "voclosporin_newmed_startdate_1",
    "voclosporinnewmedenddate1": "voclosporin_newmed_enddate_1",
    "voclosporinnewmedstartdate2": "voclosporin_newmed_startdate_2",
    "voclosporinnewmedenddate2": "voclosporin_newmed_enddate_2",
    "voclosporinnewmedstartdate3": "voclosporin_newmed_startdate_3",
    "voclosporinnewmedenddate3": "voclosporin_newmed_enddate_3",
    "voclosporinnewmedstartdate4": "voclosporin_newmed_startdate_4",
    "voclosporinnewmedenddate4": "voclosporin_newmed_enddate_4",
    "medstopped": "medstopped",
    "azathioprinemedstopped": "azathioprine_med_stopped_index",
    "azathioprinemedstoppedenddate": "azathioprine_med_stopped_enddate",
    "belimumabmedstopped": "belimumab_med_stopped_index",
    "belimumabmedstoppedenddate": "belimumab_med_stopped_enddate",
    "ciclosporinmedstopped": "ciclosporin_med_stopped_index",
    "ciclosporinmedstoppedenddate": "ciclosporin_med_stopped_enddate",
    "cyclophosphamidemedstopped": "cyclophosphamide_med_stopped_index",
    "cyclophosphamidemedstoppedenddate": "cyclophosphamide_med_stopped_enddate",
    "hydroxychloroquinemedstopped": "hydroxychloroquine_med_stopped_index",
    "hydroxychloroquinemedstoppedenddate": "hydroxychloroquine_med_stopped_enddate",
    "leflunomidemedstopped": "leflunomide_med_stopped_index",
    "leflunomidemedstoppedenddate": "leflunomide_med_stopped_enddate",
    "methotrexatemedstopped": "methotrexate_med_stopped_index",
    "methotrexatemedstoppedenddate": "methotrexate_med_stopped_enddate",
    "mycophenolatemedstopped": "mycophenolate_med_stopped_index",
    "mycophenolatemedstoppedenddate": "mycophenolate_med_stopped_enddate",
    "mycophenolicacidmedstopped": "mycophenolicacid_med_stopped_index",
    "mycophenolicacidmedstoppedenddate": "mycophenolicacid_med_stopped_enddate",
    "prednisolonemedstopped": "prednisolone_med_stopped_index",
    "prednisolonemedstoppedenddate": "prednisolone_med_stopped_enddate",
    "tacrolimusmedstopped": "tacrolimus_med_stopped_index",
    "tacrolimusmedstoppedenddate": "tacrolimus_med_stopped_enddate",
    "voclosporinmedstopped": "voclosporin_med_stopped_index",
    "voclosporinmedstoppedenddate": "voclosporin_med_stopped_enddate",
    "reviewcomments": "review_comments",
}

LUPUS_REVIEW_CASTS = {
    "cyclophosphamideinfsel": single_answer,
    "methylprednisoloneinfsel": single_answer,
    "rituximabinfsel": single_answer,
    "belimumabinfsel": single_answer,
    "prednisolonenewmed": single_answer,
    "azathioprinenewmed": single_answer,
    "belimumabnewmed": single_answer,
    "ciclosporinnewmed": single_answer,
    "cyclophosphamidenewmed": single_answer,
    "hydroxychloroquinenewmed": single_answer,
    "leflunomidenewmed": single_answer,
    "methotrexatenewmed": single_answer,
    "mycophenolatenewmed": single_answer,
    "mycophenolicacidnewmed": single_answer,
    "tacrolimusnewmed": single_answer,
    "voclosporinnewmed": single_answer,
    "azathioprinemedstopped": single_answer,
    "belimumabmedstopped": single_answer,
    "ciclosporinmedstopped": single_answer,
    "cyclophosphamidemedstopped": single_answer,
    "hydroxychloroquinemedstopped": single_answer,
    "leflunomidemedstopped": single_answer,
    "methotrexatemedstopped": single_answer,
    "mycophenolatemedstopped": single_answer,
    "mycophenolicacidmedstopped": single_answer,
    "prednisolonemedstopped": single_answer,
    "tacrolimusmedstopped": single_answer,
    "voclosporinmedstopped": single_answer,
    "obinutuzumabinfsel": single_answer,
}

NON_RENAL_PATH_FIELDS = {
    "date": "date_of_report",
    "organ": "organ_index",
    "organother": "organ_other",
    "nonrenalpathref": "nonrenal_pathref",
    "histologicalsummary": "histological_summary",
}

CMV_SUMMARY_FIELDS = {
    "lnclass": "cmv_status_index",
    "cmvmanagementstrategy": "cmv_management_strategy_index",
    "cmvstrategyother": "cmv_strategy_other",
    "prophylaxis": "prophylaxis_index",
    "prophylaxisother": "prophylaxis_other",
    "prophylaxisstartdate": "prophylaxis_start_date",
    "prophylaxisendtdate": "prophylaxis_end_date",
    "immunoattrans": CmvSummaryOption,
    "immunoattransother": "immunosuppression_at_transplant_other",
}

CMV_ANTIVIRAL_RESISTANCE_FIELDS = {
    "cmvantiviralresistancetesting": "cmv_antiviral_resistance_testing_index",
    "cmvantiviralresistancetestingdate": "cmv_antiviral_resistance_testing_date",
    "cmvantiviralresistancetestingresults": "cmv_antiviral_resistance_testing_results",
    "cmvgenemutationtesting": "cmv_gene_mutation_testing_index",
    "cmvgenemutationtestingdate": "cmv_gene_mutation_testing_date",
    "cmvgenemutationtestingresults": "cmv_gene_mutation_testing_results",
    "mutationul54": "mutation_ul54_index",
    "mutationul97": "mutation_ul97_index",
}
CORE_DATA_CHECK_FIELDS = {
    "date": "data_check_date",
    "diagnosis": "diagnosis_index",
    "diagnosisdetails": "diagnosis_details",
    "biopsy": "biopsy_index",
    "biopsydetails": "biopsy_details",
    "genetic": "genetic_index",
    "geneticdetails": "genetic_details",
    "serumcreatinine": "serum_creatinine_index",
    "serumcreatininedetails": "serum_creatinine_details",
    "creatratio": "creat_ratio_index",
    "creatratiodetails": "creat_ratio_details",
    "notes": "notes",
}
CMV_EPISODES_FIELDS = {
    "episodestartdate": "episode_start_date",
    "cmvclinicalpresentation": CmvEpisodesOption,
    "cmvclinicalpresentationother": "cmv_clinical_presentation_other",
    "cmvrecurrence": "cmv_recurrence_index",
    "cmvrecurrencedate": "cmv_recurrence_date",
    "cmvdiagnosis": "cmv_diagnosis_index",
    "immunobeforecmv": CmvEpisodesOption,
    "immunobeforecmvother": "immunosuppression_before_cmv_other",
    "treatmed1": "treatment_med_1_index",
    "treatmed1other": "treatment_med_1_other",
    "treatmed1sideeffects": "treatment_med_1_side_effects_index",
    "treatmed1sideeffectscomments": "treatment_med_1_side_effects_comments",
    "treatmed1maxdailydose": "treatment_med_1_max_daily_dose",
    "treatmedstartdate1": "treatment_med_1_start_date",
    "treatmedendtdate1": "treatment_med_1_end_date",
    "treatmed2": "treatment_med_2_index",
    "treatmed2other": "treatment_med_2_other",
    "treatmed2sideeffects": "treatment_med_2_side_effects_index",
    "treatmed2sideeffectscomments": "treatment_med_2_side_effects_comments",
    "treatmed2maxdailydose": "treatment_med_2_max_daily_dose",
    "treatmedstartdate2": "treatment_med_2_start_date",
    "treatmedendtdate2": "treatment_med_2_end_date",
    "treatmed3": "treatment_med_3_index",
    "treatmed3other": "treatment_med_3_other",
    "treatmed3sideeffects": "treatment_med_3_side_effects_index",
    "treatmed3sideeffectscomments": "treatment_med_3_side_effects_comments",
    "treatmed3maxdailydose": "treatment_med_3_max_daily_dose",
    "treatmedstartdate3": "treatment_med_3_start_date",
    "treatmedendtdate3": "treatment_med_3_end_date",
    "secondaryprophylaxis": "secondary_prophylaxis_index",
    "secondaryprophylaxisother": "secondary_prophylaxis_other",
    "secondaryprophylaxisstartdate": "secondary_prophylaxis_start_date",
    "secondaryprophylaxisendtdate": "secondary_prophylaxis_end_date",
    "immunopostcmv": CmvEpisodesOption,
    "immunopostcmvother": "immunosuppression_after_cmv_other",
    "6monthimmunodosereduction": "immunosuppression_dose_reduction_6_month_index",
    "6monthimmunodosereductiontemp": "immunosuppression_dose_reduction_6_month_temp_index",
    "cmvoutcome6mnth": "cmv_outcome_6_month_index",
    "cmvoutcome12month": "cmv_outcome_12_month_index",
    "cmvoutcomecomments": "cmv_outcome_comments",
}
STATUS_CHANGE_FIELDS = {
    "date": "data_checked_date",
    "trans": "transplant_last_year_index",
    "dialysisfirst": "first_dialysis_last_year_index",
    "dod": "deceased_index",
    "transin": "transfer_in_index",
    "prevhospital": "previous_hospital",
    "transout": "transfer_out_index",
    "nexthospital": "next_hospital",
}

SECONDARY_DIAGNOSIS_HYPERTENSION_FIELDS = {
    "secondarydiaght": "secondary_diagnosis_index",
    "secondarydiaghtother": "secondary_diagnosis_other",
    "secondarydiaghtdate": "secondary_diagnosis_date",
}

BASELINE_CLINIC_BP_MEASUREMENTS_FIELDS = {
    "date": "data_collection_date",
    "bpsysavoffice": "office_average_systolic_bp",
    "bpdiaavoffice": "office_average_diastolic_bp",
    "bpstandard": "bp_standardised_index",
    "bpobserved": "bp_observed_index",
}

HYPERTENSION_HISTORY_FIELDS = {
    "date": "data_collection_date",
    "htpresentationyear": "presentation_year",
    "htpresentationage": "presentation_age",
    "bpsyspres": "presentation_systolic_bp",
    "bpdiapres": "presentation_diastolic_bp",
    "bpsysref": "referral_systolic_bp",
    "bpdiaref": "referral_diastolic_bp",
    "smoking": "smoking_index",
    "cvdhistory": HypertensionHistoryOption,
    "cvdhistoryother": "cvd_history_other",
    "htpregnancy": "pregnancy_hypertension_index",
    "abpb": "abpm_index",
    "bpsysavday": "day_average_systolic_bp",
    "bpdiaavday": "day_average_diastolic_bp",
    "bpsysavnight": "night_average_systolic_bp",
    "bpdiaavnight": "night_average_diastolic_bp",
    "bpsysavoverall": "overall_average_systolic_bp",
    "bpdiaavoverall": "overall_average_diastolic_bp",
}

ADDITIONAL_INVESTIGATIONS_FIELDS = {
    "date": "assessment_date",
    "biochemadh": "biochemical_adherence_testing_index",
    "patfullyadh": "patient_fully_adherent_index",
    "cfpwv": "cf_pwv",
    "bapwv": "ba_pwv",
    "lvmi": "lvmi",
    "pwvdevice": "pwv_device",
    "csbp": "central_sbp",
    "cdbp": "central_dbp",
    "cap": "central_ap",
    "ca": "central_aix",
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
    39: (VasculitisDetail, VAS_DETAIL_FIELDS, {}),
    40: (VasculitisMeds, VAS_MEDS_FIELDS, VAS_MEDS_CASTS),
    41: (CakutClinicalPicture, CAKUT_FIELDS, {}),
    42: (CakutSurginter, CAKUT_SURG_FIELDS, {}),
    43: (LupusReview, LUPUS_REVIEW_FIELDS, LUPUS_REVIEW_CASTS),
    44: (NonRenalPath, NON_RENAL_PATH_FIELDS, {}),
    45: (CmvSummary, CMV_SUMMARY_FIELDS, {}),
    46: (CmvAntiviralResistance, CMV_ANTIVIRAL_RESISTANCE_FIELDS, {}),
    47: (CmvEpisodes, CMV_EPISODES_FIELDS, {}),
    48: (CoreDataCheck, CORE_DATA_CHECK_FIELDS, {}),
    49: (StatusChange, STATUS_CHANGE_FIELDS, {}),
    50: (SecondaryDiagnosisHypertension, SECONDARY_DIAGNOSIS_HYPERTENSION_FIELDS, {}),
    51: (HypertensionHistory, HYPERTENSION_HISTORY_FIELDS, {}),
    52: (BaselineClinicBpMeasurements, BASELINE_CLINIC_BP_MEASUREMENTS_FIELDS, {}),
    53: (AdditionalInvestigations, ADDITIONAL_INVESTIGATIONS_FIELDS, {}),
}


# dropped form 20 (rituximab-visits): 0 entries not copied, no radar 3 model
# dropped form 28 (test2): 0 entries not copied, no radar 3 model
# dropped form 30 (cysttest): 0 entries not copied, no radar 3 model
# dropped form 31 (cyst2): 0 entries not copied, no radar 3 model
# dropped form 32 (cyst3): 0 entries not copied, no radar 3 model
