import CGE_globals, GmsPy, pickle, pandas as pd
from Database import GpyDB, gpy
from DBWheels_mi import MergeDomains, RepeatVar
from DBWheels_robust import robust_merge_dbs
from _MixTools import OrdSet

def dfElse(k, df, kwargs):
	return kwargs[k] if k in kwargs else df

class GmsPython:
	""" standard gamspython models """
	def __init__(self,name=None,f=None,s=None,glob=None,m=[],ns={},m_kwargs={},s_kwargs={},g_kwargs={}):
		if f is not None:
			with open(f, "rb") as file:
				self.__dict__ = pickle.load(file).__dict__
		else:
			self.s = GmsPy.GmsSettings(**(s_kwargs|{'name':name})) if s is None else s
			self.ns = ns
			self.m = {}
			self.initModules(m,**m_kwargs)
			self.InitGlobals(glob,g_kwargs)

	def initModules(self,m,submodule_kwargs={},**m_kwargs):
		if any([isinstance(mi,GmsPython) for mi in m]):
			GmsPy.mergeGmsSettings(self.s,[mi.s for mi in m if isinstance(mi,GmsPython)],**m_kwargs)
		[self.addModule(mi,**submodule_kwargs) for mi in m];

	def addModule(self,m,merge_s=False,adjust_db=True,**kwargs):
		if isinstance(m,GmsPython):
			if merge_s:
				GmsPy.mergeGmsSettings(self.s,[m.s],**kwargs)
			if adjust_db:
				m.s.db = self.s.db
			self.m[m.name] = m
		else:
			self.m[m.name] = Submodule(**kwargs)

	def InitGlobals(self, glob, g_kwargs):
		self.glob = getattr(CGE_globals, glob)(kwargs_ns=self.ns,kwargs_vals=g_kwargs) if type(glob) is str else glob
		self.ns.update(self.glob.ns)
		[self.s.db.__setitem__(k,v) for k,v in self.glob.db.items()];

	# --- 		1: Interact w. namespace/database 		--- #
	def n(self, item, m=None):
		try:
			return self.ns[item] if m is None else self.modules[m[0]].n(m[1])
		except KeyError:
			return item

	def g(self, item, m=None):
		return self.s.db[self.n(item, m=m)]

	def get(self, item, m=None):
		return self.g(item, m=m).vals

	@property
	def name(self):
		return self.s.name

	# ---		2: Standard compile methods			---- #
	def compile(self,order=None,initDB=False):
		self.compile_groups()
		self.compile_args(order=order)
		if initDB:
			self.initDB()
	def compile_groups(self):
		self.s.Compile.groups.update(self.groups())
		self.s.Compile.run()
		return self.s.Compile.groups
	def compile_args(self,order=None):
		self.s['args'].update(self.args())
		self.s['args'] = self.s.sortedArgs() if order is None else self.s.sortedArgs(order=order)
		return self.s['args']
	def initDB(self):
		for m in self.m.values():
			if hasattr(m,'initDB'):
				robust_merge_dbs(self.s.db,m.initDB(m=m.name),priority='first')
	def groups(self):
		return self.getAttrFromModules('groups')
	def args(self):
		return self.getAttrFromModules('args')
	def getAttrFromModules(self,attr):
		return {k:v for d in (getattr(m,attr)(m=m.name) if hasattr(m,attr) else {} for m in self.m.values()) for k,v in d.items()}

class Submodule:
	""" Simple submodule """
	def __init__(self, name = None, ns={}, **KeyAttrs):
		self.name, self.ns = name, ns
		[setattr(self,k,v) for k,v in KeyAttrs.items()];

	def n(self,item,m=None):
		try:
			return self.ns[item] if m is None else self.m[m[0]].n(m[1])
		except KeyError:
			return item