#imports
#create an instance of FastAPI()
#initial class in class to define the name, email, subject #1 & schoolmark and exammark 
#get function to retriev that data fro

from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()

class Subject(BaseModel):
    name: str
    exam_mark: int
    school_mark: int

class Results(BaseModel):
    name: str
    email: EmailStr
    subjects: list[Subject]


@app.post ('/submission')
def html_submission (results: Results):
    return {"message": f"Hello {results.name}"}