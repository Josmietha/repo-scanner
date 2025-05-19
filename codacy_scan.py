import requests
import os
from openpyxl import Workbook

CODACY_API = "https://api.codacy.com/2.0"
TOKEN = os.getenv("CODACY_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/json"
}

def get_organizations():
    resp = requests.get(f"{CODACY_API}/organizations", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("data", [])

def get_projects(org_id):
    url = f"{CODACY_API}/organizations/{org_id}/projects"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("data", [])

def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Codacy Repos"
    ws.append(["Repo Name", "Repository URL", "Project ID"])

    orgs = get_organizations()
    print(f"🧩 Found {len(orgs)} Codacy org(s)")

    for org in orgs:
        print(f"🔍 Scanning org: {org['name']}")
        projects = get_projects(org["id"])
        for proj in projects:
            ws.append([
                proj.get("name"),
                proj.get("repositoryUrl"),
                proj.get("id")
            ])

    wb.save("codacy_repos.xlsx")
    print("✅ Codacy repos exported to codacy_repos.xlsx")

if __name__ == "__main__":
    main()
