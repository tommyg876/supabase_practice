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

supabase = create_client(url, key)

email: str = 
password: str = 
user = supabase.auth.sign_up()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Add this new route for the authenticated form
@app.get("/authenticated-form", response_class=HTMLResponse)
def read_authenticated_form():
    return FileResponse("front-end/inappform.html")

# Update your existing routes to point to the right forms
@app.get("/", response_class=HTMLResponse)
def read_form():
    return FileResponse("front-end/form.html")  # Public form

@app.get("/login", response_class=HTMLResponse)
def read_login():
    return FileResponse("front-end/login.html")  # This one is correct

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return FileResponse("front-end/dashboard.html")

# Update the submission endpoint to handle user_id
@app.post('/submission')
def html_submission(client: Client):
        user_email = client.email
        
        # Get or create client and get their ID
        client_id = get_or_create_client(client.name, client.email, client.start_date) 
        print(f"Client ID: {client_id}")

        # Save campaigns to campaigns table
        for campaign in client.campaigns:
            
            campaign_data = {
                "client_id": client_id,  # This links to the specific user
                "campaign_name": campaign.campaign_name,
                "spend": int(campaign.spend),
                "mql_target": int(campaign.mql_target),
                "channel": campaign.channel,
                "actual_mqls": int(campaign.actual_mqls)
            }
            
            print(f"Campaign data being sent: {campaign_data}")
            
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

# Add this new endpoint to get all clients and campaigns
@app.get('/api/clients')
async def get_all_clients():
    try:
        print("=== DEBUG: Starting /api/clients endpoint ===")
        
        # Check if Supabase client is working
        print(f"Supabase URL: {url}")
        print(f"Supabase Key: {key[:20]}...")
        
        # Test basic connection
        print("Testing Supabase connection...")
        test_response = supabase.table("clients").select("count").execute()
        print(f"Connection test result: {test_response}")
        
        # Get all clients
        print("Fetching clients...")
        clients_response = supabase.table("clients").select("*").execute()
        clients = clients_response.data
        print(f"Found {len(clients)} clients: {clients}")
        
        # Get all campaigns
        print("Fetching campaigns...")
        campaigns_response = supabase.table("campaigns").select("*").execute()
        campaigns = campaigns_response.data
        print(f"Found {len(campaigns)} campaigns: {campaigns}")
        
        # Group campaigns by client
        for client in clients:
            client['campaigns'] = [c for c in campaigns if c.get('client_id') == client['id']]
            print(f"Client {client['id']} has {len(client['campaigns'])} campaigns")
        
        result = {
            "success": True,
            "clients": clients,
            "total_clients": len(clients),
            "total_campaigns": len(campaigns)
        }
        
        print(f"Returning result: {result}")
        return result
        
    except Exception as e:
        print(f"=== ERROR in /api/clients ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e))
        }

# Update the /api/clients endpoint to filter by user
@app.get('/api/clients/{user_id}')
async def get_user_clients(user_id: str):
    try:
        print(f"=== DEBUG: Getting clients for user {user_id} ===")
        
        # Get clients for this specific user
        # For now, let's assume the user_id matches client_id
        # (In a real app, you'd have a user_id column in clients table)
        clients_response = supabase.table("clients").select("*").eq("id", user_id).execute()
        clients = clients_response.data
        
        print(f"Found {len(clients)} clients for user {user_id}")
        
        # Get campaigns for this user's clients
        campaigns_response = supabase.table("campaigns").select("*").eq("client_id", user_id).execute()
        campaigns = campaigns_response.data
        
        print(f"Found {len(campaigns)} campaigns for user {user_id}")
        
        # Group campaigns by client
        for client in clients:
            client['campaigns'] = [c for c in campaigns if c.get('client_id') == client['id']]
            print(f"Client {client['id']} has {len(client['campaigns'])} campaigns")
        
        return {
            "success": True,
            "clients": clients,
            "total_clients": len(clients),
            "total_campaigns": len(campaigns)
        }
        
    except Exception as e:
        print(f"Error getting user clients: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

# Add this test endpoint
@app.get('/test-database')
async def test_database():
    try:
        print("=== Testing Database Connection ===")
        
        # Test clients table
        clients_result = supabase.table("clients").select("*").execute()
        print(f"Clients table: {clients_result.data}")
        
        # Test campaigns table
        campaigns_result = supabase.table("campaigns").select("*").execute()
        print(f"Campaigns table: {campaigns_result.data}")
        
        return {
            "success": True,
            "clients_count": len(clients_result.data),
            "campaigns_count": len(campaigns_result.data),
            "clients": clients_result.data,
            "campaigns": campaigns_result.data
        }
        
    except Exception as e:
        print(f"Database test error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

# Add this endpoint to check table structure
@app.get('/check-tables')
async def check_tables():
    try:
        print("=== Checking Table Structure ===")
        
        # Check if tables exist by trying to select from them
        try:
            clients_result = supabase.table("clients").select("*").limit(1).execute()
            print(f"Clients table exists: {len(clients_result.data)} rows")
        except Exception as e:
            print(f"Clients table error: {e}")
            
        try:
            campaigns_result = supabase.table("campaigns").select("*").limit(1).execute()
            print(f"Campaigns table exists: {len(campaigns_result.data)} rows")
        except Exception as e:
            print(f"Campaigns table error: {e}")
            
        return {
            "success": True,
            "message": "Table check completed - check server logs"
        }
        
    except Exception as e:
        print(f"Table check error: {e}")
        return {
            "success": False,
            "error": str(e)
        }