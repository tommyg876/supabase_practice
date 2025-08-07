import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Debug: Check if environment variables are loaded
print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY: {key[:20] if key else 'None'}...")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

supabase = create_client(url, key)

#email: str = 
#password: str = 
#user = supabase.auth.sign_up()

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

class Campaign(BaseModel):
    campaign_name: str
    spend: float
    mql_target: int
    channel: str
    actual_mqls: int = 0

class Client(BaseModel):
    name: str
    email: EmailStr
    start_date: str
    campaigns: list[Campaign]

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: str = None
    session: dict = None

# Serve the campaign form (main page)
@app.get("/", response_class=HTMLResponse)
def read_form():
    return FileResponse("front-end/form.html")  # Use existing form.html

# Serve the login page
@app.get("/login", response_class=HTMLResponse)
def read_login():
    return FileResponse("front-end/login.html")  # This one is correct

# Serve the dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return FileResponse("front-end/dashboard.html")  # Use existing dashboard.html

@app.post('/submission')
def html_submission(client: Client):
    try:
        print(f"Received submission for: {client.name} ({client.email})")
        print(f"Campaigns: {[c.campaign_name for c in client.campaigns]}")
        
        # Get or create client and get their ID
        client_id = get_or_create_client(client.name, client.email, client.start_date) 
        print(f"Client ID: {client_id}")

        # Update clients table with campaign names
        campaigns_list = []
        for campaign in client.campaigns:
            campaigns_list.append(campaign.campaign_name)
        
        campaigns_string = ", ".join(campaigns_list)
        
        # Update the clients table with campaigns
        # supabase.table("clients").update({
        #     "campaigns": campaigns_string
        # }).eq("id", client_id).execute()
        print(f"Updated clients table with campaigns: {campaigns_string}")

        # Save campaigns to campaigns table
        for campaign in client.campaigns:
            print(f"Saving campaign: {campaign.campaign_name} (Spend: ${campaign.spend}, Target: {campaign.mql_target})")
            
            # Be explicit about which data goes in which column
            campaign_data = {
                "client_id": client_id,                  # First column - int
                "campaign_name": campaign.campaign_name,
                "spend": int(campaign.spend),
                "mql_target": int(campaign.mql_target),
                "channel": campaign.channel,
                "actual_mqls": int(campaign.actual_mqls)
            }
            
            print(f"Campaign data being sent: {campaign_data}")
            
            # Add debug lines AFTER creating campaign_data
            print(f"Database columns should be: client_id, id, campaign_name, spend, mql_target, channel, actual_mqls")
            print(f"But we're sending: {list(campaign_data.keys())}")
            
            try:
                response = supabase.table("campaigns").insert(campaign_data).execute()
                print(f"Campaign saved successfully: {response.data}")
            except Exception as e:
                print(f"Error saving campaign: {e}")
                raise e
        
        return {"success": "Client and campaigns saved successfully"}
        
    except Exception as e:
        print(f"Error in submission: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to process submission: {str(e)}"}

def get_or_create_client(name: str, email_address: str, start_date: str):
    try:
        print(f"Looking for client with email: {email_address}")
        response = supabase.table("clients").select("*").eq("email_address", email_address).execute()
        
        if response.data:
            print(f"Found existing client: {response.data[0]}")
            return response.data[0]['id']
        else:
            print(f"Creating new client: {name} ({email_address})")
            insert_response = supabase.table("clients").insert({
                "name": name, 
                "email_address": email_address,
                "start_date": start_date
            }).execute()
            print(f"New client created: {insert_response.data[0]}")
            return insert_response.data[0]['id']
            
    except Exception as e:
        print(f"Error in get_or_create_client: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post('/auth/signup')
async def signup(request: SignUpRequest):
    try:
        print(f"Signup attempt for: {request.email}")
        
        # Call Supabase auth.sign_up
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if response.user:
            print(f"User created successfully: {response.user.id}")
            return AuthResponse(
                success=True,
                message="Account created successfully! Please check your email to verify.",
                user_id=response.user.id
            )
        else:
            print(f"Signup failed: {response}")
            return AuthResponse(
                success=False,
                message="Failed to create account"
            )
            
    except Exception as e:
        print(f"Signup error: {e}")
        return AuthResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.post('/auth/signin')
async def signin(request: SignInRequest):
    try:
        print(f"Signin attempt for: {request.email}")
        
        # Call Supabase auth.sign_in_with_password
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user:
            print(f"User signed in successfully: {response.user.id}")
            return AuthResponse(
                success=True,
                message="Signed in successfully!",
                user_id=response.user.id,
                session=response.session.dict() if response.session else None
            )
        else:
            print(f"Signin failed: {response}")
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
            
    except Exception as e:
        print(f"Signin error: {e}")
        return AuthResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.post('/auth/signout')
async def signout():
    try:
        response = supabase.auth.sign_out()
        return AuthResponse(
            success=True,
            message="Signed out successfully!"
        )
    except Exception as e:
        print(f"Signout error: {e}")
        return AuthResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.get('/user/clients/{user_id}')
async def get_user_clients(user_id: str):
    try:
        # Get clients for this specific user
        response = supabase.table("clients").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "clients": response.data
            }
        else:
            return {
                "success": True,
                "clients": []
            }
            
    except Exception as e:
        print(f"Error getting user clients: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }