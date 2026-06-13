import urllib.request
import json
import os
import sys

def fetch_prs():
    # Query: author is sasikumar161106, is a PR, is merged, but NOT in sasikumar161106's own repos
    url = "https://api.github.com/search/issues?q=is:pr+author:sasikumar161106+is:merged+-user:sasikumar161106&sort=updated&order=desc"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "GitHub-Profile-PR-Updater")
    
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
        
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("items", [])[:5] # Get top 5 recent PRs
    except Exception as e:
        print(f"Error fetching PRs: {e}")
        return []

def update_readme(prs):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    start_marker = "<!-- PR_SECTION_START -->"
    end_marker = "<!-- PR_SECTION_END -->"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Markers not found in README.md")
        sys.exit(1)
        
    pr_markdown = "\n"
    # To prevent duplicates with the manually added PR, we can filter out TabTwin/pull/37
    filtered_prs = [pr for pr in prs if "TabTwin/pull/37" not in pr.get("html_url", "")]
    
    for pr in filtered_prs:
        title = pr.get("title")
        url = pr.get("html_url")
        repo_url = pr.get("repository_url", "")
        repo_name = repo_url.split("/")[-2] + "/" + repo_url.split("/")[-1] if repo_url else "Repository"
        date_str = pr.get("closed_at", "")
        date = date_str.split("T")[0] if date_str else "Unknown Date"
        pr_markdown += f"- **[{repo_name}]** [{title}]({url}) - Merged on {date}\n"
        
    pr_markdown += "\n"
    
    # If no automated PRs found (other than the manual one), just keep it empty
    if not filtered_prs:
        pr_markdown = "\n"
        
    new_content = content[:start_idx + len(start_marker)] + pr_markdown + content[end_idx:]
    
    if new_content == content:
        print("No changes to README.md")
    else:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated successfully")

if __name__ == "__main__":
    prs = fetch_prs()
    update_readme(prs)
