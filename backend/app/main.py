from fastapi import FastAPI

app = FastAPI(
    title="AI Workforce OS",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "message": "AI Workforce OS is running",
        "employee": "Sales AI Employee #001"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
