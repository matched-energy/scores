from sqlmodel import SQLModel, Field
from typing import Optional
import datetime


class RegoRoBase(SQLModel):
    accreditation_no: str = Field(primary_key=True)
    start_certificate_idx: int = Field(primary_key=True)
    end_certificate_idx: int = Field(primary_key=True)
    status_date: datetime.date = Field(primary_key=True)
    delivery_start: datetime.date = Field(primary_key=True)
    delivery_end: datetime.date = Field(primary_key=True)
    current_holder_organisation_name: str = Field(primary_key=True)
    generating_station_agent_group: str
    station_tic: float
    country: str
    technology_group: str
    output_period: str
    no_of_certificates: int
    start_certificate_no: str
    end_certificate_no: str
    mwh_per_certificate: float
    issue_date: datetime.date
    certificate_status: str
    company_registration_number: Optional[str] = None
    generation_type: Optional[str] = None
    certificate_type: str

class Rego(RegoRoBase, table=True):
    __tablename__ = "rego"

class Ro(RegoRoBase, table=True):
    __tablename__ = "ro"
    certificate_type: str = Field(primary_key=True)