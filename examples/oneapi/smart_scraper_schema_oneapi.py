""" 
Basic example of scraping pipeline using SmartScraper
"""

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************
schema= """
    { 
    "Projects": [
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            }, 
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            } 
        ] 
    } 
"""

# ************************************************
# Define the configuration for the graph
# *********************************************

graph_config = {
    "llm": {
        "api_key": "***************************",
        "model": "oneapi/qwen-turbo",
        "base_url": "http://127.0.0.1:3000/v1",  # 设置 OneAPI URL
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://127.0.0.1:11434",  # 设置 Ollama URL
    }
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="该网站为XXXXX,请提取出标题、发布时间、发布来源以及内容摘要,并以中文回答。",
    # 也可以使用已下载的 HTML 代码的字符串
    source="http://XXXX",
    schema=schema,
    config=graph_config
)

# ************************************************
# Get graph execution info
# ************************************************
result = smart_scraper_graph.run()
print(result)
print(prettify_exec_info(result))
