import uvicorn
from mangum import Mangum

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, APIRouter, Path
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from typing import List, Annotated
# from datetime import timedelta
# No specific UUID type from FastAPI for path params, use str and validate/convert in CRUD if needed.

# Adjust imports based on your project structure
from database.model import (
    UserPublic,  JobDetailsInput, UserAppMetadata,
    ResumeCreate, ResumeUpdate, ResumePublic, ResumeSchema, ResumeInDB,
    UserCreate as UserModelCreate, UserInDB as UserInDBModel
)
import database.crud as crud
# import utils as auth
# from services import llm_service, pdf_service
from core.config import settings
from services import ResumeBuilder
from utils import FileOperations

# from database.dynamodb_client import create_users_table_if_not_exists, create_resumes_table_if_not_exists


# --- DynamoDB Table Initialization Event ---
# @app.on_event("startup")
# async def startup_dynamodb_tables():
#     print("Application startup: Ensuring DynamoDB tables exist...")
#     # These functions are idempotent
#     create_users_table_if_not_exists()
#     create_resumes_table_if_not_exists()
#     print("DynamoDB tables checked/created.")


app = FastAPI(title="Resume Builder API with DynamoDB (No Auth)")
handler = Mangum(app)  # For AWS Lambda compatibility

# --- Routers ---
user_router = APIRouter(prefix="/users", tags=["Users"])
resume_router = APIRouter(tags=["Resumes"])  # Will be nested under users


# --- User Endpoints ---
@user_router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_new_user_endpoint(user_create_payload: UserModelCreate):
    try:
        created_user_in_db = await crud.create_user(user_data=user_create_payload)
        if not created_user_in_db:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")
        return UserPublic.model_validate(created_user_in_db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Unexpected error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred during user creation.")


@user_router.get("/{user_id}", response_model=UserPublic)
async def get_user_details_endpoint(user_id: str = Path(..., description="The ID of the user to retrieve")):
    user_db = await crud.get_user_by_id(user_id=user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user_db.model_dump())


@user_router.get("/{user_id}/metadata", response_model=UserAppMetadata)
async def get_user_metadata_endpoint(user_id: str = Path(..., description="The ID of the user")):
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

# --- Resume Endpoints (Nested under /users/{user_id}/resumes) ---
@resume_router.post("/users/{user_id}/resumes/upload-and-create", response_model=ResumePublic,
                    status_code=status.HTTP_201_CREATED)
async def upload_resume_file_and_create_for_user(
        user_id: str = Path(..., description="The ID of the user"),
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
        text =  FileOperations().extract_text_from_file_bytes(contents, filename)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
        print(f"Extracted text from file: {text[:100]}...")  # Log first 100 chars for debugging
        resume_builder = ResumeBuilder('google')

        # TODO : Implement the actual LLM parsing logic here

        parsed_resume_pydantic: ResumeSchema =   resume_builder.parse_file_to_json(text)# Assuming this function exists and returns a ResumeSchema object
    except Exception as e:
        print(f"LLM parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume with LLM: {str(e)}")
    parsed_resume_pydantic = clean_none_strings(parsed_resume_pydantic)
    resume_to_create = ResumeCreate(title=title, resume_data=parsed_resume_pydantic)

    created_resume_db = await crud.create_resume(user_id=user_id, resume_in=resume_to_create)
    if not created_resume_db:
        raise HTTPException(status_code=500, detail="Could not save parsed resume.")
    return ResumePublic.model_validate(created_resume_db.model_dump())


@resume_router.get("/users/{user_id}/resumes/", response_model=List[ResumePublic])
async def get_list_of_user_resumes_endpoint(user_id: str = Path(..., description="The ID of the user")):
    user = await crud.get_user_by_id(user_id)  # Optional: check if user exists
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    resumes_db_list = await crud.get_all_resumes_for_user(user_id=user_id)
    return [ResumePublic.model_validate(r.model_dump()) for r in resumes_db_list]


@resume_router.get("/users/{user_id}/resumes/{resume_id}", response_model=ResumePublic)
async def get_one_user_resume_json_endpoint(
        user_id: str = Path(..., description="The ID of the user"),
        resume_id: str = Path(..., description="The ID of the resume")
):
    resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found for this user")
    return ResumePublic(**resume_db.model_dump())



@resume_router.put("/users/{user_id}/resumes/{resume_id}", response_model=ResumePublic)
async def save_or_update_user_json_endpoint(
    resume_update_payload: ResumeUpdate,
    user_id: str = Path(..., description="The ID of the user"),
    resume_id: str = Path(..., description="The ID of the resume"),
):
    updated_resume_db = await crud.update_resume(
        user_id=user_id, resume_id=resume_id, resume_update_data=resume_update_payload
    )
    if not updated_resume_db:
        raise HTTPException(status_code=404, detail="Resume not found or failed to update")
    return ResumePublic.model_validate(updated_resume_db.model_dump())


@resume_router.post("/users/{user_id}/resumes/{resume_id}/tailor", response_model=ResumeSchema)
async def tailor_resume_for_job_endpoint(
        job_details: JobDetailsInput,
        user_id: str = Path(..., description="The ID of the user"),
        resume_id: str = Path(..., description="The ID of the resume")
):
    existing_resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not existing_resume_db:
        raise HTTPException(status_code=404, detail="Resume to tailor not found for this user")

    existing_resume_pydantic = existing_resume_db.resume_data
    try:
        #Todo : Implement the actual LLM tailoring logic here
        tailored_resume_pydantic: ResumeSchema = None
    except Exception as e:
        print(f"LLM tailoring error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor resume with LLM: {str(e)}")
    return tailored_resume_pydantic


@resume_router.get("/users/{user_id}/resumes/{resume_id}/download", response_class=StreamingResponse)
async def download_resume_as_pdf_endpoint(
        user_id: str = Path(..., description="The ID of the user"),
        resume_id: str = Path(..., description="The ID of the resume")
):
    resume_db = await crud.get_resume_by_id(user_id=user_id, resume_id=resume_id)
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found for download by this user")

    try:
        # TODO : Implement the actual PDF generation logic here
        pdf_bytes: bytes = await bytes([ord(char) for char in "testing"])  # Placeholder for actual PDF generation logic
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    safe_title = "".join(c if c.isalnum() or c in (' ', '.', '-') else '_' for c in (resume_db.title or "resume"))
    filename = f"{safe_title.replace(' ', '_')}_{resume_id[:8]}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )


@resume_router.delete("/users/{user_id}/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_endpoint(
        user_id: str = Path(..., description="The ID of the user"),
        resume_id: str = Path(..., description="The ID of the resume")
):
    deleted = await crud.delete_resume(user_id=user_id, resume_id=resume_id)
    if not deleted:  # crud.delete_resume now returns False if ConditionalCheckFailed (item not found)
        raise HTTPException(status_code=404, detail="Resume not found or failed to delete")
    return None


app.include_router(user_router)
app.include_router(resume_router)  # This router has paths like /users/{user_id}/resumes/...
