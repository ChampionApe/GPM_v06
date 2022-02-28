import pandas as pd
from _Database import gpy

# Simple methods used for writing gams text from pandas/gpy symbols
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
