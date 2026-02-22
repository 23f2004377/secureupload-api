from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import io
import os

app = FastAPI()

# --------------------------------------------------
# CORS (same style as repo)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# repo also forces headers manually (important)
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


# --------------------------------------------------
# CONFIG (YOUR CASE STUDY VALUES)
# --------------------------------------------------
VALID_TOKEN = "cwow2kvu9uq76ln9"
MAX_FILE_SIZE = 57 * 1024
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt"}
EMAIL = "23f2004377@ds.study.iitm.ac.in"


# --------------------------------------------------
# UPLOAD ENDPOINT
# --------------------------------------------------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_7196: str = Header(None),
):

    # 1 AUTHENTICATION
    if not x_upload_token_7196 or x_upload_token_7196 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2 FILE TYPE
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Bad Request")

    # 3 FILE SIZE
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    # 4 CSV PROCESSING (repo style using csv module)
    if ext == ".csv":
        try:
            text = contents.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid CSV")

        columns = list(rows[0].keys()) if rows else []

        total_value = 0.0
        category_counts = {}

        for row in rows:
            total_value += float(row["value"])
            cat = row["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        total_value = round(total_value, 2)

        return JSONResponse(content={
            "email": EMAIL,
            "filename": filename,
            "rows": len(rows),
            "columns": columns,
            "totalValue": total_value,
            "categoryCounts": category_counts
        })

    # non-csv allowed but not processed
    return JSONResponse(content={
        "email": EMAIL,
        "filename": filename,
        "message": "File accepted"
    })


# --------------------------------------------------
# LOCAL RUN (same style as repo)
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)