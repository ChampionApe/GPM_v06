import CGE_globals, GmsPy, pickle, pandas as pd, os
from Database import GpyDB, gpy
from DBWheels_mi import MergeDomains, RepeatVar
from DBWheels_robust import robust_merge_dbs
from GmsPy import gmspyStandardOrder
from _MixTools import OrdSet, NoneInit

class GmsPython:
	""" standard gamspython models """
	def __init__(self,name=None,f=None,s=None,glob=None,m=None,ns=None,m_kwargs=None,s_kwargs=None,g_kwargs=None):
		if f is not None:
			with open(f, "rb") as file:
				self.__dict__ = pickle.load(file).__dict__
		else:
			self.s = GmsPy.GmsSettings(**(NoneInit(s_kwargs,{})|{'name':name})) if s is None else s
			self.ns = NoneInit(ns,{})
			self.m = {}
			self.initModules(NoneInit(m,[]),**NoneInit(m_kwargs,{}))
			self.InitGlobals(glob,g_kwargs)

	def initModules(self,m,submodule_kwargs=None,**m_kwargs):
		if any([isinstance(mi,GmsPython) for mi in m]):
			GmsPy.mergeGmsSettings(self.s,[mi.s for mi in m if isinstance(mi,GmsPython)],**m_kwargs)
		[self.addModule(mi,**NoneInit(submodule_kwargs,{})) for mi in m];

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
	def compile(self,initDB=False,states_kwargs=None):
		self.compile_groups()
		self.compile_states(**NoneInit(states_kwargs,{}))
		if initDB:
			self.initDB()

	def compile_groups(self):
		self.s.Compile.groups.update(self.groups())
		self.s.Compile.run()
		return self.s.Compile.groups

	def compile_states(self,**kwargs):
		self.s.states.update(self.states(**kwargs))

	def states(self,compile_modules = True,order=None):
		if compile_modules:
			[m.compile_states(compile_modules=True,order=order) for m in self.m.values() if hasattr(m,'compile_states')];
		other = [m.s for m in self.m.values() if hasattr(m,'s')]+[m for m in self.m.values() if hasattr(m,'states') and isinstance(m,Submodule)];
		return GmsPy.mergeStates(self.s, other, [self.s]+other, order=order)

	def initDB(self):
		for m in self.m.values():
			if hasattr(m,'initDB'):
				robust_merge_dbs(self.s.db,m.initDB(m=m.name),priority='first')
	def groups(self):
		return self.getAttrFromModules('groups')
	def getAttrFromModules(self,attr):
		return {k:v for d in (getattr(m,attr)(m=m.name) if hasattr(m,attr) else {} for m in self.m.values()) for k,v in d.items()}

	# ---		3: Write and run methods		---- #
	def write(self, order = gmspyStandardOrder, kwargs=None, write_kwargs = None):
		self.s['args'].update(self.s.stdArgs(NoneInit(kwargs,{})))
		self.s['args'] = GmsPy.sortedArgs(self.s['args'], order = order)
		return self.s.write(**NoneInit(write_kwargs,{}))

	def run(self, model=None, db_str = None, exportdb = True, exportTo = None, ws = None, options = None, **kwargs):
		if isinstance(model, GmsPy.GmsModel):
			return self.runModel(model, db_str=db_str, exportdb=exportdb,exportTo=exportTo)
		else:
			return self.runAndInitModel(db_str=db_str, exportdb=exportdb,exportTo=exportTo,ws=ws,options=options,**kwargs)

	def runAndInitModel(self, db_str=None, exportdb=True, exportTo=None, ws=None, options=None, options_add=None, options_run = None, **kwargs):
		model = GmsPy.GmsModel(ws=ws,options=options,**kwargs)
		return self.runModel(model, db_str = db_str, exportdb=exportdb, exportTo = exportTo,options_add=options_add, options_run = options_run)

	def runModel(self,model,db_str=None, merge=True, exportdb=True, exportTo = None, options_add=None, options_run = None):
		model.addDB(self.s.db, db_str=db_str, merge=merge, exportdb=exportdb, exportTo=exportTo)
		model.run(run = '\n'.join(self.s['text'].values()), options_add=options_add, options_run = options_run)
		return model

class Submodule:
	""" Simple submodule that is not defined by a GmsSettings instance. """
	def __init__(self, name = None, ns=None, **KeyAttrs):
		self.name, self.ns = name, NoneInit(ns,{})
		[setattr(self,k,v) for k,v in KeyAttrs.items()];

	def n(self,item,m=None):
		try:
			return self.ns[item] if m is None else self.m[m[0]].n(m[1])
		except KeyError:
			return item

	def state(self,k):
		if hasattr(self,'states'):
			return self.states[k] if k in self.states else self.states[self.state]