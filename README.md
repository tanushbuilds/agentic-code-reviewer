# Agentic Code Reviewer

An AI-powered code reviewer that automatically reviews Pull Requests using Gemini.

## How it works

1. A PR is opened on GitHub
2. GitHub sends a webhook event to the server
3. The server fetches the code diff
4. Sends it to Gemini for review
5. Posts the review as a comment on the PR

## Setup

1. Clone the repo
2. Create a `.env` file with:
   GITHUB_TOKEN=your_github_token
   GEMINI_API_KEY=your_gemini_api_key
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn main:app --reload`
