from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.crew import CarbonWiseCrew
from models.schemas import (
    DrivingProfileInput, 
    CarbonRecommendationResponse, 
    AgentChatRequest, 
    UserIntentRequest,
    AuthSignupRequest,
    AuthLoginRequest,
    CompareLCAInput,
    VehicleListResponse
)
from services.db import (
    get_or_create_user, 
    save_driving_profile, 
    save_carbon_result, 
    get_vehicles, 
    save_user_intent, 
    get_dealers,
    get_analytics,
    get_user_data
)
from agents.engine import calculate_emissions
from services.email_service import EmailService
from services.telegram_service import TelegramService

# Initialize AI Crew once at startup
carbon_crew = CarbonWiseCrew()

app = FastAPI(title="CarbonWise AI Backend", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, specify domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "CarbonWise API is running"}

@app.post("/api/auth/signup")
def auth_signup(request: AuthSignupRequest):
    user = get_or_create_user(request.email, request.city)
    return {"status": "success", "user": {"name": request.name, "email": request.email, "id": str(user.get("id"))}}

@app.post("/api/auth/login")
def auth_login(request: AuthLoginRequest):
    user = get_or_create_user(request.email, "Unknown")
    return {"status": "success", "user": {"name": request.email.split('@')[0], "email": request.email, "id": str(user.get("id"))}}

@app.post("/agent/chat")
def agent_chat(request: AgentChatRequest):
    response = carbon_crew.chat(request.user_message)
    return {"response": response}

@app.post("/api/intent")
def record_intent(request: UserIntentRequest):
    # 1. Save intent to DB
    result = save_user_intent(request.user_id, request.model_dump())
    
    # 2. Trigger AI Dealer Lead Agent
    # In a real app, we'd fetch the user's data from the DB first
    # For now, we simulate the follow-up
    dealers = get_dealers(specialty=request.vehicle_type)
    if dealers:
        dealer = dealers[0]
        # Generate AI email draft
        ai_draft = carbon_crew.generate_lead_email({"city": "Unknown"}, request.model_dump())
        
        # Send Email to Dealer
        EmailService.send_dealer_lead(dealer['email'], {
            **request.model_dump(),
            "ai_draft": ai_draft
        })
        
        # Notify Partner via Telegram about the new lead
        TelegramService.send_notification(f"🚀 *New Lead Captured*\nUser reached out for *{request.vehicle_type}* ({request.intent_type}).\nLead shared with *{dealer['name']}*.")

    return {"status": "success", "recorded_intent": result}

@app.get("/api/analytics")
def fetch_analytics():
    return get_analytics()

@app.get("/api/vehicles")
def list_vehicles():
    """Returns the list of all available vehicles from Supabase."""
    vehicles = get_vehicles()
    return {"vehicles": vehicles}

@app.get("/api/user/{user_id}")
def fetch_user_data(user_id: str):
    """Fetches full profile data for a specific user."""
    return get_user_data(user_id)

@app.post("/api/compare-lca")
def compare_lca(request: CompareLCAInput):
    """Performs side-by-side LCA comparison for two vehicles."""
    vehicles_data = get_vehicles()
    selected_vehicles = [v for v in vehicles_data if str(v.get('id', '')) in [str(vid) for vid in request.vehicle_ids]]
    
    if len(selected_vehicles) < 2:
        selected_vehicles = vehicles_data[:2]

    results = []
    for vehicle in selected_vehicles:
        res = calculate_emissions(request.profile.model_dump(), vehicle)
        results.append(res)
    
    return {"results": results}

@app.post("/recommend-vehicle", response_model=CarbonRecommendationResponse)
def recommend_vehicle(profile: DrivingProfileInput):
    # 1. User tracking
    user = get_or_create_user(profile.email, profile.city, profile.is_partner)
    user_id = user.get("id")
    
    # 2. Save Driving Profile
    save_driving_profile(user_id, profile.model_dump())
    
    # 3. Get Vehicle Types
    vehicles = get_vehicles()
    
    # 4. Calculate Emissions for all available vehicle types
    comparison_data = []
    for vehicle in vehicles:
        emissions = calculate_emissions(profile.model_dump(), vehicle)
        comparison_data.append(emissions)
        
    # 5. Connect to AI Agent for Recommendation
    best_vehicle = min(comparison_data, key=lambda x: x['total_emissions'])
    
    # Use real CrewAI backened reasoning instead of placeholder logic
    agent_reasoning = carbon_crew.run(profile.model_dump(), comparison_data)

    
    # 6. Save the recommendation result
    result = {
        "vehicle_type": best_vehicle['vehicle_type'],
        "manufacturing_emissions": best_vehicle['manufacturing_emissions'],
        "usage_emissions": best_vehicle['usage_emissions'],
        "total_emissions": best_vehicle['total_emissions'],
        "recommendation": agent_reasoning
    }
    save_carbon_result(user_id, result)
    
    return CarbonRecommendationResponse(
        user_id=str(user_id),
        recommended_vehicle_type=best_vehicle['vehicle_type'],
        comparison_data=comparison_data,
        agent_reasoning=agent_reasoning
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
