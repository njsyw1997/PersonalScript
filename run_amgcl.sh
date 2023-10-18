/home/yiwei/amgcl/build/examples/solver \
-A /home/yiwei/results_null_test/2d/unstruct/refine/AMGCL_0.0/square_beam2d_2.5/bar_2d/P1/ref3/block1/Thread8/0/output/stiffness.mtx \
-f /home/yiwei/results_null_test/2d/unstruct/refine/AMGCL_0.0/square_beam2d_2.5/bar_2d/P1/ref3/block1/Thread8/0/output/rhs.mtx \
-C /home/yiwei/results_null_test/2d/unstruct/refine/AMGCL_0.0/square_beam2d_2.5/bar_2d/P1/ref3/block1/Thread8/0/output/vecpoints.mtx \
-p precond.coarsening.type="smoothed_aggregation" \
-p precond.coarsening.aggr.eps_strong=0.00 \
-p precond.relax.type="ilu0" \
-p solver.maxiter=1000 \
-p solver.type="cg" \
-b2
