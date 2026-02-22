from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import io
import os

app = FastAPI()

# --------------------------------------------------
# STRICT CORS (GRADER REQUIRES EXACT HEADER)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # MUST be False when origin is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Force CORS headers on EVERY response (including errors + OPTIONS)
@app.middleware("http")
async def force_cors_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# --------------------------------------------------
# CONFIG — YOUR ASSIGNMENT VALUES
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

    # 1 AUTH CHECK
    if not x_upload_token_7196 or x_upload_token_7196 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2 FILE TYPE CHECK
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Bad Request")

    # 3 FILE SIZE CHECK
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    # 4 CSV PROCESSING
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

    return JSONResponse(content={
        "email": EMAIL,
        "filename": filename,
        "message": "File accepted"
    })


# --------------------------------------------------
# OPTIONS PREFLIGHT HANDLER (THIS WAS MISSING)
# --------------------------------------------------
@app.options("/upload")
async def upload_options():
    return Response(status_code=200)


# --------------------------------------------------
# LOCAL RUN
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)