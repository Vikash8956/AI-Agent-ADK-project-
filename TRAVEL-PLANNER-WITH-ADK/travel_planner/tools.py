# --- GOOGLE SEARCH AGENT ---
from google.adk.tools.google_search_agent_tool import google_search
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

LLM = "gemini-3-pro-preview"

_search_agent = Agent(
    model=LLM,
    name="google_search_wrapped_agent",
    description="An agent providing Google Search grounding capability",
    instruction="""
        Answer the user's question directly using the google_search tool.

        Guidelines:
        - Provide brief, concise, and actionable information
        - Focus on what matters to a tourist or traveler
        - Do NOT ask the user to look up information themselves

        IMPORTANT:
        - Always return responses in bullet points
        - Highlight key takeaways clearly
    """,
    tools=[google_search]
)

google_search_grounding = AgentTool(agent=_search_agent)


# ---LOCATION SEARCH TOOL (OPENSTREETMAP) ----
from google.adk.tools import FunctionTool
from geopy.geocoders import Nominatim
import requests


def find_nearby_places_open(
    query: str,
    location: str,
    radius: int = 3000,
    limit: int = 5
) -> str:
    """
    Find nearby places using free OpenStreetMap (Overpass API).

    Args:
        query (str): Type of place (e.g., "restaurant", "hospital", "gym")
        location (str): City or area name
        radius (int): Search radius in meters
        limit (int): Number of results

    Returns:
        str: Formatted list of nearby places
    """

    try:
        # Step 1: Geocode location
        geolocator = Nominatim(user_agent="open_place_finder")
        loc = geolocator.geocode(location)

        if not loc:
            return f"Could not find location '{location}'."

        lat, lon = loc.latitude, loc.longitude

        # Step 2: Overpass API query
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"{query}",i](around:{radius},{lat},{lon});
          node["shop"~"{query}",i](around:{radius},{lat},{lon});
          node["name"~"{query}",i](around:{radius},{lat},{lon});
        );
        out body;
        """

        response = requests.get(overpass_url, params={"data": overpass_query})
        if response.status_code != 200:
            return f" Overpass API error: {response.status_code}"

        data = response.json()
        elements = data.get("elements", [])

        if not elements:
            return f" No results found for '{query}' near {location}."

        # Step 3: Format results
        output = [f" Top {limit} results for '{query}' near {location}:"]
        for el in elements[:limit]:
            tags = el.get("tags", {})
            name = tags.get("name", "Unnamed place")
            street = tags.get("addr:street", "")
            city = tags.get("addr:city", "")
            address = ", ".join(filter(None, [street, city]))

            output.append(f"- {name} | {address if address else 'Address not available'}")

        return "\n".join(output)

    except Exception as e:
        return f" Error searching for '{query}' near '{location}': {str(e)}"


# Register as ADK Function Tool
location_search_tool = FunctionTool(func=find_nearby_places_open)
