import pandas as pd, Database
from DBWheels_rc import rctree_pd, rc_pd, rc_pdInd
from DBWheels_mi import addGrid, add1dIndex, applyMult
from _MixTools import NoneInit

# Main methods:
# 1. updateSetValues: Update name of set elements in database using a mapping (dictionary)
# 2. read_sets: Add sets to the database by reading established variables/parameters/mappings.
# 3. update_sets: For existing database clean up set definitions and use 'read_sets' method to redefine sets.
# 4. subset_db: Subset all symbols in database. 
# 5. Aggregate database according to mapping. 

def subset_db(db,index):
	[subset_db_valsFromList(db, index.rename(k), v) for k,v in db.vardom(index.name, types = ('set','subset','mapping','variable','parameter')).items()];

def subset_db_valsFromList(db,index,listOfSymbols):
	[db[symbol].__setattr__('vals', rctree_pd(db.get(symbol), index)) for symbol in listOfSymbols];

def updateSetValues(db,set_,ns):
	""" Update set values for 'set_' using the namespace 'ns' """
	full_map = {k:k if k not in ns else ns[k] for k in db[set_]}
	for k,v in db.vardom(set_,types=['set','subset','mapping','parameter','variable']).items():
		[updateSetValue_Symbol(db,k,s,full_map) for s in v];

def updateSetValue_Symbol(db,set_,s,ns):
	if not db.get(s).empty:
		if isinstance(db.get(s),pd.MultiIndex):
			db[s].vals = db.get(s).set_levels(db.get(s).levels[db[s].domains.index(set_)].map(ns),level=set_)
		elif isinstance(db.get(s),pd.Index):
			db[s].vals = db[s].index.map(ns).unique()
		elif isinstance(db[s].index,pd.MultiIndex):
			db.get(s).index = db[s].index.set_levels(db[s].index.levels[db[s].domains.index(set_)].map(ns),level=set_)
		elif isinstance(db[s].index,pd.Index):
			db.get(s).index = db[s].index.map(ns).unique()

def add_or_merge_vals(db,symbol,name=None):
	if name is None:
		name = symbol.name
	if name in Database.symbols_db(db):
		db[name].vals = Database.merge_gpy_vals(symbol, db[name].vals)
	else:
		db[name] = symbol

def sunion_empty(ls):
	""" return empty set if the list of sets (ls) is empty"""
	try:
		return set.union(*ls)
	except TypeError:
		return set()

# Small collection of methods for cleaning/reading set elements in a database
def update_sets(db, types = None, clean=True, ignore_alias=False, clean_alias = False):
	if clean:
		clean_sets(db)
	read_sets(db, types = types, ignore_alias = ignore_alias)
	if clean_alias:
		clean_aliases(db,types)
	read_aliased_sets(db,ignore_alias)
	if clean:
		update_subsets_from_sets(db)
		update_maps_from_sets(db)

def clean_sets(db):
	""" create empty indices for all sets  """
	[db.__setitem__(set_, pd.Index([], name = set_)) for set_ in set(db.gettypes(['set']))-set(['alias_set','alias_map2'])];

def read_sets(db, types=None, ignore_alias=False):
	""" read and define set elements from all symbols of type 'types'. """
	if ignore_alias:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(NoneInit(types,['variable','parameter'])).values() for set_ in (set(symbol.domains)-db.alias_notin_db)];
	else:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(NoneInit(types,['variable','parameter'])).values() for set_ in set(symbol.domains)];

def clean_aliases(db,types):
	""" Remove aliases that are not used in variables/parameters """
	db.series['alias_'] = pd.MultiIndex.from_tuples(active_aliases(db,types), names = ['alias_set','alias_map2'])
	db.update_alias()

def active_aliases(db,types):
	""" Return list of tuples with alias_ that are used in the model variables / mappings"""
	return [(k,v) for k in db.get('alias_set') for v in [x for x in db.alias_dict[k] if len(db.vardom(k,types=types)[x])>0]]

def read_aliased_sets(db,ignore_alias):
	""" Read in all elements for aliased sets. If ignore alias"""
	for set_i in db.alias_dict:
		all_elements = sunion_empty([set(db.get(set_ij)) for set_ij in db.alias_dict0[set_i] if set_ij in db.gettypes(['set'])])
		if ignore_alias:
			[db.__setitem__(set_ij, pd.Index(all_elements,name=set_ij)) for set_ij in db.alias_dict0[set_i] if set_ij in db.gettypes(['set'])];
		else:
			[db.__setitem__(set_ij, pd.Index(all_elements,name=set_ij)) for set_ij in db.alias_dict0[set_i]];

def update_subsets_from_sets(db):
	[update_subset(db,ss) for ss in db.gettypes(['subset'])];

def update_subset(db,ss):
	if db.alias(db.get(ss).name) not in db.symbols:
		db.__setitem__(ss,pd.Index([],name=db.alias(db.get(ss).name)))
	else:
		db.__setitem__(ss,rctree_pd(s=db[ss],c=db[db.alias(db.get(ss).name)]))

def update_maps_from_sets(db):
	[update_map(db,m) for m in db.gettypes(['mapping'])];

def update_map(db,m):
	if sum([bool(set(db.symbols.keys()).intersection(db.alias_all(s))) for s in db[m].domains])<len(db[m].domains):
		db.__setitem__(m, pd.MultiIndex.from_tuples([], names = db[m].domains))
	else:
		db.__setitem__(m, rctree_pd(s=db[m], c = ('and', [db[s] for s in db[m].domains])))

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
			db['_'.join([var,name])] = Database.gpy(addGrid(v0,vT,db.get(loop),'_'.join([var,name]), gridtype=gridtype, phi=phi), **{'type':'parameter'})
	for var in set(db0.gettypes(['scalar_variable']).keys()).intersection(set(dbT.gettypes(['scalar_variable']).keys())):
		if (not checkDiff) or (abs(db0.get(var)-dbT.get(var))>error):
			db['_'.join([var,name,'ss'])] = db.get(loop)
			db['_'.join([var,name])] = Database.gpy(addGrid(db0.get(var),dbT.get(var),db.get(loop),'_'.join([var,name]),gridtype=gridtype,phi=phi),**{'type':'parameter'})
	for var in NoneInit(extractSol,{}):
		db['_'.join(['sol',var,name])] = Database.gpy(pd.Series(0, index = add1dIndex(rc_pdInd(db0[var],c=extractSol[var]),db.get(loop),sort_levels=db[loop].domains+db0[var].domains), name = '_'.join(['sol',var,name])),**{'type':'parameter'})
	update_sets(db,clean_alias=True)
	db.merge_internal()
	return db

# ----------------------- 5. Methods for aggregating database ------------------------- #
def aggDB(db, mapping, aggBy=None, replaceWith=None, checkUnique=True, AggLike = None):
	""" Aggregate symbols in db according to mapping. This does so inplace, i.e. the set aggBy is altered. 
		Note: The aggregation assumes that mapping is 'many-to-one'; if this is not the case, a warning is printed (if checkUnique) """
	aggBy,replaceWith = NoneInit(aggBy, mapping.names[0]), NoneInit(replaceWith,mapping.names[-1])
	defaultAggLike = {k: ('Sum',{}) for v,l in db.vardom(aggBy).items() for k in l}
	AggLike = defaultAggLike if AggLike is None else defaultAggLike | AggLike
	[db.__setitem__(k, aggDB_set(k, db, mapping, aggBy, replaceWith)) for k in db.vardom(aggBy,types=['set'])];
	[db.__setitem__(vi, aggDB_subset(vi, db, mapping.set_names(k,level=aggBy), k, replaceWith, checkUnique)) for k,v in db.vardom(aggBy, types=['subset']).items() for vi in v];
	[db.__setitem__(vi, aggDB_mapping(vi, db, mapping.set_names(k,level=aggBy), k, replaceWith, checkUnique)) for k,v in db.vardom(aggBy, types=['mapping']).items() for vi in v];
	[db.__setitem__(vi, eval(f"aggVar{AggLike[vi][0]}")(db.get(vi),mapping.set_names(k,level=aggBy),k,replaceWith,checkUnique,**AggLike[vi][1])) for k,v in db.vardom(aggBy).items() for vi in v];
	return db

def aggDB_set(k, db, mapping, aggBy, replaceWith):
	return mapping.get_level_values(replaceWith).unique().rename(k)

def aggDB_subset(k, db, mapping, aggBy, replaceWith,checkUnique):
	o,d1,d2 = overlaps(db[k],mapping)
	if checkUnique:
		_checkUnique(db[k].index,mapping,o,d1,d2,aggBy,replaceWith,k)
	return aggReplace(db.get(k),mapping,aggBy,replaceWith,o).unique().rename(aggBy)

def aggDB_mapping(k, db, mapping, aggBy, replaceWith, checkUnique):
	o,d1,d2 = overlaps(db[k],mapping)
	if checkUnique:
		_checkUnique(db[k].index,mapping,o,d1,d2,aggBy,replaceWith,k)
	return aggReplace(db.get(k),mapping,aggBy,replaceWith,o).unique().set_names(aggBy,level=replaceWith)

def aggVarSum(var, mapping, aggBy, replaceWith,checkUnique):
	o,d1,d2 = overlaps(var,mapping)
	if checkUnique:
		_checkUnique(var.index,mapping,o,d1,d2,aggBy,replaceWith,var.name)
	return aggReplace(var,mapping,aggBy,replaceWith,o).rename_axis(index={replaceWith: aggBy}).groupby(var.index.names).sum()

def aggVarMean(var, mapping, aggBy, replaceWith,checkUnique):
	o,d1,d2 = overlaps(var,mapping)
	if checkUnique:
		_checkUnique(var.index,mapping,o,d1,d2,aggBy,replaceWith,var.name)
	return aggReplace(var,mapping,aggBy,replaceWith,o).rename_axis(index={replaceWith: aggBy}).groupby(var.index.names).mean()

def aggVarWeightedSum(var,mapping,aggBy,replaceWith,checkUnique,weights=None):
	return aggVarSum((var*weights).dropna().droplevel(replaceWith),mapping,aggBy,replaceWith,checkUnique).rename(var.name)

def aggVarWeightedSum_gb(var,mapping,aggBy,replaceWith,checkUnique,weights=None,sumOver=None):
	return aggVarWeightedSum(var,weights,mapping,aggBy,replaceWith,checkUnique).groupby([x for x in var.index.names if x not in sumOver]).sum()

def aggVarLambda(var, mapping, aggBy, replaceWith,checkUnique, lambda_=None):
	o,d1,d2 = overlaps(var,mapping)
	if checkUnique:
		_checkUnique(var.index,mapping,o,d1,d2,aggBy,replaceWith,var.name)
	return aggReplace(var,mapping,aggBy,replaceWith,o).rename_axis(index={replaceWith: aggBy}).groupby(var.index).sum(lambda_)

def _checkUnique(index1,index2,o,d1,d2,aggBy,replaceWith,name):
	mi1,mi2 = index1.to_frame().droplevel(d1), index2.reorder_levels(o+d2).to_frame().droplevel(d2)[d2]
	if max(rc_pd(mi2,mi1).groupby(mi2.index.names).nunique()[replaceWith])>1:
		print(f"""**** Warning: The symbol {name} used 'many-to-many'-mapping. Aggregation usually assumes 'many-to-one'.""")

def aggReplace(s,mapping,aggBy,replaceWith,overlap):
	return applyMult(s,mapping.droplevel([v for v in mapping.names if v not in [replaceWith]+overlap])).droplevel(aggBy)

def overlaps(s1,s2):
	doms1,doms2 = Database.getindex(s1).names, Database.getindex(s2).names
	return [x for x in doms1 if x in doms2], [x for x in doms1 if x not in doms2], [x for x in doms2 if x not in doms1]