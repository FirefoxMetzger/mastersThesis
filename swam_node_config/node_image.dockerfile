FROM boot2docker/boot2docker

# add rexray to the image
ADD rexray_install ./rexray_install
RUN ./rexray_install/install.sh

RUN /tmp/make_iso.sh

CMD ["cat", "boot2docker.iso"]
