#!/usr/bin/with-contenv bashio
set -e

# Initialize configuration
DATA_DIR="/data"

# Create required directories
mkdir -p "${DATA_DIR}/logs" "${DATA_DIR}/cache"

# Export Home Assistant configuration if provided
if bashio::config.has_value 'ha_url'; then
    export HA_URL="$(bashio::config 'ha_url')"
fi

if bashio::config.has_value 'ha_token'; then
    export HA_TOKEN="$(bashio::config 'ha_token')"
fi

if bashio::config.has_value 'deepseek_key'; then
    export DEEPSEEK_KEY="$(bashio::config 'deepseek_key')"
fi

# Export DATA_DIR
export DATA_DIR

# Start the application
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080 --log-level info
