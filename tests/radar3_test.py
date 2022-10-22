from copyreg import dispatch_table
from sqlmodel import SQLModel, create_engine, Session
from faker import Faker

from radar_models.radar3 import *

# TODO: Convert to SQLite in memory once done with development. Maybe do something clever
# with a .env and have the ability to switch between testing and developing
engine = create_engine("postgresql://postgres:password@localhost:5432/radar3")
SQLModel.metadata.create_all(engine)
session = Session(engine)

f = Faker()

# --- No Foreign Keys --- #

session.add(Biomarker(biomarker_name=f.word(), biomarker_type=f.word()))

session.add(
    Cohort(
        cohort_code=f.text(max_nb_chars=5),
        cohort_name=f.text(max_nb_chars=20),
        cohort_short_name=f.word(),
    )
)

session.add(
    Consent(
        consent_code=f.text(max_nb_chars=5),
        consent_label=f.text(max_nb_chars=20),
        is_paediatric=f.pybool(),
        release_date=f.date(),
        consent_url=f.url(),
        is_retired=f.pybool(),
    )
)

session.add(Country(country_name=f.country(), country_code=f.country_code()))

session.add(
    ClassificationCode(
        classification_system=f.word(),
        classification_code=f.pyint(),
        classification_label=f.word(ext_word_list=["ICD", "SNOMED", "EDTA"]),
    )
)

session.add(DataSource(data_source_name=f.word()))

session.add(Drug(drug_name=f.word()))

session.add(DrugGroup(drug_group=f.word(), parent_drug_group_id=1))

session.add(Ethnicity(ethnicity_code=f.country_code(), ethnicity_label=f.country()))

session.add(
    Hospital(
        hospital_code=f.text(max_nb_chars=5),
        hospital_name=f.word(),
        hospital_short_name=f.word(),
        is_transplant_centre=f.pybool(),
    )
)

session.add(Nationality(nationality_label=f.country()))

session.add(
    Patient(patient_comment=f.sentence(nb_words=5), test=f.pybool(), control=f.pybool())
)

session.add(Specialty(specialty=f.word()))

session.add(Diagnosis(diagnosis_name=f.word(), is_retired=f.pybool()))

session.add(Relation(relationship=f.word()))

session.commit()

# # --- Foreign Keys Included --- #

session.add(
    AlportClinicalPicture(
        patient_id=1,
        date_of_picture=f.date(),
        deafness_index=1,
        deafness_date=f.date(),
        hearing_aid_date=f.date(),
    )
)

session.add(
    BiomarkerBarcode(
        patient_id=1,
        barcode=f.ean(length=8),
        sample_date=f.date_time(),
    )
)

session.add(
    BiomarkerSample(
        barcode_id=1,
        biomarker_sample_label=f.word(),
    )
)

session.commit()

session.add(
    BiomarkerResult(
        biomarker_id=1,
        biomarker_sample_id=1,
        biomarker_result_value=f.pyfloat(left_digits=1, right_digits=3, positive=True),
        measure_unit=f.word(ext_word_list=["mg", "ng", "ml"]),
    )
)

session.add(
    Consultant(
        first_name=f.first_name(),
        last_name=f.last_name(),
        email=f.email(),
        telephone_number=f.word(),
        gmc_number=f.pyint(),
        specialty_id=1,
    )
)

session.add(CountryEthnicity(ethnicity_id=1, country_id=1))

session.add(CountryNationality(nationality_id=1, country_id=1))

session.add(
    CurrentMedication(
        patient_id=1,
        cohort_id=1,
        drug_id=1,
        data_source_id=1,
        recorded_date=f.date(),
        dose_quantity=f.pyfloat(left_digits=1, right_digits=3, positive=True),
        dose_unit=f.word(ext_word_list=["mg", "ng", "ml"]),
        frequency=f.word(),
        route=f.word(),
        drug_text=f.word(),
        dose_text=f.word(),
    )
)

session.add(DiagnosisCode(diagnosis_id=1, classification_code_id=1))

session.add(
    Dialysis(
        patient_id=1,
        hospital_id=1,
        data_source_id=1,
        timeline_start=f.date(),
        timeline_end=f.date(),
        modality=f.pyint(max_value=20),
    )
)

session.add(
    FamilyHistory(
        patient_id=1,
        cohort_id=1,
        is_parental_consanguinity=f.pybool(),
        is_family_history=f.pybool(),
        other_family_history=f.sentence(nb_words=10),
    )
)

session.add(
    FamilyHistoryRelation(family_history_id=1, relation_id=1, relative_patient_id=1)
)

session.commit()
