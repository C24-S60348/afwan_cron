import os
import sys

param = sys.argv[1] if len(sys.argv) > 1 else ""

if param != "":
    print("Killing any current process...")
    os.system(f"pkill -f 'python automation_Afwan.py {param}'")  

    print("Starting the new process...")
    os.system(f"nohup python automation_Afwan.py {param} > /dev/null 2>&1 &")
    print(f"Done run automation_Afwan.py {param}")
    
    print("To check: (ps aux | grep python)")
    os.system("ps aux | grep python")

else:
    os.system(f"python automation_Afwan.py")
    print(f"Done run automation_Afwan.py ")
exit()
