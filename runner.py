import os
import sys

# Ensure the argument is provided
#if len(sys.argv) < 2:
#    print("Usage: python3 runner.py <parameter>")
#    sys.exit(1)

param = sys.argv[1] if len(sys.argv) > 1 else ""
repo_owner = "c24-s60348"
repo_name = "afwan_cron"
file_path = "automation_Afwan.py"  # Adjust if the file is in a subdirectory
raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{file_path}"

print("Downloading the latest script...")
os.system(f"wget -O automation_Afwan.py {raw_url} || curl -o automation_Afwan.py {raw_url}")

if param != "":
    print("Killing any current process...")
    os.system(f"pkill -f 'python3 automation_Afwan.py {param}'")  

    print("Starting the new process...")
    os.system(f"nohup python3 automation_Afwan.py {param} > /dev/null 2>&1 &")
    print(f"Done run automation_Afwan.py {param}")
    
    print("To check: (ps aux | grep python3)")
    os.system("ps aux | grep python3")

else:
    os.system(f"python3 automation_Afwan.py")
    print(f"Done run automation_Afwan.py ")
exit()
