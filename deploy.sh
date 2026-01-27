#!/bin/bash
# Rohrinator Deployment Script
#
# Usage:
#   ./deploy.sh                    # Build and run locally
#   ./deploy.sh --git-url URL      # Clone from git and run
#   ./deploy.sh --update           # Pull latest and restart

set -e

# Configuration
CONTAINER_NAME="rohrinator"
IMAGE_NAME="rohrinator"
PORT="${PORT:-8000}"
GIT_BRANCH="${GIT_BRANCH:-main}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

show_help() {
    cat << EOF
Rohrinator Deployment Script

Usage: ./deploy.sh [OPTIONS]

Options:
    --help              Show this help message
    --git-url URL       Clone from git repository and build
    --git-branch BRANCH Git branch to use (default: main)
    --port PORT         Port to expose (default: 8000)
    --update            Pull latest changes and restart
    --stop              Stop the container
    --logs              Show container logs
    --shell             Open shell in container

Examples:
    # Build from local files and run
    ./deploy.sh

    # Clone from GitHub and run
    ./deploy.sh --git-url https://github.com/username/rohrinator.git

    # Update running container
    ./deploy.sh --update

    # View logs
    ./deploy.sh --logs
EOF
}

build_local() {
    log "Building Docker image from local files..."
    docker build -t ${IMAGE_NAME} .
}

build_from_git() {
    local git_url=$1
    log "Building Docker image from git: ${git_url}"
    docker build -f Dockerfile.gitclone \
        --build-arg GIT_REPO="${git_url}" \
        --build-arg GIT_BRANCH="${GIT_BRANCH}" \
        -t ${IMAGE_NAME} .
}

run_container() {
    # Stop existing container if running
    if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
        log "Stopping existing container..."
        docker stop ${CONTAINER_NAME}
        docker rm ${CONTAINER_NAME}
    elif docker ps -aq -f name=${CONTAINER_NAME} | grep -q .; then
        docker rm ${CONTAINER_NAME}
    fi

    log "Starting container on port ${PORT}..."
    docker run -d \
        --name ${CONTAINER_NAME} \
        --restart unless-stopped \
        -p ${PORT}:8000 \
        -v rohrinator_data:/tmp/rohrinator \
        ${IMAGE_NAME}

    log "Container started!"
    log "Access the UI at: http://localhost:${PORT}"
    log "API docs at: http://localhost:${PORT}/docs"
}

update_container() {
    log "Pulling latest changes and rebuilding..."

    if [ -n "${GIT_URL}" ]; then
        build_from_git "${GIT_URL}"
    else
        git pull origin ${GIT_BRANCH} || true
        build_local
    fi

    run_container
}

# Parse arguments
GIT_URL=""
ACTION="run"

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --git-url)
            GIT_URL="$2"
            shift 2
            ;;
        --git-branch)
            GIT_BRANCH="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --update)
            ACTION="update"
            shift
            ;;
        --stop)
            ACTION="stop"
            shift
            ;;
        --logs)
            ACTION="logs"
            shift
            ;;
        --shell)
            ACTION="shell"
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Execute action
case $ACTION in
    run)
        if [ -n "${GIT_URL}" ]; then
            build_from_git "${GIT_URL}"
        else
            build_local
        fi
        run_container
        ;;
    update)
        update_container
        ;;
    stop)
        log "Stopping container..."
        docker stop ${CONTAINER_NAME} || true
        docker rm ${CONTAINER_NAME} || true
        log "Container stopped"
        ;;
    logs)
        docker logs -f ${CONTAINER_NAME}
        ;;
    shell)
        docker exec -it ${CONTAINER_NAME} /bin/bash
        ;;
esac
