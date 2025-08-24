import requests
from config import Config
from typing import List, Dict, Optional

class GitHubService:
    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.username = Config.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repositories(self) -> List[Dict]:
        """Holt alle öffentlichen Repos des Users"""
        url = f"{self.base_url}/users/{self.username}/repos"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            repos = response.json()
            
            print(f"🔍 DEBUG: Found {len(repos)} repositories")
            
            formatted_repos = []
            for repo in repos:
                full_name = repo["full_name"]  
                print(f"🔍 DEBUG: Repo full_name: {full_name}")
                
                formatted_repos.append({
                    "name": repo["name"],                    
                    "full_name": full_name,                 
                    "description": repo.get("description", "No description"),
                    "language": repo.get("language", "Unknown"),
                    "updated_at": repo["updated_at"],
                    "html_url": repo["html_url"]
                })
            
            return formatted_repos
            
        except requests.RequestException as e:
            print(f"❌ GitHub API Error: {e}")
            return []
    
    def get_repository_content(self, repo_name: str, path: str = "") -> Optional[Dict]:
        """Holt Datei-Inhalt aus einem Repository"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error getting content from {repo_name}/{path}: {e}")
            return None
    
    def search_in_repository(self, repo_full_name: str, query: str) -> List[Dict]:
        """Sucht nach Code in einem Repository"""
        url = f"{self.base_url}/search/code"
        params = {
            "q": f"{query} repo:{repo_full_name}", 
            "per_page": 5
        }
        
        print(f"🔍 DEBUG: Searching in repo: {repo_full_name}")
        print(f"🔍 DEBUG: Query: {params['q']}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=2)
            
            print(f"🔍 DEBUG: Status Code: {response.status_code}")
            print(f"🔍 DEBUG: Response: {response.text[:200]}...")  # Erste 200 Zeichen
            
            response.raise_for_status()
            results = response.json()
            
            print(f"🔍 DEBUG: Total count: {results.get('total_count', 0)}")
            print(f"🔍 DEBUG: Items found: {len(results.get('items', []))}")
            
            # Rest wie vorher...
            code_extensions = ['.py', '.js', '.java', '.cs', '.ts', '.php']
            
            filtered_items = []
            for item in results.get("items", [])[:3]:
                item_name = item["name"].lower()
                print(f"🔍 DEBUG: Checking file: {item_name}")
                if any(item_name.endswith(ext) for ext in code_extensions):
                    print(f"✅ DEBUG: File accepted: {item_name}")
                    filtered_items.append({
                        "name": item["name"],
                        "path": item["path"],
                        "html_url": item["html_url"],
                        "repository": item["repository"]["name"]
                    })
                else:
                    print(f"❌ DEBUG: File filtered out: {item_name}")
            
            print(f"🔍 DEBUG: Final results: {len(filtered_items)}")
            return filtered_items
            
        except requests.RequestException as e:
            print(f"❌ DEBUG: Request error: {e}")
            return []

# Test-Funktion
def test_github_service():
    gh = GitHubService()
    print("🔍 Testing GitHub Service...")
    
    repos = gh.get_repositories()
    print(f"✅ Found {len(repos)} repositories")
    
    if repos:
        print(f"📁 First repo: {repos[0]['name']}")
        return True
    return False

if __name__ == "__main__":
    test_github_service()