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

# Build and push using Cloud Build via cloudbuild.yaml (context = repo root).
# NOTE: use the cloudbuild.yaml config, NOT `builds submit --tag ... -f Dockerfile`
# — `-f` is not a valid flag for `builds submit --tag`, and cloudbuild.yaml is the
# proven path that correctly references phase3_prototype/Dockerfile.
echo ">>> Building container image (cloudbuild.yaml)..."
gcloud builds submit --config cloudbuild.yaml --timeout=900s .

# Deploy to Cloud Run
echo ">>> Deploying to Cloud Run..."
# NOTE: use --update-env-vars (NOT --set-env-vars). --set-env-vars REPLACES the
# service's entire env set, which would wipe vars not listed here — notably
# GEMINI_API_KEY (breaks analysis + silently disables semantic consensus),
# SONAR_API_KEY, CORS_ORIGINS, etc. --update-env-vars only adds/updates the
# listed vars and preserves everything already configured on the service.
gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/$(gcloud config get-value project)/${SERVICE_NAME}" \
  --region "${REGION}" \
  --platform managed \
  --max-instances "${MAX_INSTANCES}" \
  --memory "${MEMORY}" \
  --timeout=60 \
  --allow-unauthenticated \
  --update-env-vars "ENFORCE_HTTPS=true,GITHUB_APP_CLIENT_ID=${GITHUB_APP_CLIENT_ID},GITHUB_APP_CLIENT_SECRET=${GITHUB_APP_CLIENT_SECRET},JWT_SECRET=${JWT_SECRET}" \
  --port 8080

# Safeguard: route 100% of traffic to the latest revision. Without this, if the
# service ever has traffic PINNED to a specific revision, a new deploy builds and
# goes healthy but receives 0% traffic — the new code silently never goes live.
echo ">>> Routing traffic to latest revision..."
gcloud run services update-traffic "${SERVICE_NAME}" --region "${REGION}" --to-latest

echo ""
echo "=== Deployment Complete ==="
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)'
echo ""
echo "To configure custom domain (macpresearch.ysenseai.org):"
echo "  gcloud run domain-mappings create --service ${SERVICE_NAME} --domain macpresearch.ysenseai.org --region ${REGION}"
