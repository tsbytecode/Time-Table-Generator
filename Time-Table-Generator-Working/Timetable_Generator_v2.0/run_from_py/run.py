import subprocess

def launch_executable(path_to_executable):
    """
    Launches an executable file using the subprocess module.

    Args:
        path_to_executable (str): The full path to the executable file.
    """
    print(f"Attempting to launch executable: {path_to_executable}")
    try:
        # Popen is non-blocking, meaning your Python script continues to run.
        # Use subprocess.run() if you want to wait for the process to complete.
        process = subprocess.Popen([path_to_executable])
        print(f"Process launched with PID: {process.pid}")
        # To wait for the process to finish, uncomment the line below:
        # process.wait()
    except FileNotFoundError:
        print(f"Error: The executable was not found at {path_to_executable}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage: Change this to the path of your executable
    # On Windows, it could be a .exe file
    # On macOS or Linux, it's a binary file
    executable_path = "C:\\Program Files\\Notepad++\\notepad++.exe"  # Example for Windows
    # executable_path = "/Applications/Calculator.app/Contents/MacOS/Calculator" # Example for macOS
    # executable_path = "/usr/bin/gnome-calculator" # Example for Linux
    launch_executable(executable_path)