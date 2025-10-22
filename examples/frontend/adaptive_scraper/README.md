# 🎯 Adaptive Speaker Scraper - Web UI

Beautiful web interface for the intelligent adaptive speaker scraper. Automatically detects website type and chooses the optimal scraping strategy.

## 🌟 Features

- ✅ **Clean, modern UI** - Easy to use interface
- 🧠 **Intelligent detection** - Auto-detects Pure HTML, Mixed Content, or Pure Images
- 💰 **Cost-optimized** - Uses cheapest strategy that works
- 📊 **Real-time job tracking** - Watch scraping progress live
- 📥 **Excel export** - Download results with metadata
- 🎯 **Strategy display** - See which strategy was used

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install required Python packages
pip install fastapi uvicorn pandas openpyxl python-dotenv

# Make sure ScrapeGraphAI is installed
pip install scrapegraphai playwright
playwright install
```

### 2. Set Environment Variables

Create `.env` file in the root of ScrapeGraphAI project:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Start the Server

```bash
cd examples/frontend/adaptive_scraper
python backend.py
```

### 4. Open the UI

Navigate to: **http://localhost:8000/ui/index.html**

## 📖 How to Use

1. **Enter URLs**: Paste event website URLs (one per line)
2. **Click "Start Scrape"**: The system will:
   - Analyze the website
   - Choose optimal strategy (SmartScraper, OmniScraper, or ScreenshotScraper)
   - Extract all speaker data
3. **Download Results**: Click download when job completes

## 🎨 UI Overview

```
┌─────────────────────────────────────────┐
│  🎯 Adaptive Speaker Scraper            │
│  Intelligently detects website type...  │
├─────────────────────────────────────────┤
│                                         │
│  Event URLs:                            │
│  ┌─────────────────────────────────┐   │
│  │ https://example.com/speakers    │   │
│  │ https://another.com/lineup      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Timeout: [60] seconds                  │
│  Engine: [ScrapeGraphAI]                │
│                                         │
│  [Start Scrape]                         │
│                                         │
├─────────────────────────────────────────┤
│  Jobs                                   │
├──────┬──────────┬──────────┬───────────┤
│ ID   │ Status   │ File     │ Action    │
├──────┼──────────┼──────────┼───────────┤
│ 1... │ running  │ -        │ -         │
│ 2... │ complete │ vds_...  │ Download  │
└──────┴──────────┴──────────┴───────────┘
```

## 🔧 API Endpoints

### POST `/scrape_sga`
Start a new scraping job

**Request:**
```json
{
  "urls": ["https://example.com/speakers"],
  "timeout": 60
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued"
}
```

### GET `/status/{job_id}`
Get job status

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "speaker_count": 45,
  "strategy_used": "SmartScraperGraph",
  "website_type": "pure_html",
  "file_path": "outputs/example_2025_10_19.xlsx"
}
```

### GET `/download/{job_id}`
Download scraped Excel file

## 📊 Output Format

Excel file with 3 sheets:

1. **Speakers** - All speaker data
2. **Event Info** - Event metadata
3. **Metadata** - Scraping details (strategy used, completeness, etc.)

## 🎯 Strategy Detection

| Website Type | Completeness | Strategy | Cost |
|-------------|--------------|----------|------|
| Pure HTML | ≥80% | SmartScraperGraph | ~$0.01 |
| Mixed Content | 50-80% | OmniScraperGraph | ~$0.30 |
| Pure Images | <50% | ScreenshotScraperGraph | ~$0.05 |

## 🐛 Troubleshooting

### "Job failed" error
- Check that OPENAI_API_KEY is set correctly
- Verify the URL is accessible
- Check backend logs for details

### "No speakers extracted"
- The website might need JavaScript rendering
- Try increasing timeout
- Check if the website structure is unusual

### UI not loading
- Make sure backend is running on port 8000
- Check console for errors
- Verify all files are in the correct directory

## 💡 Tips

- **Test with known websites first** (like vds.tech/speakers)
- **Use gpt-4o model** for better image recognition
- **Batch multiple URLs** - each gets processed separately
- **Check the strategy used** to understand why it chose that approach

## 🔗 Related Files

- `adaptive_speaker_scraper.py` - Core adaptive scraping logic
- `ADAPTIVE_SCRAPER_README.md` - Detailed strategy documentation

---

**Happy Scraping!** 🎉
