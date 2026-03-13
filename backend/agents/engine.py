def calculate_emissions(driving_data: dict, vehicle_data: dict) -> dict:
    """
    Simplified Engine for Carbon Lifecycle Calculations
    """
    daily_km = driving_data.get('daily_distance_km', 0)
    years = driving_data.get('ownership_years', 10)
    city_ratio = driving_data.get('city_driving_ratio', 0.5)
    
    total_km = daily_km * 365 * years
    total_miles = total_km * 0.621371
    
    manufacturing = vehicle_data.get('manufacturing_emissions_kgco2', 0)
    v_type = vehicle_data.get('vehicle_type', 'ICE')
    
    usage_emissions = 0
    if v_type == 'ICE':
        mpg = vehicle_data.get('fuel_efficiency_mpg', 25)
        gallons = total_miles / mpg if mpg > 0 else 0
        usage_emissions = gallons * 8.887 # kg CO2 per gallon gasoline
    elif v_type == 'EV':
        # Assume 0.20 kWh per km
        total_kwh = total_km * 0.20  
        # Assume grid intensity is 0.385 kg CO2 per kWh (US Average)
        # This would normally be handled by the Energy Source Agent in CrewAI
        usage_emissions = total_kwh * 0.385
    elif v_type == 'Hybrid':
        mpg = vehicle_data.get('fuel_efficiency_mpg', 50)
        gallons = total_miles / mpg if mpg > 0 else 0
        usage_emissions = gallons * 8.887
        
    total = manufacturing + usage_emissions
    return {
        "vehicle_type": v_type,
        "manufacturing_emissions": manufacturing,
        "usage_emissions": round(usage_emissions, 2),
        "total_emissions": round(total, 2)
    }
