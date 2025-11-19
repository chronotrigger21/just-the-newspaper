import os
import json
import feedparser
import trafilatura
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Check for API Key
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment variables.")
    print("Please set the OPENAI_API_KEY secret in your GitHub Repository Settings.")
    # We exit with code 1 to fail the build so the user knows something is wrong
    exit(1)

import requests

# ... (imports)

# Configuration
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://moxie.foxnews.com/google-publisher/latest.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.npr.org/1001/rss.xml" 
]
OUTPUT_FILE = "src/data/daily_news.json"
MAX_STORIES = 7

def fetch_news():
    """Fetches top stories from RSS feeds."""
    print("Fetching news...")
    stories = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for feed_url in RSS_FEEDS:
        print(f"Parsing feed: {feed_url}")
        try:
            response = requests.get(feed_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"  - Failed to fetch feed (Status: {response.status_code})")
                continue
                
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                print("  - No entries found in feed.")
                continue
                
            print(f"  - Found {len(feed.entries)} entries.")
            
            for entry in feed.entries[:3]: # Get top 3 from each
                stories.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": feed.feed.title if 'title' in feed.feed else "Unknown",
                    "published": entry.published if 'published' in entry else datetime.now().isoformat()
                })
                if len(stories) >= MAX_STORIES * 2: 
                    break
        except Exception as e:
            print(f"  - Error fetching feed: {e}")
            
        if len(stories) >= MAX_STORIES * 2:
            break
            
    print(f"Fetched {len(stories)} raw stories.")
    return stories[:MAX_STORIES]

def extract_content(url):
    """Extracts main text from a URL using trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            return result if result else ""
    except Exception as e:
        print(f"Error extracting {url}: {e}")
    return ""

def summarize_article(text):
    """Summarizes text using OpenAI."""
    if not text:
        return None
        
    client = OpenAI() # Uses OPENAI_API_KEY env var
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a neutral news editor. Summarize the following article into a single, factual paragraph of 3-4 sentences. Maintain a serious, journalistic tone. Do not use bullet points."},
                {"role": "user", "content": text}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None

def save_news(news_data):
    """Saves processed news to JSON."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(news_data)} stories to {OUTPUT_FILE}")

def main():
    print(f"Starting daily fetch at {datetime.now()}")
    
    raw_stories = fetch_news()
    if not raw_stories:
        print("CRITICAL: No raw stories fetched from RSS feeds.")
        exit(1)

    processed_stories = []
    
    for story in raw_stories:
        print(f"Processing: {story['title']}")
        text = extract_content(story['link'])
        if text:
            print(f"  - Extracted {len(text)} chars. Summarizing...")
            summary = summarize_article(text)
            if summary:
                print("  - Summary generated successfully.")
                processed_stories.append({
                    "title": story['title'],
                    "summary": summary,
                    "source": story['source'],
                    "url": story['link'],
                    "date": datetime.now().strftime("%A, %B %d, %Y")
                })
            else:
                print("  - Failed to generate summary.")
        else:
            print("  - Failed to extract content.")
        
        if len(processed_stories) >= MAX_STORIES:
            break
            
    if not processed_stories:
        print("CRITICAL: No stories were processed successfully.")
        exit(1)

    save_news(processed_stories)

if __name__ == "__main__":
    main()
