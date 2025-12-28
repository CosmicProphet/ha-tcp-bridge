#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
# Run the TCP bridge server

bashio::log.info "Starting HA-TCP Bridge..."

# Get config options
PORT=$(bashio::config 'port')
bashio::log.info "TCP Port: ${PORT}"

# Export for Python
export TCP_PORT="${PORT}"

# The SUPERVISOR_TOKEN is automatically available via with-contenv
bashio::log.info "Supervisor token available: $(if [ -n "${SUPERVISOR_TOKEN}" ]; then echo 'yes'; else echo 'no'; fi)"

exec python3 /server.py
