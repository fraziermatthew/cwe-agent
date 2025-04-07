import requests
import time
from dotenv import load_dotenv
import os

# Load GitHub token from .env file
load_dotenv()
PERSONAL_ACCESS_TOKEN = os.getenv('TOKEN_KEY')

headers = {
    'Authorization': f'token {PERSONAL_ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
def get_top_repositories():
    # GitHub API request to get repositories sorted by stars
    url = 'https://api.github.com/search/repositories'
    params = {
        'q': 'stars:>0',
        'sort': 'stars',
        'order': 'desc',
        'per_page': 10
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        repositories = data['items']
        for repo in repositories:
            name = repo['full_name']
            stars = repo['stargazers_count']
            print(f"{'-'*50}")
            print(f"{name}, {stars}")
            print("Bug Issue:")
            get_bug_issue(repo['full_name'])
            print(f"{'-'*50}")
    elif response.status_code == 403:
        print("Rate limit reached. Waiting for 10 minutes before retrying...")
        time.sleep(600)  # Wait for 10 minutes to avoid throttling
        get_top_repositories()  # Retry the request
    else:
        print(f"Error: Unable to fetch repositories (Status code: {response.status_code})")

def get_bug_issue(repo_full_name):
    # GitHub API request to get issues labeled as "bug"
    url = f'https://api.github.com/repos/{repo_full_name}/issues'
    params = {
        'labels': 'bug',
        'state': 'open',
        'per_page': 1
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        issues = response.json()
        if issues:
            issue_title = issues[0]['title']
            issue_body = issues[0]['body'][:200]  # Truncate the body for clear formatting
            print(f"{issue_title}\n{issue_body}...")
        else:
            print("none")
    elif response.status_code == 403:
        print("Take a break and drink coffee - 10 minutes...")
        time.sleep(600)  # Wait for 10 minutes to avoid throttling
        get_bug_issue(repo_full_name)  # Retry the request
    else:
        print(f"Error: Unable to fetch issues for {repo_full_name} (Status code: {response.status_code})")

if __name__ == "__main__":
    get_top_repositories()