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
	map_FunkyTree[s,n,nn]
	map_spinp_FunkyTree[s,n,nn]
	map_spout_FunkyTree[s,n,nn]
	knout_FunkyTree[s,n]
	kninp_FunkyTree[s,n]
	spout_FunkyTree[s,n]
	spinp_FunkyTree[s,n]
	input_FunkyTree[s,n]
	output_FunkyTree[s,n]
	int_FunkyTree[s,n]
	map_FunkyTree_CET[s,n,nn]
	knot_FunkyTree_CET[s,n]
	branch_FunkyTree_CET[s,n]
	branch_o_FunkyTree_CET[s,n]
	branch_no_FunkyTree_CET[s,n]
	map_FunkyTree_CES[s,n,nn]
	knot_FunkyTree_CES[s,n]
	branch_FunkyTree_CES[s,n]
	knot_o_FunkyTree_CES[s,n]
	knot_no_FunkyTree_CES[s,n]
	branch2o_FunkyTree_CES[s,n]
	branch2no_FunkyTree_CES[s,n]
	exomu_FunkyTree[s,n,nn]
	endo_qD_FunkyTree[s,n]
	endo_qS_FunkyTree[s,n]
	endo_pS_FunkyTree[s,n]
;
$GDXIN %rname_24%
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
$load map_FunkyTree
$load map_spinp_FunkyTree
$load map_spout_FunkyTree
$load knout_FunkyTree
$load kninp_FunkyTree
$load spout_FunkyTree
$load spinp_FunkyTree
$load input_FunkyTree
$load output_FunkyTree
$load int_FunkyTree
$load map_FunkyTree_CET
$load knot_FunkyTree_CET
$load branch_FunkyTree_CET
$load branch_o_FunkyTree_CET
$load branch_no_FunkyTree_CET
$load map_FunkyTree_CES
$load knot_FunkyTree_CES
$load branch_FunkyTree_CES
$load knot_o_FunkyTree_CES
$load knot_no_FunkyTree_CES
$load branch2o_FunkyTree_CES
$load branch2no_FunkyTree_CES
$load exomu_FunkyTree
$load endo_qD_FunkyTree
$load endo_qS_FunkyTree
$load endo_pS_FunkyTree
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_24%
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
	qD[t,s,n]
	mu[s,n,nn]
	sigma[s,n]
	pS[t,s,n]
	pD[t,s,n]
	qS[t,s,n]
	qiv_out[t,s,n]
	qiv_inp[t,s,n]
;
$GDXIN %rname_24%
$onMulti
$load eta
$load qD
$load mu
$load sigma
$load pS
$load pD
$load qS
$load qiv_out
$load qiv_inp
$GDXIN
$offMulti;




# --------------------------------------B_FunkyTree_FunkyTree_CET-------------------------------------
#  Initialize B_FunkyTree_FunkyTree_CET equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_FunkyTree_CET[t,s,n];
E_zp_FunkyTree_CET[t,s,n]$(knot_funkytree_cet[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_FunkyTree_CET[s,nn,n] and branch_o_FunkyTree_CET[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_FunkyTree_CET[s,nn,n] and branch_no_FunkyTree_CET[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_FunkyTree_CET[t,s,n];
E_q_out_FunkyTree_CET[t,s,n]$(branch_o_funkytree_cet[s,n] and txe[t]).. 	qS[t,s,n]  =E=  sum(nn$(map_FunkyTree_CET[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_FunkyTree_CET[s,nnn,nn] and branch_o_FunkyTree_CET[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_FunkyTree_CET[s,nnn,nn] and branch_no_FunkyTree_CET[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));
EQUATION E_q_nout_FunkyTree_CET[t,s,n];
E_q_nout_FunkyTree_CET[t,s,n]$(branch_no_funkytree_cet[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_FunkyTree_CET[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_FunkyTree_CET[s,nnn,nn] and branch_o_FunkyTree_CET[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_FunkyTree_CET[s,nnn,nn] and branch_no_FunkyTree_CET[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));

# ----------------------------------------------------------------------------------------------------
#  Define B_FunkyTree_FunkyTree_CET model
# ----------------------------------------------------------------------------------------------------
Model B_FunkyTree_FunkyTree_CET /
E_zp_FunkyTree_CET, E_q_out_FunkyTree_CET, E_q_nout_FunkyTree_CET
/;




# --------------------------------------B_FunkyTree_FunkyTree_CES-------------------------------------
#  Initialize B_FunkyTree_FunkyTree_CES equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_FunkyTree_CES[t,s,n];
E_zp_out_FunkyTree_CES[t,s,n]$(knot_o_funkytree_ces[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_FunkyTree_CES[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_FunkyTree_CES[t,s,n];
E_zp_nout_FunkyTree_CES[t,s,n]$(knot_no_funkytree_ces[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_FunkyTree_CES[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_FunkyTree_CES[t,s,n];
E_q_out_FunkyTree_CES[t,s,n]$(branch2o_funkytree_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_FunkyTree_CES[s,nn,n]), qS[t,s,nn]*mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_FunkyTree_CES[s,nn,nnn]), mu[s,nn,nnn] * (pS[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));
EQUATION E_q_nout_FunkyTree_CES[t,s,n];
E_q_nout_FunkyTree_CES[t,s,n]$(branch2no_funkytree_ces[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_FunkyTree_CES[s,nn,n]), qD[t,s,nn]*mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_FunkyTree_CES[s,nn,nnn]), mu[s,nn,nnn] * (pD[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));

# ----------------------------------------------------------------------------------------------------
#  Define B_FunkyTree_FunkyTree_CES model
# ----------------------------------------------------------------------------------------------------
Model B_FunkyTree_FunkyTree_CES /
E_zp_out_FunkyTree_CES, E_zp_nout_FunkyTree_CES, E_q_out_FunkyTree_CES, E_q_nout_FunkyTree_CES
/;


qS.fx[t,s,n]$((output_FunkyTree[s,n] and ( not ((endo_qS_FunkyTree[s,n] and t0[t]))))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_FunkyTree[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_FunkyTree[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_FunkyTree[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$(exomu_FunkyTree[s,n,nn]) = mu.l[s,n,nn];
qD.fx[t,s,n]$((((int_FunkyTree[s,n] or input_FunkyTree[s,n]) and t0[t]) and ( not ((endo_qD_FunkyTree[s,n] and t0[t]))))) = qD.l[t,s,n];
pS.fx[t,s,n]$(((output_FunkyTree[s,n] and t0[t]) and ( not ((endo_pS_FunkyTree[s,n] and t0[t]))))) = pS.l[t,s,n];
pD.lo[t,s,n]$(int_FunkyTree[s,n]) = -inf;
pD.up[t,s,n]$(int_FunkyTree[s,n]) = inf;
pS.lo[t,s,n]$(((output_FunkyTree[s,n] and tx0[t]) or (endo_pS_FunkyTree[s,n] and t0[t]))) = -inf;
pS.up[t,s,n]$(((output_FunkyTree[s,n] and tx0[t]) or (endo_pS_FunkyTree[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((int_FunkyTree[s,n] or input_FunkyTree[s,n]) and tx0[t]) or (endo_qD_FunkyTree[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((int_FunkyTree[s,n] or input_FunkyTree[s,n]) and tx0[t]) or (endo_qD_FunkyTree[s,n] and t0[t]))) = inf;
qiv_inp.lo[t,s,n]$(spinp_FunkyTree[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_FunkyTree[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_FunkyTree[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_FunkyTree[s,n]) = inf;
mu.lo[s,n,nn]$(( not (exomu_FunkyTree[s,n,nn]))) = -inf;
mu.up[s,n,nn]$(( not (exomu_FunkyTree[s,n,nn]))) = inf;
qS.lo[t,s,n]$((endo_qS_FunkyTree[s,n] and t0[t])) = -inf;
qS.up[t,s,n]$((endo_qS_FunkyTree[s,n] and t0[t])) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define FunkyTree_C model
# ----------------------------------------------------------------------------------------------------
Model FunkyTree_C /
E_zp_FunkyTree_CET, E_q_out_FunkyTree_CET, E_q_nout_FunkyTree_CET, E_zp_out_FunkyTree_CES, E_zp_nout_FunkyTree_CES, E_q_out_FunkyTree_CES, E_q_nout_FunkyTree_CES
/;


solve FunkyTree_C using CNS;