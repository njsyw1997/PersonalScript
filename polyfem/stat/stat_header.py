import os
import statistics
import json
import glob
from matplotlib import pyplot as plt
from posixpath import basename
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
import matplotlib
import csv

discr_dict={'P1':1,'P2':2,'P3':3,'P4':4,'Q1':5,'Q2':6}
# mesh_dict={"square_beam_0.5":0,"square_beam_0.25":1,"square_beam_0.1":2,"square_beam_0.05":3,"square_beam_0.025":4,"square_beam_0.01":5,"square_beam_0.005":6}
# mesh_dict={"square_beam_0.025":0,"square_beam_0.022":1,"square_beam_0.021":2,"square_beam_0.020":3,"square_beam_0.019":4,"square_beam_0.016":5,"square_beam_0.013":6,"square_beam_0.01":7}
solver_list=["AMGCL","Hypre","Eigen::CholmodSupernodalLLT","Eigen::PardisoLDLT"]
class Cal_result(object):
    # solver_name="AMGCL"
    # json_name="bar"
    # discr_order=1
    # n_ref=1
    # block_size=1
    # repeat_times=5
    # result_json=[]
    # time=np.zeros((1,repeat_times),dtype=np.double)
    # iter=np.zeros((1,repeat_times),dtype=np.int32)
    # err=np.zeros((1,repeat_times),dtype=np.double)
    def __init__(self,solver_name_,mesh_name_,json_name_,discr_order_,n_ref_,block_size_,repeat_times_,num_thread_,iter_step=1):
        self.solver_name=solver_name_
        self.mesh_name=mesh_name_
        self.json_name=json_name_
        self.discr_order=discr_order_
        self.n_ref=n_ref_
        self.block_size=block_size_
        self.repeat_times=repeat_times_
        self.num_thread=num_thread_
        self.cpu_usage=np.zeros((1,repeat_times_+1),dtype=np.double)
        self.peak_memory=0
        self.result_json=[None]*(repeat_times_+1)
        #From the json file
        self.mat_size=0
        self.nonzero=0
        self.time=np.zeros((1,repeat_times_+1),dtype=np.double)
        self.iter=np.zeros((1,repeat_times_+1),dtype=np.int32)
        self.err=np.zeros((1,repeat_times_+1),dtype=np.double)
        self.iter_step=iter_step

def get_erriter(solver_name_,json_data_): 
    #return iter,err(0 if not exist,-1 if fail)
    if solver_name_=="Eigen::CholmodSupernodalLLT":
        if json_data_["solver_info"]=="Success":
            return 0,0
        else:
            return -1,-1
    if solver_name_=="Eigen::ConjugateGradient":
        return json_data_["solver_iter"], json_data_["solver_error"]

    if solver_name_=="Eigen::PardisoLDLT":
        if json_data_["solver_info"]=="Success":
            return 0,0
        else:
            return -1,-1
    if solver_name_=="Eigen::SimplicialLDLT":
        if json_data_["solver_info"]=="Success":
            return 0,0
        else:
            return -1,-1
    if solver_name_=="Catamari":
        return 0,0
    
    if ("num_iterations" in json_data_ ) and ("final_res_norm" in json_data_):
        return json_data_["num_iterations"],json_data_["final_res_norm"]
    else:
        raise Exception("Unknown json file format")

def stats(j_file_): 
    #return solving_time,iterations,error,mat_order
    with open(j_file_, 'r') as f:
        json_data = json.load(f)
    if "solver_type" in json_data["args"]:
        solver_name=json_data["args"]["solver_type"]
    else:
        solver_name=json_data["args"]["solver"]["linear"]["solver"]
    tensor_formulation=json_data["formulation"]
    mat_size=json_data["mat_size"]
    nonzero=json_data["num_non_zero"]
    peak_memory=json_data["peak_memory"]
    time_solving=json_data["time_solving"]
    num_iterations=0
    err=0
    solver_info=json_data["solver_info"]
    if (tensor_formulation=="NeoHookean") or (tensor_formulation=="IncompressibleOgden") or (tensor_formulation=="MooneyRivlin") or (tensor_formulation=="SaintVenant") or (tensor_formulation=="UnconstrainedOgden"):
        err_list=[]
        iter_list=[]
        for temp in json_data["solver_info"][0]["info"]["internal_solver"]:
            tempiter,temperr=get_erriter(solver_name,temp)
            err_list.append(temperr)
            iter_list.append(tempiter)
        err=statistics.mean(err_list)
        num_iterations=sum(iter_list)
        iter_steps=int(json_data["solver_info"][0]["info"]["iterations"])
        # Need to verify the mat_order
        return time_solving,num_iterations,err,mat_size,nonzero,peak_memory,iter_steps
    else:
        tempiter,temperr=get_erriter(solver_name,solver_info)
        return time_solving,tempiter,temperr,mat_size,nonzero,peak_memory,1
    # Add "if" for more problems  
                  
def read_cpu_usage(file):
    with open(file, "r") as f:
        lis = [line.split() for line in f] 
        l=len(list(enumerate(lis)))
        if(l==0):
            return -1
        else:
            usage=np.zeros(l,dtype=np.float64)
            for i, line in enumerate(lis):
                usage[i]=float(line[-4])/100
            return usage.max()

def data_collect(path_lists,start_index):
    result_list=[]
    fail_list=[]
    for path_list in path_lists:
        for path in path_list:
            temp_path=path.split('/')
            solver_name=temp_path[0+start_index]
            mesh_name=temp_path[1+start_index]
            json_name=temp_path[2+start_index]
            discr_order=discr_dict[temp_path[3+start_index]]
            n_ref=int(temp_path[4+start_index][-1])
            block_size=int(temp_path[5+start_index][-1])
            if len(temp_path)==7+start_index:
                num_thread=int(temp_path[6+start_index].strip("Thread"))
            else:
                num_thread=-1
            repeat_path=glob.glob(os.path.join(path,"*"))
            repeat_times=max(map(int,map(os.path.basename,repeat_path)))
            temp_result=Cal_result(solver_name,mesh_name,json_name,discr_order,n_ref,block_size,repeat_times,num_thread)
            exist_bool=True
            for inner_path in repeat_path:
                repeat_time=int(os.path.basename(inner_path))
                json_path=os.path.join(inner_path,"json","result.json")
                cpu_path=os.path.join(inner_path,"output","cpu.txt")
                if os.path.exists(cpu_path):
                    if os.path.exists(json_path):
                        temp_result.time[0,repeat_time],temp_result.iter[0,repeat_time],temp_result.err[0,repeat_time],temp_result.mat_size,temp_result.nonzero,temp_result.peak_memory,temp_result.iter_step=stats(json_path)
                        temp_result.result_json[repeat_time]=inner_path
                        temp_result.cpu_usage[0,repeat_time]=read_cpu_usage(cpu_path)
                    else:
                        fail_list.append(inner_path)
                        # print(inner_path+" is empty, corresponding test failed")
                        exist_bool=False
                else:
                    if os.path.exists(json_path):
                        temp_result.time[0,repeat_time],temp_result.iter[0,repeat_time],temp_result.err[0,repeat_time],temp_result.mat_size,temp_result.nonzero,temp_result.peak_memory,temp_result.iter_step=stats(json_path)
                        temp_result.result_json[repeat_time]=inner_path
                        temp_result.cpu_usage[0,repeat_time]=0
                    else:
                        fail_list.append(inner_path)
                        # print(inner_path+" is empty, corresponding test failed")
                        exist_bool=False                    
            if exist_bool:
                result_list.append(temp_result)
    return result_list,fail_list    

def df_create(result_list):
    columns=["Scene","Solver","Mesh","Mat Size","Nonzeros","discr_order","n_ref","Block Size","Num Thread","Peak Memory","CPU Usage","Runtime","SD","Error","Iterations","steps"]
    result_df=pd.DataFrame(columns=columns)
    for result,i in zip(result_list,range(len(result_list))):
        df_row={}
        df_row["Scene"]=result.json_name
        df_row["Mesh"]=result.mesh_name
        df_row["Mat Size"]=result.mat_size
        df_row["Nonzeros"]=result.nonzero
        df_row["Solver"]=result.solver_name
        df_row["discr_order"]=result.discr_order
        df_row["n_ref"]=result.n_ref
        df_row["Block Size"]=result.block_size
        df_row["Num Thread"]=result.num_thread
        df_row["CPU Usage"]=np.max(result.cpu_usage,axis=1)
        df_row["Peak Memory"]=result.peak_memory
        df_row["Runtime"]=np.average(result.time,axis=1)
        df_row["SD"]=np.std(result.time,axis=1)
        df_row["Error"]=np.average(result.err,axis=1)
        df_row["Iterations"]=np.average(result.iter,axis=1)
        df_row["steps"]=result.iter_step
        result_df.loc[i]=df_row
    return result_df        