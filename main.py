import os
import time
import subprocess
from threading import Lock
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

# In-memory dictionary to track job status
job_status = {}
job_status_lock = Lock()

# Timeout threshold for a job to be considered "stuck" (in seconds)
JOB_TIMEOUT = 600  # 10 minutes

class ProjectEnvVarsRequest(BaseModel):
    """Define a Pydantic model for the request body."""
    url: str
    app_env: str
    socket_project_token: str
    socket_project_id: str
    style_url: str
    app_name: str
    app_package_name: str


def run_command(command, project_id, log_file, cwd=None, env=None):
    """Run a shell command and write output to a file in real-time."""
    start_time = time.time()  # Track start time
    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, env=env
        )

        # Read line by line and write in real-time
        for line in process.stdout:
            # Check if job is stuck
            if time.time() - start_time > JOB_TIMEOUT:
                with job_status_lock:
                    job_status[project_id] = 'stuck'
                process.terminate()  # Terminate the process if it's stuck
                return "Error: Job is stuck and was terminated."

            print(line, end="")  # Also print to console
            f.write(line)
            f.flush()  # Ensure it's written immediately

        process.wait()  # Wait for process to finish
        return_code = process.returncode
        if return_code != 0:
            with job_status_lock:
                job_status[project_id] = 'failed'
            return f"Error: Process exited with code {return_code}"

    return "Command executed successfully."


def execute_build(platform: str, body: ProjectEnvVarsRequest):
    """Execute build inside Docker with project-specific environment variables."""
    project = {
        "id": body.socket_project_id,
        "token": body.socket_project_token,
    }
    config = {
        "url": body.url,
        "style_url": body.style_url,
        "app_env": body.app_env,
        "display_name": body.app_name,
        "package_name": body.app_package_name
    }

    if platform != 'android':
        return {"error": "Only Android builds are supported at the moment."}

    command = f'''
        URL="{config['url']}" \
        APP_ENV="{config['app_env']}" \
        SOCKET_PROJECT_TOKEN="{project['token']}" \
        SOCKET_PROJECT_ID="{project['id']}" \
        styleURL="{config['style_url']}" \
        APP_NAME="{config['display_name']}" \
        APP_PACKAGE_NAME="{config['package_name']}" \
        docker compose up --build
    '''

    log_file = f"logs/{project['id']}_log.txt"
    os.makedirs("logs", exist_ok=True)

    # Update job status to 'running'
    with job_status_lock:
        job_status[project['id']] = 'running'

    # Run command with real-time logging and handle failure/stuck
    result = run_command(command, project['id'], log_file, cwd="sdufReactNative", env=None)

    # Update job status to 'finished' or 'failed'
    with job_status_lock:
        if result == "Command executed successfully.":
            job_status[project['id']] = 'finished'
        # Else, it's already marked as 'failed' or 'stuck' in the run_command function

    return result


@app.post("/build/{platform}")
def trigger_build(platform: str, body: ProjectEnvVarsRequest, background_tasks: BackgroundTasks):
    """Trigger a build for a given project on a specified platform."""

    if platform not in ["android", "ios"]:
        return {"error": "Invalid platform. Use 'android' or 'ios'."}

    # Add the build job to the background tasks
    background_tasks.add_task(execute_build, platform, body)

    return {"message": f"Build for project {body.socket_project_id} ({platform}) started"}


@app.get("/logs/{project_id}")
def get_logs(project_id: str):
    """Retrieves logs for a given project."""

    log_file = f"logs/{project_id}_log.txt"
    if not os.path.exists(log_file):
        return {"error": "No logs available for this project."}

    with open(log_file, "r", encoding="utf-8") as f:
        logs = f.read()
    return {"logs": logs}


@app.get("/status/{project_id}")
def get_build_status(project_id: str):
    """Get the status of the build job."""
    with job_status_lock:
        status = job_status.get(project_id, 'unknown')

    return {"status": status}
