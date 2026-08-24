# AGENTS.md — eSIM Market Backend

## Bootstraping / Initializing

### Purpose

This repository is `esim-market-backend`, the Python backend for the eSIM Market project.

For the current task, implement **only this first section: Bootstraping / Initializing**.

The bootstrap must establish:

- a FastAPI REST API process,
- an asyncio-based long-running job process,
- MongoDB integration through Beanie ODM,
- Redis integration supporting standalone and Sentinel deployments,
- reusable startup/shutdown resource mixins,
- shared stdout/stderr/rolling-file logging,
- clean architecture boundaries,
- repository factory abstractions for eSIM sellers,
- liveness/readiness endpoints suitable for Kubernetes,
- self-hosted Swagger UI and ReDoc assets,
- two independent Docker images,
- two independent dependency manifests.

Do not implement the later sections of this document.

---

### Required Repository Structure

The repository must follow this structure:

```text
esim-market-backend/
├── AGENTS.md
├── README.md
├── .gitignore
├── .dockerignore
├── Dockerfiles/
│   ├── esim-market-backend-api
│   └── esim-market-backend-job
├── requirements-api.txt
├── requirements-job.txt
└── backend/
    ├── __init__.py
    ├── common/
    │   ├── logging/
    │   │   ├── __init__.py
    │   │   ├── logger_factory.py
    │   │   └── logging_config.py
    │   ├── env/
    │   │   ├── settings.py
    │   │   └── redis_env_settings.py
    │   └── entity/
    │       ├── db/
    │       └── domain/
    ├── usecase/
    │   ├── usecase_base.py
    │   └── ...
    ├── repository/
    │   ├── seller/
    │   │   ├── esim_seller_repository_base.py
    │   │   ├── esim_connect_repository.py
    │   │   ├── esim_xyz_repository.py
    │   │   └── repository_factory.py
    │   ├── mongodb/
    │   ├── http/
    │   └── redis/
    │       ├── __init__.py
    │       ├── entity.py
    │       ├── redis_base_repository.py
    │       ├── redis_repository_factory.py
    │       ├── redis_sentinel_repository.py
    │       ├── redis_standalone_repository.py
    │       ├── history_repository_mixin.py
    │       └── utils.py
    ├── gate/
    │   ├── integration/
    │   │   ├── api_app_base.py
    │   │   ├── mongodb_lifecycle_mixin.py
    │   │   ├── redis_lifecycle_mixin.py
    │   │   ├── health_router.py
    │   │   ├── main.py
    │   │   └── routes/
    │   └── taskmanager/
    │       ├── async_disposable.py
    │       ├── job_base.py
    │       ├── mongodb_lifecycle_mixin.py
    │       ├── redis_lifecycle_mixin.py
    │       ├── dummy_long_running_job.py
    │       └── main.py
    └── static/
        ├── swagger-ui-bundle.js
        ├── swagger-ui.css
        ├── redoc.standalone.js
        └── favicon.ico
```

If `Dockerfiles/` already exists, modify it in place.

The only dependency files must be:

```text
./requirements-api.txt
./requirements-job.txt
```

---

### Python Runtime

Both Dockerfiles must begin with:

```dockerfile
FROM python:3.12.14-slim-trixie
```

Do not silently replace that image.

---

### Pydantic Policy

Use **Pydantic 2.x only**.

At implementation time, resolve the latest stable Pydantic 2.x release compatible with the selected FastAPI, Beanie and `pydantic-settings` versions.

Do not install Pydantic 1.x.

Prefer Pydantic v2 APIs such as:

```text
model_validate
model_dump
model_dump_json
field_validator
model_validator
ConfigDict
SettingsConfigDict
```

Pin exact resolved versions in the final requirements files.

---

### Clean Architecture

Apply clean-code and clean-architecture principles.

Framework/process-specific code belongs at the gates.

Business logic belongs under:

```text
backend/usecase/
```

External-system implementations belong under:

```text
backend/repository/
```

Configuration and entities belong under:

```text
backend/common/
```

Do not put business logic inside route handlers, startup code, Redis repositories or job bootstrapping.

Use explicit dependencies and type hints.

---

### Usecase Base

Create:

```text
backend/usecase/usecase_base.py
```

with an abstract:

```text
UsecaseBase
```

Every concrete use case must inherit from it.

Use a minimal asynchronous execution contract such as:

```python
from abc import ABC, abstractmethod

class UsecaseBase(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs):
        ...
```

Do not couple `UsecaseBase` to FastAPI, Redis, MongoDB or Uvicorn.

---

### eSIM Seller Repository Abstraction

Create:

```text
backend/repository/seller/
```

Create abstract:

```text
EsimSellerRepositoryBase
```

with exactly these bootstrap operations:

```python
@abstractmethod
async def list_products(...):
    ...

@abstractmethod
async def place_order(...):
    ...
```

Use typed arguments and project-owned return models.

Do not expose raw `httpx.Response` objects to use cases.

---

### Seller Implementations

Create:

```text
EsimConnectRepository
EsimXYZRepository
```

Both inherit from `EsimSellerRepositoryBase`.

For bootstrap, these may be minimal adapters/stubs.

Do not invent undocumented seller API endpoints.

Actual eSIM Connect SDK integration belongs to Section 3.

---

### Seller RepositoryFactory

Create:

```text
backend/repository/seller/repository_factory.py
```

with:

```text
RepositoryFactory
```

Its instance `create()` method must accept an already-created `httpx.AsyncClient`.

Preferred shape:

```python
class RepositoryFactory:
    def create(
        self,
        seller: EsimSellerType,
        http_client: httpx.AsyncClient,
    ) -> EsimSellerRepositoryBase:
        ...
```

Use a typed seller Enum and mapping-based registration.

Do not create a new HTTP client per repository operation.

---

### MongoDB / Beanie

Use:

```python
from beanie import init_beanie
from pymongo import AsyncMongoClient
```

Create one Mongo client per process lifecycle.

Initialize Beanie once.

Keep Beanie `Document` classes under:

```text
backend/common/entity/db/
```

Keep pure domain models under:

```text
backend/common/entity/domain/
```

Define `MongoSettings` with flat, environment-backed properties:

```text
DEBUG
MONGO_DSN
MONGO_ENDPOINT
MONGO_DB_NAME
MONGO_USER
MONGO_PASS
MONGO_REPL
```

`MONGO_ENDPOINT`, `MONGO_USER`, and `MONGO_PASS` are required. `MONGO_DB_NAME`
defaults to `UK1648`, while `MONGO_DSN` and `MONGO_REPL` are optional.

When `MONGO_DSN` is absent, derive it after settings validation from the endpoint,
database, credentials, and optional replica-set name. When `MONGO_DSN` is supplied,
use it unchanged. Keep `AppSettings` independent so it does not instantiate required
MongoDB settings during module import.

---

### MongoDB Lifecycle Mixin

Create reusable MongoDB lifecycle mixins for both API and taskmanager.

Responsibilities:

- load settings,
- create `AsyncMongoClient` with `MONGO_DSN`,
- initialize Beanie with `MONGO_DB_NAME`,
- expose/store the client,
- close resources on shutdown/disposal.

For FastAPI expose the client on:

```python
app.state.mongodb_client
```

or a similarly stable state field.

Do not duplicate Mongo startup logic.

---

### Redis Dependencies

Both API and job runtimes must include Redis.

Use the current stable `redis` PyPI package and `redis.asyncio`.

Support:

```text
STAND_ALONE
SENTINEL
```

Standalone is primarily for local Docker Compose.

Sentinel is primarily for Kubernetes.

---

### Supplied Redis Repository Code

Integrate the supplied Redis repository code under:

```text
backend/repository/redis/
```

Preserve the intended types:

- `RedisBaseRepository`
- `RedisStandAloneRepository`
- `RedisSentinelRepository`
- `RedisRepositoryFactory`
- `RedisSentinelConnectionModel`

Preserve the mapping-based factory behavior for standalone and Sentinel repositories.

Do not blindly copy legacy imports that reference unrelated LLM/RAG project modules.

Adapt the supplied code so it compiles in this repository.

The supplied `HistoryRepositoryMixin` contains LLM/RAG-specific imports; refactor it to an eSIM-neutral form or omit it from inheritance until a real use case requires it.

Do not invent LLM/RAG classes merely to satisfy old imports.

---

### Redis Environment Settings

Place the supplied Redis environment model under:

```text
backend/common/env/redis_env_settings.py
```

Use Pydantic v2 and `pydantic-settings`.

Preserve the discriminated standalone/Sentinel configuration approach.

Support environment variables in this form:

```text
REDIS_CORE_CLUSTER_CONFIG__HOST=esim_market_redis
REDIS_CORE_CLUSTER_CONFIG__PORT=6379
REDIS_CORE_CLUSTER_CONFIG__PASSWORD=<secret>
REDIS_CORE_CLUSTER_CONFIG__CONNECTION_POOL_MAX_CONNECTIONS=100
REDIS_CORE_CLUSTER_CONFIG__KIND=STAND_ALONE
```

Do not hardcode the real Redis password in source, Dockerfiles, tests or committed env files.

---

### Redis Connection Construction

For `STAND_ALONE`, create an async Redis client/pool using configured:

- host,
- port,
- password,
- DB index,
- decode responses,
- max connections,
- socket timeout,
- socket connect timeout.

For `SENTINEL`, create async Sentinel connections suitable for Kubernetes.

Resolve master and replica/slave connections and wrap them in:

```text
RedisSentinelConnectionModel
```

Use the configured master alias.

---

### Redis Lifecycle Mixin

Create reusable Redis lifecycle mixins for API and taskmanager.

Responsibilities:

```text
startup / enter
  ├── load Redis settings
  ├── create standalone OR Sentinel connection
  ├── create RedisRepositoryFactory
  ├── create selected repository
  └── expose resources
```

and:

```text
shutdown / exit
  └── close Redis resources
```

For FastAPI expose:

```python
app.state.redis_connection
app.state.redis_repository_factory
app.state.redis_repository
```

Do not create a Redis connection per request.

---

### FastAPI Lifecycle

Use FastAPI async `lifespan`.

Do not use deprecated:

```python
@app.on_event("startup")
@app.on_event("shutdown")
```

Initialize both MongoDB/Beanie and Redis during lifespan startup and clean both up during shutdown.

Use reusable lifecycle mixins rather than embedding all resource code in `main.py`.

---

### ApiAppBase

Create:

```text
backend/gate/integration/api_app_base.py
```

with:

```text
ApiAppBase
```

It centralizes:

- FastAPI construction,
- lifespan,
- MongoDB/Beanie lifecycle,
- Redis lifecycle,
- self-hosted docs,
- root-path support,
- static files,
- router registration.

Do not put eSIM business logic in it.

---

### Unhandled Exception Middleware

Create and register:

```text
backend/gate/integration/unhandled_exception_middleware.py
```

with:

```text
UnhandledExceptionMiddleware
```

`ApiAppBase` must add this middleware to every FastAPI application it creates.

The middleware must:

- catch only unexpected request-processing exceptions,
- log the original exception and stack trace through the shared server-side logging facility,
- return a stable, sanitized JSON error envelope containing a project-owned application error code and request/correlation ID,
- avoid returning HTTP status `500`; use the project's designated non-500 unhandled-error status,
- never expose exception messages, exception types, stack traces, credentials, connection strings, source paths, or other system details to clients,
- preserve framework responses for expected errors such as validation failures and explicit `HTTPException` responses,
- avoid intercepting process-control exceptions such as cancellation,
- re-raise if an HTTP response has already started and can no longer be safely replaced.

The initial bootstrap contract is:

```json
{
  "error": {
    "code": "ESIM-UNHANDLED-001",
    "message": "An unexpected error occurred.",
    "request_id": "<opaque-correlation-id>"
  }
}
```

with HTTP status `520` and a matching `X-Request-ID` response header.

Do not use this middleware to hide expected domain errors. Expected errors must be mapped explicitly by their owning gate or use case.

---

### Liveness and Readiness

Create:

```text
backend/gate/integration/health_router.py
```

with endpoints:

```text
GET /health/live
GET /health/ready
```

`/health/live` only indicates process/event-loop liveness and must not fail just because MongoDB or Redis is temporarily unavailable.

`/health/ready` verifies required dependencies, at minimum:

```text
MongoDB
Redis
```

Use lightweight ping operations.

Return HTTP 200 when ready and HTTP 503 when a required dependency is unavailable.

Do not expose credentials, connection strings or stack traces.

---

### Self-Hosted Swagger / ReDoc

Disable FastAPI CDN-backed docs:

```python
FastAPI(
    docs_url=None,
    redoc_url=None,
    ...
)
```

Mount local assets from:

```text
backend/static/
```

Provide root-path-aware:

```text
/docs
/redoc
OAuth2 redirect
```

Vendor:

```text
swagger-ui-bundle.js
swagger-ui.css
redoc.standalone.js
favicon.ico
```

Do not require CDN access at runtime.

---

### API Requirements

Create:

```text
requirements-api.txt
```

Pin compatible exact versions of at least:

```text
fastapi
uvicorn[standard]
pydantic 2.x
pydantic-settings
beanie
pymongo
redis
httpx
```

Add only packages actually used.

---

### Job Requirements

Create:

```text
requirements-job.txt
```

Pin compatible exact versions of at least:

```text
pydantic 2.x
pydantic-settings
beanie
pymongo
redis
httpx
```

Do not add `asyncio`; it is part of Python.

Do not add FastAPI/Uvicorn unless actually required by the job runtime.

---

### API Dockerfile

Create or modify exactly:

```text
Dockerfiles/esim-market-backend-api
```

Start with:

```dockerfile
FROM python:3.12.14-slim-trixie
```

Use `/home/backend` as application directory.

Copy requirements first, install them, then:

```dockerfile
COPY ./backend /home/backend
```

The Dockerfile must use:

```dockerfile
ENTRYPOINT ["uvicorn"]
```

Use `CMD` for the module and options.

Ensure the module path works with the chosen `WORKDIR`/`PYTHONPATH`.

---

### API Reload Behavior

Development-mode FastAPI must support Uvicorn reload.

Important: `COPY ./backend /home/backend` only snapshots source at image-build time. It cannot detect later host edits.

Therefore:

- make the image compatible with `--reload`,
- production-style default execution should not require reload,
- when local Compose development is later configured, bind-mount host `./backend` into the corresponding container source path and run Uvicorn with `--reload`.

Do not claim that Docker `COPY` alone provides live reload.

Do not create Docker Compose files in this repository.

---

### Job Dockerfile

Create or modify exactly:

```text
Dockerfiles/esim-market-backend-job
```

Start with:

```dockerfile
FROM python:3.12.14-slim-trixie
```

Install Debian `dumb-init`.

Use `/home/backend`.

Copy `requirements-job.txt`, install, then:

```dockerfile
COPY ./backend /home/backend
```

Use:

```dockerfile
ENTRYPOINT ["dumb-init", "--"]
```

Use `CMD` to execute the taskmanager through `python -m ...`.

Do not run Uvicorn from this image.

---

### AsyncDisposable

Create project-owned:

```text
AsyncDisposable
```

Implement async context management:

```python
async def __aenter__(...)
async def __aexit__(...)
```

and an explicit async cleanup contract.

Cleanup should be idempotent where practical.

---

### JobBase

Create abstract:

```text
JobBase
```

A concrete job must inherit from it.

`JobBase` participates in `AsyncDisposable` lifecycle and defines:

```python
@abstractmethod
async def run(self) -> None:
    ...
```

---

### Dummy Long-Running Job

Create:

```text
backend/gate/taskmanager/dummy_long_running_job.py
```

It must:

- inherit `JobBase`,
- run continuously until cancellation/shutdown,
- avoid a busy loop,
- asynchronously sleep/wait between iterations,
- log periodically,
- respond cleanly to SIGTERM/SIGINT,
- exit its async context,
- clean up MongoDB/Redis resources.

Conceptually:

```python
while not stop_event.is_set():
    await asyncio.sleep(interval)
```

Never implement:

```python
while True:
    pass
```

---

### Job Entrypoint

Create:

```text
backend/gate/taskmanager/main.py
```

Use one:

```python
asyncio.run(main())
```

at the synchronous process boundary.

Support graceful signal-aware shutdown.

Both MongoDB/Beanie and Redis lifecycle behavior must be available to the taskmanager.

---

### Logging

Logging is a first-class bootstrap concern and must be reusable by both:

```text
backend/gate/integration
backend/gate/taskmanager
```

Use Python's standard:

```python
logging
```

package unless an existing project dependency already justifies another logging framework.

Do **not** add a third-party logging package merely to obtain stdout, stderr, or rolling-file support.

Create a reusable logging module under:

```text
backend/common/logging/
```

Recommended structure:

```text
backend/common/logging/
├── __init__.py
├── logger_factory.py
└── logging_config.py
```

The logging implementation must support three output channels:

```text
stdout
stderr
rolling file
```

#### stdout handler

Send normal operational logs to stdout.

Recommended levels:

```text
DEBUG
INFO
```

and optionally non-error warning-level messages according to the final handler filter design.

This is important for:

```text
Docker
Docker Compose
Kubernetes
OpenShift
```

where container runtimes collect stdout.

#### stderr handler

Send error logs to stderr.

At minimum:

```text
ERROR
CRITICAL
```

must be written to stderr.

Avoid duplicating the same ERROR/CRITICAL record to both stdout and stderr unless duplication is intentional and documented.

Use a logging `Filter` if necessary to keep stdout and stderr ranges non-overlapping.

#### Rolling file handler

Provide a rotating file logger using the Python standard-library handler:

```python
logging.handlers.RotatingFileHandler
```

or, if time-based rotation is explicitly more appropriate:

```python
logging.handlers.TimedRotatingFileHandler
```

For the bootstrap implementation, prefer size-based:

```text
RotatingFileHandler
```

with configuration controlled through environment settings.

Support at minimum:

```text
LOG_LEVEL
LOG_FILE_ENABLED
LOG_FILE_PATH
LOG_FILE_MAX_BYTES
LOG_FILE_BACKUP_COUNT
```

Use sensible development defaults, for example:

```text
LOG_LEVEL=INFO
LOG_FILE_ENABLED=false
LOG_FILE_PATH=/home/backend/logs/esim-market-backend.log
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=5
```

Do not hardcode production-only paths outside configuration.

Create the log directory safely when file logging is enabled.

Do not fail application startup solely because optional rolling-file logging cannot be initialized unless file logging is explicitly required.

#### Container logging policy

Container deployments should primarily rely on:

```text
stdout
stderr
```

because Kubernetes/OpenShift/Docker normally collect those streams.

Rolling-file logging is provided for:

- local development,
- standalone deployments,
- troubleshooting,
- environments where file-based logs are explicitly required.

Do not assume rolling files are durable inside Kubernetes containers.

Do not create a persistent logging volume in this repository.

Persistent log storage, if ever required, belongs to orchestration/Kubernetes configuration.

#### Shared logger factory

Create a reusable factory/helper, for example:

```python
get_logger(name: str) -> logging.Logger
```

or:

```python
LoggerFactory.create(name: str) -> logging.Logger
```

Use the same configuration for:

- FastAPI,
- Uvicorn-integrated application logs,
- MongoDB lifecycle logs,
- Redis lifecycle logs,
- repository logs,
- usecase logs,
- task-manager/job logs.

Avoid configuring handlers separately in every module.

Avoid duplicate handlers when the configuration function is called more than once.

Logging initialization must therefore be idempotent.

#### Formatting

Use a clear structured text format containing at least:

```text
timestamp
level
logger name
process id
message
```

Including thread/task context is optional.

A reasonable format is:

```text
%(asctime)s %(levelname)s %(name)s [pid=%(process)d] %(message)s
```

Do not use ANSI color codes in rolling-file output.

#### Exception logging

Use:

```python
logger.exception(...)
```

inside exception handlers when stack traces are useful.

Do not log stack traces for expected control-flow conditions.

Never log:

- Redis passwords,
- MongoDB passwords,
- seller API credentials,
- bearer tokens,
- API keys,
- complete sensitive connection URIs,
- personally sensitive request payloads.

#### Uvicorn logging

Integrate the application logging configuration cleanly with Uvicorn.

Do not allow Uvicorn to initialize a conflicting duplicate handler tree.

Preserve useful Uvicorn access/error logs.

If a custom Uvicorn `log_config` is supplied, it must remain compatible with the shared logger configuration and must not suppress application logs.

#### Job logging

The long-running dummy job must use the same logging facility.

At minimum it should log:

```text
job started
periodic heartbeat / loop activity at a reasonable interval
cancellation requested
resource cleanup
job stopped
```

Do not emit high-frequency logs on every tight-loop iteration.

---

### `.dockerignore`

Ensure repository-root `.dockerignore` excludes:

```text
.git
.gitignore
__pycache__
**/__pycache__
*.py[cod]
.pytest_cache
.mypy_cache
.ruff_cache
.venv
venv
.env
.env.*
```

Do not exclude:

```text
backend/static/
requirements-api.txt
requirements-job.txt
Dockerfiles/
```

---

### Bootstrap Validation

Run all feasible checks.

Python:

```bash
python -m compileall backend
```

API image:

```bash
docker build   -f Dockerfiles/esim-market-backend-api   -t esim-market-backend-api:local   .
```

Job image:

```bash
docker build   -f Dockerfiles/esim-market-backend-job   -t esim-market-backend-job:local   .
```

When dependencies are available, verify API:

```text
/health/live
/health/ready
/docs
/redoc
/openapi.json
/static/swagger-ui-bundle.js
/static/swagger-ui.css
/static/redoc.standalone.js
```

Test seller repository factory selection and reuse of the provided `httpx.AsyncClient`.

Test Redis standalone/Sentinel factory selection.

Test dummy-job start, cancellation and cleanup.

Do not claim validation succeeded unless actually executed.

---

### Completion Report for Section 1

Report:

1. files created,
2. files modified,
3. final directory structure,
4. exact Python image,
5. exact API dependency versions,
6. exact job dependency versions,
7. exact Pydantic 2.x version,
8. MongoDB/Beanie lifecycle design,
9. Redis standalone/Sentinel lifecycle design,
10. supplied Redis files adapted,
11. legacy Redis dependencies removed/refactored,
12. seller repository factory structure,
13. liveness/readiness behavior,
14. API Docker build result,
15. job Docker build result,
16. API health/docs validation,
17. Redis validation,
18. dummy-job validation,
19. logging configuration and validation for stdout/stderr/rolling file,
20. tests executed,
21. deviations/blockers.

Do not claim success for a step that was not executed.

---

## Complex Tuning

**SKIP THIS SECTION FOR NOW.**

This section is intentionally reserved for future work.

Do not infer or implement complex tuning during bootstrap.

---

## Integrating the API SDK with esim connect

**SKIP THIS SECTION FOR NOW.**

The `EsimConnectRepository` class and factory registration may exist as bootstrap structure, but actual eSIM Connect SDK integration must not be implemented yet.

Do not invent SDK contracts, endpoints, credentials, authentication flows or seller-specific production logic.

This section will be completed later.
