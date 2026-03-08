# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  
  # VM Instellingen: Geheugen en CPU
  config.vm.provider "virtualbox" do |vb|
     vb.memory = "4096"
     vb.cpus = 2
     # Fix voor VirtualBox 7.x schermen/netwerk indien nodig
     vb.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
  end

  # Besturingssysteem
  config.vm.box = "generic/ubuntu2204"

  # Gedeelde map configureren
  # De punt "." is je Windows map, "/vagrant" is de map in de VM
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox", owner: "vagrant", group: "vagrant"

  # FIX: Schakel de vbguest plugin uit die de "exists?" crash veroorzaakt
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  # Netwerk instellingen
  config.vm.network "private_network", ip: "192.168.56.10"

end