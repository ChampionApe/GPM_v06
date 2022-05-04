# 0.1: Auxiliary functions used for scale-preserving nests:
def _CES(px,py,mu,sigma,norm=None):
	return f"{mu} * ({py}/{px})**({sigma})" if norm is None else f"{mu} * ({py}/({px}*(1+{norm})))**({sigma})"
def _exp(px,py,mu,sigma,norm=None):
	return f"{mu} * exp(({py}-{px})*{sigma})" if norm is None else f"{mu} * exp(({py}-{px})*{sigma}-{norm})"

def _Fnorm_input_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$(map_{name}[s,nn,nnn]), {f("pD[t,s,nnn]","pS[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$(map_{name}[s,nn,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));"""

def _Fnorm_output_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,nn,n]","sigma[s,nn]")} / (sum(nnn$(map_{name}[s,nn,nnn] and branch_o_{name}[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")})+sum(nnn$(map_{name}[s,nn,nnn] and branch_no_{name}[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")})));
	E_q_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","sigma[s,nn]")} / (sum(nnn$(map_{name}[s,nn,nnn] and branch_o_{name}[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")})+sum(nnn$(map_{name}[s,nn,nnn] and branch_no_{name}[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")})));"""

def _Fnorm_input_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv[t,s,nn]);
	E_inclVal_out_{name}[t,s,n]$(knot_o_{name}[s,n] and txE[t])..	qiv[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), {f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});
	E_inclVal_nout_{name}[t,s,n]$(knot_no_{name}[s,n] and txE[t])..	qiv[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});"""

def _Fnorm_output_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,nn,n]","sigma[s,nn]")} / qiv[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","sigma[s,nn]")} / qiv[t,s,nn]);
	E_inclVal_out_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..		qiv[t,s,n]=E= sum(nn$(map_{name}[s,n,nn] and branch_o_{name}[s,nn]), {f("pS[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')})+sum(nn$(map_{name}[s,n,nn] and branch_no_{name}[s,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});"""

# 0.2: Zero profit equations:
def zp_input(name):
	return f"""E_zp_out_{name}[t,s,n]$(knot_o_{name}[s,n] and txE[t])..	pS[t,s,n]*qS[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
	E_zp_nout_{name}[t,s,n]$(knot_no_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);"""
def zp_output(name):
	return f"""E_zp_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn] and branch_o_{name}[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_{name}[s,n,nn] and branch_no_{name}[s,nn]), qD[t,s,nn]*pD[t,s,nn]);"""


# 1: Input type nests:
# 1.1: CES nest:
def CES(blockname,name,**kwargs):
	return f"""
$BLOCK B_{blockname}
	{zp_input(name)}
	E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 1.2: Scale-preserving nests:
def Fnorm_input(ftype,blockname,name,inclusiveVal=True):
	return f"""
$BLOCK B_{blockname}
	{zp_input(name)}
	{_Fnorm_input_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_input_demand(ftype,name)}
$ENDBLOCK
"""
def CES_norm(blockname,name,inclusiveVal = True):
	return Fnorm_input('CES',blockname,name,inclusiveVal=inclusiveVal)
def MNL(blockname,name,inclusiveVal=True):
	return Fnorm_input('exp',blockname,name,inclusiveVal=inclusiveVal)

# 2: Output type nests:
# 2.1: CET function:
def CET(blockname,name,**kwargs):
	return f"""
$BLOCK B_{blockname}
	{zp_output(name)}
	E_demand_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..		qS[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pS[t,s,n]/pD[t,s,nn])**(sigma[s,nn]) * qD[t,s,nn]);
	E_demand_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pD[t,s,n]/pD[t,s,nn])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""
# 2.2: scale-preserving nests: 
def Fnorm_output(ftype,blockname,name,inclusiveVal=True):
	return f"""
$BLOCK B_{blockname}
	{zp_output(name)}
	{_Fnorm_output_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_output_demand(ftype,name)}
$ENDBLOCK
"""

def CET_norm(blockname,name,inclusiveVal=True):
	return Fnorm_output('CES',blockname,name,inclusiveVal=inclusiveVal)
def MNL_out(blockname,name,inclusiveVal=True):
	return Fnorm_output('exp',blockname,name,inclusiveVal=inclusiveVal)

# 3: Adjustment costs / installation cost equations:
def sqrAdjCosts(blockname, name):
	return f"""
$BLOCK B_{blockname}
	E_lom_{name}[t,s,n](dur_{name}[s,n] and txE[t])..	qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(dur2inv[n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_pk_{name}[t,s,n]$(dur_{name}[s,n] and tx0E[t])..	pD[t,s,n]	=E= sum(nn$(dur2inv[n,nn]), Rrate[t]*(pD[t-1,s,nn]/(1+infl_LR)+icpar1[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-icpar2[s,n]))+(icpar1[s,n]*0.5)*(sqr(icpar2[s,n]*qD[t,s,n])-sqr(qD[t,s,nn]))/sqr(qD[t,s,n])-(1-rDepr[t,s,n])*(pD[t,s,nn]+icpar1[s,n]*(qD[t,s,nn]/qD[t,s,n]-icpar2[s,n])));
	E_Ktvc_{name}[t,s,n]$(dur_{name}[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n];
	E_instcost_{name}[t,s,n]$(output_{name}[s,n] and txE[t])..	ic[t,s,n] =E= (pS[t,s,n]/sum(nn$(output_{name}[s,nn]), qS[t,s,n]*pS[t,s,nn]))*sum([nn,nnn]$(dur_{name}[s,nn] and dur2inv[nn,nnn]), icpar1[s,nn]*0.5*qD[t,s,nn]*sqr(qD[t,s,nnn]/qD[t,s,nn]-icpar2[s,nn]));
$ENDBLOCK
"""


# 4: Introduce price wedge with mark-up, unit-tax, and installation costs
def PriceWedge(blockname,name):
	return f"""
$BLOCK B_{blockname}
	E_pw_{name}[t,s,n]$(output_{name}[s,n] and txE[t])..	peq[t,n] =E= (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+ic[t,s,n]);
$ENDBLOCK
"""

