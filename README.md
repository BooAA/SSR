# i10 Setup Guide

i10 is the state of the art in-kernel NVMe over TCP implementations. In this
tutorial we will setup two machines (one as host and the other as target) with
i10 I/O scheduler enable. The tutorial is based on [i10-kernel/upstream-linux](https://github.com/i10-kernel/upstream-linux)
with little modification.

[SSR Note](https://hackmd.io/Mk-YNYehSDOXaCFSaVwuvg)

## Installation

Download linux v5.9-rc2 or v5.9-rc3 and apply the i10 upstream patch.
```bash
git clone --depth 1 -b v5.9-rc3 https://github.com/torvalds/linux.git
git clone https://github.com/BooAA/i10-setup-guide.git

cp i10-setup-guide/i10.patch linux/
cd linux
patch -p1 < i10.patch
cp /boot/config-$(uname -r) .config
make oldconfig
# make menuconfig ## make sure i10 is selected as built-in or module
make -j16 bzImage
make -j16 modules
sudo make modules_install
sudo make install
```

Reboot with the new kernel.

## Setup NVMe-TCP Target

Load corresponding kernel modules on the target.
```bash
sudo modprobe nvme-fabrics
sudo modprobe nvmet
sudo modprobe nvmet-tcp
```

Create and configure an NVMe Target subsystem.
```bash
cd /sys/kernel/config/nvmet/subsystems
sudo mkdir nvme-tcp-target
cd nvme-tcp-target/
echo 1 | sudo tee -a attr_allow_any_host > /dev/null
sudo mkdir namespaces/1
cd namespaces/1
```

Attach /dev/nvme0n1 to this target and enables it.
```bash
echo -n /dev/nvme0n1 | sudo tee -a device_path > /dev/null
echo 1 | sudo tee -a enable > /dev/null
```

Create an NVMe target port, and configure the IP address and other parameters.
```bash
sudo mkdir /sys/kernel/config/nvmet/ports/1
cd /sys/kernel/config/nvmet/ports/1

echo <target-ip> | sudo tee -a addr_traddr > /dev/null

echo tcp | sudo tee -a addr_trtype > /dev/null
echo 4420 | sudo tee -a addr_trsvcid > /dev/null
echo ipv4 | sudo tee -a addr_adrfam > /dev/null
```

Finally, create a link to the subsystem from the port
```bash
sudo ln -s /sys/kernel/config/nvmet/subsystems/nvme-tcp-target/ /sys/kernel/config/nvmet/ports/1/subsystems/nvme-tcp-target
```

## Running i10

Now the target device is already initialized with NVMe over TCP.  We are going to
enable i10 scheduler and configure some parameters.

Load and enable i10 as I/O scheduler. 
```bash
# sudo modprobe i10-iosched ## if you compile i10 as kernel module
echo i10 | sudo tee -a /sys/block/nvme0n1/queue/scheduler > /dev/null
```

Configure request batch size, caravans size and delayed doorbell timeout, for example:
```bash
echo 16 | sudo tee -a /sys/block/nvme0n1/queue/iosched/batch_nr > /dev/null
echo 65536 | sudo tee -a /sys/block/nvme0n1/queue/iosched/batch_bytes > /dev/null
echo 50 | sudo tee -a /sys/block/nvme0n1/queue/iosched/batch_timeout > /dev/null
```

## Setup NVMe-TCP Host

Load corresponding kernel modules on the host.
```bash
sudo modprobe nvme-fabrics
sudo modprobe nvmet
sudo modprobe nvmet-tcp
```

Install `nvme-cli`.
```bash
sudo apt install nvme-cli
```

Connect to remote NVMe target.
```bash
sudo nvme connect -t tcp -n nvme-tcp-target -a <target-ip> -s 4420 -q nvme-tcp-host
```

If you run `nvme discover`  you should see something like below:
```bash
sudo nvme discover -t tcp -a <target-ip> -s 4420
Discovery Log Number of Records 1, Generation counter 2
=====Discovery Log Entry 0======
trtype:  tcp
adrfam:  ipv4
subtype: nvme subsystem
treq:    not specified, sq flow control disable supported
portid:  1
trsvcid: 4420
subnqn:  nvme-tcp-target
traddr:  <target-ip>
sectype: none
```

Now if you run `nvme list` or `lsblk`, you should see a new NVMe device mounted, for example:
```bash
sudo nvme list
Node             SN                   Model                                    Namespace Usage                      Format           FW Rev  
---------------- -------------------- ---------------------------------------- --------- -------------------------- ---------------- --------
/dev/nvme2n1     7c33a4f1ac57580b     Linux                                    1           1.00  TB /   1.00  TB    512   B +  0 B   5.9.0-rc
```

## FAQ

### Linux booting freezes at loading initramfs:

Modify `/etc/initramfs-tools/initramfs.conf`, using gzip as the default compression format.
```
...
COMPRESS=lz4 # change to gzip
...
```

Then update initramfs and reboot again.
```
sudo update-initframfs
```
## Reference

[i10-kernel/i10-implementation](https://github.com/i10-kernel/i10-implementation)

[i10-kernel/upstream-linux](https://github.com/i10-kernel/upstream-linux)

[How to setup NVMe/TCP with NVME-oF using KVM and QEMU](https://futurewei-cloud.github.io/ARM-Datacenter/qemu/nvme-of-tcp-vms/)
