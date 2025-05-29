#!/bin/bash
set -e

# Install curl quietly
apt-get update -qq && apt-get install -y curl --no-install-recommends

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve mistral model..."
ollama pull mistral
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid



# Start Ollama server in background
# ollama serve &

# Wait for server to be ready


# Keep container running
