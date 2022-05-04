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
	map_CES2_norm[s,n,nn]
	map_spinp_CES2_norm[s,n,nn]
	map_spout_CES2_norm[s,n,nn]
	knout_CES2_norm[s,n]
	kninp_CES2_norm[s,n]
	spout_CES2_norm[s,n]
	spinp_CES2_norm[s,n]
	input_CES2_norm[s,n]
	output_CES2_norm[s,n]
	int_CES2_norm[s,n]
	map_CES2[s,n,nn]
	knot_CES2[s,n]
	branch_CES2[s,n]
	knot_o_CES2[s,n]
	knot_no_CES2[s,n]
	branch2o_CES2[s,n]
	branch2no_CES2[s,n]
	exomu_CES2_norm[s,n,nn]
	endo_qD_CES2_norm[s,n]
	endo_qS_CES2_norm[s,n]
	endo_pS_CES2_norm[s,n]
;
$GDXIN %rname_16%
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
$load map_CES2_norm
$load map_spinp_CES2_norm
$load map_spout_CES2_norm
$load knout_CES2_norm
$load kninp_CES2_norm
$load spout_CES2_norm
$load spinp_CES2_norm
$load input_CES2_norm
$load output_CES2_norm
$load int_CES2_norm
$load map_CES2
$load knot_CES2
$load branch_CES2
$load knot_o_CES2
$load knot_no_CES2
$load branch2o_CES2
$load branch2no_CES2
$load exomu_CES2_norm
$load endo_qD_CES2_norm
$load endo_qS_CES2_norm
$load endo_pS_CES2_norm
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_16%
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
	sigma[s,n]
	pS[t,s,n]
	pD[t,s,n]
	qS[t,s,n]
	qD[t,s,n]
	eta[s,n]
	qiv_out[t,s,n]
	qiv_inp[t,s,n]
;
$GDXIN %rname_16%
$onMulti
$load mu
$load sigma
$load pS
$load pD
$load qS
$load qD
$load eta
$load qiv_out
$load qiv_inp
$GDXIN
$offMulti;




# ------------------------------------------B_CES2_norm_CES2------------------------------------------
#  Initialize B_CES2_norm_CES2 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_CES2[t,s,n];
E_zp_out_CES2[t,s,n]$(knot_o_ces2[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_CES2[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_CES2[t,s,n];
E_zp_nout_CES2[t,s,n]$(knot_no_ces2[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CES2[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_CES2[t,s,n];
E_q_out_CES2[t,s,n]$(branch2o_ces2[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_CES2[s,nn,n]), qS[t,s,nn]*mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_CES2[s,nn,nnn]), mu[s,nn,nnn] * (pS[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));
EQUATION E_q_nout_CES2[t,s,n];
E_q_nout_CES2[t,s,n]$(branch2no_ces2[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_CES2[s,nn,n]), qD[t,s,nn]*mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_CES2[s,nn,nnn]), mu[s,nn,nnn] * (pD[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));

# ----------------------------------------------------------------------------------------------------
#  Define B_CES2_norm_CES2 model
# ----------------------------------------------------------------------------------------------------
Model B_CES2_norm_CES2 /
E_zp_out_CES2, E_zp_nout_CES2, E_q_out_CES2, E_q_nout_CES2
/;


qS.fx[t,s,n]$((output_CES2_norm[s,n] and ( not ((endo_qS_CES2_norm[s,n] and t0[t]))))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_CES2_norm[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_CES2_norm[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_CES2_norm[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$(exomu_CES2_norm[s,n,nn]) = mu.l[s,n,nn];
qD.fx[t,s,n]$((((int_CES2_norm[s,n] or input_CES2_norm[s,n]) and t0[t]) and ( not ((endo_qD_CES2_norm[s,n] and t0[t]))))) = qD.l[t,s,n];
pS.fx[t,s,n]$(((output_CES2_norm[s,n] and t0[t]) and ( not ((endo_pS_CES2_norm[s,n] and t0[t]))))) = pS.l[t,s,n];
pD.lo[t,s,n]$(int_CES2_norm[s,n]) = -inf;
pD.up[t,s,n]$(int_CES2_norm[s,n]) = inf;
pS.lo[t,s,n]$(((output_CES2_norm[s,n] and tx0[t]) or (endo_pS_CES2_norm[s,n] and t0[t]))) = -inf;
pS.up[t,s,n]$(((output_CES2_norm[s,n] and tx0[t]) or (endo_pS_CES2_norm[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((int_CES2_norm[s,n] or input_CES2_norm[s,n]) and tx0[t]) or (endo_qD_CES2_norm[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((int_CES2_norm[s,n] or input_CES2_norm[s,n]) and tx0[t]) or (endo_qD_CES2_norm[s,n] and t0[t]))) = inf;
qiv_inp.lo[t,s,n]$(spinp_CES2_norm[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_CES2_norm[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_CES2_norm[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_CES2_norm[s,n]) = inf;
mu.lo[s,n,nn]$(( not (exomu_CES2_norm[s,n,nn]))) = -inf;
mu.up[s,n,nn]$(( not (exomu_CES2_norm[s,n,nn]))) = inf;
qS.lo[t,s,n]$((endo_qS_CES2_norm[s,n] and t0[t])) = -inf;
qS.up[t,s,n]$((endo_qS_CES2_norm[s,n] and t0[t])) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define CES2_norm_C model
# ----------------------------------------------------------------------------------------------------
Model CES2_norm_C /
E_zp_out_CES2, E_zp_nout_CES2, E_q_out_CES2, E_q_nout_CES2
/;


solve CES2_norm_C using CNS;