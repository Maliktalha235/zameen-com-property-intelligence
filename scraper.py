import re
import requests
from bs4 import BeautifulSoup
from database import get_connection, create_table

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

Base_url = "https://www.zameen.com"

cities = {
    "Lahore": "Lahore-1",
    "Karachi": "Karachi-2",
    "Islamabad": "Islamabad-3",
    "Rawalpindi": "Rawalpindi-41"
}

property_types = {
    "Houses": "Homes",
    "Flats": "Flats_Apartments",
    "Plots": "Plots"
}

def scrape_page(url, city, property_type):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed: {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.find_all("article")

    # Extract all phones from page at once
    phones = re.findall(r'"mobileNumbers":\["([^"]+)"', response.text)

    properties = []

    for i, listing in enumerate(listings):
        try:
            price = listing.find(attrs={"aria-label": "Price"})
            location = listing.find(attrs={"aria-label": "Location"})
            area = listing.find(attrs={"aria-label": "Area"})
            title = listing.find(attrs={"aria-label": "Title"})
            beds = listing.find(attrs={"aria-label": "Beds"})
            baths = listing.find(attrs={"aria-label": "Baths"})
            listing_date = listing.find(attrs={"aria-label": "Listing creation date"})
            link = listing.find("a", href=lambda x: x and "/Property/" in x)

            price_text = price.get_text(strip=True) if price else None
            location_text = location.get_text(strip=True) if location else None
            area_text = area.get_text(strip=True) if area else None
            title_text = title.get_text(strip=True) if title else None
            beds_text = beds.get_text(strip=True) if beds else None
            baths_text = baths.get_text(strip=True) if baths else None
            date_text = listing_date.get_text(strip=True) if listing_date else None
            page_url = Base_url + link["href"] if link else None
            phone = phones[i] if i < len(phones) else None

            if not price_text or not location_text or not title_text:
                continue

            properties.append({
                "title": title_text,
                "price": price_text,
                "location": location_text,
                "area": area_text,
                "beds": beds_text,
                "baths": baths_text,
                "city": city,
                "property_type": property_type,
                "listing_date": date_text,
                "page_url": page_url,
                "phone": phone
            })

        except Exception as e:
            continue

    return properties

def save_properties(properties):
    if not properties:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    saved = 0

    for prop in properties:
        cursor.execute("SELECT id FROM properties WHERE page_url = %s", (prop["page_url"],))
        exists = cursor.fetchone()

        if not exists:
            query = """INSERT INTO properties
            (title, price, location, area, beds, baths, city, property_type, listing_date, page_url, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                prop["title"], prop["price"], prop["location"],
                prop["area"], prop["beds"], prop["baths"],
                prop["city"], prop["property_type"],
                prop["listing_date"], prop["page_url"], prop["phone"]
            ))
            saved += 1

    conn.commit()
    cursor.close()
    conn.close()
    return saved

def scrape_city(city, property_type, pages=3):
    city_code = cities.get(city)
    type_code = property_types.get(property_type)

    if not city_code or not type_code:
        print(f"Invalid city or type: {city}, {property_type}")
        return

    total_saved = 0
    for page in range(1, pages + 1):
        url = f"{Base_url}/{type_code}/{city_code}-{page}.html"
        print(f"Scraping: {city} {property_type} Page {page}")
        properties = scrape_page(url, city, property_type)
        saved = save_properties(properties)
        total_saved += saved
        print(f"  Found: {len(properties)} | Saved: {saved}")

    print(f"Total saved for {city} {property_type}: {total_saved}")

def run_scraper():
    create_table()
    print("=" * 50)
    print("ZAMEEN.COM SCRAPER STARTING")
    print("=" * 50)

    scrape_city("Lahore", "Houses", pages=3)
    scrape_city("Karachi", "Houses", pages=3)
    scrape_city("Islamabad", "Flats", pages=3)
    scrape_city("Lahore", "Flats", pages=3)
    scrape_city("Islamabad", "Houses", pages=3)

    print("\nScraping complete!")

run_scraper()



















































