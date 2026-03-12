# webstack-project

## TLS setup with lego certificate

This project can use a publicly trusted Let's Encrypt certificate generated with lego
and then imported into Kubernetes TLS secrets.

### 1. Keep lego output local

Store lego output in the repository root as `lego/` (already gitignored), or outside
the repository if you prefer. Do not commit private keys.

### 2. Verify certificate SAN and validity

Run in VM:

```bash
openssl x509 -in /vagrant/lego/certificates/_.lauwersb.duckdns.org.crt -noout -dates -ext subjectAltName
```

Expected SAN should include:

- `*.lauwersb.duckdns.org`
- `lauwersb.duckdns.org`

This covers:

- `web.lauwersb.duckdns.org`
- `grafana.lauwersb.duckdns.org`
- `argocd.lauwersb.duckdns.org`

### 3. Import TLS secrets

Run in VM:

```bash
bash /vagrant/Webstack/k8s/cert-manager/apply-lego-tls-secrets.sh
```

This creates or updates:

- `webstack-tls` in namespace `project-webstack`
- `monitoring-tls` in namespace `monitoring`
- `argocd-tls` in namespace `argocd`

### 4. Ingress HTTPS

Ingress manifests are configured for HTTPS with TLS secrets:

- web/app/api host uses secret `webstack-tls`
- grafana host uses secret `monitoring-tls`

### 5. Demo network note

At school, map hostnames to the VM IP (`192.168.56.10`) in your demo machine hosts file,
so DNS resolution still works locally.