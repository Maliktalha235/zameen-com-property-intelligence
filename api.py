from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from groq import Groq
from typing import List
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app=FastAPI(title="Zameen Property Intelligence API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[Message] = []

def fetch_data(query,params=None):
    conn=get_connection()
    cursor=conn.cursor()
    if params:
        cursor.execute(query,params)
    else:
        cursor.execute(query)
    data=cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/")
def home():
    return{ "message":"Zameen property Intelligence API",
           "endpoints":["/properties", "/search", "/stats", "/city", "/deals", "/chat"]}

@app.get("/properties")
def get_properties(limit: int=20):
    query="""select title,price,location,
    area,beds,baths,city,property_type,
    sentiment_label,page_url from properties
    order by scraped_at desc limit %s"""
    data=fetch_data(query,(limit,))
    return {"total:":len(data),"properties":[{ "title":r[0], "price":r[1],
        "location":r[2], "area":r[3], "beds":r[4], "baths":r[5], "city":r[6],
        "type":r[7], "deal":r[8], "page_url":r[9]}
        for r in data
     ]}

@app.get("/search")
def search(city: str=None, property_type: str=None, min_beds: str=None):
    query = "SELECT title, price, location, area, beds, city, property_type, sentiment_label, page_url FROM properties WHERE 1=1"
    params=[]
    if city:
        query += " And city=%s"
        params.append(city)
    if property_type:
        query += " and property_type=%s"
        params.append(property_type)
    if min_beds:
        query += " and beds>=%s"
        params.append(min_beds)
    query += "order by scraped_at desc limit 50"

    data=fetch_data(query,params if params else None)
    return{"results":len(data), "properties":[{
            "title":"r[0]", "price": r[1], "location": r[2],
            "area": r[3], "beds": r[4], "city": r[5],
            "type": r[6], "deal": r[7], "url": r[8]}
            for r in data
    ]}

@app.get("/stats")
def stats():
    total = fetch_data("SELECT COUNT(*) FROM properties")[0][0]
    by_city = fetch_data("SELECT city, COUNT(*) FROM properties GROUP BY city")
    by_type = fetch_data("SELECT property_type, COUNT(*) FROM properties GROUP BY property_type")
    deals = fetch_data("SELECT sentiment_label, COUNT(*) FROM properties WHERE sentiment_label IS NOT NULL GROUP BY sentiment_label")
    return {
        "total_properties": total,
        "by_city": {r[0]: r[1] for r in by_city},
        "by_type": {r[0]: r[1] for r in by_type},
        "deal_analysis": {r[0]: r[1] for r in deals}
    }

@app.get("/deals")
def good_deals(city: str = None):
    query = "SELECT title, price, location, area, beds, city, page_url FROM properties WHERE sentiment_label = 'GoodDeal'"
    params = []
    if city:
        query += " AND city = %s"
        params.append(city)
    query += " ORDER BY scraped_at DESC LIMIT 30"
    data = fetch_data(query, params if params else None)
    return {"good_deals": len(data), "properties": [
        {"title": r[0], "price": r[1], "location": r[2],
         "area": r[3], "beds": r[4], "city": r[5], "url": r[6]}
        for r in data
    ]}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        question_lower = request.question.lower()

        if "lahore" in question_lower:
            data = fetch_data("""SELECT title, price, location, area, beds, city,
                property_type, sentiment_label, phone, page_url
                FROM properties WHERE city='Lahore'
                ORDER BY scraped_at DESC LIMIT 20""")
        elif "karachi" in question_lower:
            data = fetch_data("""SELECT title, price, location, area, beds, city,
                property_type, sentiment_label, phone, page_url
                FROM properties WHERE city='Karachi'
                ORDER BY scraped_at DESC LIMIT 20""")
        elif "islamabad" in question_lower:
            data = fetch_data("""SELECT title, price, location, area, beds, city,
                property_type, sentiment_label, phone, page_url
                FROM properties WHERE city='Islamabad'
                ORDER BY scraped_at DESC LIMIT 20""")
        else:
            data = fetch_data("""SELECT title, price, location, area, beds, city,
                property_type, sentiment_label, phone, page_url
                FROM properties
                ORDER BY scraped_at DESC LIMIT 20""")

        context = ""
        for r in data:
            context += f"{r[2]}|{r[1]}|{r[3]}|{r[4]}beds|{r[7]}|Ph:{r[8]}\n"

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        messages = [
            {"role": "system", "content": f"""You are a real estate assistant for Zameen Property Intelligence system.

        STRICT RULES:
        - ONLY use properties from this data — never invent or guess properties
        - NEVER suggest other websites like OLX, Property.com or any external site
        - NEVER add fake phone numbers, emails or websites
        - If property not found in data, say "I don't have that in my current listings"
        - Always show exact price from data — never estimate or approximate
        - Always include phone number from data when recommending

        PROPERTY DATA:
        {context}"""}
                ]

        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": request.question})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

















# @app.get("/chat")
# def chat(question: str):
#     from groq import Groq
#     data = fetch_data("SELECT title, price, location, area, beds, city, property_type, sentiment_label FROM properties ORDER BY scraped_at DESC LIMIT 80")
#     context = ""
#     for r in data:
#         context += f"- {r[2]} | {r[1]} | {r[3]} | {r[4]} beds | {r[5]} | {r[6]} | Deal: {r[7]}\n"
#     client = Groq(api_key="key")
#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {"role": "system", "content": f"You are a Pakistan real estate expert. Answer based on this property data:\n{context}"},
#             {"role": "user", "content": question}
#         ]
#     )
#     return {"answer": response.choices[0].message.content}