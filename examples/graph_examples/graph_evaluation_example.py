""" 
Module for evaluating the graph
"""
import os
from dotenv import load_dotenv
from scrapegraphai.evaluators import TrulensEvaluator

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
}

list_of_inputs = [
    (
        "List me all the titles and project descriptions",
        "https://perinim.github.io/projects/",
        graph_config
    ),
    (
        "Who is the author of the project?",
        "https://perinim.github.io/projects/",
        graph_config
    ),
    (
        "What are the projects about?",
        "https://perinim.github.io/projects/",
        graph_config
    ),
]

# Create the TrulensEvaluator instance
trulens_evaluator = TrulensEvaluator(graph_config["llm"]["api_key"])
# Evaluate SmartScraperGraph on the list of inputs
(results_df, answer) = trulens_evaluator.evaluate(
    list_of_inputs, dashboard=True)

print(answer)
