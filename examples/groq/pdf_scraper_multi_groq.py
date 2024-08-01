"""
Module for showing how PDFScraper multi works
"""
import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import PdfScraperMultiGraph

load_dotenv()
groq_key = os.getenv("GROQ_APIKEY")

graph_config = {
    "llm": {
        "model": "groq/gemma-7b-it",
        "api_key": groq_key,
        "temperature": 0
    },
    "library": "beautifulsoup"
}

# ***************
# Covert to list
# ***************

sources = [
    "This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weatherâ€”the interaction between call center architecture and outdoor weather conditionsâ€”in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity â€“ largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.",
    "This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weatherâ€”the interaction between call center architecture and outdoor weather conditionsâ€”in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity â€“ largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.",
    "This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weatherâ€”the interaction between call center architecture and outdoor weather conditionsâ€”in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity â€“ largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.",
    "This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weatherâ€”the interaction between call center architecture and outdoor weather conditionsâ€”in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity â€“ largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.",
]

prompt = """
You are an expert in reviewing academic manuscripts. Please analyze the abstracts provided from an academic journal article to extract and clearly identify the following elements:

Independent Variable (IV): The variable that is manipulated or considered as the primary cause affecting other variables.
Dependent Variable (DV): The variable that is measured or observed, which is expected to change as a result of variations in the Independent Variable.
Exogenous Shock: Identify any external or unexpected events used in the study that serve as a natural experiment or provide a unique setting for observing the effects on the IV and DV.
Response Format: For each abstract, present your response in the following structured format:

Independent Variable (IV):
Dependent Variable (DV):
Exogenous Shock:

Example Queries and Responses:

Query: This paper provides evidence from a natural experiment on the relationship between positive affect and productivity. We link highly detailed administrative data on the behaviors and performance of all telesales workers at a large telecommunications company with survey reports of employee happiness that we collected on a weekly basis. We use variation in worker mood arising from visual exposure to weather the interaction between call center architecture and outdoor weather conditions in order to provide a quasi-experimental test of the effect of happiness on productivity. We find evidence of a positive impact on sales performance, which is driven by changes in labor productivity largely through workers converting more calls into sales, and to a lesser extent by making more calls per hour and adhering more closely to their schedule. We find no evidence in our setting of effects on measures of high-frequency labor supply such as attendance and break-taking.

Response:

Independent Variable (IV): Employee happiness.
Dependent Variable (DV): Overall firm productivity.
Exogenous Shock: Sudden company-wide increase in bonus payments.

Query: The diffusion of social media coincided with a worsening of mental health conditions among adolescents and young adults in the United States, giving rise to speculation that social media might be detrimental to mental health. In this paper, we provide quasi-experimental estimates of the impact of social media on mental health by leveraging a unique natural experiment: the staggered introduction of Facebook across U.S. colleges. Our analysis couples data on student mental health around the years of Facebook's expansion with a generalized difference-in-differences empirical strategy. We find that the roll-out of Facebook at a college increased symptoms of poor mental health, especially depression. We also find that, among students predicted to be most susceptible to mental illness, the introduction of Facebook led to increased utilization of mental healthcare services. Lastly, we find that, after the introduction of Facebook, students were more likely to report experiencing impairments to academic performance resulting from poor mental health. Additional evidence on mechanisms suggests that the results are due to Facebook fostering unfavorable social comparisons.

Response:

Independent Variable (IV): Exposure to social media.
Dependent Variable (DV): Mental health outcomes.
Exogenous Shock: staggered introduction of Facebook across U.S. colleges.
"""
# *******************************************************
# Create the SmartScraperMultiGraph instance and run it
# *******************************************************

multiple_search_graph = PdfScraperMultiGraph(
    prompt=prompt,
    source= sources,
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
