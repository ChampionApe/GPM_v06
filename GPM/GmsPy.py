from _GmsPy import *
from Database import GpyDB

class GmsSettings:
	def __init__(self,ws=None,file_path=None, **kwargs):
		if pickle_path is not None:
			self.init_from_pickle(file_path,ws=ws)
		else:
			self.init_ws(ws)
			[setattr(self,key,value) for key,value in self.adjustedSettings(**kwargs)];
			self.states = kwargs['states'] if 'states' in kwargs else {'B': self.standardInstance()}

	def adjustedSettings(self,**kwargs):
		return {k:kwargs[k] if k in kwargs else v for k,v in self.standardSettings}

	def __getitem__(self,item):
		return self.states[self.state][item]

	def __setitem__(self,item,value):
		self.states[self.state][item] = value

	@property
	def standardSettings(self):
		return {'name': 'name', 'compiler': None, 'text': {}, 'args': {}, 'groups': None, dbs: {}, 'locals': {},'state': 'B'}

	def standardInstance(self,state='B'):
		return {'name': f"{self.name}_{state}", 'g_endo': OrdSet(), 'g_exo': OrdSet(), 'blocks': OrdSet(), 'solve': None}

	def write(self):
		""" Writes dictionary of strings that can be passed to gams. """
		if 'args' in self.states[self.state]:
			self['text'] = {k: arg2string(v[0],v[1]) for k,v in self['args'].items()}
			return self['text']
		else:
			self.text = {k: arg2string(v[0],v[1]) for k,v in self.args.items()}
			return self.text

	def init_ws(self,ws):
		if isinstance(ws,gams.GamsWorkspace):
			self.ws = ws
		elif type(ws) is str:
			self.ws = gams.GamsWorkspace(working_directory=ws)
		elif ws is None:
			self.ws = gams.GamsWorkspace()
		else:
			raise TypeError(f"The GmsSettings class cannot be initialized with ws type {type(ws)}")

	def init_from_pickle(self,file_path,ws=None):
		with open(file_path,"rb") as file:
			pickled_data=pickle.load(file)
		self.update_with_ws(ws,pickled_data.__dict__)

	def update_with_ws(self,ws,dict_):
		if ws is None:
			self.__dict__ = dict_
		else:
			self.__dict__ = {key: value for key,value in dict_.items() if key not in ('ws')}
			self.init_ws(ws)

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


