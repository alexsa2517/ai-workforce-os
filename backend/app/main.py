from fastapi import FastAPI

app = FastAPI(
    title="AI Workforce OS",
    description="AI Employee Platform",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "project": "AI Workforce OS",
        "status": "running",
        "employee": "Sales AI Employee #001"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
