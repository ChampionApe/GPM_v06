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
	map_CET2_norm[s,n,nn]
	map_spinp_CET2_norm[s,n,nn]
	map_spout_CET2_norm[s,n,nn]
	knout_CET2_norm[s,n]
	kninp_CET2_norm[s,n]
	spout_CET2_norm[s,n]
	spinp_CET2_norm[s,n]
	input_CET2_norm[s,n]
	output_CET2_norm[s,n]
	int_CET2_norm[s,n]
	map_CET2[s,n,nn]
	knot_CET2[s,n]
	branch_CET2[s,n]
	branch_o_CET2[s,n]
	branch_no_CET2[s,n]
	exomu_CET2_norm[s,n,nn]
	endo_qD_CET2_norm[s,n]
	endo_qS_CET2_norm[s,n]
	endo_pS_CET2_norm[s,n]
;
$GDXIN %rname_20%
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
$load map_CET2_norm
$load map_spinp_CET2_norm
$load map_spout_CET2_norm
$load knout_CET2_norm
$load kninp_CET2_norm
$load spout_CET2_norm
$load spinp_CET2_norm
$load input_CET2_norm
$load output_CET2_norm
$load int_CET2_norm
$load map_CET2
$load knot_CET2
$load branch_CET2
$load branch_o_CET2
$load branch_no_CET2
$load exomu_CET2_norm
$load endo_qD_CET2_norm
$load endo_qS_CET2_norm
$load endo_pS_CET2_norm
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_20%
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
$GDXIN %rname_20%
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




# ------------------------------------------B_CET2_norm_CET2------------------------------------------
#  Initialize B_CET2_norm_CET2 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_CET2[t,s,n];
E_zp_CET2[t,s,n]$(knot_cet2[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CET2[s,nn,n] and branch_o_CET2[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_CET2[s,nn,n] and branch_no_CET2[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_CET2[t,s,n];
E_q_out_CET2[t,s,n]$(branch_o_cet2[s,n] and txe[t]).. 	qS[t,s,n]  =E=  sum(nn$(map_CET2[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_CET2[s,nnn,nn] and branch_o_CET2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_CET2[s,nnn,nn] and branch_no_CET2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));
EQUATION E_q_nout_CET2[t,s,n];
E_q_nout_CET2[t,s,n]$(branch_no_cet2[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_CET2[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_CET2[s,nnn,nn] and branch_o_CET2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_CET2[s,nnn,nn] and branch_no_CET2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));

# ----------------------------------------------------------------------------------------------------
#  Define B_CET2_norm_CET2 model
# ----------------------------------------------------------------------------------------------------
Model B_CET2_norm_CET2 /
E_zp_CET2, E_q_out_CET2, E_q_nout_CET2
/;


qS.fx[t,s,n]$((output_CET2_norm[s,n] and ( not ((endo_qS_CET2_norm[s,n] and t0[t]))))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_CET2_norm[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_CET2_norm[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_CET2_norm[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$(exomu_CET2_norm[s,n,nn]) = mu.l[s,n,nn];
qD.fx[t,s,n]$((((int_CET2_norm[s,n] or input_CET2_norm[s,n]) and t0[t]) and ( not ((endo_qD_CET2_norm[s,n] and t0[t]))))) = qD.l[t,s,n];
pS.fx[t,s,n]$(((output_CET2_norm[s,n] and t0[t]) and ( not ((endo_pS_CET2_norm[s,n] and t0[t]))))) = pS.l[t,s,n];
pD.lo[t,s,n]$(int_CET2_norm[s,n]) = -inf;
pD.up[t,s,n]$(int_CET2_norm[s,n]) = inf;
pS.lo[t,s,n]$(((output_CET2_norm[s,n] and tx0[t]) or (endo_pS_CET2_norm[s,n] and t0[t]))) = -inf;
pS.up[t,s,n]$(((output_CET2_norm[s,n] and tx0[t]) or (endo_pS_CET2_norm[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((int_CET2_norm[s,n] or input_CET2_norm[s,n]) and tx0[t]) or (endo_qD_CET2_norm[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((int_CET2_norm[s,n] or input_CET2_norm[s,n]) and tx0[t]) or (endo_qD_CET2_norm[s,n] and t0[t]))) = inf;
qiv_inp.lo[t,s,n]$(spinp_CET2_norm[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_CET2_norm[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_CET2_norm[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_CET2_norm[s,n]) = inf;
mu.lo[s,n,nn]$(( not (exomu_CET2_norm[s,n,nn]))) = -inf;
mu.up[s,n,nn]$(( not (exomu_CET2_norm[s,n,nn]))) = inf;
qS.lo[t,s,n]$((endo_qS_CET2_norm[s,n] and t0[t])) = -inf;
qS.up[t,s,n]$((endo_qS_CET2_norm[s,n] and t0[t])) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define CET2_norm_C model
# ----------------------------------------------------------------------------------------------------
Model CET2_norm_C /
E_zp_CET2, E_q_out_CET2, E_q_nout_CET2
/;


solve CET2_norm_C using CNS;