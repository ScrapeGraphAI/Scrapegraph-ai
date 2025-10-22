# 🎯 Adaptive Speaker Scraper

Intelligent scraper that automatically detects website type and chooses the optimal scraping strategy.

## 🧠 How It Works

The scraper analyzes each website and classifies it into three types:

### 1. **Pure HTML**
- ✅ All speaker data in HTML text
- 💰 **Strategy**: `SmartScraperGraph` (cheapest, fastest)
- 📊 **Detection**: Completeness score ≥ 80%

### 2. **Mixed Content**
- ✅ Some data in HTML, some in images
- 💰 **Strategy**: `OmniScraperGraph` (selective image processing)
- 📊 **Detection**: 30-80% completeness + significant images
- 🎯 Only processes relevant images (not all)

### 3. **Pure Images**
- ✅ All data embedded in images/widgets
- 💰 **Strategy**: `ScreenshotScraperGraph` (full page screenshot)
- 📊 **Detection**: Completeness score < 30% or no speakers found
- 🎯 Sends 2 screenshots instead of 40+ individual images

## 🚀 Usage

### Basic Example

```python
from adaptive_speaker_scraper import scrape_with_optimal_strategy
from pydantic import BaseModel, Field
from typing import List

class Speaker(BaseModel):
    full_name: str = Field(default="")
    company: str = Field(default="")
    position: str = Field(default="")

class SpeakerScrapeResult(BaseModel):
    speakers: List[Speaker] = Field(default_factory=list)

config = {
    "llm": {
        "api_key": "your-openai-key",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
}

result = scrape_with_optimal_strategy(
    url="https://example.com/speakers",
    prompt="Extract all speakers with their names, companies, and positions",
    config=config,
    schema=SpeakerScrapeResult,
)

print(f"Strategy used: {result['strategy_used']}")
print(f"Speakers found: {len(result['data']['speakers'])}")
```

### Run Demo

```bash
python examples/adaptive_speaker_scraper.py
```

## 🎛️ Decision Flow

```
Start
  ↓
Run SmartScraperGraph (fast, cheap)
  ↓
Analyze results:
  - Completeness score
  - Number of speakers
  - Number of images
  ↓
┌─────────────────────┐
│ Completeness ≥ 80%? │ → YES → ✅ Use SmartScraperGraph result
└─────────────────────┘
         ↓ NO
┌─────────────────────────────────┐
│ 30-80% complete + many images?  │ → YES → 🔄 Re-run with OmniScraperGraph
└─────────────────────────────────┘
         ↓ NO
┌──────────────────────────────┐
│ Very low data (<30%)?        │ → YES → 📸 Use ScreenshotScraperGraph
└──────────────────────────────┘
```

## 💰 Cost Comparison

### Example: 40 speakers on a page

| Website Type | Strategy | API Calls | Cost (approx) |
|-------------|----------|-----------|---------------|
| Pure HTML | SmartScraperGraph | 1-2 text calls | $0.01 |
| Mixed Content | OmniScraperGraph | 1 text + 20 images | $0.30 |
| Pure Images | ScreenshotScraperGraph | 1 text + 2 screenshots | $0.05 |

**Without adaptive detection**: Always using OmniScraperGraph with all images would cost **$0.50+**

## 🔧 Customization

### Adjust Detection Thresholds

```python
# In detect_website_type function:

# More conservative (prefer cheaper strategies)
if completeness >= 0.7:  # Lower from 0.8
    website_type = WebsiteType.PURE_HTML

# More aggressive image processing
elif completeness >= 0.5:  # Higher from 0.3
    website_type = WebsiteType.MIXED_CONTENT
```

### Control Image Processing

```python
# In scrape_with_optimal_strategy:
omni_config["max_images"] = min(
    analysis.get("num_images_detected", 10),
    20  # Limit to 20 images maximum
)
```

## 📊 Output Format

```json
{
  "url": "https://example.com/speakers",
  "website_type": "mixed_content",
  "strategy_used": "OmniScraperGraph",
  "analysis": {
    "completeness_score": 0.45,
    "num_speakers_found": 12,
    "num_images_detected": 24
  },
  "data": {
    "event": { ... },
    "speakers": [ ... ]
  }
}
```

## 🎯 Best Practices

1. **Start with gpt-4o-mini** for initial detection (cheap)
2. **Upgrade to gpt-4o** if PURE_IMAGES detected (better vision)
3. **Cache results** to avoid re-analyzing same URLs
4. **Batch process** multiple URLs to optimize API usage

## 🐛 Troubleshooting

### "Not enough speakers extracted"
- The page might be PURE_IMAGES but detected as MIXED_CONTENT
- Solution: Lower the completeness threshold

### "Too expensive"
- Reduce `max_images` in OmniScraperGraph
- Or force ScreenshotScraperGraph for image-heavy pages

### "Missing some speakers"
- Increase `max_images` for MIXED_CONTENT sites
- Or use scroll/wait options in config for lazy-loaded content

## 📚 Related Examples

- `examples/frontend/batch_speaker_app.py` - Streamlit UI with manual strategy selection
- `examples/smart_scraper_graph/` - Text-only extraction examples
- `examples/omni_scraper_graph/` - Image+text extraction examples

---

**Key Advantage**: Automatically balances cost vs accuracy without manual intervention! 🎉
