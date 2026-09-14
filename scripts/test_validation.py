"""
Simulates the GitHub Actions validate.yml workflow locally.
Verifies all 6 validation criteria.
"""
import os
import sys
import yaml
import re

import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def test_validation():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("\n[VALIDATION] Running local simulation of .github/workflows/validate.yml ...\n")
    errors = []

    # 1. Required files exist
    required_files = [
        "README.md",
        "submission.yaml",
        "docs/problem-statement.md",
        "docs/solution-overview.md",
        "docs/architecture.md",
        "docs/setup-guide.md",
        "demo/demo-video-link.txt"
    ]
    for rf in required_files:
        path = os.path.join(root, rf)
        if not os.path.isfile(path):
            errors.append(f"❌ Missing required file: {rf}")
        else:
            print(f"✅ Found: {rf}")

    # 2. submission.yaml is valid YAML
    sub_path = os.path.join(root, "submission.yaml")
    try:
        with open(sub_path, "r", encoding="utf-8") as f:
            sub_data = yaml.safe_load(f)
        print("✅ submission.yaml is valid YAML.")
    except Exception as e:
        errors.append(f"❌ submission.yaml parsing failed: {e}")
        sub_data = None

    # 3. Required fields in submission.yaml
    if sub_data:
        team = sub_data.get("team", {})
        sub = sub_data.get("submission", {})

        def check(val, name):
            if not val or val == '""' or str(val).strip() == "":
                errors.append(f"❌ Missing required field: {name}")

        check(team.get("name"), "team.name")
        check(team.get("track"), "team.track")
        check(team.get("lead", {}).get("name"), "team.lead.name")
        check(team.get("lead", {}).get("email"), "team.lead.email")
        check(sub.get("title"), "submission.title")
        check(sub.get("problem_statement"), "submission.problem_statement")
        check(sub.get("solution_summary"), "submission.solution_summary")

        track = team.get("track", "")
        if track not in ["AI", "DevOps", "Sustainability", "Open"]:
            errors.append(f"❌ Invalid track: {track}")
        else:
            print(f"✅ team.track is valid: {track}")

        features = sub.get("key_features", [])
        if not features or len(features) < 1:
            errors.append("❌ submission.key_features must have at least 1 entry")
        else:
            print(f"✅ submission.key_features has {len(features)} items.")

    # 4. src/ has actual code
    src_dir = os.path.join(root, "src")
    code_files = []
    for dirpath, _, filenames in os.walk(src_dir):
        for f in filenames:
            if f not in ["README.md", ".env.example"]:
                code_files.append(os.path.join(dirpath, f))
    if len(code_files) < 1:
        errors.append("❌ src/ contains no source code files.")
    else:
        print(f"✅ src/ contains {len(code_files)} source code files.")

    # 5. demo video link is not placeholder
    demo_link_path = os.path.join(root, "demo", "demo-video-link.txt")
    with open(demo_link_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
    if "your-demo-video-link-here" in first_line:
        errors.append("❌ demo/demo-video-link.txt contains placeholder.")
    else:
        print(f"✅ Demo video link verified: {first_line}")

    # 6. README placeholders
    readme_path = os.path.join(root, "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    if "[Your Project Title Here]" in readme_content:
        errors.append("❌ README contains [Your Project Title Here]")
    if "[Your Team Name]" in readme_content:
        errors.append("❌ README contains [Your Team Name]")
    
    # Check for unreplaced brackets pattern
    unreplaced = re.findall(r'\[(?:[A-Z][a-z]+|\.\.\.)[^\]]*\]', readme_content)
    # Ignore markdown links e.g. [docs/setup-guide.md](...)
    suspicious = [u for u in unreplaced if not any(x in u for x in ["See demo", "See presentation", "docs/"])]
    if suspicious:
        print(f"⚠️ Note: check potential placeholders in README: {suspicious}")
    else:
        print("✅ README.md placeholders verified clear.")

    print("\n-------------------------------------------------------------")
    if errors:
        print(f"❌ VALIDATION FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("🎉 ALL VALIDATION CHECKS PASSED PERFECTLY!")
        print(f"Team:  {team.get('name')}")
        print(f"Title: {sub.get('title')}")
        print(f"Track: {team.get('track')}")
        print("-------------------------------------------------------------\n")

if __name__ == "__main__":
    test_validation()
