import os
import sys

# Ensure the argument is provided
if len(sys.argv) < 2:
    print("Usage: python3 runner.py <parameter>")
    sys.exit(1)

param = sys.argv[1]
repo_owner = "c24-s60348"
repo_name = "afwan_cron"
file_path = "automation_Afwan.py"  # Adjust if the file is in a subdirectory
raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{file_path}"

# Step 1: Download the file
os.system(f"wget -O automation_Afwan.py {raw_url} || curl -o automation_Afwan.py {raw_url}")

# Step 2: Run the script
os.system(f"python3 automation_Afwan.py {param}")