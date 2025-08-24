from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from config import Config
from github_service import GitHubService
from ai_service import AIService

# Services initialisieren
slack_app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

github_service = GitHubService()
ai_service = AIService()

@slack_app.event("app_mention")
def handle_mention(event, say):
    """Intelligenter Chat mit AI"""
    user = event["user"]
    text = event["text"]
    
    print(f"📩 AI Chat from {user}: {text}")
    
    # Bot-Mention aus Text entfernen
    clean_text = text.split(">", 1)[1].strip() if ">" in text else text
    
    # GitHub-Kontext für AI bereitstellen
    repos = github_service.get_repositories()
    context = f"Der User hat {len(repos)} GitHub Repositories."
    
    if repos:
        top_repos = repos[:3]
        repo_names = [repo['name'] for repo in top_repos]
        context += f" Wichtigste Repos: {', '.join(repo_names)}"
    
    # AI-Antwort generieren
    ai_response = ai_service.generate_response(clean_text, context)
    
    say(f"🤖 {ai_response}")

@slack_app.command("/repos")
def handle_repos_command(ack, respond, command):
    """Repository-Liste mit AI-Analyse"""
    ack()
    
    print("📋 Getting repository list with AI analysis...")
    repos = github_service.get_repositories()
    
    if not repos:
        respond("❌ Keine Repositories gefunden oder API-Fehler")
        return
    
    # Standard Repository-Liste
    repo_list = []
    for repo in repos[:5]:
        name = repo.get('name', 'Unknown')
        language = repo.get('language') or 'Unknown'
        description = repo.get('description') or 'No description'
        short_desc = description[:50] + "..." if len(description) > 50 else description
        repo_list.append(f"📁 *{name}* ({language}) - {short_desc}")
    
    repo_text = "\n".join(repo_list)
    
    # AI-Analyse hinzufügen
    ai_analysis = ai_service.analyze_repositories(repos)
    
    full_response = f"🚀 **Deine GitHub Repositories:**\n\n{repo_text}\n\n{ai_analysis}"
    respond(full_response)

@slack_app.command("/code")
def handle_search_command(ack, respond, command):
    """Intelligente Code-Suche mit AI-Erklärungen"""
    ack("🔍 Suche nach Code... das kann einen Moment dauern...")  # ← SOFORT antworten!
    
    query = command["text"].strip()
    if not query:
        respond("❌ Bitte gib einen Suchbegriff an: `/code login`")
        return
    
    print(f"🔍 AI-powered search for: {query}")
    
    try:
        # Code-Suche durchführen (mit Timeout-Protection)
        repos = github_service.get_repositories()
        if not repos:
            respond("❌ Keine Repositories gefunden")
            return
            
        results = []
        
        for repo in repos[:4]:
            try:
                repo_identifier = repo.get("full_name", repo["name"])
                print(f"🔍 DEBUG: Using repo identifier: {repo_identifier}")
                
                search_results = github_service.search_in_repository(repo_identifier, query)
                results.extend(search_results)
            except Exception as e:
                print(f"⚠️ Fehler bei {repo.get('full_name', repo['name'])}: {e}")
                continue
        
        if not results:
            respond(f"🤷‍♂️ Keine Code-Ergebnisse für '{query}' gefunden\n\n💡 Versuche andere Begriffe wie: `function`, `class`, `import`")
            return
        
        # Ergebnisse formatieren (max 3 für Speed)
        result_text = f"🔍 **Suchergebnisse für '{query}':**\n\n"
        for result in results[:3]:  # Nur 3 statt 5
            result_text += f"📄 `{result['name']}` in **{result['repository']}**\n"
            result_text += f"   📂 {result['path']}\n\n"
        
        # AI-Response vereinfachen (kein API-Call für Speed)
        simple_insight = get_simple_code_insight(query)
        
        full_response = f"{result_text}💡 **Insight:**\n{simple_insight}"
        respond(full_response)
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        respond(f"❌ Fehler bei der Suche nach '{query}'. Probiere es nochmal!")

def get_simple_code_insight(query: str) -> str:
    """Schnelle lokale Insights ohne AI-API"""
    insights = {
        "import": "📦 `import` wird verwendet um Module und Bibliotheken zu laden",
        "function": "🔧 `function` definiert wiederverwendbare Code-Blöcke", 
        "class": "🏗️ `class` erstellt Objekt-orientierte Strukturen",
        "login": "🔐 `login` implementiert User-Authentifizierung",
        "api": "🌐 `api` stellt Schnittstellen für Datenübertragung bereit",
        "test": "🧪 `test` Code überprüft ob alles korrekt funktioniert",
        "config": "⚙️ `config` verwaltet Einstellungen und Parameter"
    }
    
    query_lower = query.lower()
    for keyword, insight in insights.items():
        if keyword in query_lower:
            return insight
    
    return f"🤖 '{query}' ist ein wichtiger Begriff in der Programmierung!"

@slack_app.command("/analyze")
def handle_analyze_command(ack, respond, command):
    """Neue AI-Analyse für spezifische Fragen"""
    ack()
    
    question = command["text"].strip()
    if not question:
        respond("❌ Frage mich etwas! `/analyze Welche Sprache sollte ich als nächstes lernen?`")
        return
    
    print(f"🧠 AI Analysis: {question}")
    
    # GitHub-Kontext sammeln
    repos = github_service.get_repositories()
    context = ai_service.analyze_repositories(repos)
    
    # AI-Antwort basierend auf Portfolio
    ai_response = ai_service.generate_response(question, context)
    
    respond(f"🧠 **AI-Analyse:**\n\n🤖 {ai_response}")

# Test-Funktion
def test_slack_app():
    print("✅ Slack app with AI configured successfully!")
    print("📋 Available commands:")
    print("   - /repos - Repository-Liste mit AI-Analyse")
    print("   - /code <query> - Intelligente Code-Suche")
    print("   - /analyze <frage> - AI-basierte Analyse")
    print("   - @bot <nachricht> - Freier AI-Chat")

if __name__ == "__main__":
    test_slack_app()