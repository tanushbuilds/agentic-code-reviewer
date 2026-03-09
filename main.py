import httpx
from openai import OpenAI
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@app.post("/webhook")
async def webhook(request: Request):
    
    body = await request.json()
    
    if "action" not in body or "pull_request" not in body:
        return {"status": "ignored"}
    
    # Only trigger when PR is opened or new commits are pushed
    if body["action"] not in ["opened", "synchronize"]:
        return {"status": "ignored"}
    
    action = body["action"]
    pr_number = body["pull_request"]["number"]
    diff_url = body["pull_request"]["diff_url"]
    repo_name = body["repository"]["full_name"]
    pr_title = body["pull_request"]["title"]
    pr_description = body["pull_request"].get("body", "No description provided")
    
    # Fetch the actual code diff
    async with httpx.AsyncClient() as client:
        response = await client.get(
            diff_url,
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            follow_redirects=True
        )
        diff = response.text
    
    # Handle empty diffs
    if not diff.strip():
        return {"status": "empty diff"}
    
    # Handle huge diffs
    if len(diff) > 10000:
        diff = diff[:10000] + "\n... diff truncated due to size ..."
    
    # Send to Gemini for review
    response = gemini_client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "system",
                "content": """You are an expert code reviewer. You review pull requests thoroughly and professionally.
You always:
- Identify security vulnerabilities
- Catch bugs and edge cases
- Suggest better patterns and practices
- Give actionable, specific feedback
- Are concise but thorough
- Format your review in clean markdown"""
            },
            {
                "role": "user",
                "content": f"""Please review this pull request:

**Title:** {pr_title}
**Description:** {pr_description}

**Diff:**
{diff}"""
            }
        ]
    )
    
    review = response.choices[0].message.content
    print(f"Review:\n{review}")
    
    await post_review_comment(repo_name, pr_number, review)
    
    return {"status": "ok"}



async def post_review_comment(repo_name: str, pr_number: int, review: str):
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"body": review}
        )
        print(f"Comment posted: {response.status_code}")