import pandas as pd, Database, DBWheels_read
from _MixTools import NoneInit
from DBWheels_rc import rc_pd
from DBWheels_agg import updateSetValues
_ftype_inputs, _ftype_outputs = ('CES','CES_norm','MNL'), ('CET','CET_norm','MNL_out')
_scalePreserving = ('CES_norm','CET_norm','MNL','MNL_out')

def checkOrIgnore(d,k):
	return d[k] if k in d else k
def reverseDict(d):
	return {v:k for k,v in d.items()}

class tree:
	def __init__(self, name, tree = None, io = None, db = None, f = None,**ns):
		self.name = name
		self.db = db
		self.addFunctionandIO(f,io)
		self.sp = True if self.f in _scalePreserving else False
		self.ns = {k:v if k not in ns else ns[k] for k,v in self.standardNamespace.items()}
		self.tree = NoneInit(tree,[])

	@property
	def standardNamespace(self):
		return {k:k for k in ('n','nn','nnn','s')} | {k: k+'_'+self.name for k in ('map','knot','branch','input','output','int')}

	def addFunctionandIO(self,f,io):
		if f:
			self.f = f
			if io is None:
				self.io = 'in' if self.f in _ftype_inputs else 'out'
			else:
				self.io = io
		else:
			self.io = 'in' if io is None else io
			self.f = 'CES' if self.io == 'in' else 'CET'

	def __getitem__(self,item):
		try:
			return self.db[self.ns[item]]
		except KeyError:
			return self.db[item]

	def __setitem__(self,item,value):
		try:
			self.db[self.ns[item]] = Database.gpy(value,**{'name': self.ns[item]})
		except KeyError:
			self.db[item] = Database.gpy(value,**{'name': item})

	def get(self,item):
		return self[item].vals

	def attrs_from_tree(self):
		self['map'] = pd.MultiIndex.from_tuples(self.tree, names = [self.ns['s'], self.ns['n'],self.ns['nn']])
		self['knot'] = self.get('map').droplevel(self.ns['nn']).unique()
		self['branch'] = self.get('map').droplevel(self.ns['n']).unique().rename([self.ns['s'],self.ns['n']])
		self['n'] = self.get('knot').union(self.get('branch')).droplevel(self.ns['s']).unique()
		self['s'] = self.get('map').get_level_values(self.ns['s']).unique()
		self['input'] = self.get('branch').difference(self.get('knot')) if self.io == 'in' else self.get('knot').difference(self.get('branch'))
		self['output'] = self.get('branch').difference(self.get('knot')) if self.io == 'out' else self.get('knot').difference(self.get('branch'))
		self['int'] = (self.get('branch').union(self.get('knot'))).difference(self.get('input').union(self.get('output')))

class tree_from_data(tree):
	def __init__(self,workbook,sheet,name=None,io=None,f=None,**ns):
		""" Workbook has to be supplied"""
		super().__init__(sheet if name is None else name,db = DBWheels_read.variables(workbook[sheet]),io=io,f=f,**ns)
		self.tree = self.db['mu'].index.to_list()

class AggTree:
	def __init__(self,name="",trees=None,**ns):
		self.name=name
		self.ns = {k:v if k not in ns else ns[k] for k,v in self.standardNamespace.items()}
		self.trees = NoneInit(trees,{})
		self.prune = ('n','nn','nnn','s','input','output','int')
		self.db = Database.GpyDB(alias=pd.MultiIndex.from_tuples([(self.n('n'),self.n('nn')), (self.n('n'),self.n('nnn'))]),**{'name':self.name})

	@property
	def standardNamespace(self):
		return {k:k for k in ('n','nn','nnn','s')} | {k: k+'_'+self.name for k in ('map','branch','knot','input','output','int','sp_knots')}

	def n(self,item,local=None):
		return self.ns[item] if local is None else self.trees[local].ns[item]

	def get(self,item,local=None):
		return self.db[self.n(item,local=local)].vals

	def __setitem__(self,item,value):
		self.db[self.n(item)] = value

	def __call__(self,namespace=None):
		[tree.attrs_from_tree() for tree in self.trees.values()];
		self.attrs_from_trees()
		self.adjust_trees()
		[self.add_db_prune(tree) for tree in self.trees.values()];
		if namespace:
			updateSetValues(self.db,self.n('n'),NoneInit(namespace,{}))
		return self

	def add_db_prune(self,tree):
		[Database.GpyDBs_AOM_Second(self.db,s) for name,s in tree.db.items() if checkOrIgnore(reverseDict(tree.ns),name) not in self.prune];

	def attrs_from_trees(self):
		self['n'] = pd.Index(set.union(*[set(tree.get('n')) for tree in self.trees.values()]), name = self.n('n'))
		self['s'] = pd.Index(set.union(*[set(tree.get('s')) for tree in self.trees.values()]), name = self.n('s'))
		self['map'] = pd.MultiIndex.from_tuples(set.union(*[set(tree.get('map')) for tree in self.trees.values()]),names = [self.n('s'),self.n('n'),self.n('nn')])
		self['branch'] = pd.MultiIndex.from_tuples(set.union(*[set(tree.get('branch')) for tree in self.trees.values()]), names = [self.n('s'),self.n('n')])
		self['knot']  = pd.MultiIndex.from_tuples(set.union(*[set(tree.get('knot')) for tree in self.trees.values()]), names = [self.n('s'),self.n('n')])
		inputs = set.union(*[set(tree.get('input')) for tree in self.trees.values()])
		outputs= set.union(*[set(tree.get('output')) for tree in self.trees.values()])
		ints = set.union(*[set(tree.get('int')) for tree in self.trees.values()])
		self['input'] = pd.MultiIndex.from_tuples(inputs-outputs,names = [self.n('s'),self.n('n')])
		self['output']= pd.MultiIndex.from_tuples(outputs-inputs,names = [self.n('s'),self.n('n')])
		self['int'] = pd.MultiIndex.from_tuples((inputs.intersection(outputs)).union(ints), names = [self.n('s'),self.n('n')])
		self['sp_knots'] = pd.MultiIndex.from_tuples(set().union(*[set(tree.get('knot')) for tree in self.trees.values() if tree.sp]), names = [self.n('s'),self.n('n')])

	def adjust_trees(self):
		[self.adjust_tree_in(tree) for tree in self.trees.values() if tree.io == 'in'];
		[self.adjust_tree_out(tree) for tree in self.trees.values() if tree.io == 'out'];

	def adjust_tree_in(self,tree):
		tree.ns['knot_o'] = 'knot_o_'+tree.name
		tree.ns['knot_no'] = 'knot_no_'+tree.name
		tree.ns['branch2o'] = 'branch2o_'+tree.name
		tree.ns['branch2no']= 'branch2no_'+tree.name
		tree['knot_o'] = tree.get('knot').intersection(self.get('output'))
		tree['knot_no'] = tree.get('knot').difference(self.get('output'))
		tree['branch2o'] = rc_pd(tree['map'], self.get('output')).droplevel(self.n('n')).rename([self.n('s'),self.n('n')])
		tree['branch2no'] = rc_pd(tree['map'], ('not', self.get('output'))).droplevel(self.n('n')).rename([self.n('s'),self.n('n')])

	def adjust_tree_out(self,tree):
		tree.ns['branch_o'] = 'branch_o_'+tree.name
		tree.ns['branch_no'] = 'branch_no_'+tree.name
		tree['branch_o'] = tree.get('branch').intersection(self.get('output'))
		tree['branch_no'] = tree.get('branch').difference(tree.get('branch_o'))

class AggTree_from_data(AggTree):
	def __init__(self,file_path,read_trees=None,name="",**ns):
		""" read_trees are passed to tree_from_data """
		super().__init__(name=name,**ns)
		wb = DBWheels_read.simpleLoad(file_path)
		if read_trees is None:
			read_trees = {sheet: {} for sheet in DBWheels_read.sheetnames_from_wb(wb)}
		self.trees = {t.name: t for t in (tree_from_data(wb,k,**v) for k,v in read_trees.items())}
