import os
import requests
from openpyxl import Workbook
from getpass import getpass

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
