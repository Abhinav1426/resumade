import io
import uvicorn
from mangum import Mangum

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, APIRouter, Path, Header, Query, Body
from fastapi.responses import StreamingResponse
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Annotated, Optional
from database.model import (
    UserPublic, JobDetailsInput, UserAppMetadata,
    ResumeCreate, ResumeUpdate, ResumePublic, ResumeSchema, ResumeInDB,
    UserCreate as UserModelCreate, UserInDB as UserInDBModel, UsersResponse, MetadataResponse, ResumeBase,
    LinkedInJobRequest, LinkedInJobResponse, JobData
)
import database.crud as crud
from utils import auth
import re
# --- Authentication Models ---
from pydantic import BaseModel


# from services import llm_service, pdf_service
from core.config import settings
from services import ResumeBuilder, JsonToPDFBuilder
from utils import FileOperations, WebScraper




app = FastAPI(
    title="Resumade.in",
    version="1.0.0",
    description="An AI-powered resume builder and job application assistant",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "qwert12345")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Hide docs endpoints from OpenAPI schema
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", title=app.title)

@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)

handler = Mangum(app)  # For AWS Lambda compatibility

# --- Routers ---
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
user_router = APIRouter(prefix="/users", tags=["Users"])
resume_router = APIRouter(tags=["Resumes"])  # Will be nested under users
linkedin_router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])


class LoginRequest(BaseModel):
    identifier: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user: UserPublic
    access_token: str
    token_type: str
    expires_at: str

class LogoutResponse(BaseModel):
    message: str
# --- Authentication Endpoints ---



@auth_router.post("/login", response_model=LoginResponse)
async def login_endpoint(login_request: LoginRequest):
    identifier = login_request.identifier
    password = login_request.password
    if not identifier or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifier and password are required")
    user = await crud.get_user_by_username_or_mail(identifier)

    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is disabled")

    access_token, expires_at = auth.create_jwt_token(user.user_id)
    return LoginResponse(
        message="Login successful",
        user=UserPublic.model_validate(user.model_dump()),
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )

@auth_router.post("/logout", response_model=LogoutResponse)
async def logout_endpoint():
    return LogoutResponse(message="Logout successful. Please discard your access token.")

app.include_router(auth_router)

# --- User Endpoints ---
@user_router.post(".create", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_new_user_endpoint(user_create_payload: UserModelCreate):
    try:
        created_user_in_db = await crud.create_user(user_data=user_create_payload)
        if not created_user_in_db:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")
        return UserPublic.model_validate(created_user_in_db.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Unexpected error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred during user creation.")


@user_router.get("/{user_id}", response_model=UserPublic)
async def get_user_details_endpoint(user_id: str = Path(..., description="The ID of the user to retrieve"), current_user=Depends(auth.get_current_user)):
    user_db = await crud.get_user_by_id(user_id=user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user_db.model_dump())


@user_router.get("/{user_id}/metadata", response_model=UserAppMetadata)
async def get_user_metadata_endpoint(user_id: str = Path(..., description="The ID of the user"), current_user=Depends(auth.get_current_user)):
    user_meta_dict = await crud.get_user_app_metadata(user_id=user_id)  # Use the renamed function
    if not user_meta_dict:
        # Check if user exists at all
        user_exists = await crud.get_user_by_id(user_id)
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found, so no metadata available.")
        # If user exists but metadata function returned None, construct a default or indicate partial data
        # For this example, we assume if user_exists, crud.get_user_app_metadata should have worked or returned something
        # based on user_exists fields. This path might indicate an issue in get_user_app_metadata if user exists.
        raise HTTPException(status_code=404, detail="User metadata not found or could not be constructed.")
    return UserAppMetadata(**user_meta_dict)


def clean_none_strings(obj):
    if isinstance(obj, dict):
        return {k: clean_none_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_none_strings(v) for v in obj]
    elif obj is None:
        return ""
    return obj


@user_router.get(".getall", response_model=UsersResponse, status_code=200)
async def get_all_users_endpoint(master: str = Header(None),
                                 _=Depends(lambda master=Header(None): check_master_header(master))):
    result = await crud.get_all_users_name_email()
    return result


def check_master_header(master: str):
    if master != "getmeall":
        raise HTTPException(status_code=403, detail="Forbidden: your not authorized to access this endpoint.")


@app.get("/metadata", response_model=MetadataResponse, status_code=200)
async def get_metadata_endpoint(env: str = Header(None)):
    result = await crud.get_and_update_metadata(env)
    # Ensure prod_count is always present in the response
    if "prod_count" not in result:
        result["prod_count"] = 0
    return result


# --- Resume Endpoints (Nested under /users/{user_id}/resumes) ---
@resume_router.post("/users/{user_id}/resumes/upload-and-create", response_model=ResumePublic,
                    status_code=status.HTTP_201_CREATED)
async def upload_resume_file_and_create_for_user(
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        title: Annotated[str, Form()] = "Uploaded Resume",
        resume_file: UploadFile = File(...)
):
    # Verify user exists first (optional, but good practice if not relying on FK constraints)
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")

    if not resume_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    contents = await resume_file.read()
    filename = resume_file.filename
    try:
        text = FileOperations().extract_text_from_file_bytes(contents, filename)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
        print(f"Extracted text from file: {text[:100]}...")  # Log first 100 chars for debugging
        resume_builder = ResumeBuilder('google')

        # TODO : Implement the actual LLM parsing logic here

        parsed_resume_pydantic: ResumeSchema = resume_builder.parse_file_to_json(
            text)  # Assuming this function exists and returns a ResumeSchema object
    except Exception as e:
        print(f"LLM parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume with LLM: {str(e)}")
    parsed_resume_pydantic = clean_none_strings(parsed_resume_pydantic)
    resume_to_create = ResumeCreate(title=title, resume_data=parsed_resume_pydantic)

    created_resume_db = await crud.create_resume(user_id=user_id, resume_in=resume_to_create)
    if not created_resume_db:
        raise HTTPException(status_code=500, detail="Could not save parsed resume.")
    return ResumePublic.model_validate(created_resume_db.model_dump())


@resume_router.get("/users/{user_id}/resumes", response_model=List[ResumePublic])
async def get_list_of_user_resumes_endpoint( user_id: str = Path(..., description="The ID of the user"),x_requried_data: Optional[bool] = Header(False),current_user=Depends(auth.get_current_user)):
    user = await crud.get_user_by_id(user_id)  # Optional: check if user exists
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    resumes_db_list = await crud.get_all_resumes_for_user(user_id=user_id,x_requried_data=x_requried_data)
    return [ResumePublic.model_validate(r.model_dump()) for r in resumes_db_list]


@resume_router.get("/users/{user_id}/resumes/{resume_id}", response_model=ResumePublic)
async def get_one_user_resume_json_endpoint(
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        resume_id: str = Path(..., description="The ID of the resume")
):
    resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found for this user")
    return ResumePublic(**resume_db.model_dump())


# For updating an existing resume (PUT)
@resume_router.put("/users/{user_id}/resumes/{resume_id}", response_model=ResumePublic)
async def update_user_resume_endpoint(
    resume_update_payload: ResumeUpdate = Body(...),  # Expecting a ResumeUpdate payload with resume_data
    user_id: str = Path(..., description="The ID of the user"),
    current_user=Depends(auth.get_current_user),
    resume_id: str = Path(..., description="The ID of the resume"),
    title: str = "Untitled Resume"
):
    updated_resume_db = await crud.update_resume(
        user_id=user_id, resume_id=resume_id, resume_update_data=resume_update_payload
    )
    if not updated_resume_db:
        raise HTTPException(status_code=404, detail="Resume not found or failed to update")
    return ResumePublic.model_validate(updated_resume_db.model_dump())

# For creating a new resume (POST)
@resume_router.post("/users/{user_id}/resumes", response_model=ResumePublic)
async def create_user_resume_endpoint(
    resume_update_payload: ResumeUpdate = Body(...),  # Expecting a ResumeUpdate payload with resume_data
    user_id: str = Path(..., description="The ID of the user"),
    current_user=Depends(auth.get_current_user),
    title: str = "Untitled Resume"
):
    user = await crud.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    resume_to_create = ResumeCreate(title=title, resume_data=resume_update_payload.resume_data or ResumeSchema())
    created_resume_db = await crud.create_resume(user_id=user_id, resume_in=resume_to_create)
    if not created_resume_db:
        raise HTTPException(status_code=500, detail="Could not create new resume.")
    return ResumePublic.model_validate(created_resume_db.model_dump())

@resume_router.post("/users/{user_id}/resumes/{resume_id}/tailor", response_model=ResumePublic)
async def tailor_resume_for_job_endpoint(
        job_details: JobDetailsInput,
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        resume_id: str = Path(..., description="The ID of the resume")
):
    existing_resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not existing_resume_db:
        raise HTTPException(status_code=404, detail="Resume to tailor not found for this user")

    existing_resume_pydantic = existing_resume_db.resume_data
    try:
        # Prepare job details object: if job_description is present, use its text; if job_link is present, fetch description from link
        job_details_text = None
        if getattr(job_details, "description", None):
            job_details_text = job_details.description
        elif getattr(job_details, "job_link", None):
            # Assume you have a function called fetch_job_description_from_link(link)
            job_details_text = WebScraper().linkedin_scrape_job_details(job_details.job_link).get("description", None)
            if not job_details_text:
                raise HTTPException(status_code=400, detail="Could not fetch job description from the provided link.")
        if not job_details_text:
            raise HTTPException(status_code=400, detail="Job description or job link is required for tailoring.")

        # Call the ResumeBuilder service to tailor the resume
        tailored_resume_pydantic: ResumeSchema = ResumeBuilder('google').build_resume_json(existing_resume_pydantic.model_dump(),job_details_text,getattr(job_details, "custom_prompt", None))
        #Checking if the tailored resume is empty or None
        if not tailored_resume_pydantic:
            raise HTTPException(status_code=400, detail="Tailored resume is empty or invalid.")

        # Check if update the existing resume or create a new one version
        if job_details.update_existing_resume:
            # Update the existing resume with the tailored data
            updated_resume_db = await crud.update_resume(
                user_id=user_id, resume_id=resume_id,
                resume_update_data=ResumeUpdate(title=existing_resume_db.title, resume_data=tailored_resume_pydantic)
            )
            if not updated_resume_db:
                raise HTTPException(status_code=500, detail="Failed to update existing resume with tailored data.")
            tailored_resume = ResumePublic.model_validate(updated_resume_db.model_dump())
        else:
            # Create a new resume version with the tailored data
            if job_details.title is None or job_details.title.strip() == "" or job_details.title == "Untitled Resume":
                existing_resume_db.title = f"{existing_resume_db.title} - Tailored"
            else:
                existing_resume_db.title = job_details.title
            new_resume_to_create = ResumeCreate(title=existing_resume_db.title,
                                                 resume_data=tailored_resume_pydantic)
            created_resume_db = await crud.create_resume(user_id=user_id, resume_in=new_resume_to_create)
            if not created_resume_db:
                raise HTTPException(status_code=500, detail="Failed to create new tailored resume.")
            tailored_resume = ResumePublic.model_validate(created_resume_db.model_dump())

    except Exception as e:
        print(f"LLM tailoring error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor resume with LLM: {str(e)}")
    return tailored_resume


@resume_router.get("/users/{user_id}/resumes/{resume_id}/download", response_class=StreamingResponse)
async def download_resume_as_pdf(
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        resume_id: str = Path(..., description="The ID of the resume")
):
    resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found for download by this user")

    try:
        # TODO : Implement the actual PDF generation logic here
        pdf_bytes: bytes = JsonToPDFBuilder().build(resume_db.resume_data.model_dump()) or b""   # Assuming this function exists and returns bytes
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    safe_title = "".join(c if c.isalnum() or c in (' ', '.', '-') else '_' for c in (resume_db.title or "resume"))
    filename = f"{safe_title.replace(' ', '_')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@resume_router.post("/users/{user_id}/resumes/onfly.download", response_class=StreamingResponse)
async def onfly_download_resume_as_pdf(
        resume_payload:ResumeUpdate = Body(...),  # Expecting a ResumeUpdate payload with resume_data
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        
        
):
    if not resume_payload or not resume_payload.resume_data:
        raise HTTPException(status_code=404, detail="No resume data found for download")

    try:
        # TODO : Implement the actual PDF generation logic here
        pdf_bytes: bytes = JsonToPDFBuilder().build(resume_payload.resume_data.model_dump()) or b""   # Assuming this function exists and returns bytes
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    safe_title = "".join(c if c.isalnum() or c in (' ', '.', '-') else '_' for c in (resume_payload.title or "resume"))
    filename = f"{safe_title.replace(' ', '_')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@resume_router.delete("/users/{user_id}/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_endpoint(
        user_id: str = Path(..., description="The ID of the user"),
        current_user=Depends(auth.get_current_user),
        resume_id: str = Path(..., description="The ID of the resume")
):
    deleted = await crud.delete_resume(user_id=user_id, resume_id=resume_id)
    if not deleted:  # crud.delete_resume now returns False if ConditionalCheckFailed (item not found)
        raise HTTPException(status_code=404, detail="Resume not found or failed to delete")
    return None


# --- LinkedIn Job Scraping Endpoints ---
def extract_linkedin_job_id(url: str) -> Optional[str]:
    """
    Extract job ID from LinkedIn URLs.
    Supports patterns like:
    - https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253720687
    - https://www.linkedin.com/jobs/view/4253720687
    """
    import re
    
    # Pattern 1: currentJobId parameter
    current_job_pattern = r'currentJobId=(\d+)'
    match = re.search(current_job_pattern, url)
    if match:
        return match.group(1)
    
    # Pattern 2: /jobs/view/{job_id}
    view_pattern = r'/jobs/view/(\d+)'
    match = re.search(view_pattern, url)
    if match:
        return match.group(1)
    
    return None

@linkedin_router.post("/scrape-job", response_model=LinkedInJobResponse)
async def scrape_linkedin_job_endpoint(
    request: LinkedInJobRequest,
    current_user=Depends(auth.get_current_user)
):
    """
    Extract job ID from LinkedIn URL and scrape job details.
    Accepts URLs like:
    - https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4253720687
    - https://www.linkedin.com/jobs/view/4253720687
    """
    try:
        # Extract job ID from the provided URL
        job_id = extract_linkedin_job_id(request.linkedin_url)
        if not job_id:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract job ID from the provided LinkedIn URL. Please ensure the URL contains a valid job ID."
            )
        
        # Construct the scraping URL
        scraping_url = f"https://www.linkedin.com/jobs/view/{job_id}"
        
        # Use WebScraper to get job details
        web_scraper = WebScraper()
        scraped_data = web_scraper.linkedin_scrape_job_details(scraping_url)
        
        if not scraped_data:
            raise HTTPException(
                status_code=404,
                detail="Could not scrape job details from LinkedIn. The job may not exist or be accessible."
            )
        
        # Convert scraped data to structured JobData model
        job_data = JobData(**scraped_data) if isinstance(scraped_data, dict) else None
        
        return LinkedInJobResponse(
            job_id=job_id,
            job_data=job_data,
            scraped_url=scraping_url,
            success=True,
            message="Job details scraped successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"LinkedIn scraping error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape LinkedIn job: {str(e)}"
        )

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)  # This router has paths like /users/{user_id}/resumes/...
app.include_router(linkedin_router)
