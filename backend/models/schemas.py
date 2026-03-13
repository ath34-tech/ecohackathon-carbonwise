from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class DrivingProfileInput(BaseModel):
    daily_distance_km: float
    city_driving_ratio: float
    highway_driving_ratio: float
    ownership_years: int
    city: str
    email: str
    is_partner: bool = False

class VehicleInfo(BaseModel):
    vehicle_name: str
    vehicle_type: str
    manufacturing_emissions_kgco2: float
    battery_size_kwh: Optional[float] = None
    fuel_efficiency_mpg: Optional[float] = None

class CarbonRecommendationResponse(BaseModel):
    user_id: str
    recommended_vehicle_type: str
    comparison_data: list[dict]
    agent_reasoning: str

        
class AgentChatRequest(BaseModel):
    user_message: str

class UserIntentRequest(BaseModel):
    user_id: str
    vehicle_type: str
    intent_type: str  # e.g. "dealer_search", "rebate_check", "buy_now"
    context: Optional[str] = None

class AuthSignupRequest(BaseModel):
    name: str
    email: str
    city: Optional[str] = "Unknown"

class AuthLoginRequest(BaseModel):
    email: str

class CompareLCAInput(BaseModel):
    vehicle_ids: list[UUID]
    profile: DrivingProfileInput

class VehicleListResponse(BaseModel):
    vehicles: list[dict]
