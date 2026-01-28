import subprocess
import time
import sys
import os

# Change to backend directory
os.chdir(r"D:\hackathon\backend")

# Start server as subprocess
print("Starting server...")
server_proc = subprocess.Popen(
    [r"D:\hackathon\.venv\Scripts\python.exe", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=r"D:\hackathon\backend"
)

# Wait for server to start - read output to verify
print("Waiting for server to start...")
start_time = time.time()
server_ready = False

while time.time() - start_time < 30:  # 30 second timeout
    import select
    import socket
    
    # Try to connect to the server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            server_ready = True
            print("Server is ready!")
            break
    except:
        pass
    
    time.sleep(1)
    
    # Check if process crashed
    if server_proc.poll() is not None:
        print("Server process exited unexpectedly!")
        stdout, stderr = server_proc.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)
    
    print(f"  Waiting... ({int(time.time() - start_time)}s)")

if not server_ready:
    print("Server failed to become ready in time!")
    stdout, stderr = server_proc.communicate(timeout=5)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    sys.exit(1)

print("Server started! Running tests...")

# Run tests
try:
    result = subprocess.run(
        [r"D:\hackathon\.venv\Scripts\python.exe", r"D:\hackathon\test_ai_voice.py"],
        capture_output=True,
        text=True,
        timeout=120
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
except Exception as e:
    print(f"Test error: {e}")

# Stop server
print("\nStopping server...")
server_proc.terminate()
server_proc.wait(timeout=5)
print("Done!")
