# eSIM Market Backend

`esim-market-backend` contains the Python backend for eSIM Market. It provides the FastAPI web service, a background job process, and connections to MongoDB and Redis.

For detailed architecture, development, and orchestration guidance, see the [root `AGENTS.md`](https://github.com/tolga-kabadurmus/esim-market/blob/main/AGENTS.md).

## Relationship to the other repositories

- [`esim-market`](https://github.com/tolga-kabadurmus/esim-market) runs this backend with its dependencies through Docker Compose.
- [`esim-market-ui`](https://github.com/tolga-kabadurmus/esim-market-ui) is the web application that consumes the backend API.

## Run the backend

The simplest approach is through the parent orchestration repository. After configuring its local `.env/dev/` files, run from the `esim-market` directory:

```bash
docker compose up --build \
  esim-market-backend-api \
  esim-market-backend-job
```

Docker Compose also starts MongoDB and Redis. The API is available at <http://localhost:5002>, with documentation at <http://localhost:5002/docs>.

To build the two images directly from this repository:

```bash
docker build -f Dockerfiles/esim-market-backend-api -t esim-market-backend-api:local .
docker build -f Dockerfiles/esim-market-backend-job -t esim-market-backend-job:local .
```
