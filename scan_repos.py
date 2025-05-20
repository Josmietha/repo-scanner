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
# Step 6: Save to Excel
wb = Workbook()
ws = wb.active
ws.title = "Filtered GitHub Repos"

# Define all possible property keys you expect
custom_keys = ["export", "status"]

# Add headers
ws.append(["Name", "URL"] + [key.capitalize() for key in custom_keys])

# Write repo data
for repo in filtered_repos:
    # Clone the repo again (or cache metadata during filtering phase)
    clone_url = repo['clone_url']
    temp_dir = tempfile.mkdtemp()
    metadata = {}

    try:
        subprocess.run(["git", "clone", "--depth=1", clone_url, temp_dir], check=True, stdout=subprocess.DEVNULL)
        custom_path = os.path.join(temp_dir, ".github", "custom.json")

        if os.path.exists(custom_path):
            with open(custom_path, "r") as f:
                metadata = json.load(f)

    except Exception as e:
        print(f"⚠️ Could not re-read metadata for {repo['name']} — {e}")

    finally:
        shutil.rmtree(temp_dir)

    # Build row
    row = [repo['name'], repo['html_url']] + [metadata.get(key, "") for key in custom_keys]
    ws.append(row)

filename = f"{username}_filtered_repos.xlsx"
wb.save(filename)
print(f"📁 Excel file saved as: {filename}")
'''
from github import Github
from openpyxl import Workbook

REQUIRED_EXPORT = "true"
REQUIRED_STATUS = "changes required"

def get_org_repos_with_custom_properties(org_name, github_token):
    g = Github(github_token)
    org = g.get_organization(org_name)
    repos = org.get_repos()

    repo_data = []
    for repo in repos:
        repo_info = {
            "name": repo.name,
            "full_name": repo.full_name,
            "custom_properties": {}
        }
        try:
            # PyGithub currently does not support .get_custom_properties() natively
            # So this is a placeholder to mimic custom properties if you have an extension or wrapper.
            # Replace this block with actual API call or method if using custom implementation.
            props = repo.get_properties()  # You'll need to have this defined or monkey-patched
            for prop in props:
                repo_info["custom_properties"][prop.name] = prop.value
        except Exception as e:
            repo_info["custom_properties"]["error"] = str(e)
        repo_data.append(repo_info)
    return repo_data


def filter_repositories_by_properties(repo_data, export_value, status_value):
    filtered = []
    for repo in repo_data:
        props = repo["custom_properties"]
        if props.get("export", "").lower() == export_value and props.get("status", "").lower() == status_value:
            filtered.append(repo)
    return filtered


def export_filtered_to_excel(filtered_repos, org_name):
    wb = Workbook()
    ws = wb.active
    ws.title = "Filtered Repositories"
    ws.append(["Name", "Full Name", "Export", "Status"])

    for repo in filtered_repos:
        props = repo["custom_properties"]
        ws.append([
            repo["name"],
            repo["full_name"],
            props.get("export", ""),
            props.get("status", "")
        ])

    filename = f"{org_name}_filtered_repos.xlsx"
    wb.save(filename)
    print(f"Excel file saved as: {filename}")


if __name__ == '__main__':
    org_name = "j-chaganti"  # Replace with your GitHub org or username
    github_token = "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"  # Replace with your GitHub token

    repos_with_properties = get_org_repos_with_custom_properties(org_name, github_token)

    print(f"\nFetched {len(repos_with_properties)} repositories. Filtering based on properties...\n")

    filtered_repos = filter_repositories_by_properties(repos_with_properties, REQUIRED_EXPORT, REQUIRED_STATUS)

    for repo in filtered_repos:
        print(f"✅ Repo: {repo['name']}")
        for key, value in repo["custom_properties"].items():
            print(f"   - {key}: {value}")
        print("-" * 30)

    print(f"\nExporting {len(filtered_repos)} filtered repositories to Excel...\n")
    export_filtered_to_excel(filtered_repos, org_name)


