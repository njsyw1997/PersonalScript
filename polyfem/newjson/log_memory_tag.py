from datetime import datetime
import numpy as np
class memory_tag:
    def __init__(self):
        self.time=None
        self.memory=0
def read_memory(str):
    if str[-1]=='g':
        return float(str[:-1])
    elif str[-1]=='m':
        return float(str[:-1])/1024
    else:
        return float(str)/1024/1024
    
def find_interval(memory_tags,time,i):
    if i==len(memory_tags):
        return i-1,memory_tags[i-1].memory
    if memory_tags[i].time>time:
        j=i
        for _ in range(i):
            j=j-1
            if memory_tags[j].time<time:               
                break
        return i, np.amax(list(map(lambda x: x.memory, memory_tags[j:i])))
    else:
        return find_interval(memory_tags,time,i+1)

def log_memory_tag(log_file,cpu_file):
    new_log_file=log_file[:-4]+"_memory_tag.txt"
    memory_tags=[]
    with open(cpu_file,'r') as f:
        lis = f.readlines()
        l=len(list(enumerate(lis)))
        if(l==0):
            # return -1
            exit()
        else:
            for _, line in enumerate(lis):
                tmp_tag=memory_tag()
                tmp_tag.time=datetime.strptime(line[1:].split("]")[0], '%Y-%m-%d %H:%M:%S.%f')
                if len(line.split())>7:
                    tmp_tag.memory=read_memory(line.split()[-7])
                memory_tags.append(tmp_tag)
    tag_index=0
    prev_index=0
    max_index=0
    max_line=""
    inc_memory=0
    memory_lists=[]
    memory_lists.append(0)
    with open(log_file,'r') as f:
        with open(new_log_file,'w') as f2:
            lis = f.readlines()
            l=len(list(enumerate(lis)))
            if(l==0):
                # return -1
                exit()
            else:
                for i, line in enumerate(lis):
                    if line[0]!='[':
                        continue
                    tmp_time=datetime.strptime(line[1:].split("]")[0], '%Y-%m-%d %H:%M:%S.%f')
                    tag_index,_=find_interval(memory_tags,tmp_time,tag_index)
                    tmp_memory=np.amax(list(map(lambda x: x.memory, memory_tags[prev_index:tag_index+1])))
                    prev_index=tag_index
                    newline=str("[%.1f" % tmp_memory)+'g]'+line
                    memory_lists.append(tmp_memory)
                    if memory_lists[-1]-memory_lists[-2]>inc_memory:
                        inc_memory=memory_lists[-1]-memory_lists[-2]
                        max_index=i
                        max_line=newline
                    f2.write(newline)
    return max_index, max_line
if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv)!=2:
        print("Usage: python log_memory_tag.py base_path")
        exit()
    for i in range(1,len(sys.argv)):
        if not os.path.exists(sys.argv[i]):
            print("Path not exist: "+sys.argv[i])
            exit()
        else:
            base_path=str(sys.argv[i])
            log_file=base_path+"/log.txt"
            cpu_file=base_path+"/cpu.txt"
            index,line=log_memory_tag(log_file,cpu_file)
            print("base path: "+base_path)
            print("Max memory increase line number: "+str(index))
            print(line)
            
