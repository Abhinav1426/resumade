from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime, timezone # Import timezone
from uuid import UUID as PyUUID, uuid4 # For UUID type

# Helper to get current time in ISO format
def now_iso():
    return datetime.now(timezone.utc).isoformat()

class MetadataResponse(BaseModel):
    prod_count: int = 0
    id: str = ""
    class Config:
        extra = "allow"  # Accept any extra fields in the response

# --- Models from your JSON Schema (largely the same) ---
# (Keep your existing Social, PersonalInformation, Experience, etc. models here)
# ... (Your existing models from previous response)
class Social(BaseModel):
    name: str
    link: str

class PersonalInformation(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: str
    socials: Optional[List[Social]] = None

class Experience(BaseModel):
    designation: str
    companyName: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    caption: Optional[str] = None
    points: Optional[List[str]] = None

class EducationItem(BaseModel):
    institution: str
    degree: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    gpa: str
    gpa_out_off: str

class SkillItemDetail(BaseModel):
    name: str
    data: List[str]

class ExternalSource(BaseModel):
    name: str
    link: str

class Project(BaseModel):
    projectName: str
    caption: Optional[str] = None
    location: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    url: Optional[str] = None
    projectDetails: List[str]
    externalSources: Optional[List[ExternalSource]] = None
    technologiesUsed: Optional[List[str]] = None

class Certification(BaseModel):
    name: str
    issuing_organization: str
    issue_date: str
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None

class Award(BaseModel):
    name: str
    type: str
    location: str
    date: str # Consider using date type
    description: str

class ExtracurricularAchievement(BaseModel):
    name: str
    type: str
    location: str
    date: str # Consider using date type
    description: str

class LanguageItem(BaseModel):
    language: str
    proficiency: str


class ResumeSchema(BaseModel):
    personal_information: Optional[PersonalInformation] = None
    summary: Optional[str] = None
    experiences: Optional[List[Experience]] = None
    education: Optional[List[EducationItem]] = None
    skills: Optional[List[SkillItemDetail]] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    awards: Optional[List[Award]] = None
    extracurricular_achievements: Optional[List[ExtracurricularAchievement]] = Field(default=None, alias="extracurricular/achievements")
    languages: Optional[List[LanguageItem]] = None


    class Config:
        populate_by_name = True


# --- User and Auth Models for DynamoDB ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserInDB(UserBase): # Represents user data as stored in/retrieved from DynamoDB
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    hashed_password: str
    disabled: bool = False
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

class UserPublic(UserBase): # For API responses (excluding sensitive info)
    user_id: str
    disabled: bool
    created_at: str
    # updated_at: str # Optional to include

# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
# class TokenData(BaseModel):
#     username: Optional[str] = None # Subject of the token

class UserSummary(BaseModel):
    user_id: str
    name: str
    email: EmailStr

class UsersResponse(BaseModel):
    count: int
    users: List[UserSummary]

# --- Resume Models for API & DynamoDB ---
class ResumeBase(BaseModel):
    title: str = Field(default="Untitled Resume", max_length=100)
    resume_data: Optional[ResumeSchema] = None # The actual JSON resume content

class ResumeCreate(ResumeBase):
    pass # Inherits all fields

class ResumeUpdate(BaseModel): # For partial updates
    title: Optional[str] = Field(None, max_length=100)
    resume_data: Optional[ResumeSchema] = None

class ResumeInDB(ResumeBase): # Represents resume data in/from DynamoDB
    user_id: str # Partition Key
    resume_id: str = Field(default_factory=lambda: str(uuid4())) # Sort Key
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

class ResumePublic(ResumeBase): # For API responses
    user_id: str
    resume_id: str
    created_at: str
    updated_at: str


# --- Other API Specific Models ---
class JobDetailsInput(BaseModel):
    job_link: Optional[str] = None
    job_description: Optional[str] = None
    custom_prompt: Optional[str] = None
    update_existing_resume: Optional[bool] = False # Whether to update an existing resume with this job description
    title: str = Field(default="Untitled Resume", max_length=100)

class UserAppMetadata(BaseModel): # Example for user-specific app settings
    user_id: str
    username: str
    email: EmailStr
    preferences: Optional[Dict[str, Any]] = None


# --- LinkedIn Job Scraping Models ---
class JobData(BaseModel):
    """Structured model for LinkedIn job data"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    posted_or_reposted: Optional[str] = None
    people_clicked_apply: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields that might be scraped

class LinkedInJobRequest(BaseModel):
    linkedin_url: str = Field(..., description="LinkedIn job URL to scrape")

class LinkedInJobResponse(BaseModel):
    job_id: str
    job_data: Optional[JobData] = None
    scraped_url: str
    success: bool
    message: Optional[str] = None