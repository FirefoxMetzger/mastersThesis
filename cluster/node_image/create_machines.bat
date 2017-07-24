@echo off

setlocal
REM Make sure commands are available
SET PATH=%PATH%;"C:\Program Files\Docker Toolbox"
SET PATH=%PATH%;"C:\Program Files\Oracle\VirtualBox"

SET /p name="Enter the machine's name: "

docker-machine rm -y %name%-1
docker-machine create -d "virtualbox" %name%-1
docker-machine stop %name%-1
VBoxManage modifyvm "%name%-1" --nic1 bridged --nic2 none 
VBoxManage storageattach "%name%-1" --storagectl SATA --port 0 --device 0 --medium "F:\boot2docker.iso"

docker-machine rm -y %name%-2
docker-machine create -d "virtualbox" %name%-2
docker-machine stop %name%-2
VBoxManage modifyvm "%name%-2" --nic1 bridged --nic2 none 
VBoxManage storageattach "%name%-2" --storagectl SATA --port 0 --device 0 --medium "F:\boot2docker.iso"

endlocal
