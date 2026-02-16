# Bootstrap Digital Ocean Droplet - Implementation Plan

## Overview
Create a GitHub Actions workflow that provisions a Digital Ocean droplet with Docker/Docker Compose installed, and sets up Traefik as a reverse proxy with automatic HTTPS for managing multiple services in a monorepo using a single docker-compose.yaml file.

## Design Decisions

- **Reverse Proxy**: Traefik (Docker-native, automatic service discovery via labels, built-in Let's Encrypt)
- **Service Orchestration**: Single `docker-compose.yaml` file in `/deploy` directory for all services
- **Initial Services**: Traefik + whoami test service
- **Traefik Dashboard**: Enabled with basic authentication at `traefik.rwheadon.dev` (random credentials generated and returned by workflow)
- **Whoami Test Service**: Accessible at `whoami.rwheadon.dev`
- **Droplet Name**: Fixed name `rwp-live`
- **SSL/TLS**: Automatic HTTPS with Let's Encrypt production environment (email from `EMAIL` secret)
- **Existing Droplet**: Fail the workflow if droplet already exists
- **IP Management**: Output IP and store as repository variable named `DROPLET_IP`
- **Cloud-init Completion**: Wait using `cloud-init status --wait` via SSH
- **Firewall**: Created and attached to droplet by name (allow ports 80, 443, 22)
- **Docker Registry**: Pre-configure DockerHub authentication using `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
- **Docker Compose Version**: Latest Docker Compose v2 (plugin)
- **Repository Access**: Cloud-init clones the public repository to access deployment files
- **Deployment**: Docker-compose stack deployed via SSH after cloud-init completes

## Components to Implement

### 1. GitHub Actions Workflow (`.github/workflows/bootstrap-droplet.yaml`)
- **Trigger**: Manual workflow dispatch with inputs
- **Inputs**:
  - `region`: Digital Ocean region (e.g., `nyc3`, `sfo3`, `sgp1`)
  - `size`: Droplet size slug (e.g., `s-1vcpu-1gb`, `s-2vcpu-2gb`)
  - `image`: OS image slug (e.g., `ubuntu-22-04-x64`)
- **Secrets Required**:
  - `DIGITALOCEAN_ACCESS_TOKEN`: DO API access token
  - `DIGITALOCEAN_SSH_KEY_ID`: SSH key ID for droplet access
  - `EMAIL`: Email address for Let's Encrypt certificates
  - `DOCKERHUB_USERNAME`: DockerHub username
  - `DOCKERHUB_TOKEN`: DockerHub access token
  - `TRAEFIK_USERNAME`: Username for authentication to Traefik dashboard
  - `TRAEFIK_PASSWORD`: Password for authentication to Traefik dashboard
- **Steps**:
  1. Install `doctl` (Digital Ocean CLI)
  2. Authenticate with DO using access token
  3. Check if droplet `rwp-live` already exists (fail if it does)
  4. Create firewall for droplet (allow ports 22, 80, 443)
  5. Create droplet with cloud-init user data and attach firewall
  6. Wait for droplet to be accessible via SSH
  7. Wait for cloud-init to complete using `cloud-init status --wait`
  8. Deploy docker-compose stack (Traefik + whoami) via SSH
  9. Output droplet IP address
  10. Store IP address in repository variable as `DROPLET_IP`

### 2. Cloud-Init Configuration (`deploy/cloud-init.yaml`)
- Update system packages
- Install Docker
- Install Docker Compose v2 plugin
- Configure Docker to start on boot
- Add default user to docker group
- Log in to DockerHub using `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
- Clone the public repository to `/opt/rwp`
- Create directory structure for Docker volumes and configs
- Set up Let's Encrypt certificate storage directory

### 3. Docker Compose Configuration (`deploy/docker-compose.yaml`)
- **Traefik Service**:
  - Enable Docker provider (reads labels from containers)
  - Enable Let's Encrypt (ACME) with email from environment
  - Expose ports 80 and 443
  - Enable dashboard with basic authentication at `traefik.rwheadon.dev`
  - Mount Docker socket for service discovery
  - Persistent volume for Let's Encrypt certificates
- **Whoami Service** (test service):
  - Simple HTTP service that returns container info
  - Traefik labels for routing to `whoami.rwheadon.dev`
  - Automatic HTTPS via Traefik

### 4. Traefik Configuration
- **Static Configuration**: Via command-line arguments in docker-compose.yaml (entrypoints, providers, ACME)
- **Dynamic Configuration**: Via Docker labels on services in docker-compose.yaml

## Proposed Implementation Order

1. Create `deploy/cloud-init.yaml` - Complete droplet setup (Docker, Docker Compose, repo clone)
2. Create `deploy/docker-compose.yaml` - Traefik + whoami service configuration
3. Create `.github/workflows/bootstrap-droplet.yaml` - Main workflow
4. Test with a small droplet
5. Document usage in README.md or docs/