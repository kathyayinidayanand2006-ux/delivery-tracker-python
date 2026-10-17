# PowerShell Kubernetes Setup Script for Food Delivery Order Tracker across qa, stage, and prod
param(
    [string]$DockerUser = "kathyayinidayanand2006",
    [string]$DockerToken = "",
    [string]$DbPassword = "tracker"
)

Write-Host "=== 1. Creating Namespaces (qa, stage, prod) ===" -ForegroundColor Cyan
kubectl apply -f k8s/namespaces.yaml

Write-Host "=== 2. Creating Database Secrets (tracker-db) in qa, stage, prod ===" -ForegroundColor Cyan
foreach ($ns in @("qa", "stage", "prod")) {
    kubectl create secret generic tracker-db `
        --from-literal=password="$DbPassword" `
        -n $ns `
        --dry-run=client -o yaml | kubectl apply -f -
    Write-Host "Configured tracker-db secret in namespace: $ns" -ForegroundColor Green
}

if ($DockerToken -ne "") {
    Write-Host "=== 3. Creating Docker Hub secret 'dockerhub' in qa, stage, prod ===" -ForegroundColor Cyan
    foreach ($ns in @("qa", "stage", "prod")) {
        kubectl create secret docker-registry dockerhub `
            --docker-username=$DockerUser `
            --docker-password=$DockerToken `
            -n $ns `
            --dry-run=client -o yaml | kubectl apply -f -
        Write-Host "Configured dockerhub secret in namespace: $ns" -ForegroundColor Green
    }
} else {
    Write-Host "NOTE: No Docker token provided. Run with: .\k8s\setup-k8s.ps1 -DockerUser <user> -DockerToken <token> -DbPassword <pass>" -ForegroundColor Yellow
}

Write-Host "=== 4. Applying Workloads to qa, stage, prod ===" -ForegroundColor Cyan
kubectl apply -f k8s/qa.yaml
kubectl apply -f k8s/stage.yaml
kubectl apply -f k8s/prod.yaml

Write-Host ""
Write-Host "=== Deployments Applied Successfully ===" -ForegroundColor Green
Write-Host "To monitor QA namespace rollout:" -ForegroundColor White
Write-Host "  kubectl rollout status deployment/delivery-tracker -n qa" -ForegroundColor Yellow
Write-Host "  kubectl get pods -n qa" -ForegroundColor Yellow
Write-Host "To test Continuous Deployment Loop:" -ForegroundColor White
Write-Host "  kubectl rollout restart deployment/delivery-tracker -n qa" -ForegroundColor Yellow
Write-Host "  kubectl describe pod <pod-name> -n qa | Select-String 'image id'" -ForegroundColor Yellow
