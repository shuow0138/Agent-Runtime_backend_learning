from enum import Enum
from uuid import uuid4, UUID
from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(title = "agent_runtime")

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreate(BaseModel):
    task:str = Field(min_length = 1)
    description: str | None = None

class JobResponse(BaseModel):
    id:UUID
    task:str
    status:JobStatus
    description:str

jobs = {}

@app.get("/health")
def health():
    return {'status': 'ok'} #You return a Python dictionary. FastAPI automatically serializes it into a JSON HTTP response.

@app.get("/hello/{name}")
def say_hello(name):
    return {"message": f"Hello, {name}!"}

@app.get("/project_info")
def get_project_info():
    return {"project":"agent_runtime","version":"1.0"}

@app.post(
    "/jobs",
    response_model = JobResponse,
    status_code = status.HTTP_201_CREATED,  
    )
def create_job(job:JobCreate):
    job_id = uuid4()

    new_job = {
        "id":job_id,
        "task":job.task,
        "status":JobStatus.QUEUED,
        "description":job.description
    }

    jobs[job_id] = new_job

    return new_job