from fastapi import FastAPI

app = FastAPI(title = "agent_runtime")

@app.get("/health")
def health():
    return {'status': 'ok'} #You return a Python dictionary. FastAPI automatically serializes it into a JSON HTTP response.

@app.get("/hello/{name}")
def say_hello(name:int):
    return {"message": f"Hello, {name}!"}

@app.get("/project_info")
def get_project_info():
    return {"project":"agent_runtime","version":"1.0"}