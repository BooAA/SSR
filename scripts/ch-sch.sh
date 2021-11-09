#!/bin/bash
if [ $# != 2 ] ; then
    echo "./ch-sch.sh target_device target_schedule"
    exit
fi

target_dev=$1
target_sch=$2

sch_file=/sys/block/$target_dev/queue/scheduler
if [ -f $sch_file ] ; then
    echo ""
    echo "Old setting of $target_dev : "
    cat $sch_file

    echo $target_sch > $sch_file
    echo ""

    echo "Current setting of $target_dev : "
    cat $sch_file
    echo ""

else
    echo "Cannot find $sch_file."
    exit
fi