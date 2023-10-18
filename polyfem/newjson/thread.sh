while true; do
    # top -b -n 1 | grep yiwei | grep PolyFEM_bin | tee -a $1
    if [ $# -eq 2 ]
    then
    date +"[%Y-%m-%d %T.%3N]" | tr -d '\n' >> $1
    top -b -n 1 | grep yiwei | grep PolyFEM_bin | grep $2 >> $1 
    sleep 1
    else
    date +"[%Y-%m-%d %T.%3N]" | tr -d '\n' >> $1
    top -b -n 1 | grep yiwei | grep PolyFEM_bin  >> $1 
    sleep 0.25
    fi

done
