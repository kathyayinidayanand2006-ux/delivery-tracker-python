#!/usr/bin/env bash
# Kubernetes Setup Script for Food Delivery Order Tracker across qa, stage, and prod
set -euo pipefail

DOCKER_USER="${1:-kathyayinidayanand2006}"
DOCKER_TOKEN="${2:-}"
DB_PASSWORD="${3:-tracker}"

echo "=== 1. Creating Namespaces (qa, stage, prod) ==="
kubectl apply -f k8s/namespaces.yaml

echo "=== 2. Creating Database Secrets (tracker-db) in qa, stage, prod ==="
for ns in qa stage prod; do
  kubectl create secret generic tracker-db \
    --from-literal=password="${DB_PASSWORD}" \
    -n "${ns}" \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "Configured tracker-db secret in namespace: ${ns}"
done

if [ -n "${DOCKER_TOKEN}" ]; then
  echo "=== 3. Creating Docker Hub secret 'dockerhub' in qa, stage, prod ==="
  for ns in qa stage prod; do
    kubectl create secret docker-registry dockerhub \
      --docker-username="${DOCKER_USER}" \
      --docker-password="${DOCKER_TOKEN}" \
      -n "${ns}" \
      --dry-run=client -o yaml | kubectl apply -f -
    echo "Configured dockerhub secret in namespace: ${ns}"
  done
else
  echo "NOTE: No Docker token provided. Run with: ./k8s/setup-k8s.sh <docker-user> <docker-token> <db-password>"
fi

echo "=== 4. Applying Workloads to qa, stage, prod ==="
kubectl apply -f k8s/qa.yaml
kubectl apply -f k8s/stage.yaml
kubectl apply -f k8s/prod.yaml

echo ""
echo "=== Deployments Applied Successfully ==="
echo "To monitor QA namespace rollout:"
echo "  kubectl rollout status deployment/delivery-tracker -n qa"
echo "  kubectl get pods -n qa"
