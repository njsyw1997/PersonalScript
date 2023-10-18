import glob
import json
import math
import os
import subprocess
import tempfile
import numpy as np

# Prepare the folder
discr_order_name=["P1","P2","P3","P4","Q1","Q2"]
repeat_times=1
polyfem_exe=os.path.join("/home/yiwei/polyfem/build", "PolyFEM_bin")
current_folder = cwd = os.getcwd()
json_folder="json"
# json_list=["bar_sa_new_material.json"] 
json_list=["bar_sa.json"]
# mesh_folder="../mesh/bar/structed/tet"
# mesh_list=["square_beam_structed_45.msh"]
# mesh_folder="/home/yiwei/test_mesh/3d/unstruct"
mesh_folder="/home/yiwei/test_mesh/3d/unstruct"
mesh_list=[os.listdir(mesh_folder)[0]]
# mesh_list=["sphere_0.03.msh","sphere_0.05.msh"]

# mesh_list=["square_beam_2.50.msh"]
# mesh_list=["square_beam_struct_40.msh"]
# mesh_list=["square_beam2d_2.5.msh"]
# mesh_list=["square_beam2d_struct_5.msh"]

# solver_list=["AMGCL","Hypre","Eigen::CholmodSupernodalLLT","Eigen::PardisoLDLT"]
solver_list=["Eigen::PardisoLLT"]
# result_folder="/home/yiwei/result_new_material/novec/unconstrainedOgden"
result_folder="/home/yiwei/test_bar/tmp"

eps_strongs=[0.00] # Check if AMGCL's preconditioner is Smoothed Aggregation
discr_orders=[1]
num_threads=[8]
blocks=[3]
n_refs=[0,1]



# Make result directory
if (not os.path.exists(result_folder)):
    os.makedirs(result_folder)

def run_program(solver_,mesh_,j_file_,discr_order_,n_ref_,block_size_,repeat_time_,num_thread_,eps_strong_=None):
    if eps_strong_==None:
        temp_path=os.path.join(result_folder,solver_,os.path.splitext(os.path.basename(mesh_))[0],os.path.splitext(os.path.basename(j_file_))[0],discr_order_name[discr_order_-1],"ref"+str(n_ref_),"block"+str(block_size_),"Thread"+str(num_thread_),str(repeat_time_))
    else:
        temp_path=os.path.join(result_folder,solver_+"_"+str(eps_strong_),os.path.splitext(os.path.basename(mesh_))[0],os.path.splitext(os.path.basename(j_file_))[0],discr_order_name[discr_order_-1],"ref"+str(n_ref_),"block"+str(block_size_),"Thread"+str(num_thread_),str(repeat_time_))
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
    if eps_strong_!=None:
        json_data["solver"]["linear"]["AMGCL"]["precond"]["coarsening"]["aggr"]["eps_strong"]=eps_strong_
    json_data["solver"]["linear"]["solver"]=solver_
    json_data["geometry"]["mesh"] = mesh_
    json_data["geometry"]["n_refs"] =n_ref_ 
    json_data["space"]["discr_order"] = discr_order_
    if (solver_=="AMGCL") or (solver_=="Hypre") or (solver_=="Trilinos"):
        json_data["solver"]["linear"][solver_]["block_size"]=block_size_
    json_data["output"]["json"] = os.path.join(json_base, "result"+ ".json")
    # json_data["output"]["data"]["stiffness_mat"] = os.path.join(output_base, "stiffness.mtx")
    # json_data["output"]["data"]["full_mat"] = output_base
    # json_data["output"]["data"]["solution"] = os.path.join(output_base, "solution.mtx")
    if((discr_order_==1) and (n_ref_==0)):
        pass
        # json_data["output"]["paraview"]["file_name"] = os.path.join(output_base, "sim.vtu")
    #     json_data["output"]["data"]["full_mat"] = os.path.join(output_base, "full.mat")
    #     json_data["output"]["paraview"]["file_name"] = "sim.vtu"
    #----------------------------------------------------------------

    with tempfile.NamedTemporaryFile(suffix=".json") as tmp_json:
        with open(tmp_json.name, 'w') as file_temp:
            file_temp.write(json.dumps(json_data, indent=4))
        args = [polyfem_exe,
        '--json', tmp_json.name,"--max_threads", str(num_thread_),
        "--output_dir",output_base,"--no_strict_validation"]
        logfile = open(output_base+"/log.txt", "w")
        cpufile=open(output_base+"/cpu.txt", "w")
        cpufile.close()
        
        assert(os.environ["OMP_NUM_THREADS"]==str(num_thread_))
        p1=subprocess.Popen(args,stdout=logfile,stderr=logfile)  
        p2=subprocess.Popen(['sh', './thread.sh',output_base+"/cpu.txt",str(p1.pid)]) 
        while p1.poll() is None:
            pass
        # subprocess.run(args)    
        p2.kill()

if __name__ == '__main__':
    # if len(json_list)!=len(mesh_list):
    #     print("Json file and mesh file not match")
    #     exit(0)    
    for json_name in json_list:
        for mesh_name in mesh_list:
            json_file=os.path.join(json_folder,json_name)
            mesh_file=os.path.join(mesh_folder,mesh_name)
            for solver in solver_list:
                # block_enable=((solver=="AMGCL") or (solver=="Hypre") or (solver=="Trilinos"))# Substitute False with (solver=="Hypre") after finishing hypre block solver
                eps_strong_enable=(solver=="AMGCL") and (eps_strongs)
                for discr_order in discr_orders:
                    for n_ref in n_refs:
                        for block_size in blocks:
                            for num_thread in num_threads:
                                for repeat_time in range(repeat_times):
                                    if eps_strong_enable:
                                        for eps_strong in eps_strongs:
                                            os.environ["OMP_NUM_THREADS"]= str(num_thread)
                                            print(solver+"_"+mesh_name+"_"+discr_order_name[discr_order-1]+"_"+"n_ref"+str(n_ref)+"_"+"Block"+str(block_size)+"_eps_strong="+str(eps_strong))
                                            run_program(solver,mesh_file,json_file,discr_order,n_ref,block_size,repeat_time,num_thread,eps_strong_=eps_strong)
                                            assert(os.environ["OMP_NUM_THREADS"]==str(num_thread))
                                            os.chdir(current_folder)
                                    else:                                            
                                        os.environ["OMP_NUM_THREADS"]= str(num_thread)
                                        print(solver+"_"+mesh_name+"_"+discr_order_name[discr_order-1]+"_"+"n_ref"+str(n_ref)+"_"+"Block"+str(block_size))
                                        run_program(solver,mesh_file,json_file,discr_order,n_ref,block_size,repeat_time,num_thread)
                                        assert(os.environ["OMP_NUM_THREADS"]==str(num_thread))
                                        os.chdir(current_folder)