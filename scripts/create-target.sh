#!/bin/bash
if [ $# != 5 ] ; then
    echo "./create-target.sh protocol nvme_device target_ip port namespace"
    exit
fi

protocol=$1
target=$2
target_ip=$3
port=$4
namespace=$5

# Load kernel modules on the target
modprobe nvme-fabrics
modprobe nvmet

if [ "$protocol" == "tcp" ] ; then
    modprobe nvmet-tcp
fi

if [ "$protocol" == "rdma" ] ; then
    modprobe nvmet-rdma
    modprobe nvme-rdma
fi

if [ "$protocol" == "i10" ] ; then
    modprobe i10-target
fi

# Protocl Target
protocol_target=nvme-${protocol}-target

# Create and configure an NVME Target subsystem
subsys_dir=/sys/kernel/config/nvmet/subsystems/${protocol_target}
if [ -d ${subsys_dir} ] ; then
   echo "Subsys Directory Exists: $subsys_dir"
   exit
fi

mkdir $subsys_dir
echo 1 > $subsys_dir/attr_allow_any_host

# Attach target device to this target aned enables it
namespace_dir=$subsys_dir/namespaces/$namespace
if [ -d ${namespace_dir} ] ; then
    echo "Namespace Exists: $namespace_dir"
    exit
fi

mkdir $namespace_dir
echo -n $target > $namespace_dir/device_path
echo -n 1       > $namespace_dir/enable

# Crate an NVMe target port, and configure the IP address and other parameter
port_dir=/sys/kernel/config/nvmet/ports/$port
if [ -d ${port_dir} ] ; then
    echo "Port Exists: $port_dir"
    exit
fi

mkdir $port_dir
echo $target_ip > $port_dir/addr_traddr
echo $protocol  > $port_dir/addr_trtype
echo 4420       > $port_dir/addr_trsvcid
echo ipv4       > $port_dir/addr_adrfam

# Create link to the subsystem from the port
ln -s $subsys_dir $port_dir/subsystems/${protocol_target}
