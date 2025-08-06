import os 
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

name = 'tommy', 'paddy'

# This queries the database for students named 'tommy'
response = supabase.table("students").select("*").eq("name", name).execute()
data = response.data

if data:
    print(f"Found {len(data)} students named {name}")
    for student in data:
        print(f"ID: {student['id']}, Name: {student['name']}")
else:
    print(f"No students found with name: {name}")
