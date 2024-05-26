import os, json
from dotenv import load_dotenv
from scrapegraphai.graphs import PDFScraperGraph

load_dotenv()


# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False,
}

source = """
    The Divine Comedy, Italian La Divina Commedia, original name La commedia, long narrative poem written in Italian 
    circa 1308/21 by Dante. It is usually held to be one of the world s great works of literature. 
    Divided into three major sections—Inferno, Purgatorio, and Paradiso—the narrative traces the journey of Dante 
    from darkness and error to the revelation of the divine light, culminating in the Beatific Vision of God. 
    Dante is guided by the Roman poet Virgil, who represents the epitome of human knowledge, from the dark wood 
    through the descending circles of the pit of Hell (Inferno). He then climbs the mountain of Purgatory, guided 
    by the Roman poet Statius, who represents the fulfilment of human knowledge, and is finally led by his lifelong love, 
    the Beatrice of his earlier poetry, through the celestial spheres of Paradise.
"""

schema = """
    {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string"
            },
            "topics": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
"""

pdf_scraper_graph = PDFScraperGraph(
    prompt="Summarize the text and find the main topics",
    source=source,
    config=graph_config,
    schema=schema,
)
result = pdf_scraper_graph.run()

print(json.dumps(result, indent=4))
