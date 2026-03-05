# Appwrite Deployment Pipeline Guide

This deployment pipeline supports three deployment strategies: **Docker Compose**, **Kubernetes**, and **Docker Swarm**. Choose the one that best fits your infrastructure.

## Quick Start

### 1. Set Up GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → New repository secret):

```
DOCKER_HUB_USERNAME       # Your Docker Hub username
DOCKER_HUB_PASSWORD       # Your Docker Hub access token
DEPLOY_SSH_KEY            # SSH private key for deployment server
DEPLOY_HOST               # Server hostname/IP (e.g., 192.168.1.100)
DEPLOY_USER               # SSH user (e.g., deploy)
KUBE_CONFIG               # Base64-encoded kubeconfig file (for K8s)
```

### 2. Prepare Environment

Copy and customize the environment file:

```bash
cp .env.prod.example .env.prod
nano .env.prod
# Fill in all required values
```

Generate strong secrets:

```bash
# Generate OPENSSL_KEY_V1 (32+ chars)
openssl rand -base64 32

# Generate EXECUTOR_SECRET (32+ chars)
openssl rand -base64 32
```

## Deployment Strategies

### Option A: Docker Compose (Single Server)

Best for: Small to medium deployments, single-server setup.

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB+ RAM, 50GB+ storage

**Setup:**

```bash
# On your server, clone the repository
git clone https://github.com/appwrite/appwrite.git
cd appwrite

# Copy production compose file
cp docker-compose.prod.yml docker-compose.yml

# Copy environment file
cp .env.prod.example .env.prod
nano .env.prod  # Edit with your values

# Start services
docker compose up -d

# Verify
docker compose ps
curl http://localhost/health
```

**Deployment Flow:**
1. Push code to `main` branch
2. GitHub Actions builds and pushes image to Docker Hub
3. GitHub Actions SSH into server and redeploys:
   ```bash
   docker compose pull
   docker compose down
   docker compose up -d
   ```

**Monitoring:**

```bash
# View logs
docker compose logs -f appwrite

# Check resource usage
docker stats

# Database backup
docker exec appwrite-mariadb mysqldump -u root -p${DB_ROOT_PASS} appwrite > backup.sql

# Redis backup
docker exec appwrite-redis redis-cli BGSAVE
docker cp appwrite-redis:/data/dump.rdb ./dump.rdb
```

### Option B: Kubernetes

Best for: Multi-node, high-availability, auto-scaling requirements.

**Prerequisites:**
- Kubernetes 1.24+ cluster
- kubectl configured
- Storage class available (e.g., fast-ssd)
- 3+ worker nodes recommended

**Setup:**

```bash
# 1. Encode kubeconfig for GitHub secret
base64 ~/.kube/config | tr -d '\n'

# 2. Deploy to cluster
kubectl apply -f k8s/appwrite-deployment.yaml

# 3. Create secrets
kubectl create secret generic appwrite-secrets \
  --from-literal=DB_PASS=$(openssl rand -base64 32) \
  --from-literal=DB_ROOT_PASS=$(openssl rand -base64 32) \
  --from-literal=OPENSSL_KEY_V1=$(openssl rand -base64 32) \
  --from-literal=EXECUTOR_SECRET=$(openssl rand -base64 32) \
  -n appwrite-production

# 4. Configure ingress (example with Nginx Ingress)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: appwrite-ingress
  namespace: appwrite-production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - appwrite.example.com
    secretName: appwrite-tls
  rules:
  - host: appwrite.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: appwrite
            port:
              number: 80
EOF

# 5. Check deployment
kubectl rollout status deployment/appwrite -n appwrite-production
kubectl get pods -n appwrite-production
kubectl get svc -n appwrite-production
```

**Monitoring:**

```bash
# Pod logs
kubectl logs -f deployment/appwrite -n appwrite-production

# Describe pod
kubectl describe pod <pod-name> -n appwrite-production

# Resource usage
kubectl top pods -n appwrite-production

# Port forward for local access
kubectl port-forward svc/appwrite 8080:80 -n appwrite-production

# Database access
kubectl exec -it mariadb-0 -n appwrite-production -- mysql -u appwrite -p

# Scaling
kubectl scale deployment appwrite --replicas=5 -n appwrite-production
```

**Backup & Restore:**

```bash
# Backup database
kubectl exec mariadb-0 -n appwrite-production -- mysqldump \
  -u appwrite -p${DB_PASS} appwrite > backup.sql

# Backup persistent volumes
kubectl exec appwrite-0 -n appwrite-production -- tar czf - /storage/uploads > uploads-backup.tar.gz

# Restore
kubectl cp backup.sql appwrite-0:/tmp/backup.sql -n appwrite-production
kubectl exec appwrite-0 -n appwrite-production -- mysql -u appwrite -p${DB_PASS} appwrite < /tmp/backup.sql
```

### Option C: Docker Swarm

Best for: Medium deployments, docker-native orchestration.

**Prerequisites:**
- Docker 20.10+ on manager nodes
- 3+ manager nodes recommended
- 5+ worker nodes recommended

**Setup:**

```bash
# On manager node, initialize swarm
docker swarm init --advertise-addr <manager-ip>

# Add worker nodes
docker swarm join --token <worker-token> <manager-ip>:2377

# Deploy stack
docker stack deploy -c docker-compose.prod.yml appwrite

# Verify
docker stack ps appwrite
docker service ls
```

**Scaling:**

```bash
docker service scale appwrite_appwrite=5
```

## GitHub Actions Workflows

### 1. Build and Test (`build-and-test.yml`)
- Triggers: Push to main/develop, Pull Requests
- Actions:
  - Build Docker image
  - Run Trivy security scan
  - Run PHPUnit tests
  - Run PHP linting

### 2. Push to Registry (`push-to-registry.yml`)
- Triggers: Push to main, Git tags
- Actions:
  - Build production and development images
  - Push to Docker Hub
  - Tag with version/branch/commit

### 3. Deploy to Kubernetes (`deploy-k8s.yml`)
- Triggers: Push to main, Git tags, Manual workflow dispatch
- Actions:
  - Update deployment image
  - Rollout status
  - Health check

### 4. Deploy with Docker Compose (`deploy-compose.yml`)
- Triggers: Push to main, Git tags
- Actions:
  - SSH into deployment server
  - Pull new images
  - Restart services
  - Health verification

## CI/CD Pipeline Flow

```
Push to GitHub
    ↓
[Build & Test] (runs on every push)
    ├─ Build image
    ├─ Security scan (Trivy)
    ├─ Run tests
    └─ Lint code
    ↓
    If main branch OR tag:
    ↓
[Push to Registry]
    ├─ Build production image
    ├─ Build development image
    └─ Push to Docker Hub
    ↓
[Deploy] (Choose one or enable multiple)
    ├─ Deploy to Kubernetes
    ├─ Deploy with Docker Compose
    └─ Deploy to Docker Swarm
    ↓
[Health Check]
    └─ Verify service is running
```

## Production Best Practices

### Security
- Use strong passwords (32+ chars, mixed case, numbers, symbols)
- Rotate secrets quarterly
- Enable HTTPS only (Traefik handles auto-renewal)
- Use environment variables, never hardcode secrets
- Scan images regularly with Trivy
- Use private Docker Hub repositories

### Scaling
- Set resource limits (CPU, memory)
- Use HPA (Kubernetes) or manual scaling (Compose)
- Load test before production deployment
- Monitor CPU, memory, disk usage

### Monitoring & Logging
- Use centralized logging (ELK, Splunk, DataDog)
- Set up alerts for service failures
- Monitor error rates and latency
- Regular health checks

### Backup & Recovery
- Daily database backups
- Weekly full backups
- Test restore procedures monthly
- Store backups in multiple locations
- Document recovery runbooks

### Database
- Enable MariaDB replication for HA
- Regular OPTIMIZE TABLE
- Monitor slow queries
- Tune InnoDB settings for workload

## Troubleshooting

### Service won't start
```bash
# Docker Compose
docker compose logs appwrite

# Kubernetes
kubectl logs deployment/appwrite -n appwrite-production
kubectl describe pod <pod-name> -n appwrite-production
```

### Out of disk space
```bash
# Docker Compose
docker system prune -a --volumes

# Kubernetes
kubectl get pvc -n appwrite-production
kubectl describe pvc <pvc-name> -n appwrite-production
```

### Database connection errors
```bash
# Test database connection
docker exec appwrite mysql -h mariadb -u appwrite -p${DB_PASS} -e "SELECT 1"

# Check database logs
docker logs appwrite-mariadb
```

### High memory usage
```bash
# Check service stats
docker stats

# Kubernetes
kubectl top pods -n appwrite-production

# Increase limits in docker-compose.prod.yml or Kubernetes manifests
```

## Rollback

### Docker Compose
```bash
# Rollback to previous image
docker compose down
git checkout HEAD~1 docker-compose.yml
docker compose up -d
```

### Kubernetes
```bash
# View rollout history
kubectl rollout history deployment/appwrite -n appwrite-production

# Rollback to previous version
kubectl rollout undo deployment/appwrite -n appwrite-production

# Rollback to specific revision
kubectl rollout undo deployment/appwrite --to-revision=2 -n appwrite-production
```

## Support & Documentation

- Appwrite Docs: https://appwrite.io/docs
- GitHub Issues: https://github.com/appwrite/appwrite/issues
- Discord Community: https://discord.gg/appwrite
- Security: https://appwrite.io/security
