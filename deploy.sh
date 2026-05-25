#!/bin/bash

set -e

export PATH="/usr/local/bin:$PATH"

# =============================================================================
# VARIABLES & DEFAULT VALUES
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="dic"
GIT_REPO_URL=""
PROJECT_DIR=""
SERVER_HOST=""
DB_HOST="db"
DB_PORT="5432"
DB_NAME="dic_db"
DB_USER="dic_user"
DB_PASSWORD=""
DB_SEED="false"
SEED_DATA=""
FRONTEND_PORT="5173"
BACKEND_PORT="8000"
COMPOSE_FILE="docker-compose.yml"
LOG_FILE="${SCRIPT_DIR}/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FUNCTIONS
# =============================================================================

log() {
    local message="$1"
    local color="${2:-$NC}"
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    log "$1" "$BLUE"
}

log_success() {
    log "$1" "$GREEN"
}

log_warning() {
    log "$1" "$YELLOW"
}

log_error() {
    log "$1" "$RED"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    --repo URL              Git repository URL (required)
    --project-dir PATH      Project directory path (default: ~/projects/<PROJECT_NAME>)
    --db-host HOST          Database host (default: localhost)
    --db-port PORT          Database port (default: 5432)
    --db-name NAME         Database name (default: dic_db)
    --db-user USER          Database user (default: dic_user)
    --db-password PASS      Database password (required)
    --seed                 Enable seed data generation
    --seed-data DATA       Seed data (json string or path to file)
    --frontend-port PORT    Frontend port (default: 5173)
    --backend-port PORT     Backend port (default: 8000)
    -h, --help             Show this help message

ENVIRONMENT VARIABLES:
    GIT_REPO_URL
    DB_PASSWORD
    DB_HOST, DB_PORT, DB_NAME, DB_USER
    SEED_DATA

ARGUMENTS HAVE HIGHER PRIORITY THAN ENVIRONMENT VARIABLES

EOF
    exit 0
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if [ "$(id -u)" = "0" ]; then
        log_info "Running as root, configuring sudo..."
        echo 'root ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/nopasswd
        chmod 440 /etc/sudoers.d/nopasswd
    fi
    
    local missing_deps=()
    
    for cmd in curl git; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "Missing dependencies: ${missing_deps[*]}"
        log_info "Installing dependencies..."
        
        if [ -f /etc/os-release ]; then
            source /etc/os-release
            case "$ID" in
                ubuntu|debian)
                    sudo apt-get update
                    for dep in "${missing_deps[@]}"; do
                        case "$dep" in
                            curl)
                                sudo apt-get install -y curl
                                ;;
                            docker)
                                curl -fsSL https://get.docker.com | sh
                                sudo usermod -aG docker "$USER"
                                ;;
                            git)
                                sudo apt-get install -y git
                                ;;
                        esac
                    done
                    ;;
                fedora|rhel|centos|almalinux)
                    for dep in "${missing_deps[@]}"; do
                        case "$dep" in
                            docker)
                                sudo dnf remove podman buildah -y
                                sudo dnf install -y dnf-utils
                                sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                                sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
                                sudo systemctl start docker
                                sudo systemctl enable docker
                                ;;
                            *)
                                sudo dnf install -y "$dep"
                                ;;
                        esac
                    done
                    ;;
                arch)
                    sudo pacman -Sy --noconfirm "${missing_deps[@]}"
                    ;;
            esac
        fi
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        if ! docker-compose version &> /dev/null 2>&1; then
            log_info "Installing docker-compose..."
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            log_success "docker-compose installed"
        fi
    fi
    
    if command -v docker-compose &> /dev/null; then
        log_info "Creating docker-compose alias (v2 style)..."
        if [ -f /etc/bash.bashrc ]; then
            echo "alias docker-compose='docker-compose'" >> /etc/bash.bashrc
        fi
        if [ -f /etc/profile.d ]; then
            echo "alias docker-compose='docker-compose'" > /etc/profile.d/docker-compose-alias.sh
            chmod +x /etc/profile.d/docker-compose-alias.sh
        fi
    fi
    
    if command -v docker &> /dev/null; then
        if ! docker info &> /dev/null; then
            log_info "Starting Docker..."
            sudo systemctl start docker 2>/dev/null || sudo service docker start 2>/dev/null || log_warning "Could not start docker automatically"
        fi
    fi
    
    log_success "All dependencies satisfied"
}

create_project_dir() {
    log_info "Creating project directory..."
    
    PROJECT_DIR="${PROJECT_DIR:-$HOME/projects/$PROJECT_NAME}"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "Directory $PROJECT_DIR already exists"
    else
        mkdir -p "$(dirname "$PROJECT_DIR")"
        mkdir -p "$PROJECT_DIR"
        log_success "Created directory: $PROJECT_DIR"
    fi
}

clone_or_update_repo() {
    log_info "Cloning/updating repository..."
    
    if [ -z "$GIT_REPO_URL" ]; then
        log_error "Git repository URL is required. Use --repo or set GIT_REPO_URL"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    
    if [ -d ".git" ]; then
        log_info "Repository already exists, pulling latest changes..."
        git fetch origin
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || log_warning "Could not pull latest changes"
    else
        log_info "Cloning repository..."
        git clone "$GIT_REPO_URL" .
    fi
    
    log_success "Repository ready"
}

install_nodejs() {
    if ! command -v node &> /dev/null; then
        log_info "Installing Node.js..."
        if command -v apt-get &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif command -v yum &> /dev/null; then
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
        fi
        log_success "Node.js installed"
    fi
}

build_frontends() {
    log_info "Building frontends..."
    
    cd "$PROJECT_DIR"
    
    install_nodejs
    
    rm -rf dist 2>/dev/null || sudo rm -rf dist
    mkdir -p dist/dic dist/ucrp
    chmod 777 dist
    
    if [ -d "dic-frontend" ]; then
        log_info "Building dic-frontend..."
        cd dic-frontend
        npm install
        npm run build
        cd ..
        if [ -d "dic-frontend/dist" ]; then
            cp -r dic-frontend/dist/* dist/dic/
        fi
    fi
    
    if [ -d "plasma-optimizer" ]; then
        log_info "Building plasma-optimizer..."
        cd plasma-optimizer
        npm install
        npm run build
        cd ..
        if [ -d "plasma-optimizer/dist" ]; then
            cp -r plasma-optimizer/dist/* dist/ucrp/
        fi
    fi
    
    log_success "Frontends built and copied to dist"
}

stop_containers() {
    log_info "Stopping existing containers..."
    
    cd "$PROJECT_DIR"
    
    if [ -f "$COMPOSE_FILE" ]; then
        # Check if containers are running
        if docker-compose -f "$COMPOSE_FILE" ps &> /dev/null; then
            log_info "Stopping containers..."
            docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
            
            # Wait for containers to stop
            local max_attempts=30
            local attempt=0
            while [ $attempt -lt $max_attempts ]; do
                if ! docker-compose -f "$COMPOSE_FILE" ps &> /dev/null; then
                    break
                fi
                sleep 1
                attempt=$((attempt + 1))
            done
            
            log_success "Containers stopped"
        else
            log_info "No running containers found"
        fi
    else
        # Try to stop by project name
        local containers=$(docker ps -q --filter "name=$PROJECT_NAME")
        if [ -n "$containers" ]; then
            docker stop $containers 2>/dev/null || true
            docker rm $containers 2>/dev/null || true
        fi
    fi
}

start_containers() {
    log_info "Starting containers..."
    
    cd "$PROJECT_DIR"
    
    # Set environment variables for docker-compose
    export POSTGRES_HOST=$DB_HOST
    export POSTGRES_PORT=$DB_PORT
    export POSTGRES_DB=$DB_NAME
    export POSTGRES_USER=$DB_USER
    export POSTGRES_PASSWORD=$DB_PASSWORD
    
    if [ -f ".env" ]; then
        log_info "Using existing .env file"
    else
        log_info "Creating .env file..."
        log_info "Generating Django secret key..."
        DJANGO_SECRET_KEY=$(python3 -c "import secrets; print('django-insecure-' + ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)') for _ in range(50)))")
        
        cat > .env << EOF
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
SEED_ENABLE=$DB_SEED
SEED_DATA=$SEED_DATA
FRONTEND_PORT=$FRONTEND_PORT
BACKEND_PORT=$BACKEND_PORT
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=True
ALLOWED_HOSTS=$SERVER_HOST,localhost,127.0.0.1,backend
EOF
    fi
    
    # Build and start containers
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Containers started"
}

healthcheck() {
    log_info "Waiting for services to be ready..."
    
    local max_attempts=60
    local attempt=0
    local services=("backend" "frontend" "postgres")
    
    for service in "${services[@]}"; do
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            case "$service" in
                backend)
                    if curl -sf "http://localhost:${BACKEND_PORT}/api/" &>/dev/null; then
                        log_success "Backend is ready"
                        break
                    fi
                    ;;
                frontend)
                    if curl -sf "http://localhost:${FRONTEND_PORT}" &>/dev/null; then
                        log_success "Frontend is ready"
                        break
                    fi
                    ;;
                postgres)
                    if docker exec "${PROJECT_NAME}_postgres" pg_isready -U "$DB_USER" &>/dev/null 2>&1; then
                        log_success "Postgres is ready"
                        break
                    fi
                    ;;
            esac
            
            sleep 2
            attempt=$((attempt + 1))
            
            if [ $((attempt % 10)) -eq 0 ]; then
                log_warning "Waiting for $service... ($attempt/$max_attempts)"
            fi
        done
        
        if [ $attempt -ge $max_attempts ]; then
            log_error "$service failed to start"
            
            # Show logs for debugging
            docker-compose -f "$COMPOSE_FILE" logs "$service" | tail -50
            return 1
        fi
    done
    
    log_success "All services are ready"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local echo_progress=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repo)
                GIT_REPO_URL="$2"
                shift 2
                ;;
            --project-dir)
                PROJECT_DIR="$2"
                shift 2
                ;;
            --db-host)
                DB_HOST="$2"
                shift 2
                ;;
            --db-port)
                DB_PORT="$2"
                shift 2
                ;;
            --db-name)
                DB_NAME="$2"
                shift 2
                ;;
            --db-user)
                DB_USER="$2"
                shift 2
                ;;
            --db-password)
                DB_PASSWORD="$2"
                shift 2
                ;;
            --seed)
                DB_SEED="true"
                shift
                ;;
            --seed-data)
                SEED_DATA="$2"
                shift 2
                ;;
            --frontend-port)
                FRONTEND_PORT="$2"
                shift 2
                ;;
            --backend-port)
                BACKEND_PORT="$2"
                shift 2
                ;;
            --server-host)
                SERVER_HOST="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
    
    # Validate required args
    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD is required. Use --db-password or set DB_PASSWORD"
        exit 1
    fi
    
    # Initialize log
    echo "" > "$LOG_FILE"
    log_info "========================================="
    log_info "Starting deployment..."
    log_info "========================================="
    
    # Execute steps
    check_dependencies
    create_project_dir
    clone_or_update_repo
    build_frontends
    stop_containers
    start_containers
    
    log_success "========================================="
    log_success "Deployment completed successfully!"
    log_info "========================================="
    log_info "Logs saved to: $LOG_FILE"
}

main "$@"