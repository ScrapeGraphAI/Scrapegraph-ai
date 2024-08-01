"""
Module for showing how PDFScraper multi works
"""
import os
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from scrapegraphai.graphs import PdfScraperMultiGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

fireworks_api_key = os.getenv("FIREWORKS_APIKEY")

graph_config = {
    "llm": {
        "api_key": fireworks_api_key,
        "model": "fireworks/accounts/fireworks/models/mixtral-8x7b-instruct"
    },
    "verbose": True,
}

# ************************************************
# Define the output schema for the graph
# ************************************************

class Article(BaseModel):
    independent_variable: str = Field(description="(IV): The variable that is manipulated or considered as the primary cause affecting other variables.")
    dependent_variable: str = Field(description="(DV) The variable that is measured or observed, which is expected to change as a result of variations in the Independent Variable.")
    exogenous_shock: str = Field(description="Identify any external or unexpected events used in the study that serve as a natural experiment or provide a unique setting for observing the effects on the IV and DV.")

class Articles(BaseModel):
    articles: List[Article]

# ************************************************
# Define the sources for the graph
# ************************************************

sources = [
    "This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weather the interaction between call center architecture and outdoor weather conditions in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.",
    "The diffusion of social media coincided with a worsening of mental health conditions among adolescents and young adults in the United States, giving rise to speculation that social media might be detrimental to mental health. Our analysis couples data on student mental health around the years of Facebook's expansion with a generalized difference-in-differences empirical strategy. We find that the roll-out of Facebook at a college increased symptoms of poor mental health, especially depression. We also find that, among students predicted to be most susceptible to mental illness, the introduction of Facebook led to increased utilization of mental healthcare services. Lastly, we find that, after the introduction of Facebook, students were more likely to report experiencing impairments to academic performance resulting from poor mental health. Additional evidence on mechanisms suggests that the results are due to Facebook fostering unfavorable social comparisons."
]

prompt = """
Analyze the abstracts provided from an academic journal article to extract and clearly identify the Independent Variable (IV), Dependent Variable (DV), and Exogenous Shock.
"""

# *******************************************************
# Create the SmartScraperMultiGraph instance and run it
# *******************************************************

multiple_search_graph = PdfScraperMultiGraph(
    prompt=prompt,
    source= sources,
    schema=Articles,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
