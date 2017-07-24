#!/bin/sh

echo "Getting current manager join token"
TOKEN=$( docker swarm join-token -q manager )

echo "Joining managers into the swarm"
while read IP; do
    printf "Now processing %s \n" "$IP"
    ssh-keygen -r $IP:22
    ssh-keyscan -H $IP >> ~/.ssh/known_hosts
    ssh docker@$IP /bin/sh << EOF 
docker swarm leave --force
docker swarm join --token $TOKEN 192.168.0.40
EOF
done <managers.list

echo "Getting current join join token"
TOKEN=$( docker swarm join-token -q worker )

echo "Joining workers into the swarm"
while read IP; do
    printf "Now processing %s \n" "$IP"
    ssh-keygen -r $IP:22
    ssh-keyscan -H $IP >> ~/.ssh/known_hosts
    ssh docker@$IP /bin/sh << EOF 
docker swarm leave --force
docker swarm join --token $TOKEN 192.168.0.40
EOF
done <workers.list
