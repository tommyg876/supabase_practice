from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import Student, Subject
from calculator import ATARCalculator
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Get port from environment variable (Render sets this)
port = int(os.environ.get("PORT", 8000))

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def form_post(
    request: Request,
    student_name: str = Form(...),
    subject_name_1: str = Form(None),
    school_mark_1: float = Form(None),
    exam_mark_1: float = Form(None),
    subject_name_2: str = Form(None),
    school_mark_2: float = Form(None),
    exam_mark_2: float = Form(None),
    subject_name_3: str = Form(None),
    school_mark_3: float = Form(None),
    exam_mark_3: float = Form(None),
    subject_name_4: str = Form(None),
    school_mark_4: float = Form(None),
    exam_mark_4: float = Form(None),
    subject_name_5: str = Form(None),
    school_mark_5: float = Form(None),
    exam_mark_5: float = Form(None),
    subject_name_6: str = Form(None),
    school_mark_6: float = Form(None),
    exam_mark_6: float = Form(None),
):
    student = Student(1, student_name)

    # Loop over each subject
    for i in range(1, 7):
        name = locals()[f"subject_name_{i}"]
        school = locals()[f"school_mark_{i}"]
        exam = locals()[f"exam_mark_{i}"]

        if name and school is not None and exam is not None:
            subject = Subject(name, school, exam)
            student.add_subject(subject)

    calc = ATARCalculator(student)
    prediction = calc.predict()

    return templates.TemplateResponse("form.html", {
        "request": request,
        "result": prediction
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
