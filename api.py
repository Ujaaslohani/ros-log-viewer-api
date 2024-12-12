from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logs = []

LOG_PATTERN = re.compile(r"\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] (.*)")

def parse_log_file(file_content: str) -> List[dict]:
    parsed_logs = []
    for line in file_content.splitlines():
        match = LOG_PATTERN.match(line)
        if match:
            parsed_logs.append({
                "timestamp": match.group(1),
                "severity": match.group(2),
                "node": match.group(3),
                "message": match.group(4),
            })
    return parsed_logs

@app.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".log")):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = (await file.read()).decode("utf-8")
    global logs
    logs = parse_log_file(content)

    return {"message": "File uploaded and parsed successfully.", "total_logs": len(logs)}

@app.get("/logs")
def get_logs(severity: Optional[str] = None):
    if severity:
        filtered_logs = [log for log in logs if log["severity"].upper() == severity.upper()]
        return filtered_logs
    return logs
 