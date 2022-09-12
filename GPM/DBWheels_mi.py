import pandas as pd, numpy as np
from DBWheels_bc import sparsedomain
from DBWheels_rc import rc_pd

def RepeatVar(x,symbols,db,c='std',sort_levels=None):
	""" Broadcast domains with conditions c"""
	v = sparsedomain([x]+symbols,db=db, c = ('and', [x]+symbols) if c == 'std' else c).add(x).dropna().rename(x.name)
	return v if sort_levels is None else v.reorder_levels(sort_levels)

def MergeDomains(symbols,db,c='std',sort_levels=None):
	v = sparsedomain(symbols,db=db, c = ('and', symbols) if c == 'std' else c).dropna().index
	return v if sort_levels is None else v.reorder_levels(sort_levels)

def mergeMI(listOfMI,names=None):
	""" Merge a list of pd.MultiIndex into one. Uses pd.concat, i.e. assumes consistent index domains. """
	if listOfMI:
		return mergeMultiIndex(listOfMI)
	elif len(names)==1:
		return pd.Index([],name=names[0])
	elif len(names)>1:
		return pd.MultiIndex.from_tuples([],names=names)

def mergeMultiIndex(listOfMI):
	return pd.MultiIndex.from_frame(pd.concat([l.to_frame() for l in listOfMI]))

def mergeMult(mi1, mi2):
	""" Merge mi2 onto mi1. Merge on overlapping levels. Returns an index with the same length as mi1 (drops unused levels)"""
	o,d1,d2 = [x for x in mi1.names if x in mi2.names], [x for x in mi1.names if x not in mi2.names], [x for x in mi2.names if x not in mi1.names]
	mi1_, mi2_ = mi1.to_frame().droplevel(d1), mi2.reorder_levels(o+d2).to_frame().droplevel(d2)[d2]
	return pd.MultiIndex.from_frame(pd.concat([mi1_, rc_pd(mi2_, mi1_)],axis=1))

def applyMult(symbol, mapping):
	if isinstance(symbol,pd.Index):
		return (pd.Series(0, index = rc_pd(mapping, symbol)).add(pd.Series(0, index = symbol))).dropna().index.reorder_levels(symbol.names+[k for k in mapping.names if k not in symbol.names])
	elif isinstance(symbol,pd.Series):
		return (pd.Series(0, index = rc_pd(mapping, symbol)).add(symbol)).reorder_levels(symbol.index.names+[k for k in mapping.names if k not in symbol.index.names])

# ShockFunctions:
def add1dIndex(index,addindex,sort_levels=None):
	""" If index is None: Return simply the addindex. Else, return the cartesian product of the two. """
	if index is None:
		return addindex
	elif isinstance(index,pd.MultiIndex):
		mindex = pd.MultiIndex.from_tuples([x+(y,) for x in index for y in addindex],names=index.names+addindex.names)
	elif isinstance(index,pd.Index):
		mindex = pd.MultiIndex.from_tuples([(x,y) for x in index for y in addindex],names=index.names+addindex.names)
	return mindex if sort_levels is None else mindex.reorder_levels(sort_levels)

def grid(v0,vT,index,gridtype='linear',phi=1):
	""" If v0, vT are 1d numpy arrays, returns 2d array. If scalars, returns 1d arrays. """
	if gridtype == 'linear':
		return np.linspace(v0,vT,len(index))
	elif gridtype=='polynomial':
		return np.array([v0+(vT-v0)*((i-1)/(len(index)-1))**phi for i in range(1,len(index)+1)])

def addGrid(v0,vT,index,name,gridtype = 'linear', phi = 1,sort_levels=None):
	if isinstance(v0,pd.Series):
		return pd.DataFrame(grid(v0,vT,index,gridtype=gridtype,phi=phi).T, index = v0.index, columns = index).stack().rename(name).reorder_levels(index.names+v0.index.names if sort_levels is None else sort_levels)
	else:
		return pd.Series(grid(v0,vT,index,gridtype=gridtype,phi=phi), index = index,name=name)
