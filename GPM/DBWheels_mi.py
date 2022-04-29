import pandas as pd, Database, numpy as np
from Database import gpy
from _MixTools import NoneInit
from DBWheels_bc import sparsedomain
from DBWheels_rc import rc_pd,rc_pdInd
from DBWheels_agg import update_sets

def RepeatVar(x,symbols,db,c='std',sort_levels=None):
	""" Broadcast domains with conditions c"""
	v = sparsedomain([x]+symbols,db=db, c = ('and', [x]+symbols) if c == 'std' else c).add(x).dropna().rename(x.name)
	return v if sort_levels is None else v.reorder_levels(sort_levels)

def MergeDomains(symbols,db,c='std',sort_levels=None):
	v = sparsedomain(symbols,db=db, c = ('and', symbols) if c == 'std' else c).dropna().index
	return v if sort_levels is None else v.reorder_levels(sort_levels)

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

def gridDB(db0, dbT, name, n = 10, extractSol = None, db_name = 'grids', loop = 'l1', gridtype = 'linear', phi = 1, checkDiff = True, error = 1e-11):
	db = Database.GpyDB(ws = db0.ws, alias = db0.get('alias_'), **{'name': db_name})
	db[loop] = loop+'_'+pd.Index(range(1,n+1),name=loop).astype(str)
	for var in set(db0.gettypes('variable').keys()).intersection(set(dbT.gettypes('variable').keys())):
		commonIndex = db0.get(var).index.intersection(dbT.get(var).index)
		v0,vT = rc_pd(db0.get(var),commonIndex), rc_pd(dbT.get(var),commonIndex)
		if checkDiff:
			commonIndex = vT[abs(v0-vT)>error].index
			v0,vT = rc_pd(v0,commonIndex),rc_pd(vT,commonIndex)
		if not vT.empty:
			db['_'.join([var,name,'ss'])] = commonIndex
			db['_'.join([var,name])] = gpy(addGrid(v0,vT,db.get(loop),'_'.join([var,name]), gridtype=gridtype, phi=phi), **{'type':'parameter'})
	for var in set(db0.gettypes(['scalar_variable']).keys()).intersection(set(dbT.gettypes(['scalar_variable']).keys())):
		if (not checkDiff) or (abs(db0.get(var)-dbT.get(var))>error):
			db['_'.join([var,name,'ss'])] = db.get(loop)
			db['_'.join([var,name])] = gpy(addGrid(db0.get(var),dbT.get(var),db.get(loop),'_'.join([var,name]),gridtype=gridtype,phi=phi),**{'type':'parameter'})
	for var in NoneInit(extractSol,{}):
		db['_'.join(['sol',var,name])] = gpy(pd.Series(0, index = add1dIndex(rc_pdInd(db0[var],c=extractSol[var]),db.get(loop),sort_levels=db[loop].domains+db0[var].domains), name = '_'.join(['sol',var,name])),**{'type':'parameter'})
	update_sets(db,clean_alias=True)
	db.merge_internal()
	return db