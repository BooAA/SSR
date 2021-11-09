#!/bin/bash
if [ $# != 2 ] ; then
	echo "./run_rocksdb.sh TARGET_DIR NUM_THREADS"
	exit
fi

DB_DIR=$1/db
WAL_DIR=$1/wal
TMP_DIR=/home/paslab/db-tmp
OUTPUT_DIR=/home/paslab/Benchmark/rocksdb

if [ ! -d $DB_DIR ] ; then
	mkdir $DB_DIR
fi 

if [ ! -d $WAL_DIR ] ; then
	mkdir $WAL_DIR
fi

if [ ! -d $TMP_DIR ] ; then
	mkdir $TMP_DIR
fi

if [ ! -d $OUTPUT_DIR ] ; then
	mkdir -p $OUTPUT_DIR
fi

#NUM_KEYS=1000000
NUM_KEYS=250000000
NUM_THREADS=$2

export DB_DIR WAL_DIR TMP_DIR OUTPUT_DIR NUM_KEYS NUM_THREADS

./benchmark.sh readrandom
