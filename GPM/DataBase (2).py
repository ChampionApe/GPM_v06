from DataBase_BaseFunctions import *

# 0.1: Robust methods for adding/merging symbols
def add_symbol(db,symbol,container=None,write=True,**kwargs):
	""" Symbol ∈ {gams.database._GamsSymbol, pandas-like symbol, gpy_symbol}. db ∈ {dict, gams.GamsDatabase}. """
	gpy = gpy_symbol(symbol,**kwargs)
	if isinstance(db,(PM_database,GPM_database)):
		db[gpy.name] = gpy_type
	elif isinstance(db,gams.GamsDatabase):
		gamstransfer_from_py_(symbol,container)
		if write:
			container.write(write_to=db)

def add_or_merge(db,symbol,priority,container=None,write=True,**kwargs):
	g = gpy_symbol(symbol,**kwargs)
	if g.name in GPM_database.symbols_(db):
		gg = gpy_symbol(db[g.name])
		if priority =='first':
			vals = merge_symbols(gg.vals,g.vals)
		elif priority == 'second':
			vals = merge_symbols(g.vals,gg.vals)
		elif priority == 'replace':
			vals = g.vals
	add_symbol(db,g,container=container,write=write)

# 0.2: database functions
def dict_from_gams(db_gams,g2np):
	""" can be used as database input in PM_database """
	return {symbol.name: gpy_symbol(gpydict_from_gams_(symbol,db_gams,g2np)) for symbol in db_gams}

def gams_from_db_py(db_py,container=None):
	""" db_py ∈ {PM_database, GPM_database} """
	if container is None: 
		container = gamstransfer.Container()
	[gamstransfer_from_py_(symbol,container) for symbol in db_py];
	return container

def merge_dbs(db1,db2,priority='second'):
	""" Merge symbols from db2 into db1. Robust but slow. db1,db2 ∈ {GPM_database, PM_database, gams.GamsDatabase} """
	if isinstance(db1,gams.GamsDatabase):
		container = gamstransfer.Container()
	[add_or_merge(db1,symbol,priority,container=container,write=False) for symbol in db2];
	if isinstance(db1,gams.GamsDatabase):
		container.write_to(db1)

class gpy_symbol:
	""" Customized class of symbols used in the PM/GPM database classes. """
	def __init__(self,symbol,**kwargs):
		""" Initialize with gpy_symbol, dict, or pandas object.
			Fast init with suitable dict/gpy_symbol. """
		if isinstance(symbol,(gpy_symbol,dict)):
			[setattr(self,key,value) for key,value in symbol.items() if key not in kwargs];
			[setattr(self,key,value) for key,value in kwargs.items()];
		elif isinstance(symbol,admissable_py_types):
			self.vals = symbol
			self.name = kwargs['name'] if 'name' in kwargs else symbol.name
			self.type = type_pandas_(symbol, **kwargs)
			self.text = kw_df(kwargs,'text',"")

	def __iter__(self):
		return iter(self.vals)

	def __len__(self):
		return len(self.vals)

	def items(self):
		return self.__dict__.items()

	def copy(self):
		obj = type(self).__new__(self.__class__,None)
		obj.__dict__.update(self.__dict__)
		return obj

	@property
	def index(self):
		if isinstance(self.vals,pd.Index):
			return self.vals
		elif hasattr(self.vals,'index'):
			return self.vals.index
		else:
			return None

	@property
	def domains(self):
		return [] if self.index is None else self.index.names

	@property
	def df(self):
		""" Only works if self.vals is a pandas series + type is either variable/parameter."""
		return self.vals.to_frame(name='level' if self.type == 'variable' else 'value')

	# SUBSETTING METHODS / WRITE CONDITIONS TO GAMS:
	def rctree_gams(self,c):
		""" writes a nest of conditions into a gams statement to condition on."""
		if isinstance(c,dict):
			return self.d(d2t(c)) if list(c.keys())[0]!='not' else self.one_c(d2t(c))
		elif isinstance(c,str):
			return c
		elif isinstance(c,gpy_symbol):
			return c.write()
		else:
			return None

	def d(self,kv):
		if isinstance(kv[1],gpy_symbol):
			return f"({f' {kv[0]} '.join([self.point(vi) for vi in [kv[1]]])})"
		else:
			return f"({f' {kv[0]} '.join([self.point(vi) for vi in kv[1]])})"			

	def one_c(self,vi):
		return vi[0]+' '+self.point(vi[1])

	def point(self,vi):
		if isinstance(vi,gpy_symbol):
			return vi.write()
		elif isinstance(vi,str):
			return vi
		elif isinstance(vi,dict) and list(vi.keys())[0]!='not':
			return self.d(d2t(vi))
		elif isinstance(vi,dict):
			return self.one_c(d2t(vi))
		elif isinstance(vi,list) and len(vi)==1:
			return self.d(d2t(vi[0]))

	def rctree_pd(self,c):
		""" returns the pandas representation of the variable subsetted according to sets in the conditions tree."""
		if isinstance(c,dict):
			return self.vals[self.d_pd(d2t(c))]
		elif isinstance(c,gpy_symbol):
			return self.vals[self.bool_ss(c)]
		elif isinstance(c,str):
			raise TypeError('cannot subset pandas object with string; add gpy_symbol instead.')
		else:
			return self.vals

	def d_pd(self,kv):
		if not isinstance(kv[1],gpy_symbol):
			return self.translate_k2pd([self.point_pd(vi) for vi in kv[1]],kv[0])
		else:
			return self.translate_k2pd([self.point_pd(vi) for vi in [kv[1]]],kv[0])

	def point_pd(self,vi):
		if isinstance(vi,gpy_symbol):
			return self.bool_ss(vi)
		elif isinstance(vi,dict):
			if isinstance(d2t(vi)[1],gpy_symbol):
				return self.d_pd((d2t(vi)[0],[d2t(vi)[1]]))
			else:
				return self.d_pd(d2t(vi))

	def translate_k2pd(self,l,k):
		""" Apply and/or/not keys to list of criteria (if k=not the l is a single boolean)."""
		if k == 'and':
			return sum(l)==len(l)
		elif k == 'or':
			return sum(l)>0
		elif k == 'not' and isinstance(l,(list,set)):
			return ~l[0]
		elif k == 'not':
			return ~l

	def bool_ss(self,ss):
		return self.common_index(ss).isin(ss.index)

	def common_index(self,ss):
		return self.index.droplevel([x for x in self.domains if x not in ss.domains])

class PM_database:
	def __init__(self,database={},**kwargs):
		self.name = kw_df(kwargs,'name','rname')
		self.database = database

	def __iter__(self):
		return iter(self.database.values())

	def __len__(self):
		return len(self.database)

	def __getitem__(self,item):
		return self.database[item]

	def __setitem__(self,item,value):
		if item in self.database:
			if not is_iterable(value) and is_iterable(self[item].vals):
				value = pd.Series(value,index=self[item].index,name=self[item].name)
		self.database[item] = gpy_symbol(value,**{'name': item})

	def __getstate__(self):
		self.db_pickle = {key: self[key].__dict__ for key in self.database}
		return {key: value for key,value in self.__dict__.items() if key!='database'}

	def __setstate__(self,dict_):
		self.__dict__ = {key: value for key,value in dict_.items() if key != 'db_pickle'}
		self.database = {key: gpy_symbol(value) for key,value in dict_['db_pickle'].items()}

	def __delitem__(self,item):
		del(self.database[item])

	def copy(self):
		obj = type(self).__new__(self.__class__,None)
		obj.__dict__.update({k:v for k,v in self.__dict__.items() if k != 'database'})
		obj.database = {k:gpy_symbol(v) for k,v in self.database.items()}
		return obj

class GPM_database:
	def __init__(self,pickle_path=None,workspace=None,db=None,alias=None,**kwargs):
		""" Init methods: 	(1) from file path to a pickle (fastest, only uses the kwargs 'workspace','alias'), 
							(2) db = GPM_database (fast, only uses the kwarg 'workspace','alias'), 
							(3) db = dict (fast, but does not check validity of attributes. only uses 'workspace','alias'), 
							(4) db ∈ {None, str, gams.GamsDatabase} (slower, but more robust. uses all kwargs except 'pickle_path'); """ 
		if pickle_path is not None:
			self.init_from_pickle(pickle_path,workspace=workspace)
		elif isinstance(db,dict):
			self.update_with_ws(workspace,db)
		elif isinstance(db,GPM_database):
			self.init_from_GPM(db,workspace=workspace)
		else:
			self.init_ws(workspace)
			self.g2np = gams2numpy.Gams2Numpy(self.workspace.system_directory)
			self.name = self.versionized_name(kw_df(kwargs,'name','rname'))
			self.export_settings = {'dropattrs': ['database','workspace','g2np'], 'data_folder': kw_df(kwargs,'data_folder',os.getcwd())}
			self.init_dbs(db)
			self.series = PM_database(name=self.name, database=dict_from_gams(self.database,self.g2np))
		self.update_alias(alias=alias)

	###################################################################################################
	###									0: Pickling/load/export settings 							###
	###################################################################################################
	def versionized_name(self,name):
		""" test if name is available in the current workspace; update with an added if it is not """
		return return_version(name,self.workspace._gams_databases)

	def init_from_pickle(self,pickle_path,workspace=None):
		with open(pickle_path,"rb") as file:
			pickled_data=pickle.load(file)
		self.update_with_ws(workspace,pickled_data.__dict__)

	def init_from_GPM(self,db,workspace=None):
		self.update_with_ws(workspace,db.__dict__)

	def update_with_ws(self,workspace,dict_):
		if workspace is None:
			self.__dict__ = dict_
		else:
			self.__dict__ = {key: value for key,value in dict_.items() if key not in ('workspace','database')}
			self.init_ws(workspace)
			self.name = self.versionized_name(self.name) # update name of database if it is already used in the current workspace.
			self.init_dbs(dict_['database'])

	def init_ws(self,workspace):
		if workspace is None:
			self.workspace = gams.GamsWorkspace()
		elif type(workspace) is str:
			self.workspace = gams.GamsWorkspace(working_directory=workspace)
		elif isinstance(workspace,gams.GamsWorkspace):
			self.workspace = workspace
		self.work_folder = self.workspace.working_directory

	def init_dbs(self,db):
		if db is None:
			self.database = self.workspace.add_database(database_name=self.name)
		elif type(db) is str:
			self.database = self.workspace.add_database_from_gdx(db,database_name=self.name)
		elif isinstance(db,gams.GamsDatabase):
			self.database = self.workspace.add_database(source_database=db,database_name=self.name)
		elif isinstance(db,GPM_database):
			self.database = self.workspace.add_database(source_database=db.database,database_name=self.name)

	def update_alias(self,alias=None,priority='first'):
		if alias is None:
			alias = pd.MultiIndex.from_tuples([],names=['alias_set','alias_map2'])
		if 'alias_' not in self.series:
			self.series['alias_'] = alias
		else:
			self.series['alias_'] = self.get('alias_').union(alias)
		self.series['alias_set'] = self.get('alias_').get_level_values('alias_set').unique()
		self.series['alias_map2'] = self.get('alias_').get_level_values('alias_map2').unique()

	def __getstate__(self):
		if 'database' not in self.export_settings['dropattrs']:
			self.database.export(self.export_settings['data_folder']+'\\'+self.name+'.gdx')
		return {key: value for key,value in self.__dict__.items() if key not in self.export_settings['dropattrs']}

	def __setstate__(self,dict_):
		self.__dict__ = dict_
		try:
			self.workspace = gams.GamsWorkspace(working_directory=self.work_folder)
		except FileNotFoundError:
			self.workspace = gams.GamsWorkspace(working_directory=os.getcwd())
		self.g2np = gams2numpy.Gams2Numpy(self.ws.system_directory)
		if 'database' not in self.export_settings['dropattrs']:
			self.database = self.workspace.add_database_from_gdx(self.export_settings['data_folder']+'\\'+self.name+'.gdx')
		else:
			self.database = self.workspace.add_database()
		if 'series' in self.export_settings['dropattrs']:
			self.series = PM_database(name=self.name,database=dict_from_gams(self.database,self.g2np))
	
	def export(self,name=None,repo=None):
		name = self.name if name is None else name
		repo = self.export_settings['data_folder'] if repo is None else repo
		with open(repo+'\\'+name, "wb") as file:
			pickle.dump(self,file)

	###################################################################################################
	###								1: Properties and base methods 									###
	###################################################################################################

	def items(self):
		return self.series.items()

	def keys(self):
		return self.series.keys()

	def values(self):
		return self.series.values()

	def __iter__(self):
		return self.series.__iter__()

	def __len__(self):
		return self.series.__len__()

	def __getitem__(self,item):
		try:
			return self.series[item]
		except KeyError:
			return self.series[self.alias(item)]

	def __setitem__(self,name,value):
		self.series.__setitem__(name,value)

	def get(self,item):
		try:
			return self.series[item].vals
		except KeyError:
			return self.series[self.alias(item)].vals.rename(item)

	@staticmethod
	def symbols_(db):
		return {symbol.name: symbol for symbol in db}

	@property
	def symbols(self):
		return self.symbols_(self.series)

	@property 
	def sets(self):
		return {x+'s': [symbol.name for symbol in self.series if symbol.type==x] for x in ('set','subset','mapping')}

	@property 
	def sets_flat(self):
		return [symbol.name for symbol in self.series if agg_type(symbol.type)=='set']

	@property
	def variables(self):
		return {x+'s': [symbol.name for symbol in self.series if symbol.type==x] for x in ('scalar_variable','variable')}

	@property
	def variables_flat(self):
		return [symbol.name for symbol in self.series if agg_type(symbol.type)=='variable']

	@property 
	def parameters(self):
		return {x+'s': [symbol.name for symbol in self.series if symbol.type==x] for x in ('scalar_parameter','parameter')}

	@property 
	def parameters_flat(self):
		return [symbol.name for symbol in self.series if agg_type(symbol.type)=='parameter']

	@property
	def types(self):
		return {symbol.name: symbol.type for symbol in self.series}

	def copy(self,dropattrs=['database'],**kwargs):
		""" return copy of database. Ignore elements in dropattrs."""
		db = GPM_database(**{**self.__dict__,**kwargs})
		if 'series' not in dropattrs and 'series' not in kwargs.keys():
			db.series = self.series.copy()
		return db

	###################################################################################################
	###									2: Dealing with aliases			 							###
	###################################################################################################

	@property
	def alias_dict(self):
		return {} if 'alias_' not in self.symbols else {name: self.get('alias_').get_level_values(1)[self.get('alias_').get_level_values(0)==name] for name in self.get('alias_').get_level_values(0).unique()}

	@property
	def alias_dict0(self):
		return {key: self.alias_dict[key].insert(0,key) for key in self.alias_dict}

	@property
	def alias_notin_db(self):
		return set(self.get('alias_map2'))-set(self.sets['sets'])

	def alias_all(self,x):
		if x in self.get('alias_set').union(self.get('alias_map2')):
			return self.alias_dict0[self.alias(x)]
		else: 
			return [x]

	def alias(self,x,index_=0):
		if x in self.get('alias_set'):
			return self.alias_dict0[x][index_]
		elif x in self.get('alias_map2'):
			key = self.get('alias_').get_level_values(0)[self.get('alias_').get_level_values(1)==x][0]
			return self.alias_dict0[key][index_]
		elif x in self.sets_flat and index_==0:
			return x
		else:
			raise TypeError(f"{x} is not aliased")

	def domains_unique(self,x):
		"""
		Returns list of sets a symbol x is defined over. If x is defined over a set and its alias, only the set is returned.
		"""
		return np.unique([self.alias(name) for name in self[x].index.names]).tolist()

	def vardom(self,set_,types=['variable','parameter']):
		""" Return a dictionary with keys = aliases of the set 'x', and values = list of variables defined over the set/alias"""
		return {set_i: [x for x in set([k for k,v in self.types.items() if v in types])-set(['alias_set','alias_map2']) if set_i in self[x].domains] for set_i in self.alias_all(set_)}

	###################################################################################################
	###								3: METHODS FOR AGGREGATING A DATABASE	 						###
	###################################################################################################

	def merge_internal(self,priority='second',fast=True):
		if fast:
			container = gams_from_db_py(self.series)
			container.write(write_to=self.database)
		else:
			self.merge_dbs(self.database,self.series,priority=priority)

	###################################################################################################
	###								3.1: UPDATE DOMAINS FROM OTHER SYMBOLS	 						###
	###################################################################################################

	def update_all_sets(self,clean_up=True,types=['variable','parameter'],ign_alias=False,clean_alias=False):
		self.update_sets_from_types(clean_up=clean_up,types=types,ign_alias=ign_alias)
		if clean_alias:
			self.clean_aliases(types)
		self.update_aliased_sets(ign_alias=False)
		if clean_up:
			self.update_subsets_from_sets()
			self.update_maps_from_sets()

	def update_sets_from_types(self,clean_up=True,types=['variable','parameter'],ign_alias=False):
		if clean_up:
			[self.__setitem__(set_,pd.Index([],name=set_)) for set_ in set(self.sets['sets'])-set(['alias_set','alias_map2'])];
		[self.update_sets_from_index(self[symbol].index,ign_alias=ign_alias) for symbol in set([k for k,v in self.types.items() if v in types])-set(['alias_set','alias_map2'])];

	def update_aliased_sets(self,ign_alias=False):
		for set_i in self.alias_dict:
			all_elements = sunion_empty([set(self.get(set_ij)) for set_ij in self.alias_dict0[set_i] if set_ij in self.sets['sets']])
			if ign_alias is False:
				[self.__setitem__(set_ij,pd.Index(all_elements,name=set_ij)) for set_ij in self.alias_dict0[set_i] if set_ij in self.sets['sets']];
			else:
				[self.__setitem__(set_ij,pd.Index(all_elements,name=set_ij)) for set_ij in self.alias_dict0[set_i]];

	def update_sets_from_index(self,index_,ign_alias=False):
		""" The ign_alias=True ignores the indices defined over aliased sets that are not defined in the db"""
		if ign_alias:
			[add_or_merge(self.series,index_.get_level_values(set_).unique(),'first') for set_ in set(index_.names)-self.alias_notin_db];
		else:
			[add_or_merge(self.series,index_.get_level_values(set_).unique(),'first') for set_ in index_.names];

	def update_subsets_from_sets(self):
		[self.update_subset(ss) for ss in self.sets['subsets']];

	def update_subset(self,ss):
		if self.alias(self.get(ss).name) not in self.symbols:
			self.__setitem__(ss,pd.Index([],name=self.get(ss).name))
		else:
			self.__setitem__(ss,self[ss].rctree_pd(self[self.alias(self.get(ss).name)]))

	def update_maps_from_sets(self):
		[self.update_map(m) for m in self.sets['mappings']];

	def update_map(self,m):
		if sum([bool(set(self.symbols.keys()).intersection(self.alias_all(s))) for s in self[m].domains])<len(self[m].domains):
			self.__setitem__(m,pd.MultiIndex.from_tuples([],names=self[m].domains))
		else:
			self.__setitem__(m,self[m].rctree_pd({'and': [self[s] for s in self[m].domains]}))

	def clean_aliases(self,types):
		""" Remove aliases that are not used. """
		self['alias_'] = pd.MultiIndex.from_tuples(self.active_aliases(types), names=['alias_set','alias_map2'])
		self['alias_set'] = self.get('alias_').get_level_values('alias_set').unique()
		self['alias_map2'] = self.get('alias_').get_level_values('alias_map2').unique()

	def active_aliases(self,types):
		""" Return list of tuples with alias_ that are used in the model variables / mappings"""
		return [(k,v) for k in self.get('alias_set') for v in [x for x in self.alias_dict[k] if len(self.vardom(k,types=types)[x])>0]]