import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def is_valid_uuid(uuid_to_test):
    if not uuid_to_test or uuid_to_test == "00000000-0000-0000-0000-000000000000":
        return False
    try:
        from uuid import UUID
        UUID(str(uuid_to_test))
        # Ensure it's not the nil UUID which won't exist in the users table
        return str(UUID(str(uuid_to_test))) != "00000000-0000-0000-0000-000000000000"
    except ValueError:
        return False

supabase: Client = None
placeholders = ["http://localhost:8000", "YOUR_SUPABASE_PROJECT_URL", "dummy_url", ""]
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL not in placeholders and "dummy" not in SUPABASE_KEY and "YOUR_SUPABASE" not in SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

def get_or_create_user(email: str, city: str, is_partner: bool = False):
    if not supabase:
        return {"id": "dummy-user-id", "email": email, "city": city}
    
    # Check if user exists
    response = supabase.table("users").select("*").eq("email", email).execute()
    if response.data:
        return response.data[0]
    
    # Create new user
    new_user = {"email": email, "city": city, "is_partner": is_partner}
    response = supabase.table("users").insert(new_user).execute()
    return response.data[0]

def save_driving_profile(user_id: str, profile_data: dict):
    if not supabase or not is_valid_uuid(user_id):
        return {"id": "dummy-profile-id", **profile_data}
    
    profile_data["user_id"] = user_id
    response = supabase.table("driving_profiles").insert(profile_data).execute()
    return response.data[0]

def save_carbon_result(user_id: str, result_data: dict):
    if not supabase or not is_valid_uuid(user_id):
        return {"id": "dummy-result-id", **result_data}
        
    result_data["user_id"] = user_id
    response = supabase.table("carbon_results").insert(result_data).execute()
    return response.data[0]

def save_user_intent(user_id: str, intent_data: dict):
    """Saves a user's car-buying interest to be monetized via the Partner Dashboard."""
    if not supabase or not is_valid_uuid(user_id):
        print("\n" + "═"*50)
        print(f"💰 [LEAD CAPTURED] Monetization Opportunity Identified!")
        print(f"👤 User: {user_id}")
        print(f"🚗 Interest: {intent_data['intent_type']} for {intent_data.get('vehicle_type', 'unknown')}")
        print(f"📍 Context: {intent_data.get('context', 'Direct Click')}")
        print("═"*50 + "\n")
        return {"id": "dummy-intent-id", **intent_data, "user_id": user_id}
        
    # Standardize field names for the DB
    db_intent = {
        "user_id": user_id,
        "vehicle_type": intent_data.get("vehicle_type"),
        "intent_type": intent_data.get("intent_type"),
        "context": intent_data.get("context")
    }
    response = supabase.table("user_intents").insert(db_intent).execute()
    return response.data[0]

def get_dealers(specialty: str = None):
    if not supabase:
        return [
            {"name": "EcoMotors City", "email": "sales@ecomotors.example.com", "location": "New York", "specialty": "EV"},
            {"name": "Green Drive Toyota", "email": "contact@greendrive.example.com", "location": "San Francisco", "specialty": "Hybrid"}
        ]
    query = supabase.table("dealers").select("*")
    if specialty:
        query = query.eq("specialty", specialty)
    response = query.execute()
    return response.data

def log_notification(recipient_type: str, identifier: str, channel: str, metadata: dict):
    if not supabase:
        return {"status": "skipped", "reason": "no supabase"}
    data = {
        "recipient_type": recipient_type,
        "recipient_identifier": identifier,
        "channel": channel,
        "metadata": metadata
    }
    supabase.table("notifications_log").insert(data).execute()

def get_vehicles():
    if not supabase:
        # Mock data for local testing (Indian Context)
        return [
            {"vehicle_name": "Tata Nexon EV", "vehicle_type": "EV", "battery_size_kwh": 40.5, "fuel_efficiency_mpg": None, "manufacturing_emissions_kgco2": 11000},
            {"vehicle_name": "Maruti Suzuki Swift", "vehicle_type": "ICE", "battery_size_kwh": None, "fuel_efficiency_mpg": 23, "manufacturing_emissions_kgco2": 6500},
            {"vehicle_name": "Toyota Hyryder", "vehicle_type": "Hybrid", "battery_size_kwh": 1.5, "fuel_efficiency_mpg": 27, "manufacturing_emissions_kgco2": 8000},
            {"vehicle_name": "MG ZS EV", "vehicle_type": "EV", "battery_size_kwh": 50.3, "fuel_efficiency_mpg": None, "manufacturing_emissions_kgco2": 12500}
        ]
    response = supabase.table("vehicles").select("*").execute()
    return response.data

def get_analytics():
    """Fetches aggregated analytics data for the Partner Dashboard."""
    if not supabase:
        return {
            "totalUsers": 1423,
            "totalSimulations": 4521,
            "totalLeads": 85,
            "cityBreakdown": { 'Mumbai': 450, 'Delhi': 320, 'Bangalore': 210, 'Pune': 443 },
            "vehiclePreference": { 'EV': 2100, 'Hybrid': 1400, 'ICE': 1021 },
            "leadTrends": {"x": ['Jan', 'Feb', 'Mar'], "y": [20, 35, 85]}
        }
    
    # 1. Basic Stats
    users_count = supabase.table("users").select("id", count="exact").execute().count
    sims_count = supabase.table("carbon_results").select("id", count="exact").execute().count
    leads_count = supabase.table("user_intents").select("id", count="exact").execute().count
    
    # 2. City Breakdown
    # Note: Using count grouping in Postgrest is tricky, simplified version:
    cities_data = supabase.table("users").select("city").execute().data
    city_breakdown = {}
    for item in cities_data:
        city = item.get('city', 'Unknown')
        city_breakdown[city] = city_breakdown.get(city, 0) + 1
        
    # 3. Vehicle Preference
    results_data = supabase.table("carbon_results").select("vehicle_type").execute().data
    vehicle_preference = {}
    for item in results_data:
        vtype = item.get('vehicle_type', 'Unknown')
        vehicle_preference[vtype] = vehicle_preference.get(vtype, 0) + 1
        
    # 4. Lead Trends (Simplified)
    leads_data = supabase.table("user_intents").select("created_at").execute().data
    lead_trends = {"x": [], "y": []}
    # Logic to aggregate by week/month could go here
    
    return {
        "totalUsers": users_count or 0,
        "totalSimulations": sims_count or 0,
        "totalLeads": leads_count or 0,
        "cityBreakdown": city_breakdown,
        "vehiclePreference": vehicle_preference,
        "leadTrends": {"x": ['Jan', 'Feb', 'Mar'], "y": [20, 35, leads_count or 0]}
    }
def get_user_data(user_id: str):
    if not supabase or not is_valid_uuid(user_id):
        return {
            "user": {"email": "john.doe@example.com", "city": "San Francisco", "created_at": "2025-10-01T00:00:00Z"},
            "results": [
                {"vehicle_type": "EV", "total_emissions": 12500, "timestamp": "2026-03-10T00:00:00Z"},
                {"vehicle_type": "Hybrid", "total_emissions": 14000, "timestamp": "2026-03-01T00:00:00Z"}
            ],
            "intents": [
                {"vehicle_type": "EV", "intent_type": "dealer_search", "created_at": "2026-03-11T00:00:00Z"}
            ]
        }
    
    user = supabase.table("users").select("*").eq("id", user_id).execute().data
    results = supabase.table("carbon_results").select("*").eq("user_id", user_id).execute().data
    intents = supabase.table("user_intents").select("*").eq("user_id", user_id).execute().data
    
    return {
        "user": user[0] if user else None,
        "results": results,
        "intents": intents
    }
