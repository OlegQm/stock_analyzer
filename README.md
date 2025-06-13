# Stock Analyzer

Stock Analyzer is a web application for analyzing Yahoo Finance data. The project provides a FastAPI backend, a Streamlit frontend and a MongoDB database.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [docker compose](https://docs.docker.com/compose/)
- An OpenAI API key (required for NLP features)

### Running with Docker

1. Clone this repository.
2. Provide your OpenAI key by exporting the environment variable `OPENAI_API_KEY` or by creating a `.env` file in the project root containing it.
3. Build and start the containers:

```bash
docker compose up --build
```

4. Open the Streamlit frontend at [http://localhost:8501](http://localhost:8501).
5. The FastAPI backend will be available at [http://localhost:8000](http://localhost:8000).

### Makefile Commands

For convenience the repository contains a `Makefile` with common commands:

```bash
make up        # build and start containers
make down      # stop containers
make restart   # rebuild and restart containers
make logs      # follow container logs
make clean_all # remove all containers, images and volumes
```

## Project Structure

- `backend/` - FastAPI application
- `frontend/` - Streamlit dashboard
- `mongodb/` - MongoDB configuration
- `docker-compose.yaml` - Compose configuration
- `Makefile` - helper commands

