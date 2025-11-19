# Deployment Guide: Getting "Just the Newspaper" Online

Follow these steps to get your newspaper running on the web.

## Phase 0: Prepare Git (If not already done)

It seems Git might not be installed or configured on your system yet.

1.  **Check if Git is installed**: Open your terminal and type `git --version`.
    *   If it says "command not found" or similar, download and install it from [git-scm.com](https://git-scm.com/downloads).
2.  **Initialize the repository**:
    Open your terminal in the project folder (`Just the Newspaper`) and run:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```

## Phase 1: Create the Repository on GitHub

1.  Log in to your [GitHub account](https://github.com).
2.  Click the **+** icon in the top-right corner and select **New repository**.
3.  **Repository name**: Enter `just-the-newspaper` (or any name you like).
4.  **Public/Private**: Choose **Public** (easier for GitHub Pages) or **Private** (requires a Pro account for Pages sometimes, but usually free for public). **Public is recommended** for this project.
5.  **Initialize this repository with**: Leave all these unchecked (no README, no .gitignore, no License). We already have these locally.
6.  Click **Create repository**.
7.  **Copy the URL**: On the next screen, look for the section "…or push an existing repository from the command line". Copy the URL that looks like `https://github.com/YOUR_USERNAME/just-the-newspaper.git`.

## Phase 2: Connect Your Code (Terminal)

Now connect your local code to GitHub.

1.  Run the following command (replace the URL with the one you copied):
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/just-the-newspaper.git
    ```
2.  Push your code:
    ```bash
    git push -u origin master
    ```
    *(Note: If it asks for a password, you may need to use a Personal Access Token or sign in via the browser popup).*

## Phase 3: Configure Secrets (OpenAI Key)

For the daily news summary to work, GitHub needs your OpenAI API key.

1.  Go to your new repository page on GitHub.
2.  Click on **Settings** (top tab).
3.  On the left sidebar, scroll down to **Secrets and variables** and click **Actions**.
4.  Click the green button **New repository secret**.
5.  **Name**: `OPENAI_API_KEY`
6.  **Secret**: Paste your actual OpenAI API key (starts with `sk-...`).
7.  Click **Add secret**.

## Phase 4: Enable GitHub Pages

This tells GitHub where to show your website.

1.  Stay in **Settings**.
2.  On the left sidebar, click **Pages**.
3.  Under **Build and deployment** > **Source**, keep it as "Deploy from a branch".
4.  **BUT WAIT!** You don't need to do anything else here yet.
    *   Our "Daily Newspaper Build" workflow will automatically create a special branch called `gh-pages` when it runs successfully.
    *   Once the first build finishes (see Phase 5), come back here and ensure **Branch** is set to `gh-pages` / `(root)`.

## Phase 5: Run the First Build

1.  Click on the **Actions** tab (top of the page).
2.  You should see "Daily Newspaper Build" listed on the left.
3.  Click on it.
4.  Click the **Run workflow** button (right side) > **Run workflow**.
5.  Wait for it to finish (green checkmark).
    *   *Note: It might take 1-2 minutes.*
6.  Once finished, go back to **Settings > Pages** and make sure the branch is set to `gh-pages`.
7.  Your site URL will appear at the top of the Pages settings (e.g., `https://your-username.github.io/just-the-newspaper/`).

## Done!

Your paper is now online! It will automatically update every day at 6:00 AM EST.
