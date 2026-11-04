"""Disease-specific assessments."""

from datetime import date

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel

from radar_models.radar3.shared import BigIntPK, HasId

# --- AdverseEvents --- #


class AdverseEventBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    review_date: date
    has_hospitalisation: bool
    has_adverse_event: bool
    new_onset_cancer: date
    is_cancer_cause: bool
    thromboembolism: date
    caused_venous_thrombo_embolism_index: int
    myocardial_infarction: date
    caused_acute_myocardial_infarction_index: int
    stroke: date
    caused_stroke_index: int
    ischaemic_attack: date
    caused_ischaemic_attack_index: int
    other_adverse_event: date
    other_toxicity: str
    caused_other_index: int
    date_of_death: date
    cause_of_death: str


class AdverseEvent(AdverseEventBase, BigIntPK, table=True):
    __tablename__ = "adverse_event"


class AdverseEventRead(AdverseEventBase, HasId):
    pass


# --- AlportAssessment --- #


class AlportAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    deafness_index: int
    deafness_date: date | None = None
    hearing_aid_date: date | None = None


class AlportAssessment(AlportAssessmentBase, BigIntPK, table=True):
    __tablename__ = "alport_assessment"


class AlportAssessmentRead(AlportAssessmentBase, HasId):
    pass


# --- CalciphylaxisAssessment --- #


class CalciphylaxisAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_lesion: bool
    lesion_location: str
    has_infection: bool
    infection_location: str


class CalciphylaxisAssessment(CalciphylaxisAssessmentBase, BigIntPK, table=True):
    __tablename__ = "calciphylaxis_assessment"


class CalciphylaxisAssessmentRead(CalciphylaxisAssessmentBase, HasId):
    pass


# --- CalciphylaxisAssessmentOption --- #


class CalciphylaxisAssessmentOptionBase(SQLModel):
    calciphylaxis_assessment_id: int = Field(
        foreign_key="calciphylaxis_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class CalciphylaxisAssessmentOption(
    CalciphylaxisAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "calciphylaxis_assessment_option"


class CalciphylaxisAssessmentOptionRead(CalciphylaxisAssessmentOptionBase, HasId):
    pass


# --- CancerTumours --- #


class CancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    tumour_type: str
    other_tumour_name: str
    diagnosis_date: date
    tumour_count: int
    cns_image: str
    progression_date: date
    t_cat: str
    n_cat: str
    m_cat: str
    radiologic_tumor_size: str
    pathologic_tumor_size: str
    tumor_location: str


class CancerTumour(CancerTumourBase, BigIntPK, table=True):
    __tablename__ = "cancer_tumour"


class CancerTumourRead(CancerTumourBase, HasId):
    pass


# --- CKDAfricaGenetic --- #


class CKDAfricaGeneticBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    sickle_cell: str
    other_sickle_cell: str
    apol_1: str


class CKDAfricaGenetic(CKDAfricaGeneticBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_genetic"


class CKDAfricaGeneticRead(CKDAfricaGeneticBase, HasId):
    pass


# --- CKDAfricaRiskFactor --- #


class CKDAfricaRiskFactorBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    preterm_birth: str
    low_birth_weight: str
    malnutrition: str
    hospital_malnutrition: str


class CKDAfricaRiskFactor(CKDAfricaRiskFactorBase, BigIntPK, table=True):
    __tablename__ = "ckd_africa_risk_factor"


class CKDAfricaRiskFactorRead(CKDAfricaRiskFactorBase, HasId):
    pass


# --- CystinosisAdultVisit --- #


class CystinosisAdultVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    cystinosis_adult_visit_number: int
    visit_date: date
    urine_measurement: str
    urine_output: float
    voiding_overnight: str
    continent_day: str
    fluid_intake: float
    admission_dehydration: int
    constipation: str
    diarrhea: str
    nausea: str
    vomiting: str
    rickets: str
    kyphoscoliosis: str
    fractures: str
    muscle_strength: str
    ankle_strength: float
    elbow_strength: float
    hand_strength: float
    hip_strength: float
    knee_strength: float
    shoulder_strength: float
    wrist_strength: float
    swallowing_difficulties: str
    swallowing_difficulties_detail: str
    joint_surgery: str
    visual_impairment: str
    photophobia: str
    photophobia_grade: str
    keratoplasty_date: date
    acuity: str
    gahl_score: str
    intraocular_pressure_r: str
    intraocular_pressure_l: str
    fev1: float
    vc: float
    snip: float
    seizure: str
    headache: str
    muscle_weakness: str
    learning_difficulties: str
    cognitive_difficulties: str
    cognitive_difficulties_score: str
    movement_disorder: str
    intracranial_hypertension: str
    diabetes: str
    thyroid: str
    hypothyroidism: str
    tanner_stage: str
    wc_cystine: float
    wc_cystine_date: date
    wc_cystine_time: str
    cysteamine_last_dose: int
    cysteamine_effects: str


class CystinosisAdultVisit(CystinosisAdultVisitBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_adult_visit"


class CystinosisAdultVisitRead(CystinosisAdultVisitBase, HasId):
    pass


# --- CystinosisPaedVisit --- #


class CystinosisPaedVisitBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    cystinosis_paed_visit_number: int
    visit_date: date
    height: float
    weight: float
    urine_measurement: str
    urine_output: float
    voiding_overnight: str
    continence_day: str
    fluid_intake: float
    admission_dehydration: int
    constipation: str
    diarrhea: str
    nausea: str
    vomiting: str
    failure_to_thrive: str
    enteral_feeding: str
    feeding_start_date_1: date
    feeding_end_date_1: date
    feeding_start_date_2: date
    feeding_end_date_2: date
    feeding_start_date_3: date
    feeding_end_date_3: date
    normal_food_orally: str
    supplements: str
    growth_hormone_treatment: str
    rickets: str
    kyphoscoliosis: str
    fractures: str
    joint_surgery: str
    muscle_strength: str
    swallowing_difficulties: str
    nose_snoring: str
    tonsillectomy_date: date
    sight_impairment: str
    severe_sight_impairment: str
    photophobia: str
    photophobia_grade: str
    keratoplasty_date: date
    acuity: str
    gahl_score: str
    intraocular_pressure_r: str
    intraocular_pressure_l: str
    fev1: float
    vc: float
    snip: float
    seizure: str
    headache: str
    muscle_weakness: str
    learning_difficulties: str
    cognitive_difficulties: str
    movement_disorder: str
    intracranial_hypertension: str
    diabetes: str
    thyroid: str
    hypothyroidism: str
    tanner_stage: str
    wc_cystine: float
    wc_cystine_date: date
    wc_cystine_time: str
    cysteamine_last_dose: int
    cysteamine_effects: str


class CystinosisPaedVisit(CystinosisPaedVisitBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_paed_visit"


class CystinosisPaedVisitRead(CystinosisPaedVisitBase, HasId):
    pass


# --- CystinosisPaedVisitOption --- #


class CystinosisPaedVisitOptionBase(SQLModel):
    cystinosis_paed_visit_id: int = Field(
        foreign_key="cystinosis_paed_visit.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class CystinosisPaedVisitOption(CystinosisPaedVisitOptionBase, BigIntPK, table=True):
    __tablename__ = "cystinosis_paed_visit_option"


class CystinosisPaedVisitOptionRead(CystinosisPaedVisitOptionBase, HasId):
    pass


# --- DentAndLoweAssessment --- #


class DentAndLoweAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    aetiology: str
    causative_agent: str
    other_agent: str
    extra_involvement: str
    other_extra_involvement: str


class DentAndLoweAssessment(DentAndLoweAssessmentBase, BigIntPK, table=True):
    __tablename__ = "dent_and_lowe_assessment"


class DentAndLoweAssessmentRead(DentAndLoweAssessmentBase, HasId):
    pass


# --- DentAndLoweAssessmentOption --- #


class DentAndLoweAssessmentOptionBase(SQLModel):
    dent_and_lowe_assessment_id: int = Field(
        foreign_key="dent_and_lowe_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class DentAndLoweAssessmentOption(
    DentAndLoweAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "dent_and_lowe_assessment_option"


class DentAndLoweAssessmentOptionRead(DentAndLoweAssessmentOptionBase, HasId):
    pass


# --- EthnicOrigin --- #


class EthnicOriginBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    country_of_birth: str
    year_of_emigration: int
    ethnic_origin: str


class EthnicOrigin(EthnicOriginBase, BigIntPK, table=True):
    __tablename__ = "ethnic_origin"


class EthnicOriginRead(EthnicOriginBase, HasId):
    pass


# --- FuanAssessment --- #


class FuanAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    picture_date: date
    has_gout: bool
    gout_date: date | None = None
    has_family_gout: bool
    thp: str | None = None
    has_uti: bool
    fuan_comments: str | None = None


class FuanAssessment(FuanAssessmentBase, BigIntPK, table=True):
    __tablename__ = "fuan_assessment"


class FuanAssessmentRead(FuanAssessmentBase, HasId):
    pass


# --- Hnf1bAssessment --- #


class Hnf1bAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_single_kidney: bool
    has_hyperuricemia_gout: bool
    has_genital_malformation: bool
    genital_malformation_details: str
    has_familial_cystic_disease: bool
    has_hypertension: bool


class Hnf1bAssessment(Hnf1bAssessmentBase, BigIntPK, table=True):
    __tablename__ = "hnf1b_assessment"


class Hnf1bAssessmentRead(Hnf1bAssessmentBase, HasId):
    pass


# --- HSPAssessment --- #


class HSPAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_haematuria: bool
    is_nephrotic: bool
    mest_c_m: str
    mest_c_e: str
    mest_c_s: str
    mest_c_t: str
    mest_c_c: str


class HSPAssessment(HSPAssessmentBase, BigIntPK, table=True):
    __tablename__ = "hsp_assessment"


class HSPAssessmentRead(HSPAssessmentBase, HasId):
    pass


# --- IGAResearch --- #


class IGAResearchBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date


class IGAResearch(IGAResearchBase, BigIntPK, table=True):
    __tablename__ = "iga_research"


class IGAResearchRead(IGAResearchBase, HasId):
    pass


# --- IGAResearchOption --- #


class IGAResearchOptionBase(SQLModel):
    iga_research_id: int = Field(foreign_key="iga_research.id", sa_type=BigInteger)
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class IGAResearchOption(IGAResearchOptionBase, BigIntPK, table=True):
    __tablename__ = "iga_research_option"


class IGAResearchOptionRead(IGAResearchOptionBase, HasId):
    pass


# --- InsAssessment --- #


class InsAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_oedema: bool
    has_hypovoloemia: bool
    has_fever: bool
    has_thrombosis: bool
    has_peritonitis: bool
    has_pulmonary_oedema: bool
    has_hypertension: bool
    has_rash: bool
    rash_details: str | None = None
    has_infection: bool
    infection_details: str | None = None
    has_ophthalmoscopy: bool
    ophthalmoscopy_details: str | None = None
    ins_comments: str | None = None


class InsAssessment(InsAssessmentBase, BigIntPK, table=True):
    __tablename__ = "ins_assessment"


class InsAssessmentRead(InsAssessmentBase, HasId):
    pass


# --- InsRelapse --- #


class InsRelapseBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_relapse: date
    kidney_type: str | None = None
    viral_trigger: str | None = None
    immunisation_trigger: str | None = None
    other_trigger: str | None = None
    has_high_dose_oral_prednisolone: bool
    has_iv_methyl_prednisolone: bool
    date_of_remission: date | None = None
    remission_type: str | None = None
    peak_acr: float | None = None
    peak_pcr: float | None = None
    remission_acr: float | None = None
    remission_pcr: float | None = None
    peak_protein_dipstick: str | None = None
    remission_protein_dipstick: str | None = None
    is_relapse_sample_taken: bool


class InsRelapse(InsRelapseBase, BigIntPK, table=True):
    __tablename__ = "ins_relapse"


class InsRelapseRead(InsRelapseBase, HasId):
    pass


# --- MpgnAssessment --- #


class MpgnAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    date_of_picture: date
    has_oedema: bool
    has_hypertension: bool
    has_urticaria: bool
    has_partial_lipodystrophy: bool
    has_infection: bool
    infection_details: str | None = None
    has_ophthalmoscopy: bool
    ophthalmoscopy_details: str | None = None
    mpgn_comments: str | None = None


class MpgnAssessment(MpgnAssessmentBase, BigIntPK, table=True):
    __tablename__ = "mpgn_assessment"


class MpgnAssessmentRead(MpgnAssessmentBase, HasId):
    pass


# --- RenalCancerGenetics --- #


class RenalCancerGeneticsBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_bap1_test: bool
    bap1_variant: str
    bap1_variant_status: str
    has_fh_test: bool
    fh_variant: str
    fh_variant_status: str
    has_flcn_test: bool
    flcn_variant: str
    flcn_variant_status: str
    has_met_test: bool
    met_variant: str
    met_variant_status: str
    has_mitf_test: bool
    mitf_variant: str
    mitf_variant_status: str
    has_pten_test: bool
    pten_variant: str
    pten_variant_status: str
    has_sdha_test: bool
    sdha_variant: str
    sdha_variant_status: str
    has_sdhb_test: bool
    sdhb_variant: str
    sdhb_variant_status: str
    has_sdhc_test: bool
    sdhc_variant: str
    sdhc_variant_status: str
    has_sdhd_test: bool
    sdhd_variant: str
    sdhd_variant_status: str
    has_vhl_test: bool
    vhl_variant: str
    vhl_variant_status: str
    has_other_test: bool
    other_test_name: str
    other_variant: str
    other_variant_status: str


class RenalCancerGenetics(RenalCancerGeneticsBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics"


class RenalCancerGeneticsRead(RenalCancerGeneticsBase, HasId):
    pass


# --- RenalCancerGeneticsOption --- #


class RenalCancerGeneticsOptionBase(SQLModel):
    renal_cancer_genetics_id: int = Field(
        foreign_key="renal_cancer_genetics.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RenalCancerGeneticsOption(RenalCancerGeneticsOptionBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_genetics_option"


class RenalCancerGeneticsOptionRead(RenalCancerGeneticsOptionBase, HasId):
    pass


# --- RenalCancerTumour --- #


class RenalCancerTumourBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    tumor_type: str
    assessment_date: date
    cns_imaging_method: str
    progression_date: date
    t_cat: str
    n_cat: str
    m_cat: str
    rt_size: str
    pt_size: str
    t_loc: str


class RenalCancerTumour(RenalCancerTumourBase, BigIntPK, table=True):
    __tablename__ = "renal_cancer_tumour"


class RenalCancerTumourRead(RenalCancerTumourBase, HasId):
    pass


# --- RituximabBaselineAssessment --- #


class RituximabBaselineAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    hospital_id: int | None = Field(
        default=None, foreign_key="hospital.id", sa_type=BigInteger
    )
    data_source_id: int | None = Field(
        default=None, foreign_key="data_source.id", sa_type=BigInteger
    )
    assessment_date: date
    nephropathy: str | None = None
    has_steroids: bool
    other_previous_treatment: str | None = None
    has_past_remission: bool
    performance_status_index: int | None = None
    has_comorbidities: bool


class RituximabBaselineAssessment(
    RituximabBaselineAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_assessment"


class RituximabBaselineAssessmentRead(RituximabBaselineAssessmentBase, HasId):
    pass


# --- RituximabBaselineAssessmentOption --- #


class RituximabBaselineAssessmentOptionBase(SQLModel):
    rituximab_baseline_assessment_id: int = Field(
        foreign_key="rituximab_baseline_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RituximabBaselineAssessmentOption(
    RituximabBaselineAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_assessment_option"


class RituximabBaselineAssessmentOptionRead(
    RituximabBaselineAssessmentOptionBase, HasId
):
    pass


# --- RituximabBaselinePreviousTreatment --- #


class RituximabBaselinePreviousTreatmentBase(SQLModel):
    rituximab_baseline_assessment_id: int = Field(
        foreign_key="rituximab_baseline_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)
    treatment_start_date: date
    treatment_end_date: date | None = None


class RituximabBaselinePreviousTreatment(
    RituximabBaselinePreviousTreatmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_baseline_previous_treatment"


class RituximabBaselinePreviousTreatmentCreate(RituximabBaselinePreviousTreatmentBase):
    pass


class RituximabBaselinePreviousTreatmentRead(
    RituximabBaselinePreviousTreatmentBase, HasId
):
    pass


# --- RituximabCriterion --- #


class RituximabCriteriaBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    has_criterion_1: bool
    has_criterion_2: bool
    has_criterion_3: bool
    has_criterion_4: bool
    has_criterion_5: bool
    has_criterion_6: bool
    has_criterion_7: bool
    has_alkylating_complication: bool
    has_alkylating_failure_monitoring_requirements: bool
    has_cancer: bool
    has_cni_failure_monitoring_requirements: bool
    has_cni_therapy_complication: bool
    has_diabetes: bool
    has_drug_associated_toxicity: bool
    has_fall_in_egfr: bool
    has_hypersensitivity: bool
    has_risk_factors: bool
    has_ongoing_severe_disease: bool
    has_threatened_fertility: bool
    has_mood_disturbance: bool
    has_osteoporosis_osteopenia: bool
    has_previous_hospitalization: bool


class RituximabCriteria(RituximabCriteriaBase, BigIntPK, table=True):
    __tablename__ = "rituximab_criteria"


class RituximabCriteriaRead(RituximabCriteriaBase, HasId):
    pass


# --- RituximabFollowUpAssessment --- #


class RituximabFollowUpAssessmentBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    visit_date: date
    rituximab_follow_up_visit: str
    performance: str
    transplant: str
    haemodialysis: str
    peritoneal_dialysis: str
    immunosuppression: str
    ciclosporin_administered: date
    tacrolimus_administered: date
    cyclophosphamide_administered: date
    chlorambucil_administered: date
    prednisolone_administered: date
    rituximab_administered: date
    immunosuppression_comments: str


class RituximabFollowUpAssessment(
    RituximabFollowUpAssessmentBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_follow_up_assessment"


class RituximabFollowUpAssessmentRead(RituximabFollowUpAssessmentBase, HasId):
    pass


# --- RituximabFollowUpAssessmentOption --- #


class RituximabFollowUpAssessmentOptionBase(SQLModel):
    rituximab_follow_up_assessment_id: int = Field(
        foreign_key="rituximab_follow_up_assessment.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RituximabFollowUpAssessmentOption(
    RituximabFollowUpAssessmentOptionBase, BigIntPK, table=True
):
    __tablename__ = "rituximab_follow_up_assessment_option"


class RituximabFollowUpAssessmentOptionRead(
    RituximabFollowUpAssessmentOptionBase, HasId
):
    pass


# --- RituximabToxicity --- #


class RituximabToxicityBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    assessment_date: date
    drug_name: str
    other_drug: str
    dose: float | None = None
    retreatment: str
    toxicity: str | None = None
    other_toxicity: str | None = None


class RituximabToxicity(RituximabToxicityBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity"


class RituximabToxicityRead(RituximabToxicityBase, HasId):
    pass


# --- RituximabToxicityOption --- #


class RituximabToxicityOptionBase(SQLModel):
    rituximab_toxicity_id: int = Field(
        foreign_key="rituximab_toxicity.id", sa_type=BigInteger
    )
    option_id: int = Field(foreign_key="option.id", sa_type=BigInteger)


class RituximabToxicityOption(RituximabToxicityOptionBase, BigIntPK, table=True):
    __tablename__ = "rituximab_toxicity_option"


class RituximabToxicityOptionRead(RituximabToxicityOptionBase, HasId):
    pass


# --- SaltWastingClinicalFeature --- #


class SaltWastingClinicalFeatureBase(SQLModel):
    patient_id: int = Field(foreign_key="patient.id", sa_type=BigInteger)
    is_normal_pregnancy: bool
    abnormal_pregnancy_text: str | None = None
    has_neurological_problems: bool
    has_seizures: bool
    has_abnormal_gait: bool
    has_deafness: bool
    has_other_neurological_problem: bool
    other_neurological_problem_text: str | None = None
    has_joint_problems: bool
    joint_problems_age: int | None = None
    has_x_ray_abnormalities: bool
    has_chondrocalcinosis: bool
    has_other_x_ray_abnormality: bool
    other_x_ray_abnormality_text: str | None = None


class SaltWastingClinicalFeature(SaltWastingClinicalFeatureBase, BigIntPK, table=True):
    __tablename__ = "salt_wasting_clinical_feature"


class SaltWastingClinicalFeatureRead(SaltWastingClinicalFeatureBase, HasId):
    pass
