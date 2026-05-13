#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_SCRIPT="deploy.sh"
LOG_FILE="${SCRIPT_DIR}/remote-deploy.log"

SSH_HOST=""
SSH_PORT="22"
SSH_USER="root"
SSH_KEY=""
SSH_PASSWORD=""

GIT_REPO_URL=""
PROJECT_DIR=""
DB_PASSWORD=""
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="dic_db"
DB_USER="dic_user"
SEED_ENABLE="false"
SEED_DATA=""
FRONTEND_PORT="5173"
BACKEND_PORT="8000"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local message="$1"
    local color="${2:-$NC}"
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "$LOG_FILE"
}

log_info() { log "$1" "$BLUE"; }
log_success() { log "$1" "$GREEN"; }
log_warning() { log "$1" "$YELLOW"; }
log_error() { log "$1" "$RED"; }

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

SSH OPTIONS:
    --host HOST          SSH host (required)
    --port PORT          SSH port (default: 22)
    --user USER          SSH user (default: root)
    --key FILE           SSH private key path
    --password PASS      SSH password (if no key)

DEPLOY OPTIONS:
    --repo URL           Git repository URL (required)
    --project-dir PATH   Project directory on server
    --db-password PASS   Database password (required)
    --db-host HOST       Database host (default: localhost)
    --db-port PORT       Database port (default: 5432)
    --db-name NAME       Database name (default: dic_db)
    --db-user USER       Database user (default: dic_user)
    --seed               Enable seed data
    --seed-data DATA     Seed data (json string or path)
    --frontend-port PORT Frontend port (default: 5173)
    --backend-port PORT  Backend port (default: 8000)
    -h, --help          Show this help message

ENVIRONMENT VARIABLES:
    SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY, SSH_PASSWORD
    GIT_REPO_URL, DB_PASSWORD

EXAMPLES:
    $0 --host 192.168.1.100 --key ~/.ssh/id_rsa --repo https://github.com/user/repo --db-password mypass
    $0 --host myserver.com --user admin --password secret --repo https://github.com/user/repo --db-password mypass

EOF
    exit 0
}

check_dependencies() {
    local missing=()
    for cmd in ssh scp; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        exit 1
    fi
}

build_ssh_cmd() {
    local ssh_cmd="ssh"
    
    if [ -n "$SSH_PORT" ] && [ "$SSH_PORT" != "22" ]; then
        ssh_cmd="$ssh_cmd -p $SSH_PORT"
    fi
    
    if [ -n "$SSH_KEY" ]; then
        if [ -f "$SSH_KEY" ]; then
            ssh_cmd="$ssh_cmd -i $SSH_KEY"
        else
            log_warning "SSH key not found: $SSH_KEY"
        fi
    fi
    
    if [ -n "$SSH_PASSWORD" ]; then
        ssh_cmd="$ssh_cmd -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    else
        ssh_cmd="$ssh_cmd -o StrictHostKeyChecking=accept-new"
    fi
    
    echo "$ssh_cmd"
}

build_scp_cmd() {
    local scp_cmd="scp"
    
    if [ -n "$SSH_PORT" ] && [ "$SSH_PORT" != "22" ]; then
        scp_cmd="$scp_cmd -P $SSH_PORT"
    fi
    
    if [ -n "$SSH_KEY" ]; then
        if [ -f "$SSH_KEY" ]; then
            scp_cmd="$scp_cmd -i $SSH_KEY"
        fi
    fi
    
    echo "$scp_cmd"
}

run_remote() {
    local ssh_cmd
    ssh_cmd=$(build_ssh_cmd)
    $ssh_cmd -tt "${SSH_USER}@${SSH_HOST}" "$@"
}

upload_file() {
    local scp_cmd
    scp_cmd=$(build_scp_cmd)
    $scp_cmd "$1" "${SSH_USER}@${SSH_HOST}:$2"
}

deploy() {
    log_info "========================================="
    log_info "Starting remote deployment..."
    log_info "========================================="
    
    if [ -z "$SSH_HOST" ]; then
        log_error "SSH host is required. Use --host or set SSH_HOST"
        exit 1
    fi
    
    if [ -z "$GIT_REPO_URL" ]; then
        log_error "Git repository URL is required. Use --repo or set GIT_REPO_URL"
        exit 1
    fi
    
    if [ -z "$DB_PASSWORD" ]; then
        log_error "Database password is required. Use --db-password or set DB_PASSWORD"
        exit 1
    fi
    
    log_info "Connecting to ${SSH_USER}@${SSH_HOST}..."
    
    if ! run_remote "echo 'SSH connection OK'" &>/dev/null; then
        log_error "Failed to connect to SSH host"
        exit 1
    fi
    
    log_success "SSH connection established"
    
    log_info "Uploading deploy script..."
    upload_file "${SCRIPT_DIR}/${DEPLOY_SCRIPT}" "/tmp/${DEPLOY_SCRIPT}"
    
    log_info "Running deploy script on remote server..."
    
    local deploy_cmd="bash /tmp/${DEPLOY_SCRIPT}"
    deploy_cmd="$deploy_cmd --repo ${GIT_REPO_URL}"
    deploy_cmd="$deploy_cmd --db-password ${DB_PASSWORD}"
    deploy_cmd="$deploy_cmd --server-host ${SSH_HOST}"
    
    if [ -n "$PROJECT_DIR" ]; then
        deploy_cmd="$deploy_cmd --project-dir ${PROJECT_DIR}"
    fi
    
    if [ -n "$DB_HOST" ]; then
        deploy_cmd="$deploy_cmd --db-host ${DB_HOST}"
    fi
    
    if [ -n "$DB_PORT" ]; then
        deploy_cmd="$deploy_cmd --db-port ${DB_PORT}"
    fi
    
    if [ -n "$DB_NAME" ]; then
        deploy_cmd="$deploy_cmd --db-name ${DB_NAME}"
    fi
    
    if [ -n "$DB_USER" ]; then
        deploy_cmd="$deploy_cmd --db-user ${DB_USER}"
    fi
    
    if [ "$SEED_ENABLE" = "true" ]; then
        deploy_cmd="$deploy_cmd --seed"
    fi
    
    if [ -n "$SEED_DATA" ]; then
        deploy_cmd="$deploy_cmd --seed-data ${SEED_DATA}"
    fi
    
    if [ -n "$FRONTEND_PORT" ]; then
        deploy_cmd="$deploy_cmd --frontend-port ${FRONTEND_PORT}"
    fi
    
    if [ -n "$BACKEND_PORT" ]; then
        deploy_cmd="$deploy_cmd --backend-port ${BACKEND_PORT}"
    fi
    
    run_remote "$deploy_cmd"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "========================================="
        log_success "Remote deployment completed!"
        log_info "========================================="
    else
        log_error "Deployment failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

main() {
    echo "" > "$LOG_FILE"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --host)
                SSH_HOST="$2"
                shift 2
                ;;
            --port)
                SSH_PORT="$2"
                shift 2
                ;;
            --user)
                SSH_USER="$2"
                shift 2
                ;;
            --key)
                SSH_KEY="$2"
                shift 2
                ;;
            --password)
                SSH_PASSWORD="$2"
                shift 2
                ;;
            --repo)
                GIT_REPO_URL="$2"
                shift 2
                ;;
            --project-dir)
                PROJECT_DIR="$2"
                shift 2
                ;;
            --db-password)
                DB_PASSWORD="$2"
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
            --seed)
                SEED_ENABLE="true"
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
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
    
    check_dependencies
    deploy
}

main "$@"