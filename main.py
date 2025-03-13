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


def run_command(command, cwd=None, env=None):
    """Run a shell command and capture output."""
    try:
        result = subprocess.run(command, shell=True, check=True,
                                cwd=cwd, capture_output=True, text=True, env=env)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"


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
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("")

    logs = run_command(command, cwd="sdufReactNative")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(logs)

    return logs


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
