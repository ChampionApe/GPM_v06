import os, pandas as pd, numpy as np, gams, pickle, gams2numpy, gamstransfer, gmdcc
from collections.abc import Iterable
from six import string_types

default_attributes_variables = {k:i for k,i in zip(['level','marginal','lower','upper','scale'],range(-5,0))}
default_attributes_parameters= {k:i for k,i in zip(['value'],range(-1,0))}
admissable_py_types = (pd.Series,pd.Index, int, float,str,np.generic)

def return_version(x,dict_):
	""" Test if x is in dict_: If it is not, return x. 
	If it is rename x with x_int where int is the lowest natural number not already defined in dict_"""
	if x not in dict_:
		return x
	elif (x+'_0') not in dict_:
		return x+'_0'
	else:
		maxInt = max([int(y.split('_')[-1]) for y in dict_ if (y.rsplit('_',1)[0]==x and IfInt(y.split('_')[-1]))])
		return x+'_'+str(maxInt+1)

def IfInt(x):
	""" Tests if x is an integer + return boolean instead of valueerror"""
	try:
		int(x)
		return True
	except ValueError:
		return False

def is_iterable(arg):
	""" test if an argument is iterable and not strings. """
	return isinstance(arg, Iterable) and not isinstance(arg, string_types)

def kw_df(kwargs,key,df_val):
	return df_val if key not in kwargs else kwargs[key]

# 1: Basic functions:
def merge_symbols(s1,s2):
	if isinstance(s1,pd.Series):
		return s1.combine_first(s2)
	elif isinstance(s1,pd.Index):
		return s1.union(s2)
	elif type_pandas_(s1) in ('scalar_variable','scalar_parameter'):
		return s1

# 2: Identify types between gams databases and GPM databases:
def type_(symbol,name=None,type=None):
	if isinstance(symbol,gams.database._GamsSymbol):
		return type_gams_(symbol)
	elif isinstance(symbol,gpy_symbol):
		return symbol.type
	elif isinstance(symbol,admissable_py_types):
		return type_pandas_(symbol,name=name,type=type)

def type_gams_(symbol):
	"""  Return gpy_symbol.type from gams._GamsSymbol."""
	if isinstance(symbol,gams.GamsVariable):
		return type_gams_variable(symbol)
	elif isinstance(symbol,gams.GamsParameter):
		return type_gams_parameter(symbol)
	elif isinstance(symbol,gams.GamsSet):
		return type_gams_set(symbol)

def type_gams_variable(symbol):
	return 'scalar_variable' if symbol_is_scalar(symbol) else 'variable' 

def type_gams_parameter(symbol):
	return 'scalar_parameter' if symbol_is_scalar(symbol) else 'parameter' 

def type_gams_set(symbol):
	""" return gpy_symbol.type from gams.GamsSet """
	if len(symbol.domains_as_strings)==1:
		if symbol.domains_as_strings in [['*'], [symbol.name]]:
			return 'set'
		else:
			return 'subset'
	elif symbol.name!='SameAs':
		return 'mapping'

def type_pandas_(symbol,name=None,type=None,**kwargs):
	""" identify type from pandas-like input"""
	if isinstance(symbol, pd.Series):
		return type if type else 'variable'
	elif isinstance(symbol,pd.MultiIndex):
		return 'mapping'
	elif isinstance(symbol,pd.Index):
		return set_or_subset(symbol.name,name)
	elif isinstance(symbol,(int,float,str,np.generic)):
		return 'scalar_parameter' if type else 'scalar_variable'

def set_or_subset(s_name,name):
	return 'set' if s_name == name else 'subset'

def agg_type(type_i):
	if type_i in ('scalar_variable','variable'):
		return 'variable'
	elif type_i in ('scalar_parameter', 'parameter'):
		return 'parameter'
	elif type_i in ('set','subset','mapping'):
		return 'set'
	else:
		return type_i

# 3: From gdx data to Python/Pandas representation
# 3.1: Referencing gams._GamsSymbol
def gpydict_from_gams_(symbol,db_gams,g2np):
	if isinstance(symbol,gams.GamsSet):
		return gpydict_from_gamsSet(symbol,db_gams,g2np)
	elif isinstance(symbol,gams.GamsVariable):
		return gpydict_from_gamsVariable(symbol,db_gams,g2np)
	elif isinstance(symbol,gams.GamsParameter):
		return gpydict_from_gamsParameter(symbol,db_gams,g2np)

def gpydict_from_gamsSet(symbol,db_gams,g2np):
	return {'vals': index_from_np(np_from_gams(symbol, db_gams, g2np), symbol.name, symbol.domains_as_strings),
			'name': symbol.name, 
			'text': symbol.text,
			'type': type_gams_set(symbol)}

def gpydict_from_gamsVariable(symbol,db_gams,g2np):
	return {'vals': adjust_scalar(symbol,df_from_variable(np_from_gams(symbol,db_gams,g2np), symbol.name, symbol.domains_as_strings,**{'attributes': ['level']})['level']),
			'name': symbol.name,
			'text': symbol.text,
			'type': type_gams_variable(symbol)}

def gpydict_from_gamsParameter(symbol,db_gams,g2np):
	return {'vals': adjust_scalar(symbol,df_from_parameter(np_from_gams(symbol,db_gams,g2np), symbol.name,symbol.domains_as_strings)['value']),
			'name': symbol.name,
			'text': symbol.text,
			'type': type_gams_parameter(symbol)}

def adjust_scalar(symbol,vals):
	return vals if not symbol_is_scalar(symbol) else vals[0]

def df_from_variable(np_data,symbol_name,domains_as_strings,attributes=['level','marginal','lower','upper','scale']):
	return pd.DataFrame(np_data[:,[default_attributes_variables[k] for k in attributes]],
						index = index_from_np(np_data,symbol_name,domains_as_strings),
						columns = attributes)

def df_from_parameter(np_data,symbol_name,domains_as_strings,attributes=['value']):
	return pd.DataFrame(np_data[:,[default_attributes_parameters[k] for k in attributes]],
						index = index_from_np(np_data,symbol_name,domains_as_strings),
						columns = attributes)

def index_from_np(np_data,symbol_name,domains_as_strings):
	if len(domains_as_strings) > 1:
		return pd.MultiIndex.from_arrays([tryint(column) for column in np_data.T[0:len(domains_as_strings)]], 
										names = index_names_from_np(symbol_name,domains_as_strings))
	elif len(domains_as_strings) == 1:
		return pd.Index(tryint(np_data[:,0]),name=index_names_from_np(symbol_name,domains_as_strings)[0])
	else:
		return None

def index_names_from_np(symbol_name,domains_as_strings):
	if domains_as_strings == ["*"]:
		return [symbol_name]
	else:
		return domains_as_strings

def tryint(x):
    try:
        return x.astype(int)
    except ValueError:
        return x

def np_from_gams(symbol,db_gams,g2np):
	return g2np.gmdReadSymbolStr(db_gams,symbol.name)

def symbol_is_scalar(symbol):
	return not symbol.domains_as_strings


# 4: From Python to GAMS
def gamstransfer_from_py_(symbol,container):
	""" symbol = gpy_symbol, container = gamstransfer.Container """
	if symbol.type == 'set':
		gamstransferSet_from_py(symbol.index, container, description=symbol.text)
	elif symbol.type == 'subset':
		gamstransferSubset_from_py(symbol.index, symbol.name, container, description = symbol.text)
	elif symbol.type == 'mapping':
		gamstransferMapping_from_py(symbol.index, symbol.name, container, description = symbol.text)
	elif symbol.type == 'scalar_variable':
		gamstransferScalarVariable_from_py(symbol.vals, symbol.name, container, description = symbol.text)
	elif symbol.type =='variable':
		gamstransferVariable_from_py(symbol.df, symbol.name, container, description=symbol.text)
	elif symbol.type == 'scalar_parameter':
		gamstransferScalarParameter_from_py(symbol.vals, symbol.name, container, description=symbol.text)
	elif symbol.type == 'parameter':
		gamstransferParameter_from_py(symbol.df, symbol.name, container, description=symbol.text)

def gamstransferSet_from_py(index,container,description=""):
	gamstransfer.Set(container, index.name, description=description, records = index.astype(str))

def gamstransferSubset_from_py(index,name,container,description=""):
	gamstransfer.Set(container, name, index.name, description=description, records = index.astype(str))

def gamstransferMapping_from_py(index,name,container,description=""):
	gamstransfer.Set(container, name, index.names, description=description, records = index.to_frame(index=False).astype(str))

def gamstransferScalarVariable_from_py(scalar, name, container, description=""):
	if isinstance(scalar,pd.DataFrame):
		gamstransfer.Variable(container, name, description = description, records = scalar)
	elif not is_iterable(scalar):
		gamstransfer.Variable(container, name, description = description, records = pd.DataFrame([scalar], columns = ['level']))

def gamstransferVariable_from_py(df, name, container, description = ""):
	gamstransfer.Variable(container, name, domain= df.index.names, description=description, records = df.reset_index().astype({k:str for k in df.index.names}))

def gamstransferScalarParameter_from_py(scalar, name, container, description=""):
	gamstransfer.Parameter(container, name, description="", records = scalar)

def gamstransferParameter_from_py(df, name, container, description= ""):
	gamstransfer.Parameter(container, name, domain = df.index.names, description=description, records = df.reset_index().astype({k:str for k in df.index.names}))