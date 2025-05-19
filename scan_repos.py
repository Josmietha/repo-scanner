import os
import requests
import json
import tempfile
import subprocess
from openpyxl import Workbook
from getpass import getpass
FILTER_EXPORT_ONLY = True

#Step 1: User Input
username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')

if not username or not token:
    raise Exception("Missing required environment variables GITHUB_USERNAME or GITHUB_TOKEN")

#Step 2: Prepare API call
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}
def should_include_repo(repo):
    clone_url = repo['clone_url']
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", "--depth=1", clone_url, temp_dir], check=True, stdout=subprocess.DEVNULL)
        custom_path = os.path.join(temp_dir, ".github", "custom.json")
        if not os.path.exists(custom_path):
            return False
        with open(custom_path, "r") as f:
            metadata = json.load(f)
        if FILTER_EXPORT_ONLY and not metadata.get("export", False):
            return False
        if metadata.get("category") != FILTER_CATEGORY:
            return False
        return True
    except Exception as e:
        print(f"⚠Error reading custom.json from {repo['name']}: {e}")
        return False

print("Fetching repositories...")
page = 1
all_repos = []

print("Fetching repositories...")

while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}&visibility=all"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"🚨 API Error: {response.status_code}")
        print("Response:", response.text)
        break

    repos = response.json()

    if not repos:
        break

    all_repos.extend(repos)
    page += 1

print(f"Total repositories fetched: {len(all_repos)}")

#Step 3: Save to Excel
wb = Workbook()
ws = wb.active
ws.title = "GitHub Repos"

# Headers
ws.append([
    "Name", "URL"
])

# Repo data
for repo in all_repos:
    ws.append([
        repo.get('name', ''),
        repo.get('html_url', ''),
    ])

# File saving
filename = f"{username}_github_repos.xlsx"
wb.save(filename)

print(f"📁 Excel file saved as: {filename}")
