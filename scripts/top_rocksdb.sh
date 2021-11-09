RDMA_TARGET=/media/rdma-target
#LOCAL_TARGET=/media/local-target
for i in 8 4 2 1 16
do
	 ./run_rocksdb.sh $RDMA_TARGET $i
	 #./run_rocksdb.sh $LOCAL_TARGET $i	
done

