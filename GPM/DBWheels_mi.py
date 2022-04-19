import pandas as pd, Database
from Database import gpy
# from _MixTools import OrdSet
from DBWheels_bc import sparsedomain

def RepeatVar(x,symbols,db,c='std',sort_levels=None):
	""" Broadcast domains with conditions c"""
	v = sparsedomain([x]+symbols,db=db, c = ('and', [x]+symbols) if c == 'std' else c).add(x).dropna().rename(x.name)
	return v if sort_levels is None else v.reorder_levels(sort_levels)

def MergeDomains(symbols,db,c='std',sort_levels=None):
	v = sparsedomain(symbols,db=db, c = ('and', symbols) if c == 'std' else c).dropna().index
	return v if sort_levels is None else v.reorder_levels(sort_levels)

def ReturnAsSeries(symbol):
	if isinstance(symbol,pd.Index):
		return pd.Series(0, index = symbol)
	elif isinstance(symbol,(gpy,Database.gpy)):
		return ReturnAsSeries(symbol.vals)
	elif isinstance(symbol,pd.Series):
		return symbol