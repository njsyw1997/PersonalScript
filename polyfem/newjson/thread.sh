while true; do
    # top -b -n 1 | grep yiwei | grep PolyFEM_bin | tee -a $1
    top -b -n 1 | grep yiwei | grep PolyFEM_bin >> $1
    sleep 1
done