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
end