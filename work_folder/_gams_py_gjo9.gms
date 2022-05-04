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
	map_CES_CET_norm[s,n,nn]
	map_spinp_CES_CET_norm[s,n,nn]
	map_spout_CES_CET_norm[s,n,nn]
	knout_CES_CET_norm[s,n]
	kninp_CES_CET_norm[s,n]
	spout_CES_CET_norm[s,n]
	spinp_CES_CET_norm[s,n]
	input_CES_CET_norm[s,n]
	output_CES_CET_norm[s,n]
	int_CES_CET_norm[s,n]
	map_CES1[s,n,nn]
	knot_CES1[s,n]
	branch_CES1[s,n]
	knot_o_CES1[s,n]
	knot_no_CES1[s,n]
	branch2o_CES1[s,n]
	branch2no_CES1[s,n]
	map_CET1[s,n,nn]
	knot_CET1[s,n]
	branch_CET1[s,n]
	branch_o_CET1[s,n]
	branch_no_CET1[s,n]
	exomu_CES_CET_norm[s,n,nn]
	endo_qD_CES_CET_norm[s,n]
	endo_qS_CES_CET_norm[s,n]
	endo_pS_CES_CET_norm[s,n]
;
$GDXIN %rname_8%
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
$load map_CES_CET_norm
$load map_spinp_CES_CET_norm
$load map_spout_CES_CET_norm
$load knout_CES_CET_norm
$load kninp_CES_CET_norm
$load spout_CES_CET_norm
$load spinp_CES_CET_norm
$load input_CES_CET_norm
$load output_CES_CET_norm
$load int_CES_CET_norm
$load map_CES1
$load knot_CES1
$load branch_CES1
$load knot_o_CES1
$load knot_no_CES1
$load branch2o_CES1
$load branch2no_CES1
$load map_CET1
$load knot_CET1
$load branch_CET1
$load branch_o_CET1
$load branch_no_CET1
$load exomu_CES_CET_norm
$load endo_qD_CES_CET_norm
$load endo_qS_CES_CET_norm
$load endo_pS_CES_CET_norm
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_8%
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
	eta[s,n]
	pS[t,s,n]
	pD[t,s,n]
	qS[t,s,n]
	qD[t,s,n]
	qiv_out[t,s,n]
	qiv_inp[t,s,n]
;
$GDXIN %rname_8%
$onMulti
$load mu
$load sigma
$load eta
$load pS
$load pD
$load qS
$load qD
$load qiv_out
$load qiv_inp
$GDXIN
$offMulti;




# -----------------------------------------B_CES_CET_norm_CES1----------------------------------------
#  Initialize B_CES_CET_norm_CES1 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_CES1[t,s,n];
E_zp_out_CES1[t,s,n]$(knot_o_ces1[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_CES1[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_CES1[t,s,n];
E_zp_nout_CES1[t,s,n]$(knot_no_ces1[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CES1[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_CES1[t,s,n];
E_q_out_CES1[t,s,n]$(branch2o_ces1[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_CES1[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_q_nout_CES1[t,s,n];
E_q_nout_CES1[t,s,n]$(branch2no_ces1[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_CES1[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_CES_CET_norm_CES1 model
# ----------------------------------------------------------------------------------------------------
Model B_CES_CET_norm_CES1 /
E_zp_out_CES1, E_zp_nout_CES1, E_q_out_CES1, E_q_nout_CES1
/;




# -----------------------------------------B_CES_CET_norm_CET1----------------------------------------
#  Initialize B_CES_CET_norm_CET1 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_CET1[t,s,n];
E_zp_CET1[t,s,n]$(knot_cet1[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_CET1[s,nn,n] and branch_o_CET1[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_CET1[s,nn,n] and branch_no_CET1[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_CET1[t,s,n];
E_q_out_CET1[t,s,n]$(branch_o_cet1[s,n] and txe[t]).. 	qS[t,s,n]  =E=  sum(nn$(map_CET1[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_CET1[s,nnn,nn] and branch_o_CET1[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_CET1[s,nnn,nn] and branch_no_CET1[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));
EQUATION E_q_nout_CET1[t,s,n];
E_q_nout_CET1[t,s,n]$(branch_no_cet1[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_CET1[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_CET1[s,nnn,nn] and branch_o_CET1[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_CET1[s,nnn,nn] and branch_no_CET1[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));

# ----------------------------------------------------------------------------------------------------
#  Define B_CES_CET_norm_CET1 model
# ----------------------------------------------------------------------------------------------------
Model B_CES_CET_norm_CET1 /
E_zp_CET1, E_q_out_CET1, E_q_nout_CET1
/;


qS.fx[t,s,n]$(((output_CES_CET_norm[s,n] and ( not ((endo_qS_CES_CET_norm[s,n] and t0[t])))) or (endo_qS_CES_CET_norm[s,n] and t0[t]))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_CES_CET_norm[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_CES_CET_norm[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_CES_CET_norm[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$((exomu_CES_CET_norm[s,n,nn] or ( not (exomu_CES_CET_norm[s,n,nn])))) = mu.l[s,n,nn];
pD.lo[t,s,n]$(int_CES_CET_norm[s,n]) = -inf;
pD.up[t,s,n]$(int_CES_CET_norm[s,n]) = inf;
pS.lo[t,s,n]$((((output_CES_CET_norm[s,n] and tx0[t]) or (endo_pS_CES_CET_norm[s,n] and t0[t])) or ((output_CES_CET_norm[s,n] and t0[t]) and ( not ((endo_pS_CES_CET_norm[s,n] and t0[t])))))) = -inf;
pS.up[t,s,n]$((((output_CES_CET_norm[s,n] and tx0[t]) or (endo_pS_CES_CET_norm[s,n] and t0[t])) or ((output_CES_CET_norm[s,n] and t0[t]) and ( not ((endo_pS_CES_CET_norm[s,n] and t0[t])))))) = inf;
qD.lo[t,s,n]$(((((int_CES_CET_norm[s,n] or input_CES_CET_norm[s,n]) and tx0[t]) or (endo_qD_CES_CET_norm[s,n] and t0[t])) or (((int_CES_CET_norm[s,n] or input_CES_CET_norm[s,n]) and t0[t]) and ( not ((endo_qD_CES_CET_norm[s,n] and t0[t])))))) = -inf;
qD.up[t,s,n]$(((((int_CES_CET_norm[s,n] or input_CES_CET_norm[s,n]) and tx0[t]) or (endo_qD_CES_CET_norm[s,n] and t0[t])) or (((int_CES_CET_norm[s,n] or input_CES_CET_norm[s,n]) and t0[t]) and ( not ((endo_qD_CES_CET_norm[s,n] and t0[t])))))) = inf;
qiv_inp.lo[t,s,n]$(spinp_CES_CET_norm[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_CES_CET_norm[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_CES_CET_norm[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_CES_CET_norm[s,n]) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define CES_CET_norm_B model
# ----------------------------------------------------------------------------------------------------
Model CES_CET_norm_B /
E_zp_out_CES1, E_zp_nout_CES1, E_q_out_CES1, E_q_nout_CES1, E_zp_CET1, E_q_out_CET1, E_q_nout_CET1
/;


solve CES_CET_norm_B using CNS;