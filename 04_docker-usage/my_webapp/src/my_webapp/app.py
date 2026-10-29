from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello from uv + Docker"}


@app.get("/health")
def health():
    return {"status": "ok"}
