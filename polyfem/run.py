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
polyfem_exe=os.path.join("/home/yiwei/polyfem/build", "PolyFEM_bin")
current_folder = cwd = os.getcwd()
json_folder="json"
json_list=["bar.json"] 
mesh_folder="mesh/square"
# mesh_list=os.listdir(mesh_folder)
# mesh_list=["square_beam_0.021.msh","square_beam_0.020.msh","square_beam_0.019.msh","square_beam_0.016.msh","square_beam_0.013.msh"]
mesh_list=["square_beam_0.021.msh"]
# solver_list=["AMGCL","Hypre","Eigen::CholmodSupernodalLLT","Eigen::PardisoLDLT"]
solver_list=["AMGCL","Eigen::CholmodSupernodalLLT"]
result_folder=os.path.join(current_folder,"results","cholmod")

discr_orders=[2]
blocks=[1]
n_refs=[1]

# Make result directory
if (not os.path.exists(result_folder)):
    os.makedirs(result_folder)

def run_program(solver_,mesh_,j_file_,discr_order_,n_ref_,block_size_,repeat_time_):
    temp_path=os.path.join(result_folder,solver_+"_Parallel",os.path.splitext(os.path.basename(mesh_))[0],os.path.splitext(os.path.basename(j_file_))[0],discr_order_name[discr_order_],"ref"+str(n_ref_),"block"+str(block_size_),str(repeat_time_))
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
    if "time_sequence" in json_data["export"]:
        json_data["export"]["time_sequence"]=os.path.join(output_base, "sim" + ".pvd")
    json_data["solver_type"]=solver_
    json_data["mesh"] = mesh_
    json_data["n_refs"] =n_ref_
    json_data["discr_order"] = discr_order_
    if (solver_=="AMGCL") or (solver_=="Hypre"):
        json_data["solver_params"][solver_]["block_size"]=block_size_
    json_data["output"] = os.path.join(json_base, "result"+ ".json")
    json_data["export"]["paraview"]= os.path.join(output_base, "sol_" + ".vtu")
    #----------------------------------------------------------------

    with tempfile.NamedTemporaryFile(suffix=".json") as tmp_json:
        with open(tmp_json.name, 'w') as file_temp:
            file_temp.write(json.dumps(json_data, indent=4))

        # args = [polyfem_exe,
        #         '--json', tmp_json.name,"--max_threads", "32",
        #         '--cmd',"--log_file", output_base+"/log.txt"]
        args = [polyfem_exe,
        '--json', tmp_json.name,"--max_threads", "32",
        '--cmd',"--output_dir",output_base,"--log_file", output_base+"/log.txt","--log_level","trace"]

        subprocess.run(args) 

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
                            for repeat_time in range(repeat_times):
                                if (block_size==1) or (block_enable):
                                    run_program(solver,mesh_file,json_file,discr_order,n_ref,block_size,repeat_time)

                

