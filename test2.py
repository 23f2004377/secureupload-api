import requests

BASE = "https://secureupload-api-2iv3.onrender.com/"


# Simple connectivity test
try:
    r = requests.get("http://127.0.0.1:9000/docs")
    print("GET /docs:", r.status_code)
except Exception as e:
    print("Connection error:", e)

# Test upload endpoint
try:
    with open("q-fastapi-file-validation.csv", "rb") as f:
        r = requests.post(
            "http://127.0.0.1:9000/upload",
            files={"file": ("q-fastapi-file-validation.csv", f, "text/csv")},
            headers={"X-Upload-Token-7196": "cwow2kvu9uq76ln9"},
        )
    print("POST /upload:", r.status_code, r.text)
except Exception as e:
    print("Upload error:", e)