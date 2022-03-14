import pandas as pd, Database
from DBWheels_rc import rctree_pd

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
def update_sets(db, types = ('variable','parameter'), clean=True, ignore_alias=False, clean_alias = False):
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

def read_sets(db, types=['variable','parameter'], ignore_alias=False):
	""" read and define set elements from all symbols of type 'types'. """
	if ignore_alias:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(types).values() for set_ in (set(symbol.domains)-db.alias_notin_db)];
	else:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(types).values() for set_ in set(symbol.domains)];

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