# AI Notes API

A simple FastAPI project with user authentication, note management, and AI-powered summarization. Supports Docker deployment.

## Requirements

- Python 3.10+
- Docker & Docker Compose (optional for containerized setup)

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ai-notes-api
````

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

* **Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

* **Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with the following generic values:

```env
# PostgreSQL credentials
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name

# Database URL for app
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@host.docker.internal:5432/your_database_name

# Secret key for JWT auth
SECRET_KEY=your_secret_key_here
```

> Note: `host.docker.internal` is required for Docker to connect to the host PostgreSQL server on Windows/macOS.
> Replace placeholders with your own credentials.

### 5. Run the app locally

```bash
uvicorn app.main:app --reload
```

The API docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 6. Run with Docker

```bash
docker-compose up --build
```

* App will be available at [http://localhost:8000/docs](http://localhost:8000/docs)
* PostgreSQL container will store data in a Docker volume.

### 7. Features

* User signup/login with JWT authentication
* Roles: `ADMIN` and `AGENT`
* Notes creation, update, delete
* Async AI summarization (optional local LLM)
* Dockerized setup for easy deployment



