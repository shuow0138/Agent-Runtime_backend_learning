from fastapi.testclient import TestClient
from app.main import app, jobs
from uuid import UUID
import pytest
client = TestClient(app)

@pytest.fixture(autouse = True)
def clear_jobs():
    jobs.clear()
    yield
    jobs.clear()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {'status':'ok'}

def test_create_job():
    response = client.post(
        "/jobs",
        json = {
            "task": "get summary",
            "description": "get a brief summary of the topic"
        }
    )

    assert response.status_code == 201
    assert response.json()['task'] == "get summary"
    assert response.json()['description'] == "get a brief summary of the topic"
    assert response.json()['status'] == "queued"
    UUID(response.json()['id'])

def test_get_job():
    response = client.post(
        "/jobs",
        json = {
            "task" : "test_get_job",
        }
    )
    id = str(response.json()['id'])
    response2 = client.get(f"/jobs/{id}")
    assert response2.status_code == 200
    assert response2.json()['task'] == "test_get_job"
    assert response2.json()['description'] == None
    assert response2.json()["status"] == "queued"

def test_get_jobs():
    client.post(
        "/jobs",
        json = {
            "task":"test job 1"
        }
    )
    client.post(
        "/jobs",
        json = {
            "task":"test job 2"
        }
    )

    response = client.get("/jobs")
    assert response.status_code == 200
    assert response.json()[0]["task"] == "test job 1"
    assert response.json()[1]["task"] == "test job 2"

def test_delete_job():
    post1 = client.post(
            "/jobs",
            json = {
                "task":"test job 1"
            }
        )
    post2 = client.post(
            "/jobs",
            json = {
                "task":"test job 2"
            }
        )
    id1 = post1.json()['id']
    id2 = post2.json()["id"]
    response = client.get("/jobs")
    assert response.json()[0]["task"] == "test job 1"
    assert response.json()[1]["task"] == "test job 2"

    response2 = client.delete(f"/jobs/{id1}")
    assert response2.status_code == 204

    response3 = client.get(f"/jobs/{id1}")
    assert response3.status_code == 404

    response4 = client.get("/jobs")
    assert response4.json()[0]["task"] == "test job 2"

def test_delete_job_conflict():
    post1 = client.post(
                "/jobs",
                json = {
                    "task":"test job 1"
                }
            )
    post2 = client.post(
                "/jobs",
                json = {
                    "task":"test job 2"
                }
            )
    id1 = post1.json()['id']
    id2 = post2.json()["id"]
    response = client.get("/jobs")
    assert response.json()[0]["task"] == "test job 1"
    assert response.json()[1]["task"] == "test job 2"
    id1 = UUID(id1)
    jobs[id1]["status"] = "running"
    response2 = client.delete(f"/jobs/{id1}")
    assert response2.status_code == 409

    response3 = client.get(f"/jobs/{id1}")
    assert response3.status_code == 200

    response4 = client.get("/jobs")
    assert response4.json()[0]["task"] == "test job 1"
    


