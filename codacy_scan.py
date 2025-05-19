import os
import requests
from openpyxl import Workbook

CODACY_TOKEN = os.getenv("CODACY_TOKEN")
if not CODACY_TOKEN:
    raise Exception("🚨 Missing required environment variable: CODACY_TOKEN")

HEADERS = {
    "api-token": CODACY_TOKEN,
    "Accept": "application/json"
}

def get_organizations():
    url = "https://api.codacy.com/organizations"
    response = requests.get(url, headers=HEADERS)
    print(f"🔍 Fetching organizations: {response.status_code}")
    response.raise_for_status()
    return response.json().get("data", [])

def get_repos_for_org(org_id):
    url = f"https://api.codacy.com/2.0/organizations/{org_id}/repositories"
    response = requests.get(url, headers=HEADERS)
    print(f"📦 Fetching repos for Org {org_id}: {response.status_code}")
    response.raise_for_status()
    return response.json().get("data", [])

def export_to_excel(repos):
    wb = Workbook()
    ws = wb.active
    ws.title = "Codacy Repos"

    ws.append(["Repository Name", "Language", "Provider", "Enabled", "URL"])

    for repo in repos:
        ws.append([
            repo.get("name", ""),
            repo.get("language", ""),
            repo.get("provider", ""),
            str(repo.get("enabled", False)),
            repo.get("url", "")
        ])

    filename = "codacy_repos.xlsx"
    wb.save(filename)
    print(f"✅ Excel saved: {filename}")

def main():
    all_repos = []
    orgs = get_organizations()

    if not orgs:
        print("❌ No organizations found for your Codacy token.")
        return

    for org in orgs:
        org_id = org.get("id")
        if org_id:
            repos = get_repos_for_org(org_id)
            all_repos.extend(repos)

    if not all_repos:
        print("⚠️ No repositories found across your organizations.")
    else:
        export_to_excel(all_repos)

if __name__ == "__main__":
    main()
