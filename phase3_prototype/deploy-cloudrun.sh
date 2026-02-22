#!/bin/bash
# MACP Research Assistant — GCP Cloud Run Deployment Script
# =========================================================
# Usage: Run from repo root:  ./phase3_prototype/deploy-cloudrun.sh
#
# Prerequisites:
#   - gcloud CLI authenticated and project set
#   - Docker or Cloud Build enabled
#   - Environment variables configured in Cloud Run console
#   - JWT_SECRET set in Cloud Run env vars

set -euo pipefail

# Ensure we're at the repo root (build context must include tools/)
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

SERVICE_NAME="macp-research-assistant"
REGION="us-central1"
MAX_INSTANCES=3
MEMORY="512Mi"

echo "=== MACP Research Assistant — Cloud Run Deployment ==="
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Build and push using Cloud Build (context = repo root, Dockerfile in phase3_prototype/)
echo ">>> Building container image..."
gcloud builds submit \
  --tag "gcr.io/$(gcloud config get-value project)/${SERVICE_NAME}" \
  --timeout=600s \
  -f phase3_prototype/Dockerfile .

# Deploy to Cloud Run
echo ">>> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/$(gcloud config get-value project)/${SERVICE_NAME}" \
  --region "${REGION}" \
  --platform managed \
  --max-instances "${MAX_INSTANCES}" \
  --memory "${MEMORY}" \
  --allow-unauthenticated \
  --set-env-vars "ENFORCE_HTTPS=true,GITHUB_APP_CLIENT_ID=${GITHUB_APP_CLIENT_ID},GITHUB_APP_CLIENT_SECRET=${GITHUB_APP_CLIENT_SECRET},JWT_SECRET=${JWT_SECRET}" \
  --port 8080

echo ""
echo "=== Deployment Complete ==="
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)'
echo ""
echo "To configure custom domain (macpresearch.ysenseai.org):"
echo "  gcloud run domain-mappings create --service ${SERVICE_NAME} --domain macpresearch.ysenseai.org --region ${REGION}"
