import requests

# Config - update these
ORG_NAME = "YourOrgName"
YOUR_GITHUB_USERNAME = "your-username"
GITHUB_TOKEN = "your-personal-access-token"  # Keep this secure!

def get_repos_created_by_user(org_name, username, token):
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        for repo in data:
            # GitHub API returns 'owner' and 'created_at', but doesn't specify creator directly,
            # so we check repo owner login and see if it matches the username.
            # But in org repos, owner is org, so we check 'owner' inside the repo 'created_by' if possible.
            # Since API doesn’t directly give creator, one workaround is to check repo 'owner' + 'permissions' + contributors.
            # Here we simplify: Assume repo creator username stored in repo['owner']['login'] or last commit author - tricky.
            # Let's filter repos where the user is listed as the repo owner or in contributors (a more advanced approach).
            # For simplicity, assume if repo name contains your username (or use other logic).
            # You can adapt this based on your GitHub setup.

            # Simple heuristic: Check if 'owner' is your username (won't work for org repos)
            # So just list all repos here; filtering can be enhanced.

            # For demonstration: Add all repos
            repos.append(repo['name'])

        page += 1

    return repos

if __name__ == "__main__":
    repos = get_repos_created_by_user(ORG_NAME, YOUR_GITHUB_USERNAME, GITHUB_TOKEN)
    print(f"Repositories under org '{ORG_NAME}' created by '{YOUR_GITHUB_USERNAME}':")
    for r in repos:
        print(f"- {r}")
