from groq import Groq 
from database import get_connection

client=Groq(api_key="your groq key")

def get_sentiment(title,price, location):
    prompt= f"Property:{title} | Price: {price} | Location: {location}. Is this a Good Deal, Fair Deal, or Expensive? Reply with only one: GoodDeal, FairDeal, or Expensive."

    response= client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system", "content":"You are Pakistan real state analyst. Analyze property listings briefly."},
            {"role":"user","content":prompt}]
    )
    label=response.choices[0].message.content.strip()
    if "GoodDeal" in label:
        return "GoodDeal"
    elif "Expensive" in label:
        return "Expensive"
    else:
        return "FairDeal"
    
def analyze_properties():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("Select id, title, price, location from properties where sentiment_label is null limit 200")
    rows=cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        print("All properties already analyzed!")
        return
    
    print(f"Analyzing {len(rows)} properties....")

    conn=get_connection()
    cursor=conn.cursor()

    for row in rows:
        id,title,price,location=row
        label=get_sentiment(title,price,location)
        update_query="update properties set sentiment_label=%s where id = %s"
        cursor.execute(update_query,(label,id))
        print(f"{label} ---> {price} | {location}")

    conn.commit()
    cursor.close()
    conn.close()
    print("analysis complete...")

analyze_properties()