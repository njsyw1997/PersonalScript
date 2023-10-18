import os
import subprocess
cpu_path="/home/yiwei/test_bar/tmp/Eigen::PardisoLLT/square_beam_1.25/bar_sa/P1/ref1/block3/Thread8/0/output/polysolve_cpu.txt"
cpufile=open(cpu_path, "w")
cpufile.close()
p1=subprocess.Popen(['sh', './thread.sh',cpu_path])
polysolve_test="/home/yiwei/polysolve/build/tests/unit_tests"
args=[polysolve_test]
subprocess.run(args)     
# subprocess.run(args)    
p1.kill()