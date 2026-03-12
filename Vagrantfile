Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "8192"
     vb.cpus = 4
     vb.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
  end

  # Gebruik rsync voor betere stabiliteit in Linux-omgevingen
  config.vm.synced_folder ".", "/vagrant", type: "rsync",
    rsync__exclude: [".git/", ".vagrant/"]

  config.vm.network "private_network", ip: "192.168.56.10"

  config.trigger.before :halt do |trigger|
    trigger.info = "Downscalen monitoring en argocd deployments naar 0 replicas..."
    trigger.on_error = :continue
    trigger.run_remote = {
      inline: <<-SHELL
        if ! command -v kubectl >/dev/null 2>&1; then
          echo "[trigger:halt] kubectl niet gevonden, sla downscaling over."
          exit 0
        fi

        echo "[trigger:halt] Downscalen monitoring deployments naar 0..."
        if kubectl scale deployment -n monitoring --all --replicas=0; then
          echo "[trigger:halt] monitoring downscale uitgevoerd."
        else
          echo "[trigger:halt] monitoring downscale mislukt."
        fi

        echo "[trigger:halt] Downscalen argocd deployments naar 0..."
        if kubectl scale deployment -n argocd --all --replicas=0; then
          echo "[trigger:halt] argocd downscale uitgevoerd."
        else
          echo "[trigger:halt] argocd downscale mislukt."
        fi
      SHELL
    }
  end

  config.trigger.after :up do |trigger|
    trigger.info = "Wacht 180 seconden en schaal monitoring/argocd deployments naar 1 replica..."
    trigger.run_remote = {
      inline: <<-SHELL
        if ! command -v kubectl >/dev/null 2>&1; then
          echo "[trigger:up] kubectl niet gevonden, sla upscaling over."
          exit 0
        fi

        echo "[trigger:up] Wacht 180 seconden voor upscaling..."
        sleep 180

        echo "[trigger:up] Upscalen monitoring deployments naar 1..."
        if kubectl scale deployment -n monitoring --all --replicas=1; then
          echo "[trigger:up] monitoring upscaling uitgevoerd."
        else
          echo "[trigger:up] monitoring upscaling mislukt."
        fi

        echo "[trigger:up] Wacht 30 seconden voor argocd upscaling..."
        sleep 30

        echo "[trigger:up] Upscalen argocd deployments naar 1..."
        if kubectl scale deployment -n argocd --all --replicas=1; then
          echo "[trigger:up] argocd upscaling uitgevoerd."
        else
          echo "[trigger:up] argocd upscaling mislukt."
        fi
      SHELL
    }
  end
end