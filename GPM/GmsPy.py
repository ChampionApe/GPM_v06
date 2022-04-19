from _GmsPy import *
from Database import GpyDB
from DBWheels_rc import rc_AdjGpy
from DBWheels_robust import robust_merge_dbs
import GmsWrite
gmspyStandardOrder =  ('root','functions','declare','declare_groups','load_groups','blocks','fix','unfix','model','solve')

def sortedArgs(args, order = gmspyStandardOrder):
	return {k:v for d in ({kk:vv for kk,vv in args.items() if kk.endswith(o)} for o in order) for k,v in d.items()}
def mergeDictAttrs(l,attr,sort=False):
	return sortedArgs({k:v for d in l for k,v in getattr(d,attr).items()},order=sort) if sort else {k:v for d in l for k,v in getattr(d,attr).items()}
def merge2dbs(main,other_i,residual=True):
	d = other_i.partition_db()
	robust_merge_dbs(main.db, d['non_var'],priority='second')
	robust_merge_dbs(main.db, d['var_endo'],priority='second')
	robust_merge_dbs(main.db, d['var_exo'],priority='first')
	if residual:
		robust_merge_dbs(main.db, d['residual'],priority='first')
def mergeDbs(main,other,residual=True):
	[merge2dbs(main,other_i,residual=residual) for other_i in other];
	return main.db
def mergeOrdSets(l,attr,state):
	return OrdSet([x for y in l for x in y.try_state(state)[attr]])
def attrFromState(s,attr,state):
	return s[attr] if state not in s.try_state(state) else s.try_state(state)[attr] 
def mergeStates_k(main,other,l,k,args=True):
	d = {'name': main.name+'_'+B, 'g_endo': mergeOrdSets(l,'g_endo',k), 'g_exo': mergeOrdSets(l,'g_exo',k),'blocks':mergeOrdSets(l,'blocks',k), 'solve': main.try_state(k)['solve']}
	if any(['args' in other_i.try_state(k) for other_i in l]) and args:
		return d | {'args': sortedArgs({key:value for di in [attrFromState(other_i,'args',k) for other_i in l] for key,value in di.items()}),
					'text': sortedArgs({key:value for di in [attrFromState(other_i,'text',k) for other_i in l] for key,value in di.items()})}
	else:
		return d
def mergeStates(main,other,l,args=True):
	return {k: mergeStates_k(main,other,l,k,args=args) for other_i in l for k in other_i.states}
def mergeGmsSettings(main,other,order=gmspyStandardOrder,residual=True,args=True):
	l = [main]+other
	mdicts = {k: mergeDictAttrs(l,k) for k in ('macros','groups','locals')}
	mdictsSorted = {k: mergeDictAttrs(l,k,sort=order) for k in ('args','text')}
	mdictmain = {k: getattr(main,k) for k in ('name','from_db','state','Precompiler','Precompiler_options')}
	main.addAdjustedSettings(mdictmain | mdicts | mdictsSorted | {'states': mergeStates(main,other,l,args=args), 'db': main.db})
	main.Compile.run()
	mergeDbs(main,other,residual=residual)
	return main

class GmsSettings:
	# ---	0: Initialization	--- #
	def __init__(self,f=None,**kwargs):
		if f:
			with open(f,"rb") as file:
				self = pickle.load(file)
		else:
			self.addAdjustedSettings(kwargs)

	def addAdjustedSettings(self,kwargs):
		mergedDict = self.standardSettings | kwargs
		[setattr(self,key,value) for key,value in {k: self.AdjustInit(k,mergedDict) for k in mergedDict if k != 'groups'}.items()];
		self.states = kwargs['states'] if 'states' in kwargs else {'B': self.standardInstance()}

	def AdjustInit(self,k,kwargs):
		if k == 'Compile':
			return Compile(groups=kwargs['groups']) if kwargs[k] is None else kwargs[k]
		elif k == 'Precompiler':
			return Precompiler(**kwargs['Precompiler_options']) if kwargs[k] is None else kwargs[k]
		else:
			return kwargs[k]

	@property
	def standardSettings(self):
		return {'name': 'name', 'macros':{}, 'text': {}, 'args': {}, 'from_db': 'vars', 'db': GpyDB(), 'locals': {}, 
				'state': 'B','Compile':None, 'Precompiler': None, 'groups': {},'Precompiler_options': {'has_read_file': True}}

	def standardInstance(self,state='B'):
		return {'name': f"{self.name}_{state}", 'g_endo': OrdSet(), 'g_exo': OrdSet(), 'blocks': OrdSet(), 'solve': None}

	def __getitem__(self,item):
		try:
			return self.states[self.state][item]
		except KeyError:
			return getattr(self,item)

	def __setitem__(self,item,value):
		if item in ('g_endo','g_exo','blocks'):
			self.states[self.state][item] = OrdSet(value)
		else:
			self.states[self.state][item] = value

	def setstate(self,state=None):
		if state is None:
			self.state = list(self.states.keys())[0]
		elif state in self.states:
			self.state = state
		else:
			self.states[state] = self.standardInstance(state=state)
			self.state = state

	def try_state(self,state):
		return self.states[self.state] if state not in self.states else self.states[state]

	# ---	1: Subsetting	--- #
	# NB: Only works properly if groups are compiled using self.Compile and not self.Precompiler (gamY version)
	def metagroup(self,g):
		""" g ∈ {'g_exo','g_endo'} """
		return self.Compile.metaGroup(self.db,gs=self[g].v)
	def var_ss(self,var,g):
		""" type(var) == str, type(g) == _GmsPy.Group"""
		if self.db[var].type == 'scalar_variable':
			return self.db[var] if var in g.conditions else None
		else:
			return rc_AdjGpy(self.db[var],c=g.conditions[var]) if var in g.conditions else None
	def db_ss(self,g):
		""" g ∈ {'g_exo','g_endo'} """
		g = self.metagroup(g)
		return {k:v for k,v in {s: self.var_ss(s,g) for s in g.conditions} if v}
	def partition_db(self):
		d = {'non_var': self.db.gettypes(('set','subset','mapping','parameter','scalar_parameter')),
			 'var_endo': self.db_ss('g_endo'), 'var_exo': self.db_ss('g_exo')}
		d['residual'] = {k:v for k,v in self.db.gettypes(('scalar_variable','variable')).items() if k not in (list(d['var_endo'])+list(d['var_exo']))}
		return d

	# ---	2: Writing methods	--- #
	def reset_Precompiler(self):
		self.Precompiler = Precompiler(**(self.Precompiler_options | {'locals_': self.Precompiler.locals, 'user_functions': self.Precompiler.user_functions}))

	def write(self,check_root=True,reset=True,**kwargs):
		""" compile text from args. """
		if reset:
			self.reset_Precompiler()
		if 'args' in self.states[self.state]:
			if check_root:
				self['args'] = self.check_root(self['args'])
			self['text'] = {k: GmsWrite.arg2string(v,self.Precompiler) for k,v in self['args'].items()}
			return self['text']
		else:
			if check_root:
				self.args = self.check_root(self.args)
			self.text = {k: GmsWrite.arg2string(v,self.Precompiler) for k,v in self.args.items()}
			return self.text

	def check_root(self,args):
		return {'root': GmsWrite.write_root()} | args if not (list(args.keys()))[0].endswith(('root','root.gms','root.gmy','root.txt')) else args

	def stdArgs(self,blocks='',functions=None,prefix=None,prefix_run=None,run=True):
		return GmsWrite.standardArgs(self,self.db,f"""%{self.db.name}%""",blocks=blocks,functions=functions,run=run,prefix=self.name+'_' if prefix is None else prefix, prefix_run = self['name']+'_' if prefix_run is None else prefix_run)

	def stdArgs_gamY(self,blocks='',functions=None,declare_groups='',prefix=None,prefix_run=None,run=True):
		return GmsWrite.standardArgs_gamY(self,self.db,f"""%{self.db.name}%""",blocks=blocks,functions=functions,declare_groups=declare_groups,run=run,prefix=self.name+'_' if prefix is None else prefix, prefix_run = self['name']+'_' if prefix_run is None else prefix_run)

	def sortedArgs(self, order = gmspyStandardOrder):
		return sortedArgs(self['args'],order=order)

class GmsModel:
	def __init__(self,ws=None,options={},**kwargs):
		self.init_ws(ws)
		self.init_opt(**options,**kwargs)

	def init_ws(self,ws):
		if isinstance(ws,gams.GamsWorkspace):
			self.ws = ws
		elif type(ws) is str:
			self.ws = gams.GamsWorkspace(working_directory=ws)
		elif ws is None:
			self.ws = gams.GamsWorkspace()
		else:
			raise TypeError(f"The GmsModel class cannot be initialized with ws type {type(ws)}")

	def write_options(self,options_string):
		with open(os.path.join(self.ws.working_directory,self.opt_name), "w") as f:
			f.write(options_string)

	def init_opt(self,opt=None,opt_file=None,opt_name=None,**kwargs):
		self.opt_name = opt_name if opt_name else "options.opt"
		if isinstance(opt,str):
			self.write_options(opt)
			self.opt = self.ws.add_options()
			self.opt.file = 1
		elif isinstance(opt, gams.GamsOptions):
			self.opt = opt
		elif opt_file:
			self.opt = self.ws.add_options(opt_file=opt_file)
			self.opt.file = 1
		else:
			self.opt = self.ws.add_options()
		[setattr(self.opt,key,value) for key,value in kwargs.items()];
		
	@property
	def work_folder(self):
		return self.ws.working_directory

	def run(self,run=None,runfile=None,options_add={},options_run={},db_as_gpy=True):
		self.add_job(run=run,runfile=runfile,options=options_add)
		self.run_job(options=options_run)
		self.out_db = GpyDB(db=self.job.out_db,ws=self.ws) if db_as_gpy else None

	def add_job(self,run=None, runfile = None, options={}):
		if run:
			self.job = self.ws.add_job_from_string(run,**options)
		elif runfile:
			runfile = runfile if os.path.isabs(runfile) else os.path.join(self.work_folder,runfile)
			self.job = self.ws.add_job_from_file(runfile,**options)

	def run_job(self,options={}):
		self.job.run(gams_options=self.opt,**options)

	def addlocal(self,placeholder,local):
		self.opt.defines[placeholder] = local
