# Just the Newspaper

A minimalist, single-page web application that updates once daily with summarized headlines from primary sources. Designed to look like a traditional black-and-white newspaper.

## Project Overview

- **Frontend**: Astro (Static Site Generator)
- **Backend**: Python (Data fetching & processing)
- **Automation**: GitHub Actions (Daily cron job)
- **Hosting**: GitHub Pages

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- OpenAI API Key

### Local Development

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd just-the-newspaper
    ```

2.  **Install Dependencies**
    ```bash
    # Python
    pip install -r requirements.txt

    # Node.js
    npm install
    ```

3.  **Environment Variables**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-...
    ```

4.  **Run the Backend (Fetch News)**
    ```bash
    python daily_fetch.py
    ```
    This will generate `src/data/daily_news.json`.

5.  **Run the Frontend (Dev Server)**
    ```bash
    npm run dev
    ```
    Visit `http://localhost:4321` to see the site.

## Deployment

The project is configured to deploy automatically to GitHub Pages using GitHub Actions.

1.  Push the code to GitHub.
2.  Go to **Settings > Secrets and variables > Actions**.
3.  Add a new repository secret named `OPENAI_API_KEY` with your OpenAI API key.
4.  The workflow `Daily Newspaper Build` will run automatically every day at 6:00 AM EST, or you can trigger it manually from the **Actions** tab.

## Customization

- **News Sources**: Edit `RSS_FEEDS` in `daily_fetch.py`.
- **Styling**: Edit `src/styles/global.css` or `src/pages/index.astro`.
