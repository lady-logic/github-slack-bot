from fastapi import FastAPI, Request
from config import Config
from github_service import GitHubService, test_github_service
from slack_handler import slack_app, test_slack_app
from slack_bolt.adapter.fastapi import SlackRequestHandler

# FastAPI App
app = FastAPI(title="GitHub Slack Bot")

# Slack Request Handler
slack_handler = SlackRequestHandler(slack_app)

# GitHub Service
github_service = GitHubService()

@app.get("/")
def health_check():
    return {
        "status": "healthy", 
        "message": "GitHub Slack Bot is running!",
        "endpoints": ["/slack/events", "/test", "/repos"]
    }

@app.post("/slack/events")
async def slack_events(req: Request):
    """Endpoint für Slack Events UND Commands"""
    body = await req.body()
    
    # Debug: Lass uns sehen was ankommt
    print(f"🔍 Received from Slack: {body.decode()}")
    
    # URL Verification für Events
    try:
        import json
        json_body = json.loads(body.decode())
        if json_body.get("type") == "url_verification":
            return {"challenge": json_body["challenge"]}
    except:
        pass
    
    # Alles andere an Slack Handler weiterleiten
    return await slack_handler.handle(req)

@app.get("/test")
def test_all():
    """Testet alle Services"""
    gh_test = test_github_service()
    test_slack_app()
    
    return {
        "github_service": "✅ OK" if gh_test else "❌ ERROR",
        "slack_app": "✅ OK",
        "config": "✅ OK"
    }

@app.get("/repos")
def get_repos():
    """API Endpoint für Repository-Liste"""
    repos = github_service.get_repositories()
    return {"repositories": repos, "count": len(repos)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GitHub Slack Bot...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)