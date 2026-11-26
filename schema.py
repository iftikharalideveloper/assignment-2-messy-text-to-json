from typing import Optional

from pydantic import BaseModel, Field


class Extracted(BaseModel):
    job_title: Optional[str] = Field(
        default=None, description="The title or position of the advertised job."
    )

    company: Optional[str] = Field(
        default=None, description="The name of the hiring company or organization."
    )

    location: Optional[str] = Field(
        default=None,
        description="The job location, including remote or hybrid details.",
    )

    employment_type: Optional[str] = Field(
        default=None,
        description="The employment type, such as full-time, part-time, or contract.",
    )

    salary: Optional[str] = Field(
        default=None, description="The advertised salary or compensation range."
    )

    experience: Optional[str] = Field(
        default=None, description="The required years or level of experience."
    )

    description: Optional[str] = Field(
        default=None, description="A summary of the advertised job responsibilities."
    )

    requirements: list[str] = Field(
        default_factory=list,
        description="A list of skills, qualifications, and job requirements.",
    )

    application_url: Optional[str] = Field(
        default=None, description="The URL provided for applying to the job."
    )

    contact_email: Optional[str] = Field(
        default=None, description="The recruitment contact email, if provided."
    )
