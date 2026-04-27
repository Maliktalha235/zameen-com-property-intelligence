import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.zameen.com/Homes/Lahore-1-1.html"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Find all property listings
listings = soup.find_all("article")
print(f"Total listings found: {len(listings)}")
print("\n--- First Property ---")

if listings:
    first = listings[0]
    
    # Price
    price = first.find(attrs={"aria-label": "Price"})
    print("Price:", price.get_text(strip=True) if price else "Not found")
    
    # Location
    location = first.find(attrs={"aria-label": "Location"})
    print("Location:", location.get_text(strip=True) if location else "Not found")
    
    # Area
    area = first.find(attrs={"aria-label": "Area"})
    print("Area:", area.get_text(strip=True) if area else "Not found")
    
    # Title/heading
    title = first.find("h2")
    print("Title:", title.get_text(strip=True) if title else "Not found")
    
    # Property URL
    link = first.find("a", href=True)
    print("URL:", link["href"] if link else "Not found")
    
    # WhatsApp button - extract phone number
    whatsapp = first.find("a", href=lambda x: x and "whatsapp" in x.lower())
    if whatsapp:
        href = whatsapp.get("href", "")
        # Phone number is after "phone=" in the URL
        if "phone=" in href:
            phone = href.split("phone=")[1].split("&")[0]
            print("Phone:", phone)
        else:
            print("Phone: Not in href")
    else:
        print("WhatsApp: Not found")
    
    # Print all aria-labels available in first listing
    print("\n--- All aria-labels in first listing ---")
    all_aria = first.find_all(attrs={"aria-label": True})
    for tag in all_aria:
        print(f"aria-label='{tag['aria-label']}': {tag.get_text(strip=True)[:50]}")