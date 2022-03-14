import pandas as pd
from _Database import gpy

class OrdSet:
	def __init__(self,i=[]):
		self.v = list(dict.fromkeys(i))

	def __iter__(self):
		return iter(self.v)

	def __len__(self):
		return len(self.v)

	def __getitem__(self,item):
		return self.v[item]

	def __setitem__(self,item,value):
		self.v[item] = value

	def __add__(self,o):
		return OrdSet(self.v+list(o))

	def __sub__(self,o):
		return OrdSet([x for x in self.v if x not in o])

	def union(self,*args):
		return OrdSet(self.__add__([x for l in args for x in l]))

	def intersection(self,*args):
		return OrdSet([x for l in self.union(args) for x in l if x in self.v])

	def update(self,*args):
		self.v = self.union(*args).v

# 1: Simple methods used for writing gams text from pandas/gpy symbols
def write_gpy(s=None,c=None,alias={}, lag = {},l="",**kwargs):
	if s.type == 'set':
		return s.name+condition(c=c) if s.name not in alias else alias[s.name]+condition(c=c)
	elif s.type in ('subset','mapping'):
		return s.name+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type =='variable':
		return s.name+l+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type == 'scalar_variable':
		return s.name+l+condition(c=c)
	elif s.type == 'parameter':
		return s.name+gmsdomains(s,alias=alias,lag=lag)+condition(c=c)
	elif s.type == 'scalar_parameter':
		return s.name+condition(c=c)

def condition(c=None):
	return '' if c is None else f"$({point(c)})"

def point(vi):
	if isinstance(vi, gpy):
		return write_gpy(vi)
	elif isinstance(vi,dict):
		return write_gpy(**vi)
	elif isinstance(vi,tuple):
		return write_tuple(vi)
	elif isinstance(vi,str):
		return vi

def write_tuple(tup):
	if tup[0] == 'not':
		return f"( not ({point(tup[1])}))"
	else:
		return f"({f' {tup[0]} '.join([point(vi) for vi in tup[1]])})"

def gmsdomains(s,alias={},lag={}):
	return list2string([alias.get(item,item)+str(lag.get(item,'')) for item in s.domains])

def list2string(list_):
	return '[{x}]'.format(x=','.join(list_)) if list_ else ''

# 2: Writing methods for entire databases (of type GpyDB):
def write_from_db(db,types=('sets','alias','sets_other','sets_load','par','par_load','var','var_load'),exceptions=OrdSet(),exceptions_load=OrdSet(),gdx=None,onmulti=True):
	alltypes = {'sets': write_sets(db,exceptions=exceptions), 'alias': write_aliased_sets(db,exceptions=exceptions),'sets_other': write_sets_other(db,exceptions=exceptions), 'sets_load': write_sets_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load),
				'par': write_parameters(db,exceptions), 'par_load': write_parameters_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load),
				'var': write_variables(db,exceptions), 'var_load': write_variables_load(db,gdx,onmulti=onmulti,exceptions_load=exceptions_load)}
	return {k:v for k,v in alltypes.items() if k in types}

def write_sets(db,exceptions=OrdSet()):
	if bool(OrdSet(db.gettypes('set'))-OrdSet(db.get('alias_map2'))-exceptions) is False:
		return ''
	else:
		out_str = 'sets\n'
		for s in (OrdSet(db.gettypes('set'))-OrdSet(db.get('alias_map2'))-exceptions):
			out_str += '\t'+write_gpy(s=db[s])+'\n'
		return out_str+';\n\n'

def write_aliased_sets(db,exceptions=OrdSet()):
	out_str = ''
	for k,v in db.alias_dict.items():
		if k not in exceptions:
			out_str += 'alias({x},{y});\n'.format(x=k, y=','.join(list(v)))
	return out_str+'\n'

def write_sets_other(db,exceptions=OrdSet()):
	if bool(OrdSet(db.gettypes(('subset','mapping')))-exceptions) is False:
		return ''
	else:
		out_str = 'sets\n'
		for s in (OrdSet(db.gettypes(('subset','mapping')))-exceptions):
			out_str += '\t'+write_gpy(s=db[s])+'\n'
		return out_str+';\n\n'

def write_sets_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	if bool(OrdSet(db.gettypes(('set','subset','mapping')))-OrdSet(db.get('alias_map2'))-exceptions_load) is False:
		return ''
	else:
		out_str = '$GDXIN '+gdx+'\n'
		if onmulti:
			out_str += '$onMulti\n'
		for s in (OrdSet(db.gettypes(('set','subset','mapping')))-OrdSet(db.get('alias_map2'))-exceptions_load):
			out_str += '$load '+s+'\n'
		out_str += '$GDXIN\n'
		if onmulti:
			out_str += '$offMulti\n;\n'
		return out_str

def write_parameters(db,exceptions=OrdSet()):
	if bool(OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions) is False:
		return ''
	else:
		out_str = 'parameters\n'
		for s in (OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions):
			out_str += '\t'+write_gpy(s=db[s])+'\n'
		return out_str+';\n\n'

def write_parameters_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	if bool(OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions_load) is False:
		return ''
	else:
		out_str = '$GDXIN '+gdx+'\n'
		if onmulti:
			out_str += '$onMulti\n'
		for s in (OrdSet(db.gettypes(('scalar_parameter','parameter')))-exceptions_load):
			out_str += '$load '+s+'\n'
		out_str += '$GDXIN\n'
		if onmulti:
			out_str += '$offMulti\n'
		return out_str+'\n;\n'

def write_variables(db,exceptions=OrdSet()):
	if bool(OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions) is False:
		return ''
	else:
		out_str = 'variables\n'
		for s in (OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions):
			out_str += '\t'+write_gpy(s=db[s])+'\n'
		return out_str+';\n\n'

def write_variables_load(db,gdx,onmulti=True,exceptions_load=OrdSet()):
	if bool(OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions_load) is False:
		return ''
	else:
		out_str = '$GDXIN '+gdx+'\n'
		if onmulti:
			out_str += '$onMulti\n'
		for s in (OrdSet(db.gettypes(('scalar_variable','variable')))-exceptions_load):
			out_str += '$load '+s+'\n'
		out_str += '$GDXIN\n'
		if onmulti:
			out_str += '$offMulti\n'
		return out_str+'\n;\n'

# 3 root file:
default_options_root = {'SYSOUT': 'OFF', 'SOLPRINT': 'OFF', 'LIMROW': '0', 'LIMCOL': '0', 'DECIMALS': '6'}
def auxdict2equal(k,v):
	return k+'='+v 
def write_root(**kwargs):
	return f"""$ONEOLCOM
$EOLCOM #
OPTION {', '.join([auxdict2equal(k,v) for k,v in (default_options_root | kwargs).items()])};
"""

# 4: Write group statements