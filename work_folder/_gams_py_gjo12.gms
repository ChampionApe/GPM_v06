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
	map_ExtremeFunk[s,n,nn]
	map_spinp_ExtremeFunk[s,n,nn]
	map_spout_ExtremeFunk[s,n,nn]
	knout_ExtremeFunk[s,n]
	kninp_ExtremeFunk[s,n]
	spout_ExtremeFunk[s,n]
	spinp_ExtremeFunk[s,n]
	input_ExtremeFunk[s,n]
	output_ExtremeFunk[s,n]
	int_ExtremeFunk[s,n]
	map_ExtremeF1[s,n,nn]
	knot_ExtremeF1[s,n]
	branch_ExtremeF1[s,n]
	knot_o_ExtremeF1[s,n]
	knot_no_ExtremeF1[s,n]
	branch2o_ExtremeF1[s,n]
	branch2no_ExtremeF1[s,n]
	map_ExtremeF2[s,n,nn]
	knot_ExtremeF2[s,n]
	branch_ExtremeF2[s,n]
	branch_o_ExtremeF2[s,n]
	branch_no_ExtremeF2[s,n]
	exomu_ExtremeFunk[s,n,nn]
	endo_qD_ExtremeFunk[s,n]
	endo_qS_ExtremeFunk[s,n]
	endo_pS_ExtremeFunk[s,n]
;
$GDXIN %rname_11%
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
$load map_ExtremeFunk
$load map_spinp_ExtremeFunk
$load map_spout_ExtremeFunk
$load knout_ExtremeFunk
$load kninp_ExtremeFunk
$load spout_ExtremeFunk
$load spinp_ExtremeFunk
$load input_ExtremeFunk
$load output_ExtremeFunk
$load int_ExtremeFunk
$load map_ExtremeF1
$load knot_ExtremeF1
$load branch_ExtremeF1
$load knot_o_ExtremeF1
$load knot_no_ExtremeF1
$load branch2o_ExtremeF1
$load branch2no_ExtremeF1
$load map_ExtremeF2
$load knot_ExtremeF2
$load branch_ExtremeF2
$load branch_o_ExtremeF2
$load branch_no_ExtremeF2
$load exomu_ExtremeFunk
$load endo_qD_ExtremeFunk
$load endo_qS_ExtremeFunk
$load endo_pS_ExtremeFunk
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_11%
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
$GDXIN %rname_11%
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




# ---------------------------------------B_ExtremeFunk_ExtremeF1--------------------------------------
#  Initialize B_ExtremeFunk_ExtremeF1 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_ExtremeF1[t,s,n];
E_zp_out_ExtremeF1[t,s,n]$(knot_o_extremef1[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_ExtremeF1[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_ExtremeF1[t,s,n];
E_zp_nout_ExtremeF1[t,s,n]$(knot_no_extremef1[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_ExtremeF1[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_ExtremeF1[t,s,n];
E_q_out_ExtremeF1[t,s,n]$(branch2o_extremef1[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_ExtremeF1[s,nn,n]), qS[t,s,nn]*mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_ExtremeF1[s,nn,nnn]), mu[s,nn,nnn] * (pS[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));
EQUATION E_q_nout_ExtremeF1[t,s,n];
E_q_nout_ExtremeF1[t,s,n]$(branch2no_extremef1[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_ExtremeF1[s,nn,n]), qD[t,s,nn]*mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_ExtremeF1[s,nn,nnn]), mu[s,nn,nnn] * (pD[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));

# ----------------------------------------------------------------------------------------------------
#  Define B_ExtremeFunk_ExtremeF1 model
# ----------------------------------------------------------------------------------------------------
Model B_ExtremeFunk_ExtremeF1 /
E_zp_out_ExtremeF1, E_zp_nout_ExtremeF1, E_q_out_ExtremeF1, E_q_nout_ExtremeF1
/;




# ---------------------------------------B_ExtremeFunk_ExtremeF2--------------------------------------
#  Initialize B_ExtremeFunk_ExtremeF2 equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_ExtremeF2[t,s,n];
E_zp_ExtremeF2[t,s,n]$(knot_extremef2[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_ExtremeF2[s,nn,n] and branch_o_ExtremeF2[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_ExtremeF2[s,nn,n] and branch_no_ExtremeF2[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_ExtremeF2[t,s,n];
E_q_out_ExtremeF2[t,s,n]$(branch_o_extremef2[s,n] and txe[t]).. 	qS[t,s,n]  =E=  sum(nn$(map_ExtremeF2[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_ExtremeF2[s,nnn,nn] and branch_o_ExtremeF2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_ExtremeF2[s,nnn,nn] and branch_no_ExtremeF2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));
EQUATION E_q_nout_ExtremeF2[t,s,n];
E_q_nout_ExtremeF2[t,s,n]$(branch_no_extremef2[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_ExtremeF2[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_ExtremeF2[s,nnn,nn] and branch_o_ExtremeF2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_ExtremeF2[s,nnn,nn] and branch_no_ExtremeF2[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));

# ----------------------------------------------------------------------------------------------------
#  Define B_ExtremeFunk_ExtremeF2 model
# ----------------------------------------------------------------------------------------------------
Model B_ExtremeFunk_ExtremeF2 /
E_zp_ExtremeF2, E_q_out_ExtremeF2, E_q_nout_ExtremeF2
/;


qS.fx[t,s,n]$(((output_ExtremeFunk[s,n] and ( not ((endo_qS_ExtremeFunk[s,n] and t0[t])))) or (endo_qS_ExtremeFunk[s,n] and t0[t]))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_ExtremeFunk[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_ExtremeFunk[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_ExtremeFunk[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$((exomu_ExtremeFunk[s,n,nn] or ( not (exomu_ExtremeFunk[s,n,nn])))) = mu.l[s,n,nn];
pD.lo[t,s,n]$(int_ExtremeFunk[s,n]) = -inf;
pD.up[t,s,n]$(int_ExtremeFunk[s,n]) = inf;
pS.lo[t,s,n]$((((output_ExtremeFunk[s,n] and tx0[t]) or (endo_pS_ExtremeFunk[s,n] and t0[t])) or ((output_ExtremeFunk[s,n] and t0[t]) and ( not ((endo_pS_ExtremeFunk[s,n] and t0[t])))))) = -inf;
pS.up[t,s,n]$((((output_ExtremeFunk[s,n] and tx0[t]) or (endo_pS_ExtremeFunk[s,n] and t0[t])) or ((output_ExtremeFunk[s,n] and t0[t]) and ( not ((endo_pS_ExtremeFunk[s,n] and t0[t])))))) = inf;
qD.lo[t,s,n]$(((((int_ExtremeFunk[s,n] or input_ExtremeFunk[s,n]) and tx0[t]) or (endo_qD_ExtremeFunk[s,n] and t0[t])) or (((int_ExtremeFunk[s,n] or input_ExtremeFunk[s,n]) and t0[t]) and ( not ((endo_qD_ExtremeFunk[s,n] and t0[t])))))) = -inf;
qD.up[t,s,n]$(((((int_ExtremeFunk[s,n] or input_ExtremeFunk[s,n]) and tx0[t]) or (endo_qD_ExtremeFunk[s,n] and t0[t])) or (((int_ExtremeFunk[s,n] or input_ExtremeFunk[s,n]) and t0[t]) and ( not ((endo_qD_ExtremeFunk[s,n] and t0[t])))))) = inf;
qiv_inp.lo[t,s,n]$(spinp_ExtremeFunk[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_ExtremeFunk[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_ExtremeFunk[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_ExtremeFunk[s,n]) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define ExtremeFunk_B model
# ----------------------------------------------------------------------------------------------------
Model ExtremeFunk_B /
E_zp_out_ExtremeF1, E_zp_nout_ExtremeF1, E_q_out_ExtremeF1, E_q_nout_ExtremeF1, E_zp_ExtremeF2, E_q_out_ExtremeF2, E_q_nout_ExtremeF2
/;


solve ExtremeFunk_B using CNS;