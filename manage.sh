#!/bin/bash

# Banking Agent Management Script
# Manages MCP server, agent service, and test client

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log files
LOG_DIR="$PROJECT_DIR/logs"
MCP_SERVER_LOG="$LOG_DIR/mcp_server.log"
AGENT_SERVICE_LOG="$LOG_DIR/agent_service.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# PID files
PID_DIR="$PROJECT_DIR/.pids"
MCP_SERVER_PID="$PID_DIR/mcp_server.pid"
AGENT_SERVICE_PID="$PID_DIR/agent_service.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if process is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Start MCP Server
start_mcp_server() {
    if is_running "$MCP_SERVER_PID"; then
        print_warning "MCP Server is already running (PID: $(cat $MCP_SERVER_PID))"
        return
    fi
    
    print_info "Starting MCP Server..."
    nohup uv run python -m mcp_server.main > "$MCP_SERVER_LOG" 2>&1 &
    echo $! > "$MCP_SERVER_PID"
    
    sleep 2
    if is_running "$MCP_SERVER_PID"; then
        print_success "MCP Server started (PID: $(cat $MCP_SERVER_PID))"
    else
        print_error "Failed to start MCP Server"
        cat "$MCP_SERVER_LOG"
        exit 1
    fi
}

# Start Agent Service
start_agent_service() {
    if is_running "$AGENT_SERVICE_PID"; then
        print_warning "Agent Service is already running (PID: $(cat $AGENT_SERVICE_PID))"
        return
    fi
    
    print_info "Starting Agent Service..."
    nohup uv run python -m mcp_client.agent_service > "$AGENT_SERVICE_LOG" 2>&1 &
    echo $! > "$AGENT_SERVICE_PID"
    
    sleep 2
    if is_running "$AGENT_SERVICE_PID"; then
        print_success "Agent Service started (PID: $(cat $AGENT_SERVICE_PID))"
    else
        print_error "Failed to start Agent Service"
        cat "$AGENT_SERVICE_LOG"
        exit 1
    fi
}

# Start Frontend
start_frontend() {
    if is_running "$FRONTEND_PID"; then
        print_warning "Frontend is already running (PID: $(cat $FRONTEND_PID))"
        return
    fi
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found"
        return
    fi
    
    print_info "Starting Frontend..."
    cd frontend
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID"
    cd ..
    
    sleep 2
    if is_running "$FRONTEND_PID"; then
        print_success "Frontend started (PID: $(cat $FRONTEND_PID))"
        local dev_url=$(grep "Local:" "$FRONTEND_LOG" | head -n 1 | awk '{print $NF}')
        if [ -n "$dev_url" ]; then
            print_info "Frontend URL: $dev_url"
        fi
    else
        print_error "Failed to start Frontend"
        cat "$FRONTEND_LOG"
        exit 1
    fi
}

# Stop MCP Server
stop_mcp_server() {
    if is_running "$MCP_SERVER_PID"; then
        local pid=$(cat "$MCP_SERVER_PID")
        print_info "Stopping MCP Server (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$MCP_SERVER_PID"
        print_success "MCP Server stopped"
    else
        print_warning "MCP Server is not running"
    fi
}

# Stop Agent Service
stop_agent_service() {
    if is_running "$AGENT_SERVICE_PID"; then
        local pid=$(cat "$AGENT_SERVICE_PID")
        print_info "Stopping Agent Service (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$AGENT_SERVICE_PID"
        print_success "Agent Service stopped"
    else
        print_warning "Agent Service is not running"
    fi
}

# Stop Frontend
stop_frontend() {
    if is_running "$FRONTEND_PID"; then
        local pid=$(cat "$FRONTEND_PID")
        print_info "Stopping Frontend (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$FRONTEND_PID"
        print_success "Frontend stopped"
    else
        print_warning "Frontend is not running"
    fi
}

# Status
show_status() {
    echo -e "\n${BLUE}=== Banking Agent Status ===${NC}\n"
    
    if is_running "$MCP_SERVER_PID"; then
        echo -e "${GREEN}●${NC} MCP Server: ${GREEN}Running${NC} (PID: $(cat $MCP_SERVER_PID)) [Port 8001]"
    else
        echo -e "${RED}●${NC} MCP Server: ${RED}Stopped${NC}"
    fi
    
    if is_running "$AGENT_SERVICE_PID"; then
        echo -e "${GREEN}●${NC} Agent Service: ${GREEN}Running${NC} (PID: $(cat $AGENT_SERVICE_PID)) [Port 8000]"
    else
        echo -e "${RED}●${NC} Agent Service: ${RED}Stopped${NC}"
    fi

    if is_running "$FRONTEND_PID"; then
        echo -e "${GREEN}●${NC} Frontend: ${GREEN}Running${NC} (PID: $(cat $FRONTEND_PID))"
    else
        echo -e "${RED}●${NC} Frontend: ${RED}Stopped${NC}"
    fi
    
    echo ""
}

# Show logs
show_logs() {
    local service=$1
    local lines=${2:-50}
    
    case $service in
        mcp|server)
            [ -f "$MCP_SERVER_LOG" ] && tail -n "$lines" "$MCP_SERVER_LOG" || print_error "Logs not found"
            ;;
        agent|service)
            [ -f "$AGENT_SERVICE_LOG" ] && tail -n "$lines" "$AGENT_SERVICE_LOG" || print_error "Logs not found"
            ;;
        frontend|ui)
            [ -f "$FRONTEND_LOG" ] && tail -n "$lines" "$FRONTEND_LOG" || print_error "Logs not found"
            ;;
        all)
            print_info "MCP Logs:" && show_logs mcp "$lines"
            print_info "Agent Logs:" && show_logs agent "$lines"
            print_info "Frontend Logs:" && show_logs frontend "$lines"
            ;;
        *)
            print_error "Unknown service: $service"
            exit 1
            ;;
    esac
}

# Main command handler
case "${1:-}" in
    start)
        case "${2:-all}" in
            mcp|server) start_mcp_server ;;
            agent|service) start_agent_service ;;
            frontend|ui) start_frontend ;;
            all)
                start_mcp_server
                sleep 2
                start_agent_service
                sleep 1
                start_frontend
                show_status
                ;;
            *) print_error "Unknown service: $2" ; exit 1 ;;
        esac
        ;;
    
    stop)
        case "${2:-all}" in
            mcp|server) stop_mcp_server ;;
            agent|service) stop_agent_service ;;
            frontend|ui) stop_frontend ;;
            all)
                stop_frontend
                stop_agent_service
                stop_mcp_server
                ;;
            *) print_error "Unknown service: $2" ; exit 1 ;;
        esac
        ;;
    
    restart)
        $0 stop "$2"
        sleep 1
        $0 start "$2"
        ;;
    
    status)
        show_status
        ;;
    
    logs)
        show_logs "${2:-all}" "${3:-50}"
        ;;
    
    clean)
        print_info "Cleaning log files and PID files..."
        rm -rf "$LOG_DIR"/* "$PID_DIR"/*
        print_success "Cleaned"
        ;;
    
    plot)
        print_info "Generating agent graph visualization..."
        uv run python -m mcp_client.visualize_graph --output agent_graph.png
        ;;
    
    help|--help|-h)
        cat << EOF
${BLUE}Banking Agent Management Script${NC}

Usage: $0 <command> [options]

${GREEN}Commands:${NC}
  start [service]     Start services (mcp, agent, frontend, or all)
  stop [service]      Stop services (mcp, agent, frontend, or all)
  restart [service]   Restart services
  status              Show status of all services
  logs [service] [n]  Show last n lines of logs
  clean               Clean logs and PID files
  plot                Plot agent graph as PNG
  help                Show this help

${GREEN}Services:${NC}
  mcp/server, agent/service, frontend/ui, all (default)
EOF
        ;;
    
    *)
        print_error "Unknown command: ${1:-}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
