# Extract structured data from an X post

Use Xquik when a public X status page does not expose stable HTML to the
browser loader. The integration retrieves the post through the published tweet
lookup API, then runs the normal SmartScraperGraph extraction pipeline.

Install the optional dependency:

```bash
pip install scrapegraphai x_twitter_scraper
```

Copy `.env.example` to `.env` and set both API keys. Then run:

```bash
python examples/xquik_tweet/xquik_tweet.py
```

The source can be a public `x.com` or `twitter.com` status URL. It can also be
a numeric tweet ID.

Xquik is an independent third-party service. Not affiliated with X Corp.
