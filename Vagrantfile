Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "8192"
     vb.cpus = 4
     vb.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
  end

  # Gebruik rsync voor betere stabiliteit in Linux-omgevingen
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"

  config.vm.network "private_network", ip: "192.168.56.10"
end