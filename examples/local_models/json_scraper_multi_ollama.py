"""
Module for showing how PDFScraper multi works
"""
import os 
from scrapegraphai.graphs import PdfScraperMultiGraph

graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        "model_tokens": 4000,
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
    },
    "verbose": True,
    "headless": False,
}
FILE_NAME = "inputs/example.json"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

    
json_scraper_graph = JSONScraperGraph(
    prompt="List me all the authors, title and genres of the books",
    source=text,  # Pass the content of the file, not the file object
    config=graph_config
)



results = []
for source in sources:
    pdf_scraper_graph = PdfScraperMultiGraph(
        prompt=prompt,
        source=source,
        config=graph_config
    )
    result = pdf_scraper_graph.run()
    results.append(result)

print(results)
