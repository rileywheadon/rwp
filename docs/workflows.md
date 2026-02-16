# GitHub Actions 

This file documents the repository's CI/CD workflows located under `.github/workflows/`.

## Bootstrap Digital Ocean Droplet (`bootstrap.yaml`)

- Path: `.github/workflows/bootstrap.yaml`
- Trigger: manual (`workflow_dispatch`) with three inputs: `region`, `size`, `image`.
- Purpose: create a new droplet named `rwp-live` and provision using `deploy/cloud-init.yaml`.

### Technical Details

- Uses `digitalocean/action-doctl@v2` to call the DigitalOcean API.
- Expects these secrets and environment variables to exist:
  - `secrets.DIGITALOCEAN_ACCESS_TOKEN` (required)
  - `secrets.DIGITALOCEAN_SSH_PRIVATE_KEY` (private key for initial SSH access)
  - `secrets.DIGITALOCEAN_SSH_KEY_ID` (public key id to attach to droplet)
  - `secrets.DOCKERHUB_TOKEN` (injected into cloud-init)
  - environment variables: `DROPLET_NAME=rwp-live`, `DOCKERHUB_USERNAME`, `EMAIL`
- Workflow actions:
  1. Checkout repo.
  2. Install `doctl` and prepare SSH key.
  3. Abort if a droplet named `rwp-live` already exists.
  4. Templatize `deploy/cloud-init.yaml` (substituting Docker Hub creds and metadata) to `/tmp/cloud-init.yaml`.
  5. Create droplet with `--user-data-file` and wait for it.
  6. Poll SSH until available and wait for `cloud-init` to finish.
  7. Emit a step summary with the droplet IP and inputs.

### Notes

- Fails early if a droplet with the same name exists.
- SSH availability is polled (30 attempts × 10s); failure means manual inspection.
- `cloud-init` failures must be diagnosed on the droplet (logs: `/var/log/cloud-init.log`).
- The cloud-init templating injects secrets into the instance — ensure secrets are rotated and access is limited.

## Deploy to Droplet (`deploy.yaml`)

- Path: `.github/workflows/deploy.yaml`
- Trigger: `push` on `main` branch.
- Purpose: pull the latest images and restart the `docker compose` stack on the existing `rwp-live` droplet.

### Technical Details

- Uses `digitalocean/action-doctl@v2` to query droplet public IP by name.
- Expects these secrets and environment variables to exist:
  - `secrets.DIGITALOCEAN_ACCESS_TOKEN`
  - `secrets.DIGITALOCEAN_SSH_PRIVATE_KEY`
  - environment variables: `DROPLET_NAME=rwp-live`
- Workflow actions:
  1. Checkout repo.
  2. Install `doctl` and prepare SSH key.
  3. Resolve droplet public IP via `doctl compute droplet get`.
  4. SSH into `root@<droplet-ip>` and run in `/opt/rwp/deploy`: 
     1. `docker compose pull`
     2. `docker compose up -d`
     3. `docker compose ps`

### Notes

- Fails if droplet cannot be found or has no public IPv4.
- Assumes that deployment artifacts (compose files, credentials) are present under `/opt/rwp/deploy`.
- `docker compose` commands run as root; ensure the `deploy` directory is the canonical runtime location.