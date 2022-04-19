from CGE_GmsPython import *
import _gamYProd

class Production(GmsPython):
	def __init__(self, f=None, tree=None, ns={}, s=None, glob=None, s_kwargs = {}, g_kwargs = {}):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(name=tree.name if tree else None, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		if f is None:
			self.readTree(tree)

	def readTree(self,tree):
		robust_merge_dbs(self.s.db,tree.db,priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.addCalibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','sp')})

	@property
	def default_variables(self):
		return ('pS','pD','qS','qD','mu','sigma','qnorm','qiv')
	def initDB(self,m=None):
		return robust_merge_dbs(self.s.db,{self.n(s): self.initSymbol(s,m=m) for s in self.default_variables},priority='first')
	def initSymbol(self,s,m=None):
		if s == 'pS':
			return gpy(pd.Series(1, index = MergeDomains([self.get('t'),self.get('output',m=m)],self.s.db), name=self.n(s)))
		elif s == 'qS':
			return gpy(pd.Series(1, index = MergeDomains([self.get('t'),self.get('output',m=m)],self.s.db), name=self.n(s)))
		elif s == 'pD':
			return gpy(pd.Series(1, index = MergeDomains([self.get('t'),self.get('int',m=m).union(self.get('input',m=m))],self.s.db), name = self.n(s)))
		elif s == 'qD':
			return gpy(pd.Series(0.5, index = MergeDomains([self.get('t'),self.get('int',m=m).union(self.get('input',m=m))],self.s.db), name = self.n(s)))
		elif s == 'mu':
			return gpy(pd.Series(0.5, index = self.get('map',m=m), name = self.n(s)))
		elif s == 'sigma':
			return gpy(pd.Series(0.5, index = self.get('knot',m=m), name = self.n(s)))
		elif s == 'qnorm':
			return gpy(pd.Series(0, index = MergeDomains([self.get('t'),self.get('knot',m=m)],self.s.db),name=self.n(s)),**{'type':'parameter'})
		elif s =='qiv':
			return gpy(pd.Series(1, index = self.get('sp_knots',m=m), name = self.n(s)))

	def addCalibrationSubsets(self,tree):
		""" Define the subset of prices that are endogenous in calibration mode"""
		self.ns['endo_pS'] = 'endo_pS_'+self.name
		self.s.db[self.ns['endo_pS']] = pd.MultiIndex.from_tuples([s for l in [self.endo_pS_from_tree(t) for t in tree.trees.values()] for s in l], names = [self.n('s'),self.n('n')])

	def endo_pS_from_tree(self,t):
		if t.io == 'in':
			return t.get('knot_o')
		elif t.io == 'out':
			map_o = t.get('map')[t.get('map').droplevel(self.n('n')).isin(t.get('branch_o').rename({self.n('n'):self.n('nn')}))]
			return map_o.to_frame(index=False).groupby([self.n('s'),self.n('n')]).first().reset_index()[[self.n('s'),self.n('nn')]].to_records(index=False)

	def args(self,m=None):
		return {self.name+'_blocks': '\n'.join([getattr(_gamYProd, module.f)(self.name+'_'+name,name) for name,module in self.m.items()])}
	def states(self,m=None):
		return {k: self.s.standardInstance(state=k) | {attr: getattr(self,attr+'_all')()[k] for attr in ('g_endo','g_exo','blocks')} for k in ('B','C')}
	def groups(self,m=None):
		return {g.name: g for g in self.groups_(m=m)}
	def g_endo_all(self):
		return {'B': OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_exo_in_calib"]),
				'C': OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_endo_in_calib"])}
	def g_exo_all(self):
		return {'B': OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_endo_in_calib"]),
				'C': OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_exo_in_calib"])}
	def blocks_all(self):
		return {k: OrdSet([f"{self.name}_{name}" for name in self.m]) for k in ('B','C')}

	def groups_(self,m=None):
		return [GmsPy.Group(f"G_{self.name}_exo_always", v = [('qS',self.g('output',m=m)),('pD',self.g('input',m=m)), ('sigma',self.g('knot',m=m))]),
				GmsPy.Group(f"G_{self.name}_endo_always",v = [
					('pD',self.g('int',m=m)),
					('pS', ('and', [self.g('endo_pS',m=m), self.g('t0')])),
					('pS', ('and', [self.g('output',m=m), self.g('tx0')])),
					('qD',('and', [self.g('int',m=m), self.g('tx0')])), 
					('qD',('and', [self.g('input',m=m), self.g('tx0')]))]),
				GmsPy.Group(f"G_{self.name}_exo_in_calib",v= [
					('qD', ('and', [self.g('int',m=m), self.g('t0')])), 
					('qD', ('and', [self.g('input',m=m), self.g('t0')])),
					('pS', ('and', [self.g('output',m=m),('not', self.g('endo_pS',m=m),self.g('t0'))]))]),
				GmsPy.Group(f"G_{self.name}_endo_in_calib",v=[('mu',self.g('map',m=m))])]
