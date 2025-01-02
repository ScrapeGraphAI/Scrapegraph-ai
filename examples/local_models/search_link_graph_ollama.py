""" 
Basic example of scraping pipeline using SmartScraper
"""
from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import prettify_exec_info
# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3.1:8b",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "base_url": "http://localhost:11434", # set ollama URL arbitrarily
    },
  
    "verbose": True,
    "headless": False,
    "filter_config": {
        "diff_domain_filter": True,
        # "img_exts": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        # "lang_indicators": ['lang=', '/fr', '/pt', '/es', '/de', '/jp', '/it'],
        # "irrelevant_keywords": [
        #         '/login', '/signup', '/register', '/contact', 'facebook.com', 'twitter.com', 
        #         'linkedin.com', 'instagram.com', '.js', '.css', '/wp-content/', '/wp-admin/', 
        #         '/wp-includes/', '/wp-json/', '/wp-comments-post.php', ';amp', '/about', 
        #         '/careers', '/jobs', '/privacy', '/terms', '/legal', '/faq', '/help',
        #         '.pdf', '.zip', '/news', '/files', '/downloads'
        #     ]
    },
}

# ************************************************
# Create the SearchLinkGraph instance and run it
# ************************************************

smart_scraper_graph = SearchLinkGraph(
    source="https://sport.sky.it/nba?gr=www",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
