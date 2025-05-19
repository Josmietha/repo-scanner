'''import os
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
        return True
    except Exception as e:
        print(f"⚠Error reading custom.json from {repo['name']}: {e}")
        return False

print("Fetching repositories...")
page = 1
all_repos = []


while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}&visibility=all"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        print("Response:", response.text)
        break

    repos = response.json()

    if not repos:
        break

    all_repos.extend(repos)
    page += 1

print(f"Total repositories fetched: {len(all_repos)}")
filtered_repos = [repo for repo in all_repos if should_include_repo(repo)]
print(f"✅ {len(filtered_repos)} repos matched criteria")

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

print(f"Excel file saved as: {filename}")
'''
import os
import requests
import json
import tempfile
import subprocess
from openpyxl import Workbook
import shutil

# 🔍 Filter Conditions
REQUIRED_EXPORT = True
REQUIRED_STATUS = "changes required"

# Step 1: Environment Variables
username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')

if not username or not token:
    raise Exception("Missing GITHUB_USERNAME or GITHUB_TOKEN")

# Step 2: API Setup
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

# Step 3: Define Filtering Logic
def should_include_repo(repo):
    clone_url = repo['clone_url']
    temp_dir = tempfile.mkdtemp()

    try:
        # Shallow clone for speed
        subprocess.run(["git", "clone", "--depth=1", clone_url, temp_dir], check=True, stdout=subprocess.DEVNULL)

        # Look for custom.json
        custom_path = os.path.join(temp_dir, ".github", "custom.json")
        if not os.path.exists(custom_path):
            return False
        
        with open(custom_path, "r") as f:
            metadata = json.load(f)

        # Apply filters
        if metadata.get("export") != REQUIRED_EXPORT:
            return False
        if metadata.get("status", "").lower() != REQUIRED_STATUS.lower():
            return False

        return True

    except Exception as e:
        print(f"⚠️ Skipping {repo['name']}: error while reading metadata – {e}")
        return False

    finally:
        shutil.rmtree(temp_dir)  # Clean up after clone

# Step 4: Fetch All Repos
print("📡 Fetching repositories...")
page = 1
all_repos = []
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

print(f"🧮 Total repositories fetched: {len(all_repos)}")

# Step 5: Apply Filtering
print("🧹 Filtering based on custom.json properties...")
filtered_repos = [repo for repo in all_repos if should_include_repo(repo)]
print(f"✅ {len(filtered_repos)} repos matched (export=true AND status='changes required')")

# Step 6: Save to Excel
wb = Workbook()
ws = wb.active
ws.title = "Filtered GitHub Repos"
ws.append(["Name", "URL"])

for repo in filtered_repos:
    ws.append([repo['name'], repo['html_url']])

filename = f"{username}_filtered_repos.xlsx"
wb.save(filename)
print(f"📁 Excel file saved as: {filename}")
