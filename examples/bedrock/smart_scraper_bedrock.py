"""
Smartscraper example on bedrock
"""
import boto3

from scrapegraphai.graphs import SmartScraperGraph

# 0a. Initialize session
# If not required delete it
session = boto3.Session(
    aws_access_key_id="...",
    aws_secret_access_key="...",
    aws_session_token="...",
    region_name="us-east-1"
)

# 0b. Initialize client
client = session.client("bedrock-runtime")

# 1. Define graph configuration
config = {
    "llm": {
        "client": client,
        "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        "temperature": 0.0,
        "format": "json"
    },
    "embeddings": {
        "client": client,
        "model": "bedrock/cohere.embed-multilingual-v3",
    },
}

# 2. Create graph instance
graph = SmartScraperGraph(
    prompt="List me all the articles",
    source="https://perinim.github.io/projects",
    config=config
)

# 3. Scrape away!
print(graph.run())
