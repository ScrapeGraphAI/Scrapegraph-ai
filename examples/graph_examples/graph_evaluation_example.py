""" 
Module for evaluating the graph
"""
import os
from scrapegraphai.evaluators import TrulensEvaluator
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")

llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
}

list_of_inputs = [
    ("List me all the titles and project descriptions",
     "https://perinim.github.io/projects/", llm_config),
    ("Who is the author of the project?",
     "https://perinim.github.io/projects/", llm_config),
    ("What is the project about?", "https://perinim.github.io/projects/", llm_config)
]

# Create the TrulensEvaluator instance
trulens_evaluator = TrulensEvaluator(openai_key)
# Evaluate SmartScraperGraph on the list of inputs
(results_df, answer) = trulens_evaluator.evaluate(list_of_inputs, dashboard=False)

# Print the results
print(answer)
