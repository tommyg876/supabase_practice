from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import Student, Subject
from calculator import ATARCalculator

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/predict", response_class=HTMLResponse)
async def form_post(
    request: Request,
    student_name: str = Form(...),
    subject_name: str = Form(...),
    school_mark: float = Form(...),
    exam_mark: float = Form(...)
):
    student = Student(1, student_name)
    subject = Subject(subject_name, school_mark, exam_mark)
    student.add_subject(subject)
    
    calc = ATARCalculator(student)
    prediction = calc.predict()

    return templates.TemplateResponse("form.html", {
        "request": request,
        "result": prediction
    })
