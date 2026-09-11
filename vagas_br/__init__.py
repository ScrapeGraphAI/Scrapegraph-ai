"""Brazilian tech job aggregator built on top of ScrapeGraphAI.

Collects developer / technology openings (CLT and PJ) from several Brazilian
job boards, normalises location (city, UF, region), contract type and work
model, stores them in SQLite and serves a filterable web page.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
