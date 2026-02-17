from __future__ import annotations 

import os
import re
from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, status, Response
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Mini Resume Management", version="1.0.0")

CANDIDATES: Dict[int, "CandidateOut"] = {}  # in-memory store: {id: candidate_data}

NEXT_ID = 1  # auto-increment id: 1,2,3...

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # create uploads folder if not exists

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}  # allowed resume file types


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)  # keep only digits


def _safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")   # remove special characters to make filename safe
    return name or "resume"


def _parse_skills(skills_raw: str) -> List[str]:
    skills = [s.strip() for s in skills_raw.split(",")]   # convert "Python, SQL" -> ["Python", "SQL"] and remove duplicates
    skills = [s for s in skills if s]
    seen = set()
    unique = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def _get_unique_save_path(candidate_id: int, original_filename: str) -> str:
    safe_name = _safe_filename(original_filename)  # save with original name; if same name exists, add _(id) to avoid overwrite
    base, ext = os.path.splitext(safe_name)

    path = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.exists(path):
        return path

    new_name = f"{base}_({candidate_id}){ext}"
    return os.path.join(UPLOAD_DIR, new_name)


class CandidateBase(BaseModel):
    Full_Name: str = Field(..., min_length=2, max_length=100)
    DOB: date
    Contact_Number: str
    Address: str = Field(..., min_length=5, max_length=300)
    Qualification: str = Field(..., min_length=2, max_length=120)
    Graduation_Year: int = Field(..., ge=1950, le=2100)
    Years_of_Experience: float = Field(..., ge=0, le=60)
    Skills: List[str] = Field(..., min_length=1)

    @field_validator("DOB")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v > date.today():  # future DOB not allowed
            raise ValueError("DOB cannot be in the future.")
        return v

    @field_validator("Contact_Number")
    @classmethod
    def validate_contact_number(cls, v: str) -> str:
        digits = _normalize_phone(v)  # normalize before checking length
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Contact number must contain 10 to 15 digits.")
        return digits

    @field_validator("Skills")
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:  # ensure at least one non-empty skill
        cleaned = [s.strip() for s in v if s and s.strip()]
        if not cleaned:
            raise ValueError("Skills must contain at least one skill.")
        return cleaned


class CandidateOut(CandidateBase): # extra fields returned in API responses
    id: int
    resume_filename: str
    resume_path: str
    created_at: datetime


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"} 


@app.post("/candidates", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def upload_candidate(
    Full_Name: str = Form(...),
    DOB: str = Form(..., description="YYYY-MM-DD"),
    Contact_Number: str = Form(...),
    Address: str = Form(...),
    Qualification: str = Form(...),
    Graduation_Year: int = Form(...),
    Years_of_Experience: float = Form(...),
    Skills: str = Form(..., description="Comma-separated skills, e.g. Python, FastAPI"),
    Resume: UploadFile = File(...),
):
    global NEXT_ID  # to update the auto-increment counter

    ext = os.path.splitext(Resume.filename or "")[1].lower()   # validate resume file type
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Only PDF/DOC/DOCX allowed. Got: {ext or 'unknown'}",
        )

    try:      # validate DOB format
        dob_date = date.fromisoformat(DOB)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="DOB must be in YYYY-MM-DD format",
        )

    skills_list = _parse_skills(Skills)     # convert skills string to list

    try:     
        base = CandidateBase(
            Full_Name=Full_Name,
            DOB=dob_date,
            Contact_Number=Contact_Number,
            Address=Address,
            Qualification=Qualification,
            Graduation_Year=Graduation_Year,
            Years_of_Experience=Years_of_Experience,
            Skills=skills_list,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    candidate_id = NEXT_ID      # generate next id (1,2,3...)
    NEXT_ID += 1

    original_name = Resume.filename or "resume"       # save resume file inside uploads/
    stored_path = _get_unique_save_path(candidate_id, original_name)

    content = await Resume.read()  
    with open(stored_path, "wb") as f:  
        f.write(content)

    candidate = CandidateOut(    
        id=candidate_id,
        **base.model_dump(),
        resume_filename=os.path.basename(stored_path),
        resume_path=stored_path,
        created_at=datetime.utcnow(),
    )

    CANDIDATES[candidate_id] = candidate  # store in memory
    return candidate


@app.get("/candidates", response_model=List[CandidateOut])
def list_candidates(
    skill: Optional[str] = Query(None),
    Min_Experience: Optional[float] = Query(None, ge=0),
    Graduation_Year: Optional[int] = Query(None, ge=1950, le=2100),
):
    results = list(CANDIDATES.values())  # all candidates

    if skill:       # filter by exact skill (case-insensitive)
        s = skill.strip().lower()
        results = [c for c in results if any(x.lower() == s for x in c.Skills)]

    if Min_Experience is not None:       # filter by minimum experience
        results = [c for c in results if c.Years_of_Experience >= Min_Experience]

    if Graduation_Year is not None:       # filter by graduation year
        results = [c for c in results if c.Graduation_Year == Graduation_Year]

    results.sort(key=lambda c: c.created_at, reverse=True)  
    return results


@app.get("/candidates/{id}", response_model=CandidateOut)
def get_candidate(candidate_id: int):      # get single candidate by id
    candidate = CANDIDATES.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@app.delete("/candidates/{id}")
def delete_candidate(candidate_id: int):        # remove candidate from memory
    candidate = CANDIDATES.pop(candidate_id, None)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    try:        # delete stored resume file
        if candidate.resume_path and os.path.exists(candidate.resume_path):
            os.remove(candidate.resume_path)
    except Exception:
        pass

    return {"detail": "deleted successfully"}
