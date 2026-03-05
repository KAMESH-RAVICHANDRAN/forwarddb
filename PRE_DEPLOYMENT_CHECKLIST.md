# Appwrite Deployment Pipeline - Checklist

## Pre-Deployment Tasks

### 1. Local Setup
- [ ] Clone repository
- [ ] Review all new files created:
  - [ ] `.github/workflows/build-and-test.yml`
  - [ ] `.github/workflows/push-to-registry.yml`
  - [ ] `.github/workflows/deploy-k8s.yml`
  - [ ] `.github/workflows/deploy-compose.yml`
  - [ ] `docker-compose.prod.yml`
  - [ ] `k8s/appwrite-deployment.yaml`
  - [ ] `DEPLOYMENT.md`
  - [ ] `SECURITY.prod.md`
  - [ ] `DEPLOY_SETUP.sh`
  - [ ] `PIPELINE_SUMMARY.md`
  - [ ] `.env.prod.example`

### 2. Configuration
- [ ] Copy `.env.prod.example` to `.env.prod`
- [ ] Generate OPENSSL_KEY_V1: `openssl rand -base64 32`
- [ ] Generate EXECUTOR_SECRET: `openssl rand -base64 32`
- [ ] Fill in all environment variables in `.env.prod`:
  - [ ] `APP_DOMAIN`
  - [ ] `CONSOLE_DOMAIN`
  - [ ] Database credentials
  - [ ] SMTP settings
  - [ ] Storage settings
  - [ ] Docker Hub credentials
  - [ ] S3 credentials (if using)
- [ ] Verify `.env.prod` is in `.gitignore` (never commit)
- [ ] Set file permissions: `chmod 600 .env.prod`

### 3. GitHub Setup
- [ ] Go to repository Settings → Secrets and variables → Actions
- [ ] Add required secrets:
  - [ ] `DOCKER_HUB_USERNAME`
  - [ ] `DOCKER_HUB_PASSWORD`
  - [ ] `DEPLOY_SSH_KEY` (for Compose deployment)
  - [ ] `DEPLOY_HOST` (for Compose deployment)
  - [ ] `DEPLOY_USER` (for Compose deployment)
  - [ ] `KUBE_CONFIG` (for Kubernetes deployment, base64-encoded)
- [ ] Verify no secrets are hardcoded in workflows
- [ ] Enable required permissions for workflows:
  - [ ] Contents: read
  - [ ] Packages: write
  - [ ] Actions: read

### 4. Infrastructure Setup (Choose One)

#### Option A: Docker Compose (Single Server)
- [ ] Provision server with:
  - [ ] Docker Engine 20.10+
  - [ ] Docker Compose 2.0+
  - [ ] 8GB+ RAM
  - [ ] 50GB+ storage
  - [ ] SSH access for deployment user
- [ ] Create deployment user: `useradd deploy`
- [ ] Set up SSH key authentication
- [ ] Create deployment directory: `/opt/appwrite`
- [ ] Test SSH access from GitHub Actions

#### Option B: Kubernetes
- [ ] Provision cluster with 3+ nodes
- [ ] Install kubectl
- [ ] Verify cluster connectivity: `kubectl cluster-info`
- [ ] Create namespaces:
  - [ ] `kubectl create namespace appwrite-production`
  - [ ] `kubectl create namespace appwrite-staging`
- [ ] Configure storage class for fast-ssd
- [ ] Set up ingress controller (Nginx recommended)
- [ ] Generate kubeconfig and base64 encode:
  - [ ] `base64 ~/.kube/config | tr -d '\n'`
- [ ] Create certificate issuer (Let's Encrypt)
- [ ] Test deployment connection: `kubectl auth can-i get pods`

#### Option C: Docker Swarm
- [ ] Provision 3+ manager nodes
- [ ] Provision 5+ worker nodes
- [ ] Initialize swarm: `docker swarm init --advertise-addr <IP>`
- [ ] Join worker nodes to swarm
- [ ] Set up volume driver (NFS recommended)
- [ ] Verify swarm status: `docker node ls`

### 5. SSL/TLS Certificate Setup
- [ ] For Kubernetes: Install cert-manager
  - [ ] `helm repo add jetstack https://charts.jetstack.io`
  - [ ] `helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace`
  - [ ] Create Let's Encrypt ClusterIssuer
- [ ] For Docker Compose: Traefik auto-renewal enabled (built-in)
- [ ] Test certificate provisioning
- [ ] Verify HTTPS works: `curl https://your-domain/health`

### 6. Database Setup
- [ ] Provision database server (or use managed service)
- [ ] Create database: `CREATE DATABASE appwrite;`
- [ ] Create database user with appropriate permissions
- [ ] Backup initial state
- [ ] Test connection from app servers
- [ ] Enable automated backups (daily)
- [ ] Test backup restoration

### 7. Storage Setup
- [ ] If using local storage:
  - [ ] Create directories: `/storage/{uploads,cache,config,functions,sites,builds}`
  - [ ] Set permissions: `chmod 755`
  - [ ] Mount on separate disk (recommended)
- [ ] If using S3:
  - [ ] Create S3 bucket
  - [ ] Create IAM user with bucket access
  - [ ] Enable versioning
  - [ ] Enable server-side encryption
  - [ ] Test write/read permissions

### 8. Monitoring Setup
- [ ] Set up logging system:
  - [ ] [ ] Prometheus + Grafana, or
  - [ ] [ ] ELK Stack, or
  - [ ] [ ] Datadog, or
  - [ ] [ ] New Relic
- [ ] Configure alerts for:
  - [ ] Service down
  - [ ] High CPU/Memory
  - [ ] Database errors
  - [ ] Disk full
- [ ] Create dashboards for:
  - [ ] Service health
  - [ ] Performance metrics
  - [ ] Error rates
  - [ ] Resource usage

### 9. Backup & Disaster Recovery
- [ ] Set up automated database backups (daily)
- [ ] Set up automated storage backups (weekly)
- [ ] Test restore procedures
- [ ] Document recovery runbook
- [ ] Verify backups stored off-site
- [ ] Schedule quarterly DR drill

### 10. Security Hardening
- [ ] Review SECURITY.prod.md checklist
- [ ] Set up firewall rules
- [ ] Enable SSH key-based auth only
- [ ] Disable root login
- [ ] Set up fail2ban (if not managed)
- [ ] Enable audit logging
- [ ] Rotate secrets before first deploy
- [ ] Run initial Trivy scan

## Deployment Tasks

### 1. Initial Deployment

#### Docker Compose
- [ ] SSH into server
- [ ] Clone repository: `git clone <repo> /opt/appwrite && cd /opt/appwrite`
- [ ] Copy production compose: `cp docker-compose.prod.yml docker-compose.yml`
- [ ] Copy environment: `cp .env.prod.example .env.prod`
- [ ] Edit .env.prod with production values
- [ ] Set permissions: `chmod 600 .env.prod`
- [ ] Start services: `docker compose up -d`
- [ ] Wait 30 seconds for services to initialize
- [ ] Verify health: `curl http://localhost/health`
- [ ] Check container logs: `docker compose logs appwrite`

#### Kubernetes
- [ ] Apply manifests: `kubectl apply -f k8s/appwrite-deployment.yaml`
- [ ] Create secrets: `kubectl create secret generic appwrite-secrets ... -n appwrite-production`
- [ ] Wait for rollout: `kubectl rollout status deployment/appwrite -n appwrite-production`
- [ ] Verify pods: `kubectl get pods -n appwrite-production`
- [ ] Test health: `kubectl port-forward svc/appwrite 8080:80 -n appwrite-production`
- [ ] Access: `curl http://localhost:8080/health`

### 2. Verify Deployment
- [ ] Check service is running
- [ ] Verify health endpoint responds: `/health`
- [ ] Check database connectivity
- [ ] Verify Redis connectivity
- [ ] Test API endpoints
- [ ] Check console UI loads
- [ ] Review container logs for errors
- [ ] Monitor resource usage (CPU, memory)
- [ ] Verify SSL/TLS certificate
- [ ] Test HTTPS redirect (HTTP → HTTPS)

### 3. Post-Deployment
- [ ] Create first admin account
- [ ] Configure console domain
- [ ] Set up SMTP test (send verification email)
- [ ] Test file upload functionality
- [ ] Review security headers
- [ ] Run initial backup
- [ ] Document any issues found
- [ ] Notify team of successful deployment
- [ ] Create runbook for on-call team

## Ongoing Maintenance

### Weekly
- [ ] Review error logs
- [ ] Check disk usage
- [ ] Monitor performance metrics
- [ ] Review security alerts
- [ ] Check for failed backups

### Monthly
- [ ] Apply security patches
- [ ] Review resource utilization
- [ ] Update monitoring thresholds
- [ ] Verify backup restoration works
- [ ] Rotate non-critical secrets

### Quarterly
- [ ] Full security audit
- [ ] Performance tuning review
- [ ] Disaster recovery drill
- [ ] Update capacity planning
- [ ] Rotate critical secrets
- [ ] Update security documentation

### Annually
- [ ] Penetration testing
- [ ] Complete system audit
- [ ] Update architecture documentation
- [ ] Review and update security policies

## Troubleshooting Checklist

If deployment fails, check:
- [ ] GitHub Actions logs (Actions tab)
- [ ] Secrets are correctly configured
- [ ] Environment variables are all set
- [ ] Docker Hub credentials are valid
- [ ] SSH key has correct permissions (600)
- [ ] SSH key is added to deployment server
- [ ] Kubernetes API is accessible
- [ ] Database is running and accessible
- [ ] Storage paths exist and have correct permissions
- [ ] Network connectivity between services
- [ ] DNS resolution working
- [ ] SSL certificates are valid

## Rollback Plan

If deployment issues occur:
1. [ ] Stop new deployment
2. [ ] Revert to previous image tag
3. [ ] Verify previous version deployed
4. [ ] Post-mortem: document what went wrong
5. [ ] Fix issue
6. [ ] Test in staging
7. [ ] Redeploy to production

## Sign-Off

- [ ] All infrastructure ready
- [ ] All secrets configured
- [ ] All documentation reviewed
- [ ] Backup procedures tested
- [ ] Team trained
- [ ] Ready for first deployment

**Deployment Date:** _______________
**Deployed By:** _______________
**Approved By:** _______________
**Notes:** ________________________________________________________________

---

For detailed instructions, see DEPLOYMENT.md
For security review, see SECURITY.prod.md
