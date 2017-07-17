#!/bin/sh

source_path="/rexray_install"

# download and install the binary
curl -sSL https://dl.bintray.com/emccode/rexray/stable/0.9.2/rexray-Linux-x86_64-0.9.2.tar.gz > rexray.tar.gz
tar -xzvf rexray.tar.gz && cp rexray /rootfs/usr/bin

# add a rexray config file (will be used whenever the rexray service is started
mkdir -p $ROOTFS/etc/rexray
cp $source_path/config.yml $ROOTFS/etc/rexray/config.yml

# make rexray autostart
cp $source_path/startup $ROOTFS/etc/init.d/rexray
cp $source_path/rc $ROOTFS/etc/rc.d/rexray
cat $source_path/bootscript.sh >> $ROOTFS/opt/bootscript.sh
