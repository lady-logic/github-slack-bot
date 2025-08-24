import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN", "")  
    
    @classmethod
    def validate(cls):
        required = ["GITHUB_TOKEN", "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing environment variables: {missing}")
        
        # Warnung für HF Token
        if not cls.HUGGING_FACE_TOKEN:
            print("⚠️  HUGGING_FACE_TOKEN nicht gesetzt - AI nutzt Fallback-Responses")

# Test beim Import
Config.validate()
print("✅ Configuration loaded successfully!")