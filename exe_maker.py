'''
A script to make main.exe from main.py while also removing useless files and folders.
Run this script to make/update main.exe with main.py.
'''

import os
import shutil

def remove(name, file=True):
    try:
        if file:
            os.remove(name)
        else:
            shutil.rmtree(name)
        print(f"\033[92m Successfully deleted {name}")
    except Exception as e:
        print(f"\033[91m Failed to delete {name}\n{e}")

print("\033[92m Creating main.exe from main.py...\033[0m")
os.system("pyinstaller main.py --onefile --noconsole")

if os.path.exists("main.exe"):
    remove("main.exe")
os.rename("./dist/main.exe", "main.exe")

remove("main.spec")
remove("build", file=False)
remove("dist", file=False)
print("\033[92m Successfully created main.exe from main.py\033[0m")