# CarbonWise Technical Guide & Feature Breakdown

This document serves as a comprehensive reference for the CarbonWise Lifecycle Assessment (LCA) platform. It explains the terminology, the logic behind the features, and provides a script for presenting the application.

---

## 1. Glossay of Terms

### Environmental Terms
*   **LCA (Life Cycle Assessment)**: A methodology for assessing environmental impacts associated with all the stages of a vehicle's life—from raw material extraction through materials processing, manufacture, distribution, use, repair and maintenance, and disposal (recycling).
*   **Manufacturing Emissions**: The "upfront" carbon cost. This includes the CO2 produced while mining materials (like lithium for batteries) and the factory energy used to build the car.
*   **Usage Emissions**: The carbon footprint generated while driving. For EVs, this comes from the electricity grid; for ICE/Hybrids, it comes from burning fuel.
*   **Grid Greening**: The concept that as countries switch to renewable energy (solar/wind), the electricity used to charge EVs becomes "cleaner" over time, reducing their usage emissions.
*   **Carbon Break-even (Payback Period)**: The point in time (usually in years or km) when an EV's lower usage emissions finally "cancel out" its higher manufacturing emissions compared to a petrol car.

### Financial Terms
*   **TCO (Total Cost of Ownership)**: The total amount spent on a vehicle over its life, including the purchase price, fuel/electricity, maintenance, and insurance.
*   **Federal Rebate**: Government incentives (Tax credits) provided to encourage the adoption of sustainable mobility.
*   **Financial Drift**: The percentage difference in total cost between two vehicle types over a 10-year period.

### UI & System Terms
*   **Node**: A specific vehicle or user data point in the system's analysis graph.
*   **City Congestion Vector**: A variable representing the percentage of driving done in stop-and-go city traffic, which significantly affects fuel efficiency vs. regenerative braking in EVs.
*   **Technex Verified**: Indicates that the calculations follow standardized LCA protocols.

---

## 2. Feature Details

### A. AI Recommendation Engine (Home Page)
*   **Logic**: Uses a Pydantic-driven backend to analyze your specific driving profile.
*   **The Agent**: A specialized AI agent (CrewAI) processes the raw CO2 numbers and provides a natural language recommendation based on your city and habits.

### B. Interactive Fleet Simulation (Compare Page)
*   **Side-by-Side Analysis**: Compare any two vehicles from the Supabase dataset.
*   **10-Year TCO Path**: A dynamic projection of costs in ₹ (Rupees) including energy savings.
*   **Carbon Trajectory Chart**: A step-chart showing how emissions accumulate year-over-year.
*   **Grid Simulation**: A toggle that lets you see how much cleaner an EV gets if the power grid improves.

### C. Live Profile Integration (Profile Page)
*   **Real Data Fetching**: No placeholders. User names, cities, and join dates are pulled live from Supabase.
*   **LCA Logs**: A historical record of every simulation you've run, allowing you to track your research history.
*   **Session Guard**: Automatically detects if your login session is missing required ID nodes and prompts for a sync.

---

## 3. Teaching Script (Page-by-Page)

### [Page 1: The Dashboard]
**Script**: "Welcome to the CarbonWise Dashboard. Here, we start by creating your **Driving Profile**. Enter your daily mileage and **City Congestion Vector**—that is, how much of your drive is in heavy traffic. Our **AI Agent** will then crunch the **LCA (Life Cycle Assessment)** data to give you a personalized recommendation. Notice the **Nutritional Label**—just like food, we show you exactly what 'ingredients' (Manufacturing vs. Usage emissions) go into your car's footprint."

### [Page 2: The Comparison Engine]
**Script**: "Now let's dive into the **Fleet Simulation**. Switch between different **Nodes** to see a side-by-side battle. On the left, we have the **TCO Chart** in Rupees—this proves that while an EV might cost more upfront, the energy savings over 10 years bring the cost down. On the right is the **Carbon Break-even** chart. It shows you the exact year where an EV becomes 'greener' than a petrol car. Toggle the **Grid Greening** switch to see how future renewable energy makes your EV even more sustainable."

### [Page 3: The User Profile]
**Script**: "Finally, your **Profile Node** stores all your research. Unlike static apps, this is synced with **Supabase**. You can see your **LCA Logs**, which are your past simulations, and your **Active Intentions**—these are the dealers we've matched you with based on your interest in sustainable mobility. If you see a **Stale Session** alert, it's our security system ensuring your ID nodes are perfectly synced for data integrity."

---
*Documentation generated for CarbonWise v1.0*
