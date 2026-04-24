from scraper import run_scraper
from sentiment import analyze_properties

print("="*50)
print("ZAMEEN PROPERTY INTELLIGENCE PIPELINE")
print("="*50)

print("\n[1/2] Scraping properties...")
run_scraper()

print("\n[2/2] Analyzing deals...")
analyze_properties()

print("\nDone! Run: uvicorn api:app --reload")
print("\nAPI Endpoints:")
print("  /properties        → all properties")
print("  /search?city=Lahore → filter by city")
print("  /deals?city=Lahore  → good deals only")
print("  /stats             → market overview")
print("  /chat?question=... → AI property assistant")