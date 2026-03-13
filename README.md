# BL Webstack Project

Deze README documenteert het volledige project, inclusief:
- lokale run met Docker Compose
- deployment op Kubernetes (kind)
- Ingress, TLS, monitoring (Prometheus/Grafana)
- GitOps via ArgoCD
- CI/CD via GitHub Actions

De tekst is opgebouwd als commandolog: elke stap bevat het commando, wat het doet, waarom je het gebruikt, en uitleg van parameters/opties.

## 1. Projectoverzicht

Dit project bouwt een eenvoudige webstack met 3 lagen:
- Frontend: statische pagina via Lighttpd
- API: FastAPI (Python)
- Database: MariaDB

In Kubernetes wordt dit uitgebreid met:
- NGINX Ingress controller
- TLS-secrets op basis van een lego Let's Encrypt certificaat
- monitoring via kube-prometheus-stack + custom ServiceMonitor
- Grafana dashboard als ConfigMap
- ArgoCD Application voor GitOps sync

## 2. Repositorystructuur

```text
BL_webstack-project/
  Vagrantfile
  commando's.txt
  lego/
  Webstack/
    .env
    docker-compose.yml
    api/
    db/
    frontend/
    k8s/
  .github/workflows/build-image.yaml
```

Belangrijkste configuraties:
- `Vagrantfile`: VM resources, sync en auto scale-down/-up triggers voor namespaces `monitoring` en `argocd`
- `Webstack/docker-compose.yml`: lokale containers voor DB/API/frontend
- `Webstack/k8s/base/*.yaml`: app manifests
- `Webstack/k8s/monitoring/*.yaml`: observability
- `Webstack/k8s/argocd/*.yaml`: GitOps
- `Webstack/k8s/cert-manager/apply-lego-tls-secrets.sh`: TLS secret import

## 3. Voorvereisten

### 3.1 Hostmachine (Windows)

Installeer:
- VirtualBox
- Vagrant

Controleer versies:

```powershell
vagrant --version
VBoxManage --version
```

Wat doet dit en waarom:
- `vagrant --version`: toont geïnstalleerde Vagrant-versie om te controleren of de CLI beschikbaar is
- `VBoxManage --version`: toont VirtualBox-versie; Vagrant gebruikt VirtualBox als provider in dit project

Parameters:
- `--version`: print enkel versie-info en stopt meteen

Screenshot:
- Maak screenshot van beide versies in 1 terminalvenster
- Bewaar als `docs/screenshots/01-host-versions.png`

### 3.2 Vagrant plugin (aanbevolen)

```powershell
vagrant plugin install vagrant-vbguest
```

Wat doet dit en waarom:
- Installeert plugin die VirtualBox Guest Additions kan beheren
- In jouw `Vagrantfile` staat een check op deze plugin; als de plugin bestaat, wordt auto-update uitgeschakeld voor stabiel gedrag

Parameters:
- `plugin install`: subcommand om plugin te installeren
- `vagrant-vbguest`: pluginnaam

## 4. VM opstarten en binnenkomen

Ga naar de projectroot en start de VM:

```powershell
cd "C:\Users\school\Documents\thomasmore\linux web en network services\BL_webstack-project"
vagrant up
```

Wat doet dit en waarom:
- `cd ...`: zet je shell in de map met `Vagrantfile`
- `vagrant up`: maakt en start de VM (`bento/ubuntu-22.04`) met 8 GB RAM, 4 CPU's en private network `192.168.56.10`

Parameters:
- `up`: start en provisiont de VM op basis van `Vagrantfile`

Ga de VM in:

```powershell
vagrant ssh
```

Wat doet dit en waarom:
- Opent SSH sessie naar de draaiende VM waar je Docker/kind/kubectl commando's uitvoert

Parameters:
- `ssh`: opent shell op de VM

Screenshot:
- VM `up` output: `docs/screenshots/03-vagrant-up.png`
- SSH prompt in VM: `docs/screenshots/04-vagrant-ssh.png`

## 5. Eenmalige tool-installatie in de VM (als nodig)

Als een tool ontbreekt (`command not found`), installeer ze met onderstaande stappen.

### 5.1 Basispackages

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release git
```

Wat doet dit en waarom:
- `apt update`: vernieuwt pakketindex
- `apt install`: installeert basispakketten nodig voor Docker en downloads

Parameters:
- `sudo`: voer uit met rootrechten
- `install`: installeer pakketten
- `-y`: antwoord automatisch "yes"

### 5.2 Docker Engine + Compose plugin

```bash
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
newgrp docker
```

Wat doet dit en waarom:
- Installeert Docker + Compose plugin
- Voegt je user toe aan de `docker` groep zodat `sudo` meestal niet meer nodig is
- `newgrp docker` activeert nieuwe groepsrechten in huidige sessie

Parameters:
- `-aG`: append (`-a`) gebruiker aan extra groep (`-G`)

### 5.3 kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Wat doet dit en waarom:
- Downloadt de nieuwste stabiele `kubectl`
- Installeert binary system-wide met correcte rechten

Parameters:
- `-L` bij `curl`: volg redirects
- `-O`: schrijf output naar bestand met originele bestandsnaam
- `-s`: silent mode (minder ruis)
- `install -o root -g root -m 0755`: owner root, group root, executable permissies

### 5.4 kind

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

Wat doet dit en waarom:
- Downloadt kind binary en maakt die uitvoerbaar
- Verplaatst binary naar pad dat in PATH zit

Parameters:
- `-Lo`: `-L` follow redirect + `-o` output-bestand
- `chmod +x`: voeg execute-bit toe

### 5.5 Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Wat doet dit en waarom:
- Installeert Helm 3, nodig voor `kube-prometheus-stack`

Parameters:
- `| bash`: pipe script-output direct naar bash

### 5.6 Installatie verifiëren

```bash
docker --version
docker compose version
kubectl version --client
kind version
helm version
```

Waarom:
- Controle dat alle tools bruikbaar zijn voor de rest van de deployment

Screenshot:
- Bewaar als `docs/screenshots/05-vm-tools-versions.png`

## 6. Optie A: lokaal draaien met Docker Compose

Werk in de VM:

```bash
cd /vagrant/Webstack
docker compose up -d --build
```

Wat doet dit en waarom:
- `cd /vagrant/Webstack`: ga naar map met `docker-compose.yml`
- `docker compose up`: start services uit composebestand
- `--build`: bouw images opnieuw (zeker dat codewijzigingen mee zijn)
- `-d`: detached mode (terminal blijft vrij)

Parameters:
- `up`: maak en start containers
- `-d`: run in achtergrond
- `--build`: force rebuild

Controleer status:

```bash
docker compose ps
curl -s http://localhost:8000/health
curl -s http://localhost:8000/user
```

Wat doet dit en waarom:
- `docker compose ps`: toont containerstatus
- `curl .../health`: API liveness endpoint
- `curl .../user`: test DB-read via API

Parameters:
- `-s` bij `curl`: silent output zonder voortgangsbalk

Open frontend in browser:
- `http://192.168.56.10:8080`
- `http://192.168.56.10:8081`
- `http://192.168.56.10:8082`

Stoppen:

```bash
docker compose down
```

Wat doet dit en waarom:
- Stopt en verwijdert compose-resources (netwerken/containers)

## 7. Optie B: Kubernetes deployment (kind)

> Deze optie sluit aan op je manifests in `Webstack/k8s`.

### 7.1 Cluster maken

```bash
cd /vagrant/Webstack
kind create cluster --config k8s/kind-config.yaml
```

Wat doet dit en waarom:
- Maakt een kind cluster met 1 control-plane en 2 workers
- Port mappings 80/443 zorgen dat Ingress bereikbaar is vanaf host

Parameters:
- `create cluster`: maak nieuwe cluster
- `--config`: gebruik eigen kind-config

Verifiëren:

```bash
kubectl cluster-info
kubectl get nodes -o wide
```

Wat doet dit en waarom:
- `cluster-info`: controle control plane endpoint
- `get nodes -o wide`: lijst nodes met extra info (IP, runtime, etc.)

Parameters:
- `-o wide`: uitgebreid outputformaat

Screenshot:
- `docs/screenshots/09-kind-create-nodes.png`

### 7.2 NGINX Ingress controller installeren

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=Ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
```

Wat doet dit en waarom:
- `apply -f <url>`: installeert ingress-nginx manifests voor kind
- `wait ...`: blokkeert tot de ingress controller pod klaar is

Parameters:
- `-f`: lees manifest van bestand/URL
- `--namespace`: doelnamespace
- `--for=condition=Ready`: wacht op Ready conditie
- `pod`: resource type waarop gewacht wordt
- `--selector`: labelselector om juiste pod(s) te targeten
- `--timeout=180s`: max wachttijd

Screenshot:
- `docs/screenshots/10-ingress-nginx-ready.png`

### 7.3 Namespaces aanmaken

```bash
kubectl apply -f k8s/project-namespaces.yaml
kubectl get ns
```

Wat doet dit en waarom:
- Maakt namespaces `project-webstack`, `monitoring`, `argocd`, `cert-manager`
- `get ns` controleert of ze bestaan

Parameters:
- `ns`: korte alias voor namespaces

Screenshot:
- `docs/screenshots/11-namespaces.png`

### 7.4 Base applicatie deployen

```bash
kubectl apply -f k8s/base/project-secrets.yaml
kubectl apply -f k8s/base/db-pvc.yaml
kubectl apply -f k8s/base/mariadb-congifmap.yaml
kubectl apply -f k8s/base/mariadb.yaml
kubectl apply -f k8s/base/api.yaml
kubectl apply -f k8s/base/frontend.yaml
kubectl apply -f k8s/base/ingress.yaml
```

Wat doet dit en waarom:
- Secrets, persistent storage en init-script voor MariaDB
- Deployment/Service voor API en frontend
- Ingress routes op host `web.lauwersb.duckdns.org`, inclusief `/api` rewrite

Parameters:
- `apply`: maakt resource aan of werkt resource bij
- `-f`: manifestbestand

Controle:

```bash
kubectl get pods -n project-webstack
kubectl get svc -n project-webstack
kubectl get ingress -n project-webstack
```

Wat doet dit en waarom:
- Controle dat pods/services/ingress effectief draaien

Parameters:
- `-n`: namespace voor de query
- `svc`: service resource alias

Screenshot:
- `docs/screenshots/12-base-resources.png`

### 7.5 Monitoring stack installeren

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -f k8s/monitoring/monitoring.yaml
kubectl apply -f k8s/monitoring/grafana-dashboard-bl.yaml
kubectl apply -f k8s/monitoring/grafana-ingress.yaml
```

Wat doet dit en waarom:
- Voeg Helm chart repo toe en update index
- Installeer/upgrade `kube-prometheus-stack` release naam `prometheus`
- Pas custom ServiceMonitor, dashboard en ingress toe

Parameters:
- `repo add`: voeg chart repository toe
- `repo update`: refresh repo metadata
- `upgrade --install`: upgrade als release bestaat, anders install
- `-n monitoring`: deploy in namespace `monitoring`
- `--create-namespace`: maak namespace indien nodig

Controle:

```bash
kubectl get pods -n monitoring
kubectl get ingress -n monitoring
```

Screenshot:
- `docs/screenshots/13-monitoring-installed.png`

### 7.6 ArgoCD installeren en app registreren

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f k8s/argocd/webstack-application.yaml
kubectl apply -f k8s/argocd/argocd-ingress.yaml
```

Wat doet dit en waarom:
- Installeert ArgoCD controllers/server in namespace `argocd`
- Registreert jouw GitOps Application (`webstack`) die `Webstack/k8s` recursief volgt
- Stelt ingress in op `argocd.lauwersb.duckdns.org`

Parameters:
- `-n argocd`: voer `apply` uit in ArgoCD namespace
- `-f`: installatie-URL en daarna lokale manifests

Initieel ArgoCD admin wachtwoord opvragen:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d; echo
```

Wat doet dit en waarom:
- Leest het tijdelijke admin wachtwoord uit Kubernetes Secret

Parameters:
- `get secret`: haal secret op
- `-o jsonpath="{.data.password}"`: output alleen veld `data.password`
- `base64 -d`: decodeer base64 naar leesbare tekst
- `; echo`: newline na output

Screenshot:
- `docs/screenshots/14-argocd-installed.png`
- `docs/screenshots/15-argocd-login.png`

### 7.7 TLS certificaat valideren en secrets importeren

Controleer certificaat:

```bash
openssl x509 -in /vagrant/lego/certificates/_.lauwersb.duckdns.org.crt -noout -dates -ext subjectAltName
```

Wat doet dit en waarom:
- Leest certificaatinfo, controleert geldigheid en SAN-domeinen

Parameters:
- `x509`: parse X.509 cert
- `-in`: invoerbestand
- `-noout`: geen ruwe cert output
- `-dates`: toon notBefore/notAfter
- `-ext subjectAltName`: toon SAN extension

TLS secrets toepassen:

```bash
bash /vagrant/Webstack/k8s/cert-manager/apply-lego-tls-secrets.sh
```

Wat doet dit en waarom:
- Script maakt/update TLS secrets:
  - `webstack-tls` in `project-webstack`
  - `monitoring-tls` in `monitoring`
  - `argocd-tls` in `argocd`

Parameters:
- `bash`: run script met Bash
- Script accepteert optioneel 1 argument: certificaatmap (default `/vagrant/lego/certificates`)

Verifiëren:

```bash
kubectl get secret webstack-tls -n project-webstack
kubectl get secret monitoring-tls -n monitoring
kubectl get secret argocd-tls -n argocd
```

Screenshot:
- `docs/screenshots/16-tls-verify-and-secrets.png`

### 7.8 Hosts-file aanpassen op demomachine

Voeg op de machine waarmee je test deze regels toe aan hosts-file:

```text
192.168.56.10 web.lauwersb.duckdns.org
192.168.56.10 grafana.lauwersb.duckdns.org
192.168.56.10 argocd.lauwersb.duckdns.org
```

Waarom:
- In school/demo-netwerk wil je domeinen laten resolven naar je VM IP

Windows openen als administrator:

```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Screenshot:
- `docs/screenshots/17-hosts-file.png`

### 7.9 Eindcontrole

```bash
kubectl get pods -A
kubectl get ingress -A
curl -I https://web.lauwersb.duckdns.org
curl -I https://grafana.lauwersb.duckdns.org
curl -I https://argocd.lauwersb.duckdns.org
```

Wat doet dit en waarom:
- Clusterbreed overzicht van pods en ingresses
- HTTP headers valideren dat endpoints reageren

Parameters:
- `-A`: alle namespaces
- `-I`: haal alleen response headers op

Screenshot:
- `docs/screenshots/18-final-validation.png`

## 8. CI/CD workflow (GitHub Actions)

Workflowbestand: `.github/workflows/build-image.yaml`

Bij push naar `main`:
1. API image build + push naar Docker Hub met tag `${{ github.sha }}`
2. Frontend image build + push
3. Update van image tags in:
   - `Webstack/k8s/base/api.yaml`
   - `Webstack/k8s/base/frontend.yaml`
4. Commit en push terug naar `main` als manifest effectief wijzigde

Commando's om pipeline te triggeren:

```bash
git add .
git commit -m "Deploy update"
git push origin main
```

Wat doet dit en waarom:
- Brengt codewijzigingen naar `main` zodat workflow automatisch start

Parameters:
- `-m`: commit message inline
- `origin`: remote naam
- `main`: branchnaam

Screenshot:
- `docs/screenshots/19-github-actions-success.png`

## 9. Troubleshooting

### 9.1 Ingress geeft 404

Controleer host in ingress manifests:
- `web.lauwersb.duckdns.org` moet exact kloppen

Controle:

```bash
kubectl describe ingress -n project-webstack
```

### 9.2 API kan DB niet bereiken

Controleer:

```bash
kubectl logs -n project-webstack deploy/api-deployment
kubectl logs -n project-webstack deploy/mariadb-deployment
kubectl get secret mariadb-secrets -n project-webstack -o yaml
```

Waarom:
- Logs tonen connectiefouten
- Secret bevestigt of credentials beschikbaar zijn

### 9.3 ArgoCD overschrijft manuele kubectl edits

Verklaring:
- ArgoCD `selfHeal` staat aan; handmatige wijzigingen worden teruggezet naar Git-state

Oplossing:
- Wijzig manifests in Git en push naar `main`

## 10. Screenshots checklist

Plaats screenshots in `docs/screenshots/` met exact deze namen:

1. `01-host-versions.png`
2. `02-vagrant-plugin.png`
3. `03-vagrant-up.png`
4. `04-vagrant-ssh.png`
5. `05-vm-tools-versions.png`
6. `06-compose-up.png`
7. `07-compose-health-user.png`
8. `08-compose-frontend-browser.png`
9. `09-kind-create-nodes.png`
10. `10-ingress-nginx-ready.png`
11. `11-namespaces.png`
12. `12-base-resources.png`
13. `13-monitoring-installed.png`
14. `14-argocd-installed.png`
15. `15-argocd-login.png`
16. `16-tls-verify-and-secrets.png`
17. `17-hosts-file.png`
18. `18-final-validation.png`
19. `19-github-actions-success.png`

Tip voor leesbaarheid:
- Gebruik één terminal met groot lettertype
- Zoom browser op 110-125%
- Knip irrelevante delen weg
- Toon in elke screenshot de volledige command output plus prompt

## 11. Afsluiten van de omgeving

In VM:

```bash
exit
```

Op host:

```powershell
vagrant halt
```

Wat doet dit en waarom:
- `exit`: verlaat VM shell
- `vagrant halt`: stopt VM netjes

Opmerking:
- In jouw `Vagrantfile` staat een `before :halt` trigger die deployments in `monitoring` en `argocd` naar 0 replicas schaalt om resources te sparen.
