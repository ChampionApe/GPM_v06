

# ----------------------------------------------------------------------------------------------------$FIX G_V01_NT_exo_always, G_V01_NT_exo_base, G_V01_T_exo_always, G_V01_T_exo_base;
# ----------------------------------------------------------------------------------------------------
$offlisting
sigma.FX[s,n]$((V01_ES[s,n]) or ((V01_NT_out[s,n]) or (V01_NT_int[s,n]))) = sigma.L[s,n];
pD.FX[s,n]$(V01_inp[s,n]) = pD.L[s,n];
qS.FX[s,n]$(V01_NT_out[s,n]) = qS.L[s,n];
mu.FX[s,n,nn]$(((V01_inp2T[s,n,nn] and V01_dur[s,n]) or (V01_T2ES[s,n,nn] and not V01_T2ESNorm[s,n,nn])) or (((V01_T2ESNorm[s,n,nn]) or (V01_inp2T[s,n,nn] and not V01_dur[s,n])) or (V01_NT_map[s,n,nn]))) = mu.L[s,n,nn];
theta.FX[s,n]$(V01_T[s,n]) = theta.L[s,n];
$onlisting

# ----------------------------------------------------------------------------------------------------$UNFIX G_V01_NT_endo_always, G_V01_NT_endo_base, G_V01_T_endo_always, G_V01_T_endo_base, G_V01_ACC_endo_base;
# ----------------------------------------------------------------------------------------------------
$offlisting
pS.lo[s,n]$(V01_NT_out[s,n]) = -inf;
pS.up[s,n]$(V01_NT_out[s,n]) = inf;
pD.lo[s,n]$((V01_T[s,n]) or ((V01_ES[s,n]) or (V01_NT_int[s,n]))) = -inf;
pD.up[s,n]$((V01_T[s,n]) or ((V01_ES[s,n]) or (V01_NT_int[s,n]))) = inf;
qD.lo[s,n]$((V01_inp[s,n]) or ((V01_T[s,n]) or (((V01_NT_inp[s,n] and not V01_NT_x[s,n]) or (V01_NT_int[s,n])) or (V01_NT_x[s,n])))) = -inf;
qD.up[s,n]$((V01_inp[s,n]) or ((V01_T[s,n]) or (((V01_NT_inp[s,n] and not V01_NT_x[s,n]) or (V01_NT_int[s,n])) or (V01_NT_x[s,n])))) = inf;
lambda.lo[s,n]$(V01_ES[s,n]) = -inf;
lambda.up[s,n]$(V01_ES[s,n]) = inf;
$onlisting

# ----------------------------------------------------------------------------------------------------
#  Define V01_B model
# ----------------------------------------------------------------------------------------------------
Model V01_B /
E_V01_NT_ZP_out, E_V01_NT_ZP_nout, E_V01_NT_qD_out, E_V01_NT_qD_nout, E_V01_T_qD, E_V01_T_pES, E_V01_T_pT, E_V01_T_sum, E_V01_ACC_inp
/;

scalars V01_B_modelstat, V01_B_solvestat;
solve V01_B using CNS;
V01_B_modelstat = V01_B.modelstat; V01_B_solvestat = V01_B.solvestat;
