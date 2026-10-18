import time
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "25f2004209@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-997kyb.example.com"

app = FastAPI()

# Added first => inner layer. Only the one assigned origin is ever allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)


# Added last => outermost, so EVERY response (incl. preflights/errors) gets the headers.
@app.middleware("http")
async def add_request_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception:
        response = Response("Internal Server Error", status_code=500)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{max(time.perf_counter() - start, 0.0):.6f}"
    return response


@app.get("/")
def root():
    return {"status": "ok"}


@app.options("/stats")
def stats_options():
    # Real CORS preflights are answered by CORSMiddleware; this covers plain OPTIONS.
    return Response(status_code=200)


@app.get("/stats")
def stats(values: str = ""):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }
