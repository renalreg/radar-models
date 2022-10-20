from sqlmodel import SQLModel, create_engine, Session

from radar_models.radar3 import *

# TODO: Convert to SQLite in memory once done with development. Maybe do something clever
# with a .env and have the ability to switch between testing and developing
engine = create_engine(
    "postgresql://postgres:password@localhost:5432/radar3", echo=True
)
SQLModel.metadata.create_all(engine)

session = Session(engine)

patient = Patient(patient_comment="what a guy", test=False, control=False)
session.add(patient)
session.commit()

classification_code = ClassificationCode(
    classification_system="ABC",
    classification_code="CBA",
    classification_label="This is a code",
)
session.add(classification_code)
session.commit()

cohort = Cohort(
    cohort_code="ABC", cohort_name="This cohort", cohort_short_name="cohort"
)
session.add(cohort)
session.commit()

country = Country(country_name="ABC", country_code="CBA")
session.add(country)
session.commit()

hospital = Hospital(
    hospital_code="ABC",
    hospital_name="The Big Bad Hospital",
    hospital_short_name="BBH",
    is_transplant_centre=True,
)
session.add(hospital)
session.commit()

alport_clinical_picture = AlportClinicalPicture(
    patient_id=1,
    date_of_picture=datetime.now(),
    deafness_state=1,
    deafness_date=datetime.strptime("16-01-1998", "%d-%m-%Y"),
    hearing_aid_date=date(2001, 9, 10),
)
session.add(alport_clinical_picture)
session.commit()

biomarker = Biomarker(biomarker_name="something", biomarker_type="that type")
session.add(biomarker)
session.commit()

biomarker_barcode = BiomarkerBarcode(
    patient_id=1,
    barcode="ABC123",
    sample_date=datetime.strptime("16-01-1998", "%d-%m-%Y"),
)
session.add(biomarker_barcode)
session.commit()

biomarker_sample = BiomarkerSample(barcode_id=1, biomarker_sample_label="this thing")
session.add(biomarker_sample)
session.commit()

biomarker_result = BiomarkerResult(
    biomarker_id=1,
    biomarker_sample_id=1,
    biomarker_result_value=1.23456787,
    measure_unit="mg",
)
session.add(biomarker_result)
session.commit()
