from enum import Enum
from uuid import uuid4, UUID
from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
import asyncio
import time
from app.database import Base, engine, get_db
from app.db_models import Job
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session


app = FastAPI(title = "agent_runtime")

Base.metadata.create_all(bind=engine)

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreate(BaseModel):
    task:str = Field(min_length = 1)
    description: str | None = None

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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
def create_job(
    job:JobCreate,
    db:Session = Depends(get_db)
    ):
    new_job = Job(
        task = job.task,
        description = job.description,
        status = JobStatus.QUEUED.value,
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@app.get("/jobs/{job_id}", 
         response_model = JobResponse)
def get_job(
    job_id:UUID,
    db:Session = Depends(get_db),
    ):
    job = db.get(Job,job_id)

    if job is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Job Not Found"
        )
    return job

@app.get("/jobs", 
         response_model = list[JobResponse])
def get_jobs(
    limit : int = Query(default = 10, ge = 1 , le = 100),
    filter: JobStatus | None = Query(default = None),
    db: Session = Depends(get_db)
):
    if filter is not None:
        stmt = select(Job).where(Job.status == filter).limit(limit)
    else:
        stmt = select(Job).limit(limit)
  
    jobs = db.scalars(stmt).all()
    return jobs

@app.get("/jobs/count")
def count_jobs(
    status: JobStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(func.count()).select_from(Job)

    if status is not None:
        stmt = stmt.where(Job.status == status.value)

    count = db.scalar(stmt)

    return {"count": count}
    
@app.delete("/jobs/{job_id}", 
            status_code = status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id:UUID,
    db:Session = Depends(get_db)
    ):
    job = db.get(Job,job_id)

    if job is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Job Not Found"
        )

    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "cannot remove a running job"
        )
    
    db.delete(job)
    db.commit()

