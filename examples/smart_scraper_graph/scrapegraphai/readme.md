# Smart Scraper Examples with Scrapegraph AI

This repository contains examples demonstrating how to use Scrapegraph AI's powerful web scraping capabilities to transform websites into structured data using natural language prompts.

## About Scrapegraph AI

[Scrapegraph AI](https://scrapegraphai.com) is a powerful web scraping API that transforms any website into structured data for AI agents and analytics. It's built specifically for AI agents and LLMs, featuring natural language instructions and structured JSON output.

Key features:
- Universal data extraction from any website
- Intelligent processing with advanced AI
- Lightning-fast setup with official SDKs
- Enterprise-ready with automatic proxy rotation
- Seamless integration with RAG systems

## Examples Included

### 1. Smart Scraper
The `smartscraper_scrapegraphai.py` example demonstrates how to extract structured data from a single website using natural language prompts.

### 2. Search Scraper
The `searchscraper_scrapegraphai.py` example shows how to:
- Search the internet for relevant information
- Extract structured data from multiple sources
- Merge and analyze information from different websites
- Get comprehensive answers to complex queries

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Scrapegraph-ai.git
cd Scrapegraph-ai
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `examples/smart_scraper_graph` directory with:
```env
SCRAPEGRAPH_API_KEY=your-api-key-here
```

## Usage

### Smart Scraper Example
```bash
python smartscraper_scrapegraphai.py
```

### Search Scraper Example
```bash
python searchscraper_scrapegraphai.py
```

## Example Outputs

### Smart Scraper Output
```python
Request ID: abc123...
Result: {
    "founders": [
        {
            "name": "Marco Vinciguerra",
            "role": "Founder & Software Engineer",
            "bio": "LinkedIn profile of Marco Vinciguerra"
        },
        {
            "name": "Lorenzo Padoan",
            "role": "Founder & CEO",
            "bio": "LinkedIn profile of Lorenzo Padoan"
        }
    ]
}
Reference URLs: ["https://scrapegraphai.com/about"]
```

### Search Scraper Output
```python
Request ID: xyz789...
Number of sources processed: 3

Extracted Information:
{
    "features": [
        "Universal data extraction",
        "Intelligent processing with AI",
        "Lightning-fast setup",
        "Enterprise-ready with proxy rotation"
    ],
    "benefits": [
        "Perfect for AI agents and LLMs",
        "Natural language instructions",
        "Structured JSON output",
        "Seamless RAG integration"
    ]
}

Sources:
1. https://scrapegraphai.com
2. https://scrapegraphai.com/features
3. https://scrapegraphai.com/docs
```

## Features Demonstrated

- Environment variable configuration
- API client initialization
- Smart scraping with natural language prompts
- Search-based scraping across multiple sources
- Error handling and response processing
- Secure credential management

## Pricing and Credits

Scrapegraph AI offers various pricing tiers:
- Free: 50 credits included
- Starter: $20/month, 5,000 credits
- Growth: $100/month, 40,000 credits
- Pro: $500/month, 250,000 credits
- Enterprise: Custom solutions

Service costs:
- Smart Scraper: 10 credits per webpage
- Search Scraper: 30 credits per query

## Support and Resources

- [Official Documentation](https://scrapegraphai.com/docs)
- [API Status](https://scrapegraphai.com/status)
- Contact: contact@scrapegraphai.com

## Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure
- Use environment variables for sensitive credentials

## License

This example is provided under the same license as Scrapegraph AI. See the [Terms of Service](https://scrapegraphai.com/terms) for more information.
