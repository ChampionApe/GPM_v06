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
;

alias(n,nn,nnn);

sets
	alias_[alias_set,alias_map2]
	t[t]
	t0[t]
	tE[t]
	tx0[t]
	txE[t]
	map_CET2[s,n,nn]
	map_spinp_CET2[s,n,nn]
	map_spout_CET2[s,n,nn]
	knout_CET2[s,n]
	kninp_CET2[s,n]
	spout_CET2[s,n]
	spinp_CET2[s,n]
	input_CET2[s,n]
	output_CET2[s,n]
	int_CET2[s,n]
	knot_CET2[s,n]
	branch_CET2[s,n]
	branch_o_CET2[s,n]
	branch_no_CET2[s,n]
	exomu_CET2[s,n,nn]
	endo_qD_CET2[s,n]
	endo_qS_CET2[s,n]
	endo_pS_CET2[s,n]
;
$GDXIN %rname_4%
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load alias_
$load t
$load t0
$load tE
$load tx0
$load txE
$load map_CET2
$load map_spinp_CET2
$load map_spout_CET2
$load knout_CET2
$load kninp_CET2
$load spout_CET2
$load spinp_CET2
$load input_CET2
$load output_CET2
$load int_CET2
$load knot_CET2
$load branch_CET2
$load branch_o_CET2
$load branch_no_CET2
$load exomu_CET2
$load endo_qD_CET2
$load endo_qS_CET2
$load endo_pS_CET2
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_4%
$onMulti
$load R_LR
$load g_LR
$load infl_LR
$load qnorm_out
$load qnorm_inp
$GDXIN
$offMulti;

variables
	mu[s,n,nn]
	qD[t,s,n]
	eta[s,n]
	pS[t,s,n]
	pD[t,s,n]
	qS[t,s,n]
	sigma[s,n]
	qiv_out[t,s,n]
	qiv_inp[t,s,n]
;
$GDXIN %rname_4%
$onMulti
$load mu
$load qD
$load eta
$load pS
$load pD
$load qS
$load sigma
$load qiv_out
$load qiv_inp
$GDXIN
$offMulti;




# ---------------------------------------------B_CET2_CET2--------------------------------------------
#  Initialize B_CET2_CET2 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_CET2[t,s,n];
E_zp_CET2[t,s,n]$(knot_cet2[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CET2[s,nn,n] and branch_o_CET2[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_CET2[s,nn,n] and branch_no_CET2[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_demand_out_CET2[t,s,n];
E_demand_out_CET2[t,s,n]$(branch_o_cet2[s,n] and txe[t]).. 		qS[t,s,n]  =E=  sum(nn$(map_CET2[s,n,nn]), mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
EQUATION E_demand_nout_CET2[t,s,n];
E_demand_nout_CET2[t,s,n]$(branch_no_cet2[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_CET2[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_CET2_CET2 model
# ----------------------------------------------------------------------------------------------------
Model B_CET2_CET2 /
E_zp_CET2, E_demand_out_CET2, E_demand_nout_CET2
/;


qS.fx[t,s,n]$(((output_CET2[s,n] and ( not ((endo_qS_CET2[s,n] and t0[t])))) or (endo_qS_CET2[s,n] and t0[t]))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_CET2[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_CET2[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_CET2[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$((exomu_CET2[s,n,nn] or ( not (exomu_CET2[s,n,nn])))) = mu.l[s,n,nn];
pD.lo[t,s,n]$(int_CET2[s,n]) = -inf;
pD.up[t,s,n]$(int_CET2[s,n]) = inf;
pS.lo[t,s,n]$((((output_CET2[s,n] and tx0[t]) or (endo_pS_CET2[s,n] and t0[t])) or ((output_CET2[s,n] and t0[t]) and ( not ((endo_pS_CET2[s,n] and t0[t])))))) = -inf;
pS.up[t,s,n]$((((output_CET2[s,n] and tx0[t]) or (endo_pS_CET2[s,n] and t0[t])) or ((output_CET2[s,n] and t0[t]) and ( not ((endo_pS_CET2[s,n] and t0[t])))))) = inf;
qD.lo[t,s,n]$(((((int_CET2[s,n] or input_CET2[s,n]) and tx0[t]) or (endo_qD_CET2[s,n] and t0[t])) or (((int_CET2[s,n] or input_CET2[s,n]) and t0[t]) and ( not ((endo_qD_CET2[s,n] and t0[t])))))) = -inf;
qD.up[t,s,n]$(((((int_CET2[s,n] or input_CET2[s,n]) and tx0[t]) or (endo_qD_CET2[s,n] and t0[t])) or (((int_CET2[s,n] or input_CET2[s,n]) and t0[t]) and ( not ((endo_qD_CET2[s,n] and t0[t])))))) = inf;
qiv_inp.lo[t,s,n]$(spinp_CET2[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_CET2[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_CET2[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_CET2[s,n]) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define CET2_B model
# ----------------------------------------------------------------------------------------------------
Model CET2_B /
E_zp_CET2, E_demand_out_CET2, E_demand_nout_CET2
/;


solve CET2_B using CNS;