FROM boot2docker/boot2docker

# add rexray to the image
ADD rexray_install /rexray_install
ADD tmp/rexray/config.yml /rexray_install
RUN ./rexray_install/install.sh

# enable REX-Ray with docker -- allows node to access persistent storage
ADD tmp/rexray/rexray.spec $ROOTFS/etc/docker/plugins/rexray.spec

# deploy the self-signed certificate -- allows node to access registry
ADD tmp/registry/certs/certificate.crt $ROOTFS/etc/docker/certs.d/{}/certificate.crt

RUN /tmp/make_iso.sh

CMD ["cat", "boot2docker.iso"]
