#!/bin/sh

IP_ADDRESS="192.168.0.40"
TARGET=docker@$IP_ADDRESS

# create a temporary directory
mkdir -p tmp

# setup a new swarm on the host
ssh $TARGET docker swarm leave --force
ssh $TARGET docker swarm init

# -- PORTAINER --
docker pull portainer/portainer
docker tag portainer/portainer $IP_ADDRESS/portainer
docker save $IP_ADDRESS/portainer > tmp/portainer.tar.gz
ssh $TARGET docker load <tmp/portainer.tar.gz

# -- REGISTRY --
docker pull registry
docker tag registry $IP_ADDRESS/registry
docker save $IP_ADDRESS/registry > tmp/registry.tar.gz
ssh $TARGET docker load <tmp/registry.tar.gz
ssh $TARGET docker volume create registry_data

# setup the secrets
cat registry/certs/certificate.crt | ssh $TARGET docker secret create registry_certificate -
cat registry/certs/private.key | ssh $TARGET docker secret create registry_private_key -

# launch the stack
scp base-stack.yml $TARGET:~
ssh $TARGET docker stack deploy --compose-file=base-stack.yml BASE
