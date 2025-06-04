import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AWS_REGION_NAME: str = None  # Your AWS region
    AWS_ACCESS_KEY_ID: Optional[str] = None# Optional: For local dev if not using profiles
    AWS_SECRET_ACCESS_KEY: Optional[str] = None  # Optional
    DYNAMODB_ENDPOINT_URL: Optional[str] = "http://localhost:8000"  # For DynamoDB Local, e.g., "http://localhost:8000"

    DYNAMODB_USERS_TABLE_NAME: str = "users"
    DYNAMODB_RESUMES_TABLE_NAME: str = "resuma_data"
    DYNAMODB_METADATA_TABLE_NAME : str = "metadata"

    # SECRET_KEY: str = "YOUR_VERY_SECRET_KEY_FOR_JWT"
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    deepseek_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_key: Optional[str] = None
    gemini_url: Optional[str] = None
    deepseek_url: Optional[str] = None
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()

# Example .env file for local development with DynamoDB Local:
# AWS_REGION_NAME="us-east-1" # Region doesn't matter much for local, but SDK needs one
# DYNAMODB_ENDPOINT_URL="http://localhost:8000"
# DYNAMODB_USERS_TABLE_NAME="resumeAppUsersDev"
# DYNAMODB_RESUMES_TABLE_NAME="resumeAppResumesDev"
# SECRET_KEY="your_jwt_secret"
# ACCESS_TOKEN_EXPIRE_MINUTES=60

# For AWS deployment, remove DYNAMODB_ENDPOINT_URL or set it to None
# and ensure your environment (e.g., EC2 instance role, Lambda execution role)
# has the necessary IAM permissions and AWS_ACCESS_KEY_ID/SECRET_ACCESS_KEY are configured
# if not using instance profiles or environment variables provided by AWS services.