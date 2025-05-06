#!/bin/bash
# Script to deploy the Wikidata MCP server to Fly.io

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "flyctl is not installed. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Commit changes to git
echo "Committing changes to git..."
git add .
git commit -m "chore: deploy to fly.io"
git push

# Login to Fly.io if needed
echo "Checking Fly.io authentication..."
flyctl auth whoami || flyctl auth login

# Launch the app (first time only)
if [ "$1" == "--first-time" ]; then
    echo "Creating new Fly.io app..."
    flyctl launch --no-deploy
    exit 0
fi

# Deploy the app
echo "Deploying to Fly.io..."
flyctl deploy

# Show the deployed app URL
echo "Deployment complete! Your app is available at:"
flyctl open
