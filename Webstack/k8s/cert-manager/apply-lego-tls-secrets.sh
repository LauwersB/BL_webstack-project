#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="${1:-/vagrant/lego/certificates}"
CRT_FILE="${CERT_DIR}/_.lauwersb.duckdns.org.crt"
KEY_FILE="${CERT_DIR}/_.lauwersb.duckdns.org.key"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl not found in PATH"
  exit 1
fi

if [[ ! -f "${CRT_FILE}" ]]; then
  echo "Certificate file not found: ${CRT_FILE}"
  exit 1
fi

if [[ ! -f "${KEY_FILE}" ]]; then
  echo "Key file not found: ${KEY_FILE}"
  exit 1
fi

apply_tls_secret() {
  local namespace="$1"
  local secret_name="$2"

  echo "Applying TLS secret ${secret_name} in namespace ${namespace}..."
  kubectl -n "${namespace}" create secret tls "${secret_name}" \
    --cert="${CRT_FILE}" \
    --key="${KEY_FILE}" \
    --dry-run=client -o yaml | kubectl apply -f -
}

apply_tls_secret project-webstack webstack-tls
apply_tls_secret monitoring monitoring-tls
apply_tls_secret argocd argocd-tls

echo "TLS secrets applied successfully."
