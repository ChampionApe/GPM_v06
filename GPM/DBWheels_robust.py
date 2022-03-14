from Database import *

# Robust methods
# 1: Merge database methods
def robust_merge_dbs(db1,db2,priority='second'):
	""" merge db2 into db1; priority = 'first' uses db1 if there is overlap. 'second' uses db2. This is much slower if priority = 'first'. """
	if isinstance(db1,(GpyDB,SeriesDB,dict)):
		if isinstance(db2,(GpyDB,SeriesDB,dict)):
			merge_dbs_GpyDB(db1,db2,priority=priority)
		elif isinstance(db2,gams.GamsDatabase):
			merge_dbs_GpyDB_gams(db1,db2,get_g2np(db2),priority=priority)
	elif isinstance(db1,gams.GamsDatabase):
		if isinstance(db2,(GpyDB,SeriesDB,dict)):
			merge_dbs_gams_GpyDB(db1,db2,get_g2np(db1),priority=priority)
		elif isinstance(db2,gams.GamsDatabase):
			merge_dbs_gams(db1,db2,get_g2np(db1),priority=priority)

def get_g2np(db):
	if isinstance(db,gams.GamsDatabase):
		return gams2numpy.Gams2Numpy(db.workspace.system_directory)
	elif isinstance(db,GpyDB):
		return db.g2np
	else:
		raise TypeError(f"db of type {type(db)} cannot access g2np.")

def iters_db_py(db):
	return db if isinstance(db,(GpyDB,SeriesDB)) else db.values()

def merge_dbs_GpyDB(db1,db2,priority='second'):
	"""" merge db2 into db1. """
	if priority == 'second':
		[GpyDBs_AOM_Second(db1,symbol) for symbol in iters_db_py(db2)];
	elif priority== 'first':
		[GpyDBs_AOM_First(db1,symbol) for symbol in iters_db_py(db2)];

def merge_dbs_GpyDB_gams(db_py,db_gms,g2np,priority='second'):
	""" Merge db_gms into db_py. """
	if priority == 'second':
		[GpyDBs_AOM_Second(db_py,symbol) for symbol in dict_from_GamsDatabase(db_gms,g2np).values()];
	elif priority == 'first':
		[GpyDBs_AOM_First(db_py,symbol) for symbol in dict_from_GamsDatabase(db_gms,g2np).values()];

def merge_dbs_gams_GpyDB(db_gms,db_py,g2np,priority='second'):
	""" merge db_py into db_gms."""
	if priority == 'second':
		[gpy2db_gams_AOM(s,db_gms,g2np,merge=True) for s in iters_db_py(db_py)];
	elif priority == 'first':
		if isinstance(db_py,GpyDB):
			d = db_py.series.database.copy()
		elif isinstance(db_py,SeriesDB):
			d = db_py.database.copy()
		elif type(db_py) is dict:
			d = db_py.copy()
		merge_dbs_GpyDB_gams(d, db_gms, g2np, priority='second') # merge db_gms into dictionary of gpy symbols.
		merge_dbs_gams_GpyDB(db_gms, d, g2np,priority='second') # merge gpy symbols into gams.

def merge_dbs_gams(db1,db2,g2np,priority='second'):
	""" Merge db2 into db1. """
	if priority=='second':
		[gpy2db_gams_AOM(s,db1,g2np,merge=True) for s in dict_from_GamsDatabase(db2,g2np).values()];
	elif priority=='first':
		d = dict_from_GamsDatabase(db2,g2np) # copy of db2.
		merge_dbs_GpyDB_gams(d,db1,g2np) # merge into d with priority to db1.
		merge_dbs_gams_GpyDB(db1,d,g2np,priority='second') 


# 2: Robust methods for adding/merging symbols
def robust_gpy(symbol,db=None,g2np=None,**kwargs):
	if isinstance(symbol,admissable_gpy_types):
		return gpy(symbol,**kwargs)
	elif isinstance(symbol,admissable_gamsTypes):
		return gpy(gpydict_from_GamsSymbol(db, g2np, symbol))
	else:
		try:
			return gpy(gpydict_from_GmdSymbol(db,g2np,symbol))
		except:
			raise TypeError(f"Tried to initiate gpy symbol from gams.Database._gmd. Check consistency of types: {type(symbol),type(db)}.")

def robust_add(db,symbol,db_from=None,g2np=None,merge=False,**kwargs):
	""" Symbol ∈ {gams.database._GamsSymbol, pandas-like symbol, gpy}"""
	s = robust_gpy(symbol,db=db_from, g2np = g2np, **kwargs)
	if isinstance(db,(dict, GpyDB, SeriesDB)):
		db[s.name] = s
	elif isinstance(db, gams.GamsDatabase):
		gpy2db_gams(s,db[s.name],db,g2np,merge=merge)
	else:
		raise TypeError("Check type(db).")

def robust_add_or_merge(db,symbol,db_from=None,g2np=None,merge=True,**kwargs):
	""" If 'symbol' exists in db merge with priority to new values in 'symbol'. """
	s = robust_gpy(symbol,db=db_from, g2np = g2np, **kwargs)
	if isinstance(db,(dict, GpyDB,SeriesDB)):
		if s.name in symbols_db(db):
			db[s.name].vals = merge_gpy_vals(s.vals, db[s.name].vals)
		else:
			db[s.name] = s
	elif isinstance(db, gams.GamsDatabase):
		gpy2db_gams_AOM(s,db,g2np,merge=merge)
	else:
		raise TypeError("Check type(db).")
