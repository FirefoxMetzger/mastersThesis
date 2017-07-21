#!/bin/bash

echo "Getting current manager join token"
TOKEN=$( ssh docker@192.168.0.40 docker swarm join-token -q manager )

while read IP; do
    printf "Now processing %s \n" "$IP"
    ssh-keygen -r $IP:22
    ssh-keyscan -H $IP >> ~/.ssh/known_hosts
    ssh docker@$IP /bin/sh << EOF 
docker swarm leave --force
docker swarm join --token $TOKEN 192.168.0.40
EOF
done <managers.list
