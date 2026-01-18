from google.adk.agents import Agent, AgentTool
from travel_planner.tools import google_search_grounding, location_search_tool

LLM = "gemini-3-pro-preview"


# ---------------- NEWS AGENT ----------------
news_agent = Agent(
    model=LLM,
    name="news_agent",
    description="Suggests key travel events and news; uses search for current info.",
    instruction="""
        You are responsible for providing a list of travel-related
        events and news recommendations based on the user's query.
        Limit the results to 10 items.
        You must use the google_search_grounding tool.
    """,
    tools=[google_search_grounding]
)


# ---------------- PLACES AGENT ----------------
places_agent = Agent(
    model=LLM,
    name="places_agent",
    description="Suggests locations based on user preferences.",
    instruction="""
        You are responsible for suggesting places based on the user's query.
        Limit the results to 10 items.
        Each place must include:
        - Name
        - Location
        - Address
        - Latitude and Longitude (use location_search_tool)
    """,
    tools=[location_search_tool]
)


# ---------------- MAIN TRAVEL INSPIRATION AGENT ----------------
travel_inspiration_agent = Agent(
    model=LLM,
    name="travel_planner_main",
    description="Inspires users with travel ideas and destinations.",
    instruction="""
        You are a travel inspiration agent helping users find their next
        dream vacation destination.

        Your goals:
        - Suggest destinations
        - Recommend activities at those destinations

        If the user asks for historical or general information,
        answer briefly and relate it back to travel inspiration.

        Tool usage:
        - Use news_agent to provide current travel events and news.
        - Use places_agent to suggest locations, nearby places, or hotels.
          Example: "find hotels near Eiffel Tower".
    """,
    tools=[
        AgentTool(agent=news_agent),
        AgentTool(agent=places_agent)
    ]
)
