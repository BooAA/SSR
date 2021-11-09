#!/bin/bash
if [ $# != 2 ] ; then
    echo "./create-client.sh protocol target_ip"
    exit
fi

protocol=$1
target_ip=$2

modprobe nvme-fabrics
modprobe nvmet
if [ "$protocol" == "rdma" ] ; then
    modprobe nvme-rdma
elif [ "$protocol" == "i10" ] ; then
    modprobe i10-host
else 
    modprobe nvmet-tcp
fi

nvme connect -t $protocol \
             -n nvme-$protocol-target \
             -a $target_ip \
             -s 4420

lsblk
