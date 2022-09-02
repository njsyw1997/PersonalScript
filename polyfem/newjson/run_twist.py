import glob
import json
import math
import os
import subprocess
import tempfile
from unittest import result
import numpy as np

# Prepare the folder
discr_order_name=["P1","P2","P3","P4","Q1","Q2"]
repeat_times=1
polyfem_exe=os.path.join("/home/yiwei/polyfem_new/build", "PolyFEM_bin")
current_folder = cwd = os.getcwd()
json_folder="json"
json_list=["mat-twist.json"] 
mesh_folder="../mesh/twist"
# mesh_list=['mat100x100t40.msh', 'mat40x40.msh', 'mat150x150t40.msh', 'mat20x20.msh']
mesh_list=['mat225x225t40.msh']
# solver_list=["AMGCL","Hypre","Eigen::CholmodSupernodalLLT","Eigen::PardisoLDLT"]
solver_list=["Hypre","Eigen::CholmodSupernodalLLT","Eigen::PardisoLDLT"]
result_folder="/home/yiwei/results_new/twist"

discr_orders=[1]
blocks=[1,3]
n_refs=[0]
num_threads=[64]

# Make result directory
if (not os.path.exists(result_folder)):
    os.makedirs(result_folder)

def run_program(solver_,mesh_,j_file_,discr_order_,n_ref_,block_size_,repeat_time_,num_thread_):
    temp_path=os.path.join(result_folder,solver_,os.path.splitext(os.path.basename(mesh_))[0],os.path.splitext(os.path.basename(j_file_))[0],discr_order_name[discr_order_-1],"ref"+str(n_ref_),"block"+str(block_size_),"Thread"+str(num_thread_),str(repeat_time_))
    if (not os.path.exists(temp_path)):
        os.makedirs(temp_path)
    json_base=os.path.join(temp_path,"json")
    output_base=os.path.join(temp_path,"output")
    if (not os.path.exists(json_base)):
        os.makedirs(json_base)
    if (not os.path.exists(output_base)):
        os.makedirs(output_base)
    with open(j_file_, 'r') as f:
        json_data = json.load(f)
    json_data["solver"]["linear"]["solver"]=solver_
    json_data["geometry"][0]["mesh"] = mesh_
    # json_data["geometry"]["n_refs"] =n_ref_ #Not implemented in newest polyfem
    json_data["space"]["discr_order"] = discr_order_
    if (solver_=="AMGCL") or (solver_=="Hypre"):
        json_data["solver"]["linear"][solver_]["block_size"]=block_size_
    json_data["output"]["json"] = os.path.join(json_base, "result"+ ".json")
    json_data["output"]["paraview"]["file_name"]= os.path.join(output_base, "sim" + ".pvd")
    #----------------------------------------------------------------

    with tempfile.NamedTemporaryFile(suffix=".json") as tmp_json:
        with open(tmp_json.name, 'w') as file_temp:
            file_temp.write(json.dumps(json_data, indent=4))
        args = [polyfem_exe,
        '--json', tmp_json.name,"--max_threads", str(num_thread_),
        "--output_dir",output_base,"--ns"]
        logfile = open(output_base+"/log.txt", "w")
        cpufile=open(output_base+"/cpu.txt", "w")
        cpufile.close()
        p1=subprocess.Popen(['sh', './thread.sh',output_base+"/cpu.txt"])
        assert(os.environ["OMP_THREAD_LIMIT"]==str(num_thread_))
        subprocess.run(args,stdout=logfile,stderr=logfile)     
        # subprocess.run(args)    
        p1.kill()

if __name__ == '__main__':
    # if len(json_list)!=len(mesh_list):
    #     print("Json file and mesh file not match")
    #     exit(0)    
    for json_name in json_list:
        for mesh_name in mesh_list:
            json_file=os.path.join(json_folder,json_name)
            mesh_file=os.path.join(mesh_folder,mesh_name)
            for solver in solver_list:
                block_enable=((solver=="AMGCL") or (solver=="Hypre"))# Substitute False with (solver=="Hypre") after finishing hypre block solver
                for discr_order in discr_orders:
                    for n_ref in n_refs:
                        for block_size in blocks:
                            for num_thread in num_threads:
                                for repeat_time in range(repeat_times):
                                    if (block_size==1) or (block_enable):
                                        os.environ["OMP_THREAD_LIMIT"]= str(num_thread)
                                        print(solver+"_"+mesh_name+"_"+discr_order_name[discr_order]+"_"+"n_ref"+str(n_ref)+"_"+"Block"+str(block_size))                                        
                                        run_program(solver,mesh_file,json_file,discr_order,n_ref,block_size,repeat_time,num_thread)                                        
                                        assert(os.environ["OMP_THREAD_LIMIT"]==str(num_thread))
                         

                

