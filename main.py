import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="front-end"), name="static")

class Subject(BaseModel):
    name: str
    exam_mark: int
    school_mark: int

class Results(BaseModel):
    name: str
    email: EmailStr
    subjects: list[Subject]

# Serve the HTML form
@app.get("/", response_class=HTMLResponse)
def read_form():
    return FileResponse("front-end/form.html")

@app.post('/submission')
def html_submission(results: Results, request: Request):
    try:
        # Get the authorization header
        auth_header = request.headers.get('authorization')
        
        if not auth_header:
            return {"error": "No authorization token provided"}
        
        # Extract the token
        token = auth_header.replace('Bearer ', '')
        
        # Verify the token with Supabase
        try:
            user_response = supabase.auth.get_user(token)
            user = user_response.user
            print(f"Authenticated user: {user.email}")
        except Exception as e:
            print(f"Authentication error: {e}")
            return {"error": "Invalid authentication token"}
        
        # Get or create student and get their ID
        student_id = get_or_create_student(results.name, results.email) 

        # Update students table
        try:
            subjects_list = []
            for subject in results.subjects:
                subjects_list.append(subject.name)
            
            subjects_string = ", ".join(subjects_list)
            
            supabase.table("students").update({
                "subjects": subjects_string
            }).eq("id", student_id).execute()
            print("Updated students table successfully")
            
        except Exception as e:
            print(f"Error updating students table: {e}")
            return {"error": "Failed to update students table"}
        
        # Insert into subjects table
        try:
            for subject in results.subjects:
                supabase.table("subjects").insert({
                    "student_id": student_id,
                    "subject_name": subject.name,
                    "exam_mark": subject.exam_mark,
                    "school_mark": subject.school_mark
                }).execute()
                print(f"Saved subject: {subject.name}")
            
        except Exception as e:
            print(f"Error saving subjects: {e}")
            return {"error": "Failed to save subjects"}
        
        return {"success": "Student and subjects saved successfully"}
        
    except Exception as e:
        print(f"Error in submission: {e}")
        return {"error": "Failed to process submission"}

def get_or_create_student(name: str, email_address: str):
    try:
        response = supabase.table("students").select("*").eq("email_address", email_address).execute()
        
        if response.data:
            return response.data[0]['id']
        else:
            insert_response = supabase.table("students").insert({"name": name, "email_address": email_address}).execute()
            return insert_response.data[0]['id']
            
    except Exception as e:
        print(f"Error in get_or_create_student: {e}")
        raise HTTPException(status_code=500, detail="Database error")