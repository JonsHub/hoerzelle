import subprocess
import os
import time
def restart_maico():
    for i in range(5, 0, -1):
        print(f"Restarting in {i} seconds...")
        time.sleep(1)
    try:
        os.system("taskkill /F /IM maico32.exe")
        time.sleep(2)
        subprocess.Popen("E:\\maico32.exe")
        print("maico32.exe restarted")
    except Exception as e:
        print(f"Error restarting maico: {e}")

if __name__ == "__main__":
    restart_maico()