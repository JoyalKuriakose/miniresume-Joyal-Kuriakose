# Mini Resume Management API (FastAPI)

## a) Python Version Used

- Python 3.10.10  
(Recommended: Python 3.10 or higher)

---

## b) Installation Steps

### 1. Open the Project Folder
Open the project folder in VS Code:
```

miniresume-joyal-kuriakose

````

### 2. Create Virtual Environment

#### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
````

#### Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

## c) Steps to Run the Application

Start the FastAPI server using:

```bash
uvicorn main:app --reload
```

The server will run at:

```
http://127.0.0.1:8000
```

### Available URLs:

* Health Check:

  ```
  http://127.0.0.1:8000/health
  ```

* Swagger API Documentation:

  ```
  http://127.0.0.1:8000/docs
  ```

---

## d) Example API Request / Response

### 1. Health Check

**Request:**

```bash
curl http://127.0.0.1:8000/health
```

**Response:**

```json
{
  "status": "ok"
}
```

---

### 2. Create Candidate (Upload Resume)

**Request (multipart/form-data):**

```bash
curl -X POST "http://127.0.0.1:8000/candidates" \
  -F "Full_Name=Joyal Kuriakose" \
  -F "DOB=2002-09-02" \
  -F "Contact_Number=9846560891" \
  -F "Address=Kottayam, Kerala" \
  -F "Qualification=MCA" \
  -F "Graduation_Year=2025" \
  -F "Years_of_Experience=0" \
  -F "Skills=Python, FastAPI, SQL" \
  -F "Resume=@resume.pdf"
```

**Example Response:**

```json
{
  "Full_Name": "Joyal Kuriakose",
  "DOB": "2002-01-15",
  "Contact_Number": "9846560891",
  "Address": "Kottayam, Kerala",
  "Qualification": "MCA",
  "Graduation_Year": 2025,
  "Years_of_Experience": 0.0,
  "Skills": ["Python", "FastAPI", "SQL"],
  "id": 1,
  "resume_filename": "resume.pdf",
  "resume_path": "uploads/resume.pdf",
  "created_at": "2026-02-17T06:30:00.000000"
}
```

---

### 3. List Candidates (With Filters)

**Request:**

```bash
curl "http://127.0.0.1:8000/candidates?skill=Python&Min_Experience=0&Graduation_Year=2026"
```

**Example Response:**

```json
[
  {
    "Full_Name": "Joyal Kuriakose",
    "DOB": "2001-09-02",
    "Contact_Number": "9846560891",
    "Address": "Kottayam, Kerala",
    "Qualification": "MCA",
    "Graduation_Year": 2025,
    "Years_of_Experience": 0.0,
    "Skills": ["Python", "FastAPI", "SQL"],
    "id": 1,
    "resume_filename": "resume.pdf",
    "resume_path": "uploads/resume.pdf",
    "created_at": "2026-02-17T06:30:00.000000"
  }
]
```

---

### 4. Get Candidate by ID

**Request:**

```bash
curl "http://127.0.0.1:8000/candidates/1"
```

**Example Response:**

```json
{
  "Full_Name": "Joyal Kuriakose",
  "DOB": "2001-09-02",
  "Contact_Number": "9846560891",
  "Address": "Kottayam, Kerala",
  "Qualification": "MCA",
  "Graduation_Year": 2025,
  "Years_of_Experience": 0.0,
  "Skills": ["Python", "FastAPI", "SQL"],
  "id": 1,
  "resume_filename": "resume.pdf",
  "resume_path": "uploads/resume.pdf",
  "created_at": "2026-02-17T06:30:00.000000"
}
```

---

### 5. Delete Candidate

**Request:**

```bash
curl -X DELETE "http://127.0.0.1:8000/candidates/1"
```

**Example Response:**

```json
{
  "detail": "deleted successfully"
}
```

