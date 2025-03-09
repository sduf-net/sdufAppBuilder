import os
import subprocess
import sys
from fastapi import FastAPI

app = FastAPI()

def run_command(command, cwd=None, env=None):
    """Run a shell command and capture output."""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def execute_build(project_id, platform):
    """Execute build inside Docker with project-specific environment variables."""
    # Mocked retrieval of project and config (Replace with actual DB queries)
    project = {"id": project_id, "name": "SampleProject", "token": "project_token"}
    config = {"display_name": "MyApp", "package_name": "com.example.myapp"}
    
    command = f'''
    URL="http://react_native_url" \
    APP_ENV="{project['name']}" \
    SOCKET_PROJECT_TOKEN="{project['token']}" \
    SOCKET_PROJECT_ID="{project['id']}" \
    styleURL="http://maptiler_url" \
    APP_NAME="{config['display_name']}" \
    APP_PACKAGE_NAME="{config['package_name']}" \
    docker compose up --build
    '''
    
    log_file = f"logs/{project_id}_log.txt"
    os.makedirs("logs", exist_ok=True)
    with open(log_file, "w") as f:
        f.write("")
    
    logs = run_command(command, cwd="/path/to/react_native_project")
    with open(log_file, "a") as f:
        f.write(logs)
    
    return logs

@app.post("/build/{project_id}/{platform}")
def trigger_build(project_id: str, platform: str):
    if platform not in ["android", "ios"]:
        return {"error": "Invalid platform. Use 'android' or 'ios'."}
    
    logs = execute_build(project_id, platform)
    return {"message": f"Build for project {project_id} ({platform}) started", "logs": logs}

@app.get("/logs/{project_id}")
def get_logs(project_id: str):
    log_file = f"logs/{project_id}_log.txt"
    if not os.path.exists(log_file):
        return {"error": "No logs available for this project."}
    
    with open(log_file, "r") as f:
        logs = f.read()
    return {"logs": logs}
