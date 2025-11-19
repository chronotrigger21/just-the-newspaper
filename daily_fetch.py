import os
import json
import feedparser
import trafilatura
import requests
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Check for API Key
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment variables.")
    print("Please set the OPENAI_API_KEY secret in your GitHub Repository Settings.")
    exit(1)

# Configuration
# Google News RSS Search for AP and Reuters (past 24h)
RSS_FEED_URL = "https://news.google.com/rss/search?q=site:apnews.com+OR+site:reuters.com+when:1d&hl=en-US&gl=US&ceid=US:en"
OUTPUT_FILE = "src/data/daily_news.json"
MAX_STORIES = 7

def fetch_news():
    """Fetches top stories from Google News RSS (AP & Reuters)."""
    print("Fetching news from Google News (AP/Reuters)...")
    stories = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Parsing feed: {RSS_FEED_URL}")
        response = requests.get(RSS_FEED_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  - Failed to fetch feed (Status: {response.status_code})")
            return []
            
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print("  - No entries found in feed.")
            return []
            
        print(f"  - Found {len(feed.entries)} entries.")
        
        for entry in feed.entries:
            # Extract source from the entry if available, otherwise default
            source = "News"
            if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                source = entry.source.title
            elif 'apnews.com' in entry.link:
                source = "AP News"
            elif 'reuters.com' in entry.link:
                source = "Reuters"

            stories.append({
                "title": entry.title,
                "link": entry.link, # Google News redirect link
                "source": source,
                "published": entry.published if hasattr(entry, 'published') else datetime.now().isoformat()
            })
            if len(stories) >= MAX_STORIES * 2: # Fetch extra to account for extraction failures
                break
                
    except Exception as e:
        print(f"  - Error fetching feed: {e}")
            
    print(f"Fetched {len(stories)} raw stories.")
    return stories[:MAX_STORIES + 3] # Return a few extra for processing

def extract_content(url):
    """Extracts main text from a URL using trafilatura, handling Google News redirects."""
    try:
        # Use requests to follow redirects and get the final content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            # Pass the HTML content directly to trafilatura
            result = trafilatura.extract(response.text, include_comments=False, include_tables=False)
            return result if result else ""
        else:
            print(f"Failed to fetch URL {url} (Status: {response.status_code})")
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
