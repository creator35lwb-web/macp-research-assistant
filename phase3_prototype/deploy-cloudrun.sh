#!/bin/bash
# MACP Research Assistant — GCP Cloud Run Deployment Script
# =========================================================
# Usage: ./deploy-cloudrun.sh
#
# Prerequisites:
#   - gcloud CLI authenticated and project set
#   - Docker or Cloud Build enabled
#   - Environment variables configured in Cloud Run console

set -euo pipefail

SERVICE_NAME="macp-research-assistant"
REGION="us-central1"
MAX_INSTANCES=3
MEMORY="512Mi"

echo "=== MACP Research Assistant — Cloud Run Deployment ==="
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Build and push using Cloud Build
echo ">>> Building container image..."
gcloud builds submit \
  --tag "gcr.io/$(gcloud config get-value project)/${SERVICE_NAME}" \
  --timeout=600s

# Deploy to Cloud Run
echo ">>> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/$(gcloud config get-value project)/${SERVICE_NAME}" \
  --region "${REGION}" \
  --platform managed \
  --max-instances "${MAX_INSTANCES}" \
  --memory "${MEMORY}" \
  --allow-unauthenticated \
  --set-env-vars "ENFORCE_HTTPS=true" \
  --port 8080

echo ""
echo "=== Deployment Complete ==="
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)'
echo ""
echo "To configure custom domain (macpresearch.ysenseai.org):"
echo "  gcloud run domain-mappings create --service ${SERVICE_NAME} --domain macpresearch.ysenseai.org --region ${REGION}"
