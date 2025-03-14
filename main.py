import os
import subprocess
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()


class ProjectEnvVarsRequest(BaseModel):
    """Define a Pydantic model for the request body."""
    url: str
    app_env: str
    socket_project_token: str
    socket_project_id: str
    style_url: str
    app_name: str
    app_package_name: str


def run_command(command, log_file, cwd=None, env=None):
    """Run a shell command and write output to a file in real-time."""
    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, env=env
        )

        # Read line by line and write in real-time
        for line in process.stdout:
            print(line, end="")  # Also print to console
            f.write(line)
            f.flush()  # Ensure it's written immediately

        process.wait()  # Wait for process to finish
        return_code = process.returncode
        if return_code != 0:
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

    # Run command with real-time logging
    return run_command(command, log_file, cwd="sdufReactNative")


@app.post("/build/{platform}")
def trigger_build(platform: str, body: ProjectEnvVarsRequest, background_tasks: BackgroundTasks):
    """Trigger a build for a given project on a specified platform."""

    if platform not in ["android", "ios"]:
        return {"error": "Invalid platform. Use 'android' or 'ios'."}

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
