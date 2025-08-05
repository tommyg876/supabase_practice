import os
from supabase import create_client, Client
from database import Student, Subject, student, math, eng

SUPABASE_URL="https://wdpyzgcwxngzudnezvxa.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndkcHl6Z2N3eG5nenVkbmV6dnhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4Njk2ODcsImV4cCI6MjA2OTQ0NTY4N30.6_U4wJh9EcTO2ql-CZDAKrHa8ueCRz--Vhei-_zOe3w"


def get_or_create_student (name:str):
    data = supabase.table("students").select("*").eq("name", "Tommy").execute()
    if data.date:
        return data.id
    else:
        supabase.table("students").insert("name":name)



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)