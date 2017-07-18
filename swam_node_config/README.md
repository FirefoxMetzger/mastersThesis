To setup this swarm, virtual box has to activate its SOAP websocket on the 
address specified in build_node_image

VBoxManage setproperty websrvauthlibrary null
vboxwebsrv -H 0.0.0.0 -v
