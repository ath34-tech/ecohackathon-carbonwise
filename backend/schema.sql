-- Supabase / PostgreSQL Schema Definition for CarbonWise AI

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100),
    is_partner BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Driving Profiles Table
CREATE TABLE IF NOT EXISTS driving_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    daily_distance NUMERIC NOT NULL,
    city_driving_ratio NUMERIC NOT NULL CHECK (city_driving_ratio >= 0 AND city_driving_ratio <= 1),
    highway_driving_ratio NUMERIC NOT NULL CHECK (highway_driving_ratio >= 0 AND highway_driving_ratio <= 1),
    ownership_years INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Vehicles Table (Static Dataset)
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_name VARCHAR(255) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL, -- e.g., EV, ICE, Hybrid
    battery_size_kwh NUMERIC, -- for EVs
    fuel_efficiency_mpg NUMERIC, -- for ICE/Hybrid
    manufacturing_emissions_kgco2 NUMERIC NOT NULL
);

-- Carbon Results Table
CREATE TABLE IF NOT EXISTS carbon_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(50) NOT NULL,
    manufacturing_emissions NUMERIC NOT NULL,
    usage_emissions NUMERIC NOT NULL,
    total_emissions NUMERIC NOT NULL,
    recommendation TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Insert sample vehicles for testing (Indian Context)
INSERT INTO vehicles (vehicle_name, vehicle_type, battery_size_kwh, fuel_efficiency_mpg, manufacturing_emissions_kgco2)
VALUES 
('Tata Nexon EV', 'EV', 40.5, NULL, 11000),
('Maruti Suzuki Swift', 'ICE', NULL, 23, 6500),
('Toyota Hyryder', 'Hybrid', 1.5, 27, 8000),
('MG ZS EV', 'EV', 50.3, NULL, 12500)
ON CONFLICT DO NOTHING;

-- User Intents / Leads Table
CREATE TABLE IF NOT EXISTS user_intents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(50),
    intent_type VARCHAR(50) NOT NULL, -- e.g., 'dealer_search', 'buy_now'
    context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Dealers Table
CREATE TABLE IF NOT EXISTS dealers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(255),
    specialty VARCHAR(50), -- EV, Luxury, Eco, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Notifications Log
CREATE TABLE IF NOT EXISTS notifications_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient_type VARCHAR(50) NOT NULL, -- 'dealer', 'partner'
    recipient_identifier VARCHAR(255) NOT NULL, -- email or chat_id
    channel VARCHAR(20) NOT NULL, -- 'email', 'telegram'
    status VARCHAR(20) DEFAULT 'sent',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Insert sample dealers (Indian Cities)
INSERT INTO dealers (name, email, location, specialty)
VALUES 
('Tata Motors Mumbai', 'sales.mumbai@tatamotors.example.com', 'Mumbai', 'EV'),
('Maruti Arena Delhi', 'contact.delhi@marutisuzuki.example.com', 'Delhi', 'ICE'),
('Reliable Toyota Bangalore', 'leads.blr@reliabletoyota.example.com', 'Bangalore', 'Hybrid'),
('MG Motor Pune', 'support.pune@mgmotor.example.com', 'Pune', 'EV'),
('Hyderabad EcoDrive', 'sales.hyd@ecodrive.example.com', 'Hyderabad', 'EV'),
('Chennai Green Wheels', 'contact.chn@greenwheels.example.com', 'Chennai', 'Hybrid'),
('Kolkata Smart Mobility', 'leads.kol@smartmobility.example.com', 'Kolkata', 'EV'),
('Ahmedabad Auto Hub', 'sales.ahd@autohub.example.com', 'Ahmedabad', 'ICE'),
('Jaipur Royal MG', 'contact.jpr@mgmotor.example.com', 'Jaipur', 'EV'),
('Surat Solar Cars', 'leads.srt@solarcars.example.com', 'Surat', 'EV'),
('Lucknow Green Motors', 'sales.lko@greenmotors.example.com', 'Lucknow', 'Hybrid'),
('Chandigarh EV Station', 'contact.chd@evstation.example.com', 'Chandigarh', 'EV')
ON CONFLICT DO NOTHING;

-- Insert sample users
INSERT INTO users (email, city)
VALUES 
('arjun.mehta@example.in', 'Mumbai'),
('priya.sharma@example.in', 'Delhi'),
('rahul.nair@example.in', 'Bangalore'),
('sneha.patel@example.in', 'Ahmedabad'),
('amit.gupta@example.in', 'Pune'),
('ananya.das@example.in', 'Kolkata'),
('vikram.singh@example.in', 'Jaipur'),
('karthik.r@example.in', 'Chennai'),
('mohammad.ali@example.in', 'Hyderabad'),
('deepa.k@example.in', 'Chandigarh')
ON CONFLICT DO NOTHING;

-- Insert sample carbon results (Simulations)
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'EV', 11000, 1500, 12500, 'Highly recommended for Mumbai stop-and-go traffic.' FROM users WHERE email = 'arjun.mehta@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'ICE', 6500, 12000, 18500, 'Consider an EV for better long-term savings in Delhi.' FROM users WHERE email = 'priya.sharma@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'Hybrid', 8000, 5000, 13000, 'Great balanced choice for Bangalore commutes.' FROM users WHERE email = 'rahul.nair@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'EV', 11000, 1000, 12000, 'Excellent footprint for Ahmedabad driving conditions.' FROM users WHERE email = 'sneha.patel@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'EV', 11000, 2000, 13000, 'EV is the best choice for Pune hilly terrain.' FROM users WHERE email = 'amit.gupta@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'ICE', 6500, 15000, 21500, 'High usage detected. Recommend shifting to EV in Kolkata.' FROM users WHERE email = 'ananya.das@example.in' ON CONFLICT DO NOTHING;
INSERT INTO carbon_results (user_id, vehicle_type, manufacturing_emissions, usage_emissions, total_emissions, recommendation)
SELECT id, 'Hybrid', 8000, 6000, 14000, 'Hybrid provides good range for Jaipur highways.' FROM users WHERE email = 'vikram.singh@example.in' ON CONFLICT DO NOTHING;

-- Insert sample user intents (Leads)
INSERT INTO user_intents (user_id, vehicle_type, intent_type, context)
SELECT id, 'EV', 'dealer_search', 'Looking for Tata Nexon EV dealers' FROM users WHERE email = 'arjun.mehta@example.in' ON CONFLICT DO NOTHING;
INSERT INTO user_intents (user_id, vehicle_type, intent_type, context)
SELECT id, 'Hybrid', 'buy_now', 'Interested in Toyota Hyryder availability' FROM users WHERE email = 'rahul.nair@example.in' ON CONFLICT DO NOTHING;
INSERT INTO user_intents (user_id, vehicle_type, intent_type, context)
SELECT id, 'EV', 'dealer_search', 'Ready for MG ZS EV test drive' FROM users WHERE email = 'amit.gupta@example.in' ON CONFLICT DO NOTHING;
INSERT INTO user_intents (user_id, vehicle_type, intent_type, context)
SELECT id, 'EV', 'buy_now', 'EV inquiry for Ahmedabad' FROM users WHERE email = 'sneha.patel@example.in' ON CONFLICT DO NOTHING;
INSERT INTO user_intents (user_id, vehicle_type, intent_type, context)
SELECT id, 'Hybrid', 'dealer_search', 'Searching for hybrid options in Jaipur' FROM users WHERE email = 'vikram.singh@example.in' ON CONFLICT DO NOTHING;
