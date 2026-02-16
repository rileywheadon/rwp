# Riley Wheadon's Projects (`rwp`)

## Goals

Complete infrastructure as code setup:

- Provision a new droplet with flexible configuration using GHA.
- Immediately deploy all services after provisioning.
- Support for easy re-scaling of droplet (with downtime).
- Support for easy teardown of droplet.

Observability stack (deployed as a service).

Complete test suite for all deployed services.

Dependency management:

- All services use the same dependency versions (single version policy).
- Use Renovate GitHub bot for dependency updates.

Periodic, automateds backups to ensure data safety.

## Architecture

- All applications are deployed onto a single DO droplet.
- All applications run their database directly on the droplet.
- All applications use my personal DockerHub container registry.

### Monorepo Design

1. Easy reuse of shared dependencies and libraries.
2. No need for shared CI setup across many repositories.
3. No overhead to create new projects.
4. No need to handle versioning of multiple projects.

### Continuous Integration

For each service, we will have a GitHub action that does the following:

- Pulls the Tailwind CSS executable
- Build the Tailwind CSS file
- Apply database migrations
- Run tests using the test container
- Build Docker container(s)
- Push Docker container(s) to my DockerHub container registry
- SSH into the droplet
- Pull the Docker container(s) from the container registry

We will use path-based workflows to only build the services that were modified.

## Services

### Test Service

- Flask
- PostgreSQL
- SQLAlchemy
- Alembic
- HTMX
- AlpineJS
- TailwindCSS

### Observability Service

Pings the other services in the monorepo to get their health status.

Also keeps track of the four golden signals:

- Latency
- Traffic
- Errors
- Saturation

### Other Services

- My [personal website](https://rwheadon.dev)
- The UBC USS [course map](https://map.ubcuss.ca) and [main site](https://ubcuss.ca)
- An updated version of [Poll](https://github.com/rileywheadon/poll-app)
- A copy of the [FFA framework website](https://github.com/rileywheadon/ffa-website)
