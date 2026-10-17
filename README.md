# Food Delivery Order Tracker

A FastAPI application for tracking delivery order state across restaurant staff, customers, and kitchen views. The service uses PostgreSQL as the source of truth, Redis for caching and pub/sub notifications, and a pure state machine in `app/states.py` to enforce legal transitions.

## Tech stack

- Python 3.12
- FastAPI
- PostgreSQL
- Redis
- Docker + Docker Compose
- pytest + Ruff

## Local run

```bash
docker compose up --build
curl http://localhost:8080/health
```

Expected health output:

```json
{"status":"ok","postgres":true,"redis":true}
```

## Endpoints

- `GET /health` — checks PostgreSQL and Redis separately
- `POST /orders` — create a new order
- `GET /orders/{id}` — fetch current order state, served from cache when available
- `DELETE /orders/{id}` — delete a delivered or cancelled order
- `POST /orders/{id}/status` — advance or reject a status transition
- `POST /orders/{id}/cancel` — cancel before cooking begins
- `GET /orders/{id}/watch` — wait for a pub/sub update
- `GET /restaurants/{name}/queue` — return outstanding orders for a restaurant

Order lifecycle:

`placed -> accepted -> cooking -> out_for_delivery -> delivered`

A customer may cancel only while the order is still before cooking starts.
Orders can be deleted only after they reach a terminal state. Deleting an order
also removes its event history through the database foreign-key cascade and
invalidates its cached snapshot.

For a complete local CRUD demonstration, create an order with `POST /orders`,
read it with `GET /orders/{id}`, advance it through the status endpoint until
it is delivered, then delete it with `DELETE /orders/{id}`. Check persistence
with `docker compose exec db psql -U tracker -d tracker -c 'SELECT id, status FROM orders;'`.

## Why the database is the authority

The subtle bug is a classic read-then-write race:

1. Staff member A reads the order and sees `accepted`.
2. Staff member B reads the same order and also sees `accepted`.
3. A writes `cooking`.
4. B writes `cancelled` or an earlier status based on stale data.

If that stale write is allowed, the order moves backwards, which violates the business rule and breaks customer trust.

The fix is to make the database reject stale writes. The application does this by checking `expected` against the current status in code and then issuing a conditional update:

```sql
UPDATE orders
SET status = %s, version = version + 1, updated_at = now()
WHERE id = %s AND status = %s
RETURNING id
```

The `WHERE status = current_status` clause means the second writer does not overwrite the first. If a row is not updated, the app raises a conflict (`409`) instead of silently undoing progress. This is exactly why the `expected` field is included in the API payload and why `is_backwards` is treated separately from an illegal transition.

## State machine

`app/states.py` contains the pure logic used to validate transitions and guard concurrency. It covers:

- all legal transitions
- invalid moves
- cancellation rules
- terminal states
- progress and remaining stages
- stale expected-status checks

The state-machine and API unit tests do not require PostgreSQL or Redis. The
integration tests verify behavior against real PostgreSQL and Redis services.

## CI pipeline

On `main`, CircleCI runs secret scanning, Ruff, unit tests, integration tests
against real Postgres and Redis services, then builds and pushes the Docker
image to Docker Hub as `qa` and `main-<short-sha>`. On `staging` and `prod`,
it only builds and pushes the corresponding moving tag (`stage` or `prod`) and
immutable branch/SHA tag. Configure `DOCKERHUB_USER` and a Docker Hub access
token in CircleCI project environment variables as `DOCKERHUB_USER` and
`DOCKERHUB_TOKEN`; do not put credentials in the repository.

## Kubernetes

The manifests under `k8s/` use one shared base and separate `qa`, `stage`, and
`prod` overlays. Each namespace has the application, Postgres (with a PVC),
and Redis; application Pods run migrations in an init container, use the
namespace's Docker Hub pull secret, and pull their own moving tag with
`imagePullPolicy: Always`. Replace `REPLACE_WITH_DOCKERHUB_USER` in each
overlay's `kustomization.yaml` with the Docker Hub account that owns
`delivery-tracker-python`.

Create the namespaces, then create a Docker Hub pull secret and a database
password secret in **each** namespace before applying the matching overlay:

```powershell
kubectl apply -f k8s/namespaces.yaml
foreach ($ns in @("qa", "stage", "prod")) {
  kubectl create secret docker-registry dockerhub -n $ns `
    --docker-username="$env:DOCKERHUB_USER" `
    --docker-password="$env:DOCKERHUB_TOKEN"
  kubectl create secret generic tracker-db -n $ns `
    --from-literal=password="$env:TRACKER_DB_PASSWORD"
}
kubectl apply -k k8s/overlays/qa
kubectl apply -k k8s/overlays/stage
kubectl apply -k k8s/overlays/prod
```

Set `TRACKER_DB_PASSWORD` locally before running those commands. Do not commit
it. After a `main` PR merges and CircleCI pushes the new `qa` image, refresh
the deployment and verify the rollout and image digest:

```powershell
kubectl rollout restart deployment/delivery-tracker -n qa
kubectl rollout status deployment/delivery-tracker -n qa
kubectl get pods -n qa -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}'
kubectl get pod <pod-name> -n qa -o jsonpath='{.status.containerStatuses[0].imageID}'
```

Compare the returned digest with the digest reported for the image pushed by
the corresponding CircleCI build.

## Migration and infrastructure

The database schema and seed data live under `migrations/`. The compose stack includes:

- app
- PostgreSQL
- Redis
- migration job

The migration job runs all SQL files in filename order and then the app starts only after the database is ready. The same migration module is used by
the Kubernetes init container so the deployed image matches the one built by
the pipeline.
