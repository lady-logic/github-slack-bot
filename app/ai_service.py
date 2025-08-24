import requests
from config import Config
from typing import List, Dict, Optional
import json

class AIService:
    def __init__(self):
        # Hugging Face kostenlose Inference API
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = "microsoft/DialoGPT-medium"  # Guter Chat-Model
        self.headers = {
            "Authorization": f"Bearer {Config.HUGGING_FACE_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, user_message: str, context: str = "") -> str:
        """Generiert KI-Antwort basierend auf User-Message und Kontext"""
        
        # Prompt für GitHub-Assistant erstellen
        prompt = self._build_prompt(user_message, context)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # DialoGPT gibt Array zurück
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Nur die neue Antwort extrahieren (nach dem Prompt)
                    answer = generated_text[len(prompt):].strip()
                    return answer if answer else "🤔 Hmm, lass mich anders antworten..."
                
            print(f"❌ AI API Error: {response.status_code} - {response.text}")
            return self._fallback_response(user_message)
            
        except requests.RequestException as e:
            print(f"❌ AI Request failed: {e}")
            return self._fallback_response(user_message)
    
    def _build_prompt(self, user_message: str, context: str) -> str:
        """Baut intelligenten Prompt für GitHub-Assistant"""
        
        base_prompt = """Du bist ein hilfreicher GitHub-Assistant. Du hilfst Entwicklern mit ihren Repositories.

"""
        
        if context:
            base_prompt += f"Kontext: {context}\n\n"
        
        base_prompt += f"Benutzer: {user_message}\nAssistent:"
        
        return base_prompt
    
    def _fallback_response(self, user_message: str) -> str:
        """Fallback wenn AI nicht verfügbar"""
        fallbacks = {
            "repository": "📁 Ich kann dir mit deinen Repositories helfen! Verwende `/repos` für eine Liste.",
            "code": "💻 Für Code-Suche verwende `/search <suchbegriff>`",
            "help": "🤖 Ich bin dein GitHub-Assistant! Frage mich nach deinen Repos oder suche Code.",
        }
        
        user_lower = user_message.lower()
        for keyword, response in fallbacks.items():
            if keyword in user_lower:
                return response
        
        return "🤖 Entschuldigung, ich bin gerade nicht ganz da. Probiere `/repos` oder `/code <begriff>`!"

    def analyze_repositories(self, repos: List[Dict]) -> str:
        """Analysiert Repository-Liste und gibt Insights"""
        if not repos:
            return "❌ Keine Repositories gefunden."
        
        # Einfache Statistiken
        total = len(repos)
        languages = {}
        recent_repos = []
        
        for repo in repos:
            lang = repo.get('language', 'Unknown')
            if lang != 'Unknown':
                languages[lang] = languages.get(lang, 0) + 1
            
            # Letzte 3 Repos (vereinfacht)
            if len(recent_repos) < 3:
                recent_repos.append(repo['name'])
        
        # Top-Sprache
        top_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unbekannt"
        
        analysis = f"""📊 **Repository-Analyse:**
        
🔢 **Total:** {total} Repositories
🏆 **Haupt-Sprache:** {top_language}
📈 **Aktuelle Projekte:** {', '.join(recent_repos)}

💡 **Insight:** Du arbeitest hauptsächlich mit {top_language}. 
{self._get_language_tip(top_language)}"""
        
        return analysis
    
    def _get_language_tip(self, language: str) -> str:
        """Gibt Tipps basierend auf Haupt-Programmiersprache"""
        tips = {
            "Python": "Perfekt für AI, Data Science und Automation! 🐍",
            "JavaScript": "Super für Web-Development und Node.js! 🚀",
            "Java": "Robust für Enterprise-Anwendungen! ☕",
            "C#": "Ideal für .NET und Windows-Development! 💎",
            "Go": "Schnell und effizient für Backend-Services! ⚡"
        }
        return tips.get(language, "Interessante Sprache! Keep coding! 💻")

# Test-Funktion
def test_ai_service():
    ai = AIService()
    print("🧠 Testing AI Service...")
    
    # Test-Response ohne API-Call
    response = ai._fallback_response("Hallo")
    print(f"✅ Fallback response: {response}")
    
    return True

if __name__ == "__main__":
    test_ai_service()