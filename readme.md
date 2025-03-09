# React Native App Builder

## Overview
The **React Native App Builder** is an FastAPI-based service that automates the build process for React Native applications. It supports both Android and iOS builds by leveraging Docker containers to ensure a consistent, scalable, and secure build environment.

## Features
- **Automated Build Execution**: Trigger builds via API calls for Android and iOS platforms.
- **Dockerized Environment**: Ensures consistency and eliminates dependency issues.
- **Project-Specific Configurations**: Dynamically injects environment variables into the build process.
- **Build Logging & Retrieval**: Stores logs per project, accessible via API.
- **Secure & Scalable**: Designed to be deployed in production environments with cloud-native architectures.

## Architecture
The application follows a **microservices-oriented** approach with FastAPI as the backend framework. It integrates with:
- **Docker Compose** for isolated and reproducible builds.
- **Persistent Logging** for tracking build progress and debugging.
- **Project Configuration Management** to customize builds per project.

## API Endpoints
### 1. Trigger a Build
**Endpoint:** `POST /build/{project_id}/{platform}`

**Description:** Initiates a build for the given project and platform.

**Parameters:**
- `project_id` *(string)*: Unique identifier of the project.
- `platform` *(string)*: Either `android` or `ios`.

**Response:**
```json
{
  "message": "Build for project {project_id} ({platform}) started",
  "logs": "...initial logs..."
}
```

### 2. Retrieve Build Logs
**Endpoint:** `GET /logs/{project_id}`

**Description:** Fetches the latest build logs for a specific project.

**Parameters:**
- `project_id` *(string)*: Unique identifier of the project.

**Response:**
```json
{
  "logs": "...build logs..."
}
```

## Deployment
### Prerequisites
- **Docker & Docker Compose** installed on the system.
- **Python 3.8+** with FastAPI dependencies.

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/sduf-net/sdufAppBuilder.git
   cd sdufAppBuilder
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start the API server:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Configuration
Environment variables used in the build process:
- `URL` - React Native project repository URL
- `APP_ENV` - Project environment (e.g., staging, production)
- `SOCKET_PROJECT_TOKEN` - Authentication token for the project
- `SOCKET_PROJECT_ID` - Unique project identifier
- `styleURL` - Map styling URL (if applicable)
- `APP_NAME` - Application display name
- `APP_PACKAGE_NAME` - Application package identifier

## Security Considerations
- **Environment Variables**: Ensure sensitive values are stored securely and not hardcoded.
- **Docker Isolation**: Each build runs in an isolated container to prevent conflicts.
- **Access Controls**: API authentication and authorization mechanisms should be implemented for production.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
