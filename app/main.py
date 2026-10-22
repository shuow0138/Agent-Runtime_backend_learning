from enum import Enum
from uuid import uuid4, UUID
from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field
import asyncio
import time

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
    description:str | None = None

jobs = {}

@app.get("/health")
def health():
    return {'status': 'ok'} #You return a Python dictionary. FastAPI automatically serializes it into a JSON HTTP response.

@app.get("/hello/{name}")
def say_hello(name:str):
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

@app.get("/jobs/{job_id}", 
         response_model = JobResponse)
def get_job(job_id:UUID):
    if job_id not in jobs:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Job Not Found"
        )
    return jobs[job_id]

@app.get("/jobs", 
         response_model = list[JobResponse])
def get_jobs(
    limit : int = Query(default = 10, ge = 1 , le = 100),
    filter: JobStatus | None = Query(default = None)
):
    all_jobs = list(jobs.values())
    if filter:
        all_jobs = [job for job in all_jobs if job['status'] == filter]
    return all_jobs[:limit]

@app.delete("/jobs/{job_id}", 
            status_code = status.HTTP_204_NO_CONTENT)
def delete_job(job_id:UUID):
    if job_id not in jobs:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Job Not Found"
        )

    if jobs[job_id]["status"] == JobStatus.RUNNING:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "cannot remove a running job"
        )
    
    del jobs[job_id]


