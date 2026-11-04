"""RaDaR3: organisation tables

Moves the RaDaR2 organisation tables onto the RaDaR3 schema, keeping every row
and every id so foreign keys from tables not yet migrated stay valid.

    specialties        -> specialty            (renamed in place)
    consultants        -> consultant           (renamed in place)
    consents           -> consent              (renamed in place)
    groups (HOSPITAL)  -> hospital             (new table, rows copied with ids)
    groups (COHORT)    -> cohort               (new table, rows copied with ids)
    group_consultants  -> hospital_consultant  (renamed in place)

`groups` is NOT dropped here. ~40 RaDaR2 tables (group_patients, patient_numbers,
every source_group_id, ...) still point at it, and its OTHER / SYSTEM rows have no
RaDaR3 home. Drop it in the migration that repoints those tables.

Columns RaDaR3 does not have are dropped:
    consents.consent_type, consents.weight
Constraints RaDaR3 does not declare are dropped:
    consultants.gmc_number UNIQUE, group_consultants (group_id, consultant_id) UNIQUE,
    group_consultants.consultant_id ON DELETE/UPDATE CASCADE

Upgrade only.

Revision ID: radar3_organisation
Revises: <set to your current head>
Create Date: 2026-11-03
"""

from alembic import op
import sqlalchemy as sa

from radar_models.radar3 import Country, Ethnicity
import radar_models.radar2 as radar_2
revision = "9aaa2a094682"
down_revision = "131fa3437195"
branch_labels = None
depends_on = None


# --------------------------------------------------------------------------- #
def update_country():

    op.rename_table(
        radar_2.Country,Country.__tablename__,
    )
    op.alter_column(Country.__tablename__,column_name='label',new_column_name="country_name")
    op.alter_column(Country.__tablename__,column_name='code',new_column_name="id")

def update_ethnicities():

    op.rename_table(
        radar_2.Ethnicity,Ethnicity.__tablename__,
    )
    op.alter_column(
        Ethnicity.__tablename__,column_name='label',new_column_name="ethnicity_label"
    )



def upgrade():



def downgrade():
    raise NotImplementedError("Upgrade-only migration.")