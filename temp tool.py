import os
import sys
import shutil
import psutil
import ctypes

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Attempting to relaunch as administrator...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

def get_temp_directories():
    """Get a list of all temp directories in Windows 10."""
    return [
        os.getenv("TEMP"),
        os.getenv("TMP"),
        "C:\\Windows\\Temp",
        "C:\\Users\\Public\\Temp",
        os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp"),
    ]

def close_open_files_in_dir(directory):
    """Close any open files or applications using files in the given directory."""
    for proc in psutil.process_iter(attrs=['pid', 'name', 'open_files']):
        try:
            open_files = proc.info['open_files']
            if open_files:
                for file in open_files:
                    if file.path.startswith(directory):
                        print(f"Closing {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                        proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def delete_temp_files():
    """Delete all files in Windows temp directories."""
    temp_dirs = get_temp_directories()

    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            print(f"Cleaning directory: {temp_dir}")
            close_open_files_in_dir(temp_dir)
            try:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                        except Exception as e:
                            print(f"Failed to delete {file_path}: {e}")

                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            shutil.rmtree(dir_path)
                            print(f"Deleted directory: {dir_path}")
                        except Exception as e:
                            print(f"Failed to delete {dir_path}: {e}")
            except Exception as e:
                print(f"Error cleaning {temp_dir}: {e}")
        else:
            print(f"Directory does not exist: {temp_dir}")

if __name__ == "__main__":
    delete_temp_files()
