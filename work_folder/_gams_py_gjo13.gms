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
	map_FunnyName[s,n,nn]
	map_spinp_FunnyName[s,n,nn]
	map_spout_FunnyName[s,n,nn]
	knout_FunnyName[s,n]
	kninp_FunnyName[s,n]
	spout_FunnyName[s,n]
	spinp_FunnyName[s,n]
	input_FunnyName[s,n]
	output_FunnyName[s,n]
	int_FunnyName[s,n]
	map_FunnyNameInp[s,n,nn]
	knot_FunnyNameInp[s,n]
	branch_FunnyNameInp[s,n]
	knot_o_FunnyNameInp[s,n]
	knot_no_FunnyNameInp[s,n]
	branch2o_FunnyNameInp[s,n]
	branch2no_FunnyNameInp[s,n]
	map_FunnyNameOut[s,n,nn]
	knot_FunnyNameOut[s,n]
	branch_FunnyNameOut[s,n]
	branch_o_FunnyNameOut[s,n]
	branch_no_FunnyNameOut[s,n]
	exomu_FunnyName[s,n,nn]
	endo_qD_FunnyName[s,n]
	endo_qS_FunnyName[s,n]
	endo_pS_FunnyName[s,n]
;
$GDXIN %rname_12%
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
$load map_FunnyName
$load map_spinp_FunnyName
$load map_spout_FunnyName
$load knout_FunnyName
$load kninp_FunnyName
$load spout_FunnyName
$load spinp_FunnyName
$load input_FunnyName
$load output_FunnyName
$load int_FunnyName
$load map_FunnyNameInp
$load knot_FunnyNameInp
$load branch_FunnyNameInp
$load knot_o_FunnyNameInp
$load knot_no_FunnyNameInp
$load branch2o_FunnyNameInp
$load branch2no_FunnyNameInp
$load map_FunnyNameOut
$load knot_FunnyNameOut
$load branch_FunnyNameOut
$load branch_o_FunnyNameOut
$load branch_no_FunnyNameOut
$load exomu_FunnyName
$load endo_qD_FunnyName
$load endo_qS_FunnyName
$load endo_pS_FunnyName
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_out[t,s,n]
	qnorm_inp[t,s,n]
;
$GDXIN %rname_12%
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
$GDXIN %rname_12%
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




# --------------------------------------B_FunnyName_FunnyNameInp--------------------------------------
#  Initialize B_FunnyName_FunnyNameInp equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_FunnyNameInp[t,s,n];
E_zp_out_FunnyNameInp[t,s,n]$(knot_o_funnynameinp[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_FunnyNameInp[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_FunnyNameInp[t,s,n];
E_zp_nout_FunnyNameInp[t,s,n]$(knot_no_funnynameinp[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_FunnyNameInp[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_FunnyNameInp[t,s,n];
E_q_out_FunnyNameInp[t,s,n]$(branch2o_funnynameinp[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_FunnyNameInp[s,nn,n]), qS[t,s,nn]*mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_FunnyNameInp[s,nn,nnn]), mu[s,nn,nnn] * (pS[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));
EQUATION E_q_nout_FunnyNameInp[t,s,n];
E_q_nout_FunnyNameInp[t,s,n]$(branch2no_funnynameinp[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_FunnyNameInp[s,nn,n]), qD[t,s,nn]*mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) / sum(nnn$(map_FunnyNameInp[s,nn,nnn]), mu[s,nn,nnn] * (pD[t,s,nn]/pD[t,s,nnn])**(sigma[s,nn])));

# ----------------------------------------------------------------------------------------------------
#  Define B_FunnyName_FunnyNameInp model
# ----------------------------------------------------------------------------------------------------
Model B_FunnyName_FunnyNameInp /
E_zp_out_FunnyNameInp, E_zp_nout_FunnyNameInp, E_q_out_FunnyNameInp, E_q_nout_FunnyNameInp
/;




# --------------------------------------B_FunnyName_FunnyNameOut--------------------------------------
#  Initialize B_FunnyName_FunnyNameOut equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_FunnyNameOut[t,s,n];
E_zp_FunnyNameOut[t,s,n]$(knot_funnynameout[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_FunnyNameOut[s,nn,n] and branch_o_FunnyNameOut[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_FunnyNameOut[s,nn,n] and branch_no_FunnyNameOut[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_FunnyNameOut[t,s,n];
E_q_out_FunnyNameOut[t,s,n]$(branch_o_funnynameout[s,n] and txe[t]).. 	qS[t,s,n]  =E=  sum(nn$(map_FunnyNameOut[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_FunnyNameOut[s,nnn,nn] and branch_o_FunnyNameOut[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_FunnyNameOut[s,nnn,nn] and branch_no_FunnyNameOut[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));
EQUATION E_q_nout_FunnyNameOut[t,s,n];
E_q_nout_FunnyNameOut[t,s,n]$(branch_no_funnynameout[s,n] and txe[t]).. 		qD[t,s,n]  =E=  sum(nn$(map_FunnyNameOut[s,n,nn]), qD[t,s,nn]*mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) / (sum(nnn$(map_FunnyNameOut[s,nnn,nn] and branch_o_FunnyNameOut[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pS[t,s,nnn])**(eta[s,nn]))+sum(nnn$(map_FunnyNameOut[s,nnn,nn] and branch_no_FunnyNameOut[s,nnn]), mu[s,nnn,nn] * (pD[t,s,nn]/pD[t,s,nnn])**(eta[s,nn]))));

# ----------------------------------------------------------------------------------------------------
#  Define B_FunnyName_FunnyNameOut model
# ----------------------------------------------------------------------------------------------------
Model B_FunnyName_FunnyNameOut /
E_zp_FunnyNameOut, E_q_out_FunnyNameOut, E_q_nout_FunnyNameOut
/;


qS.fx[t,s,n]$(((output_FunnyName[s,n] and ( not ((endo_qS_FunnyName[s,n] and t0[t])))) or (endo_qS_FunnyName[s,n] and t0[t]))) = qS.l[t,s,n];
pD.fx[t,s,n]$(input_FunnyName[s,n]) = pD.l[t,s,n];
sigma.fx[s,n]$(kninp_FunnyName[s,n]) = sigma.l[s,n];
eta.fx[s,n]$(knout_FunnyName[s,n]) = eta.l[s,n];
mu.fx[s,n,nn]$((exomu_FunnyName[s,n,nn] or ( not (exomu_FunnyName[s,n,nn])))) = mu.l[s,n,nn];
pD.lo[t,s,n]$(int_FunnyName[s,n]) = -inf;
pD.up[t,s,n]$(int_FunnyName[s,n]) = inf;
pS.lo[t,s,n]$((((output_FunnyName[s,n] and tx0[t]) or (endo_pS_FunnyName[s,n] and t0[t])) or ((output_FunnyName[s,n] and t0[t]) and ( not ((endo_pS_FunnyName[s,n] and t0[t])))))) = -inf;
pS.up[t,s,n]$((((output_FunnyName[s,n] and tx0[t]) or (endo_pS_FunnyName[s,n] and t0[t])) or ((output_FunnyName[s,n] and t0[t]) and ( not ((endo_pS_FunnyName[s,n] and t0[t])))))) = inf;
qD.lo[t,s,n]$(((((int_FunnyName[s,n] or input_FunnyName[s,n]) and tx0[t]) or (endo_qD_FunnyName[s,n] and t0[t])) or (((int_FunnyName[s,n] or input_FunnyName[s,n]) and t0[t]) and ( not ((endo_qD_FunnyName[s,n] and t0[t])))))) = -inf;
qD.up[t,s,n]$(((((int_FunnyName[s,n] or input_FunnyName[s,n]) and tx0[t]) or (endo_qD_FunnyName[s,n] and t0[t])) or (((int_FunnyName[s,n] or input_FunnyName[s,n]) and t0[t]) and ( not ((endo_qD_FunnyName[s,n] and t0[t])))))) = inf;
qiv_inp.lo[t,s,n]$(spinp_FunnyName[s,n]) = -inf;
qiv_inp.up[t,s,n]$(spinp_FunnyName[s,n]) = inf;
qiv_out.lo[t,s,n]$(spout_FunnyName[s,n]) = -inf;
qiv_out.up[t,s,n]$(spout_FunnyName[s,n]) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define FunnyName_B model
# ----------------------------------------------------------------------------------------------------
Model FunnyName_B /
E_zp_out_FunnyNameInp, E_zp_nout_FunnyNameInp, E_q_out_FunnyNameInp, E_q_nout_FunnyNameInp, E_zp_FunnyNameOut, E_q_out_FunnyNameOut, E_q_nout_FunnyNameOut
/;


solve FunnyName_B using CNS;