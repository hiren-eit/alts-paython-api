import os
import sys
def stop_project():
    print("Stopping project processes...")
    try:
        # Kill python.exe and uvicorn.exe processes forcefully
        # /F = force, /IM = image name
        os.system("taskkill /F /IM python.exe /T")
        os.system("taskkill /F /IM uvicorn.exe /T")
        print("Successfully stopped all Python and Uvicorn processes.")
    except Exception as e:
        print(f"Error stopping processes: {e}")
if __name__ == "__main__":
    stop_project()