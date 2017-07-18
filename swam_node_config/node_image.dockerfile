FROM boot2docker/boot2docker

# add rexray to the image
ADD rexray_install ./rexray_install
RUN ./rexray_install/install.sh

# deploy the self-signed certificate to access the registry
ADD registry/certs/certificate.crt $ROOTFS/etc/docker/certs.d/{}/certificate.crt

RUN /tmp/make_iso.sh

CMD ["cat", "boot2docker.iso"]
