from GmsWrite import write_gpy

def equation(name,domains,conditions,LHS,RHS,eqtype='E'):
	return f"""{name}{domains}{'$('+conditions+')' if conditions != '' else conditions}..	{LHS} ={eqtype}= {RHS};"""

def get(x,ns,ns_i,db,local):
	return db[ns_i[x]] if local else db[ns[x]]

def write(x,ns,ns_i,db,c=None,alias={},lag={},l="",local=True,local_c=None):
	return write_gpy(s=get(x,ns,ns_i,db,local), c = get(c,ns,ns_i,local_c) if c else None, alias=alias_ns(alias,ns), lag = lag, l=l)

def alias_ns(a,ns):
	return {ns[k]:ns[v] for k,v in a.items()}

def doms(x):
	return '['+','.join(x.domains)+']' if x.domains else ''

class NS:
	def __init__(self,ns,ns_i,db,name):
		self.ns = ns
		self.ns_i = ns_i
		self.db = db
		self.name = name

	def w(self,x,c=None,alias={},lag={},l="",local=False,local_c=None):
		return write(x,self.ns,self.ns_i,self.db,c=c,alias=alias,lag=lag,l=l,local=local,local_c=local_c)

	def g(self,x,local=False):
		return get(x,self.ns,self.ns_i,self.db,local)

	def d(self,x,local=False):
		return doms(self.g(x,local=local))

	@property
	def block(self):
		return """$BLOCK B_{name}
{x}
$ENDBLOCK""".format(name=self.name,x='\t'+'\n\t'.join(self.run()))

class CES(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2 = self.w('map',local=True,alias={'n':'nn','nn':'n'})
		qD2,pD2 = self.w('qD',alias={'n':'nn'}),self.w('pD',alias={'n':'nn'})
		qS2,pS2 = self.w('qS',alias={'n':'nn'}),self.w('pS',alias={'n':'nn'})
		sigma2 = self.w('sigma',alias={'n':'nn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp_out(qD2,pD2,txE),self.zp_nout(qD2,pD2,txE), self.demand_out(pS2,qS2,sigma2,txE), self.demand_nout(pD2,qD2,sigma2,txE)]

	def zp_out(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_out_{self.name}", f"{self.d('pS')}", self.w('knot_o',local=True)+txE, f"{self.w('pS')}*{self.w('qS')}", RHS)

	def zp_nout(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_nout_{self.name}", f"{self.d('pD')}", self.w('knot_no',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}", RHS)

	def demand_out(self,pS2,qS2,sigma2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({pS2}/{self.w('pD')})**({sigma2}) * {qS2})"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qD')}", self.w('branch2o',local=True)+txE, f"{self.w('qD')}", RHS)

	def demand_nout(self,pD2,qD2,sigma2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({pD2}/{self.w('pD')})**({sigma2}) * {qD2})"""
		return equation(f"E_demand_nout_{self.name}", f"{self.d('qD')}", self.w('branch2no',local=True)+txE, f"{self.w('qD')}", RHS)

class CES_norm(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2,map_3 = self.w('map',local=True,alias={'n':'nn','nn':'n'}), self.w('map',local=True,alias={'n':'nnn'})
		mu3,pD3 = self.w('mu',alias={'n':'nnn'}), self.w('pD',alias={'n':'nnn'})
		qD2,pD2 = self.w('qD',alias={'n':'nn'}),self.w('pD',alias={'n':'nn'})
		qS2,pS2 = self.w('qS',alias={'n':'nn'}),self.w('pS',alias={'n':'nn'})
		sigma2 = self.w('sigma',alias={'n':'nn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp_out(qD2,pD2,txE),self.zp_nout(qD2,pD2,txE), self.demand_out(pS2,qS2,sigma2,map_3,mu3,pD3,txE), self.demand_nout(pD2,qD2,sigma2,map_3,mu3,pD3,txE)]

	def zp_out(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_out_{self.name}", f"{self.d('pS')}", self.w('knot_o',local=True)+txE, f"{self.w('pS')}*{self.w('qS')}", RHS)

	def zp_nout(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_nout_{self.name}", f"{self.d('pD')}", self.w('knot_no',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}", RHS)

	def demand_out(self,pS2,qS2,sigma2,map_3,mu3,pD3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({pS2}/{self.w('pD')})**({sigma2}) * {qS2} / sum({self.ns['nnn']}$({map_3}), {mu3} * ({pS2}/{pD3})**({sigma2})))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qD')}", self.w('branch2o',local=True)+txE, f"{self.w('qD')}", RHS)

	def demand_nout(self,pD2,qD2,sigma2,map_3,mu3,pD3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({pD2}/{self.w('pD')})**({sigma2}) * {qD2} / sum({self.ns['nnn']}$({map_3}), {mu3} * ({pD2}/{pD3})**({sigma2})))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qD')}", self.w('branch2o',local=True)+txE, f"{self.w('qD')}", RHS)

class MNL(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2,map_3 = self.w('map',local=True,alias={'n':'nn','nn':'n'}), self.w('map',local=True,alias={'n':'nnn'})
		mu3,pD3 = self.w('mu',alias={'n':'nnn'}), self.w('pD',alias={'n':'nnn'})
		qD2,pD2 = self.w('qD',alias={'n':'nn'}),self.w('pD',alias={'n':'nn'})
		qS2,pS2 = self.w('qS',alias={'n':'nn'}),self.w('pS',alias={'n':'nn'})
		sigma2 = self.w('sigma',alias={'n':'nn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp_out(qD2,pD2,txE),self.zp_nout(qD2,pD2,txE), self.demand_out(pS2,qS2,sigma2,map_3,mu3,pD3,txE), self.demand_nout(pD2,qD2,sigma2,map_3,mu3,pD3,txE)]

	def zp_out(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_out_{self.name}", f"{self.d('pS')}", self.w('knot_o',local=True)+txE, f"{self.w('pS')}*{self.w('qS')}", RHS)

	def zp_nout(self,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}),{qD2}*{pD2})"""
		return equation(f"E_zp_nout_{self.name}", f"{self.d('pD')}", self.w('knot_no',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}", RHS)

	def demand_out(self,pS2,qS2,sigma2,map_3,mu3,pD3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * exp(({pS2}-{self.w('pD')})*({sigma2})) * {qS2} / sum({self.ns['nnn']}$({map_3}), {mu3} * exp(({pS2}-{pD3})*({sigma2}))))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qD')}", self.w('branch2o',local=True)+txE, f"{self.w('qD')}", RHS)

	def demand_nout(self,pD2,qD2,sigma2,map_3,mu3,pD3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * exp(({pD2}-{self.w('pD')})*({sigma2})) * {qD2} / sum({self.ns['nnn']}$({map_3}), {mu3} * exp(({pD2}-{pD3})*({sigma2}))))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qD')}", self.w('branch2o',local=True)+txE, f"{self.w('qD')}", RHS)


class CET(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2 = self.w('map',local=True,alias={'n':'nn', 'nn': 'n'})
		branch_o2, branch_no2 = self.w('branch_o',local=True,alias={'n':'nn'}), self.w('branch_no',local=True,alias={'n':'nn'})
		qS2,qD2 = self.w('qS',alias={'n':'nn'}), self.w('qD',alias={'n':'nn'})
		pS2,pD2 = self.w('pS',alias={'n':'nn'}), self.w('pD',alias={'n':'nn'})
		sigma2 = self.w('sigma',alias={'n':'nn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp(map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE), self.demand_out(pD2,qD2,sigma2,txE), self.demand_nout(pD2,qD2,sigma2,txE)]

	def zp(self,map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({map_2} and {branch_o2}), {qS2}*{pS2})+sum({self.ns['nn']}$({map_2} and {branch_no2}), {qD2}*{pD2})"""
		return equation(f"E_zp_{self.name}", f"{self.d('pD')}", self.w('knot',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}",RHS)

	def demand_out(self,pD2,qD2,sigma2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({self.w('pS')}/{pD2})**({sigma2}) * {qD2})"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qS')}", self.w('branch_o',local=True)+txE, f"{self.w('qS')}",RHS)

	def demand_nout(self,pD2,qD2,sigma2,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({self.w('pD')}/{pD2})**({sigma2}) * {qD2})"""
		return equation(f"E_demand_nout_{self.name}", f"{self.d('qD')}", self.w('branch_no',local=True)+txE, f"{self.w('qD')}",RHS)

class CET_norm(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2,map_3 = self.w('map',local=True,alias={'n':'nn', 'nn': 'n'}), self.w('map',local=True,alias={'n':'nnn'})
		branch_o2, branch_no2 = self.w('branch_o',local=True,alias={'n':'nn'}), self.w('branch_no',local=True,alias={'n':'nn'})
		branch_o3, branch_no3 = self.w('branch_o',local=True,alias={'n':'nnn'}),self.w('branch_no',local=True,alias={'n':'nnn'})
		qS2,qD2 = self.w('qS',alias={'n':'nn'}), self.w('qD',alias={'n':'nn'})
		pS2,pS3 = self.w('pS',alias={'n':'nn'}), self.w('pS',alias={'n':'nnn'})
		pD2,pD3 = self.w('pD',alias={'n':'nn'}), self.w('pD',alias={'n':'nnn'})
		sigma2,mu3 = self.w('sigma',alias={'n':'nn'}), self.w('mu',alias={'n':'nnn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp(map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE), self.demand_out(pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE), self.demand_nout(pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE)]

	def zp(self,map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({map_2} and {branch_o2}), {qS2}*{pS2})+sum({self.ns['nn']}$({map_2} and {branch_no2}), {qD2}*{pD2})"""
		return equation(f"E_zp_{self.name}", f"{self.d('pD')}", self.w('knot',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}",RHS)

	def demand_out(self,pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({self.w('pS')}/{pD2})**({sigma2}) * {qD2}) / (sum({self.ns['nnn']}$({map_3} and {branch_o3}), {mu3}*({pS3}/{pD2})**({sigma2})+sum({self.ns['nnn']} and {branch_no3}), {mu3}*({pD3}/{pD2})**({sigma2})))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qS')}", self.w('branch_o',local=True)+txE, f"{self.w('qS')}",RHS)

	def demand_nout(self,pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * ({self.w('pD')}/{pD2})**({sigma2}) * {qD2}) / (sum({self.ns['nnn']}$({map_3} and {branch_o3}), {mu3}*({pS3}/{pD2})**({sigma2})+sum({self.ns['nnn']} and {branch_no3}), {mu3}*({pD3}/{pD2})**({sigma2})))"""
		return equation(f"E_demand_nout_{self.name}", f"{self.d('qD')}", self.w('branch_no',local=True)+txE, f"{self.w('qD')}",RHS)

class MNL_out(NS):
	def __init__(self,ns,ns_i,db,name,dynamic=True):
		super().__init__(ns,ns_i,db,name)
		self.dynamic = dynamic

	def run(self):
		map_2,map_3 = self.w('map',local=True,alias={'n':'nn', 'nn': 'n'}), self.w('map',local=True,alias={'n':'nnn'})
		branch_o2, branch_no2 = self.w('branch_o',local=True,alias={'n':'nn'}), self.w('branch_no',local=True,alias={'n':'nn'})
		branch_o3, branch_no3 = self.w('branch_o',local=True,alias={'n':'nnn'}),self.w('branch_no',local=True,alias={'n':'nnn'})
		qS2,qD2 = self.w('qS',alias={'n':'nn'}), self.w('qD',alias={'n':'nn'})
		pS2,pS3 = self.w('pS',alias={'n':'nn'}), self.w('pS',alias={'n':'nnn'})
		pD2,pD3 = self.w('pD',alias={'n':'nn'}), self.w('pD',alias={'n':'nnn'})
		sigma2,mu3 = self.w('sigma',alias={'n':'nn'}), self.w('mu',alias={'n':'nnn'})
		txE = f" and {self.w('txE')}" if self.dynamic else ''
		return [self.zp(map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE), self.demand_out(pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE), self.demand_nout(pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE)]

	def zp(self,map_2,branch_o2,branch_no2,qS2,pS2,qD2,pD2,txE):
		RHS = f"""sum({self.ns['nn']}$({map_2} and {branch_o2}), {qS2}*{pS2})+sum({self.ns['nn']}$({map_2} and {branch_no2}), {qD2}*{pD2})"""
		return equation(f"E_zp_{self.name}", f"{self.d('pD')}", self.w('knot',local=True)+txE, f"{self.w('pD')}*{self.w('qD')}",RHS)

	def demand_out(self,pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * exp(({self.w('pS')}-{pD2})*({sigma2})) * {qD2}) / (sum({self.ns['nnn']}$({map_3} and {branch_o3}), {mu3}*exp(({pS3}-{pD2})*({sigma2})))+sum({self.ns['nnn']} and {branch_no3}), {mu3}*exp(({pD3}-{pD2})*({sigma2}))))"""
		return equation(f"E_demand_out_{self.name}", f"{self.d('qS')}", self.w('branch_o',local=True)+txE, f"{self.w('qS')}",RHS)

	def demand_nout(self,pD2,pD3,pS3,qD2,sigma2,map_3,branch_o3,branch_no3,mu3,txE):
		RHS = f"""sum({self.ns['nn']}$({self.w('map',local=True)}), {self.w('mu')} * exp(({self.w('pD')}-{pD2})*({sigma2})) * {qD2}) / (sum({self.ns['nnn']}$({map_3} and {branch_o3}), {mu3}*exp(({pS3}-{pD2})*({sigma2})))+sum({self.ns['nnn']} and {branch_no3}), {mu3}*exp(({pD3}-{pD2})*({sigma2}))))"""
		return equation(f"E_demand_nout_{self.name}", f"{self.d('qD')}", self.w('branch_no',local=True)+txE, f"{self.w('qD')}",RHS)
