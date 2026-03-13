from crewai import Agent, Task, Crew, Process, LLM
import os

from dotenv import load_dotenv
load_dotenv()

# We use the native CrewAI LLM wrapper initialized for Gemini
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

class CarbonWiseCrew:
    def __init__(self):
        # Initialize 5 agents according to HLD
        self.user_query_agent = Agent(
            role='User Query Agent',
            goal='Interpret user inputs and structure driving data appropriately.',
            backstory='An expert data interpreter who structures user mobility queries.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.driving_pattern_agent = Agent(
            role='Driving Pattern Agent',
            goal='Calculate total driving distance and energy consumption parameters.',
            backstory='A logistics expert focused on analyzing long-term driving habits.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.lifecycle_emission_agent = Agent(
            role='Lifecycle Emission Agent',
            goal='Compute vehicle lifecycle emissions from manufacturing to disposal.',
            backstory='An environmental scientist specializing in automotive lifecycle analysis (LCA).',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.energy_source_agent = Agent(
            role='Energy Source Agent',
            goal='Determine electricity carbon intensity based on geographic location.',
            backstory='An energy grid analyst with deep knowledge of regional power sources.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        self.recommendation_agent = Agent(
            role='Recommendation Agent',
            goal='Synthesize data to generate the optimal sustainable vehicle recommendation for the Indian market.',
            backstory='A sustainability advisor who personalizes eco-friendly transportation advice, focusing on Indian infrastructure and pricing in Rupees (₹).',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        self.dealer_lead_agent = Agent(
            role='Dealer Lead Agent',
            goal='Draft professional, high-conversion lead emails to car dealers.',
            backstory='A master of business communication who knows how to present user intent to dealers effectively.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def generate_lead_email(self, user_data: dict, intent_data: dict):
        """Generates a professional email draft for a dealer based on user intent."""
        if not os.getenv("GEMINI_API_KEY"):
            return "Professional interest recorded. Follow up pending."
            
        lead_task = Task(
            description=f"""
            Draft a professional lead email for a dealer.
            User Profile: {user_data}
            Interest: {intent_data.get('vehicle_type')}
            Intent Action: {intent_data.get('intent_type')}
            
            The email should:
            1. Introduce the user as a matching high-intent lead from CarbonWise.
            2. Explain why they are a good match (based on their driving habits).
            3. Use a tone that encourages the dealer to offer a test drive or special quote.
            4. Be concise and professional.
            """,
            agent=self.dealer_lead_agent,
            expected_output="A professional email body draft."
        )
        
        crew = Crew(
            agents=[self.dealer_lead_agent],
            tasks=[lead_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

    def run(self, user_data: dict, comparison_results: list[dict]):
        if not os.getenv("GEMINI_API_KEY"):
            return "CrewAI agents are structured but require a GEMINI_API_KEY to execute. Falling back to rule-based recommendation."
            
        # 1. User Query Interpretation Task
        interpret_task = Task(
            description=f"Analyze the user driving profile {user_data}. Identify the primary vehicle usage (e.g., commute, family, utility) and any specific geographic or habit-based constraints in the Indian context.",
            agent=self.user_query_agent,
            expected_output="A concise summary of user intent and driving requirements."
        )

        # 2. Driving Pattern Analysis Task
        pattern_task = Task(
            description=f"Examine the mileage and driving habits in {user_data}. Highlight how these patterns favor different vehicle technologies (EV, Hybrid, or ICE) considering Indian fuel and electricity costs.",
            agent=self.driving_pattern_agent,
            context=[interpret_task],
            expected_output="An analysis of the user's driving efficiency potential based on their habits."
        )

        # 3. Lifecycle Emission Assessment Task
        lifecycle_task = Task(
            description=f"Compare the vehicle lifecycle data: {comparison_results}. Explain the carbon trade-offs between manufacturing high-impact batteries (EVs) vs. operational tailpipe emissions (ICE).",
            agent=self.lifecycle_emission_agent,
            expected_output="A specialized breakdown of manufacturing vs usage carbon trade-offs for this specific comparison."
        )

        # 4. Energy Source & Grid Analysis Task
        grid_task = Task(
            description=f"Given the user's location in {user_data.get('city', 'Unknown')}, evaluate how Indian electricity carbon intensity (focused on coal-heavy but growing renewables) affects the EVs in {comparison_results}.",
            agent=self.energy_source_agent,
            expected_output="An assessment of regional grid cleanliness and its impact on the user's potential EV performance."
        )

        # 5. Final Personalized Recommendation Task
        recommend_task = Task(
            description=f"Synthesize the findings from all previous analyses along with the raw calculated data {comparison_results}. Generate the ultimate personalized, human-friendly recommendation in Rupees (₹).",
            agent=self.recommendation_agent,
            context=[interpret_task, pattern_task, lifecycle_task, grid_task],
            expected_output="A compelling 3-4 sentence recommendation that feels personal, mentions specific data points (grid, lifecycle, or habits), and encourages a sustainable purchase."
        )
        
        crew = Crew(
            agents=[
                self.user_query_agent, 
                self.driving_pattern_agent, 
                self.lifecycle_emission_agent, 
                self.energy_source_agent, 
                self.recommendation_agent
            ],
            tasks=[interpret_task, pattern_task, lifecycle_task, grid_task, recommend_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
        
    def chat(self, user_message: str):
        if not os.getenv("GEMINI_API_KEY"):
            return "I am the CarbonWise AI Assistant. Please configure my GEMINI_API_KEY in the backend so I can fully assist you!"
            
        # 1. Interpret Chat Intent
        query_task = Task(
           description=f"The user said: '{user_message}'. Determine their primary goal (asking for info, looking to buy, or technical question).",
           agent=self.user_query_agent,
           expected_output="A classification of the user's intent."
        )

        # 2. Formulate Expert Response
        response_task = Task(
           description=f"Based on the user's message '{user_message}' and their intent, formulate a helpful, expert response as the CarbonWise Purchase Concierge. Proactively guide them toward sustainable choices and local dealer options if relevant.",
           agent=self.recommendation_agent,
           context=[query_task],
           expected_output="A friendly, detailed, and persuasive chat response."
        )
        
        crew = Crew(
           agents=[self.user_query_agent, self.recommendation_agent],
           tasks=[query_task, response_task],
           process=Process.sequential,
           verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
