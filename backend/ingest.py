import os
import requests
import logging
from sentence_transformers import SentenceTransformer
from database import SessionLocal, DocumentChunk, init_db
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bundled_data = [
    {
        "source": "Lenny Podcast: Finding Product-Market Fit",
        "chunks": [
            "Lenny: So when we talk about product-market fit, what is the key indicator that you've found it? Guest: It's when the market is pulling the product out of your hands. You don't have to push anymore. The servers are melting down, people are complaining about bugs but still using it every day. That's the real sign.",
            "Guest: Another way to measure PMF is the Sean Ellis test. If you ask your users how they would feel if they could no longer use your product, and more than 40% say they would be 'very disappointed', you have product-market fit. It's a great leading indicator."
        ]
    },
    {
        "source": "Lenny Podcast: Growth Metrics & North Star",
        "chunks": [
            "Lenny: Let's dive into growth metrics. A lot of people track DAU and MAU, but what should they actually be tracking? Guest: DAU/MAU ratio is fine for social apps, but for SaaS, it's about the North Star metric. What metric truly captures the value delivered to the user? For Airbnb, it's nights booked.",
            "Guest: Activation is the most important step in the funnel. If a user signs up but doesn't experience the 'aha' moment within the first 7 days, they're gone forever. You need to relentlessly optimize that first week experience."
        ]
    },
    {
        "source": "Lenny Podcast: Retention and Habit Formation",
        "chunks": [
            "Lenny: How do the best consumer apps build habits? Guest: It comes down to the Hook Model. Trigger, Action, Variable Reward, Investment. The best apps like Instagram or TikTok have mastered the variable reward. You don't know what you're going to get when you open the app.",
            "Guest: Long-term retention flattens out only if you provide compounding value. The more the user puts into the product, the better it gets. Think about Spotify playlists or Evernote notes. The switching costs become too high."
        ]
    },
    {
        "source": "Lenny Podcast: Pricing Strategy",
        "chunks": [
            "Lenny: Pricing is notoriously hard. Should startups do freemium or free trial? Guest: Freemium is a marketing expense, not a revenue model. Only do freemium if your product has inherent virality or network effects. Otherwise, a 14-day reverse trial is usually better for B2B SaaS.",
            "Guest: Also, most startups undercharge. The easiest way to increase revenue is simply to raise prices. If you're delivering 10x value compared to what you charge, you have room to increase prices. Value-based pricing is the holy grail."
        ]
    },
    {
        "source": "Lenny Podcast: Building High-Performing Teams",
        "chunks": [
            "Lenny: How do you structure teams for speed? Guest: Amazon's two-pizza rule is famous for a reason. If a team can't be fed by two pizzas, it's too big. Keep teams small, autonomous, and cross-functional. They need engineering, design, and PM all together.",
            "Guest: When hiring PMs, I look for extreme ownership and raw intellect. I don't care if they know the specific industry. A great PM can learn the industry in a month, but you can't teach someone to be a proactive problem solver. They either have that drive or they don't.",
            "Guest: Lastly, make sure you celebrate wins. It sounds basic, but in high-growth environments, people burn out because they hit a goal and immediately look at the next one. Take a minute to recognize the achievement."
        ]
    }
]

def fetch_from_github():
    url = "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/transcripts.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Failed to fetch from GitHub: {e}. Falling back to bundled data.")
        return None

def ingest_data():
    init_db()
    db = SessionLocal()
    
    try:
        existing_count = db.query(DocumentChunk).count()
        if existing_count > 0:
            logger.info(f"Database already contains {existing_count} chunks. Skipping ingestion.")
            return

        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        data = fetch_from_github()
        if not data:
            data = bundled_data
            
        chunks_added = 0
        for item in data:
            source = item.get("source", "Unknown Source")
            chunks = item.get("chunks", [])
            for chunk_text in chunks:
                embedding = model.encode(chunk_text).tolist()
                chunk = DocumentChunk(
                    content=chunk_text,
                    embedding=embedding,
                    source=source
                )
                db.add(chunk)
                chunks_added += 1
                
        db.commit()
        logger.info(f"Successfully ingested {chunks_added} chunks.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()
