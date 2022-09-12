$ONEOLCOM
$EOLCOM #
;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: load_level
# ----------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------
#  Define function: load_fixed
# ----------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


sets
	alias_set
	alias_map2
	n
	s
	t
;

alias(n,nn,nnn);

sets
	alias_[alias_set,alias_map2]
	t0[t]
	tE[t]
	tx0[t]
	txE[t]
	map_CET1[s,n,nn]
	map_spinp_CET1[s,n,nn]
	map_spout_CET1[s,n,nn]
	knout_CET1[s,n]
	kninp_CET1[s,n]
	spout_CET1[s,n]
	spinp_CET1[s,n]
	input_CET1[s,n]
	output_CET1[s,n]
	int_CET1[s,n]
	knot_CET1[s,n]
	branch_CET1[s,n]
	branch_o_CET1[s,n]
	branch_no_CET1[s,n]
	exomu_CET1[s,n,nn]
	endo_qD_CET1[s,n]
	endo_qS_CET1[s,n]
	endo_pS_CET1[s,n]
;
$GDXIN %rname_17%
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load t
$load alias_
$load t0
$load tE
$load tx0
$load txE
$load map_CET1
$load map_spinp_CET1
$load map_spout_CET1
$load knout_CET1
$load kninp_CET1
$load spout_CET1
$load spinp_CET1
$load input_CET1
$load output_CET1
$load int_CET1
$load knot_CET1
$load branch_CET1
$load branch_o_CET1
$load branch_no_CET1
$load exomu_CET1
$load endo_qD_CET1
$load endo_qS_CET1
$load endo_pS_CET1
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_17%
$onMulti
$load R_LR
$load g_LR
$load infl_LR
$load qnorm_out
$load qnorm_inp
$GDXIN
$offMulti;

variables
	eta[s,n]
	mu[s,n,nn]
	pS[t,s,n]
	pD[t,s,n]
	qS[t,s,n]
	qD[t,s,n]
	sigma[s,n]
	qiv_out[t,s,n]
	qiv_inp[t,s,n]
;
$GDXIN %rname_17%
$onMulti
$load eta
$load mu
$load pS
$load pD
$load qS
$load qD
$load sigma
$load qiv_out
$load qiv_inp
$GDXIN
$offMulti;




# ---------------------------------------------B_CET1_CET1--------------------------------------------
#  Initialize B_CET1_CET1 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_CET1[t,s,n];
E_zp_CET1[t,s,n]$(knot_cet1[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CET1[s,nn,n] and branch_o_CET1[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_CET1[s,nn,n] and branch_no_CET1[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_demand_out_CET1[t,s,n];
E_demand_out_CET1[t,s,n]$(branch_o_cet1[s,n] and txe[t]).. 		qS[t,s,n]  =E=  sum(nn$(map_CET1[s,n,nn]), mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
EQUATION E_demand_nout_CET1[t,s,n];
E_demand_nout_CET1[t,s,n]$(branch_no_cet1[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_CET1[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_CET1_CET1 model
# ----------------------------------------------------------------------------------------------------
Model B_CET1_CET1 /
E_zp_CET1, E_demand_out_CET1, E_demand_nout_CET1
/;


qS.fx[t,s,n]$((output_CET1[s,n] and ( not ((endo_qS_CET1[s,n] and t0[t]))))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_CET1[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_CET1[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_CET1[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$(exomu_CET1[s,n,nn]) = mu.l[s,n,nn];
qD.fx[t,s,n]$((((int_CET1[s,n] or input_CET1[s,n]) and t0[t]) and ( not ((endo_qD_CET1[s,n] and t0[t]))))) = qD.l[t,s,n];
pS.fx[t,s,n]$(((output_CET1[s,n] and t0[t]) and ( not ((endo_pS_CET1[s,n] and t0[t]))))) = pS.l[t,s,n];
pD.lo[t,s,n]$(int_CET1[s,n]) = -inf;
pD.up[t,s,n]$(int_CET1[s,n]) = inf;
pS.lo[t,s,n]$(((output_CET1[s,n] and tx0[t]) or (endo_pS_CET1[s,n] and t0[t]))) = -inf;
pS.up[t,s,n]$(((output_CET1[s,n] and tx0[t]) or (endo_pS_CET1[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((int_CET1[s,n] or input_CET1[s,n]) and tx0[t]) or (endo_qD_CET1[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((int_CET1[s,n] or input_CET1[s,n]) and tx0[t]) or (endo_qD_CET1[s,n] and t0[t]))) = inf;
qiv_inp.lo[t,s,n]$(spinp_CET1[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_CET1[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_CET1[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_CET1[s,n]) = inf;
mu.lo[s,n,nn]$(( not (exomu_CET1[s,n,nn]))) = -inf;
mu.up[s,n,nn]$(( not (exomu_CET1[s,n,nn]))) = inf;
qS.lo[t,s,n]$((endo_qS_CET1[s,n] and t0[t])) = -inf;
qS.up[t,s,n]$((endo_qS_CET1[s,n] and t0[t])) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define CET1_C model
# ----------------------------------------------------------------------------------------------------
Model CET1_C /
E_zp_CET1, E_demand_out_CET1, E_demand_nout_CET1
/;


solve CET1_C using CNS;