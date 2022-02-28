import pandas as pd, Database

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
		clean_sets(db,types=types, ignore_alias=ignore_alias)
	read_sets(db, types = types, ignore_alias = ignore_alias)
	if clean_alias:
		clean_aliases(db,types)
	read_aliased_sets(db,ignore_alias)


def clean_sets(db, types=['variable','parameter'], ignore_alias=False):
	""" create empty indices for all sets  """
	[db.__setitem__(set_, pd.Index([], name = set_)) for set_ in set(db.gettypes(['set'])-set(['alias_set','alias_map2']))];

def read_sets(db, types=['variable','parameter'], ignore_alias=False):
	""" read and define set elements from all symbols of type 'types'. """
	if ignore_alias:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(types).values() for set_ in (set(symbol.domains)-db.alias_notin_db)];
	else:
		[add_or_merge_vals(db, symbol.index.get_level_values(set_).unique()) for symbol in db.gettypes(types).values() for set_ in set(symbol.domains)];

def clean_aliases(db,types):
	""" Remove aliases that are not used in variables/parameters """
	db.update_alias(pd.MultiIndex.from_tuples(active_aliases(db,types), names = ['alias_set','alias_map2']))

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


# MISSING THIS PART: BUT NEED THE PANDAS CONDITION TREES TO CONTINUE.
		# if clean_up:
		# 	self.update_subsets_from_sets()
		# 	self.update_maps_from_sets()
