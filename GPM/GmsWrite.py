from _GmsWrite import *

def standardArgs(settings, db, gdx, blocks = None, functions = None, run = True, prefix = '', prefix_run = '', options = None):
	""" Returns the 'standard' components. Use GmsPy.Groups to handle grouping of variables. """
	args = {'root': write_root(**NoneInit(options,{})), prefix+'functions': args_functions(f=functions), prefix+'declare': write_declare(db, gdx, from_db=settings.from_db), 
			prefix+'blocks': blocks}
	args = {k:v for k,v in args.items() if v}
	return args | standardRun(settings,db,prefix=prefix_run) if run else args

def standardArgs_gamY(settings,db,gdx, blocks = None, functions = None, declare_groups = '', run = True, prefix = '', prefix_run='', options=None):
	args = {'root': write_root(**NoneInit(options,{})), prefix+'functions': args_functions(f=functions), prefix+'declare': write_declare(db, gdx, from_db='sets'), 
			prefix+'declare_groups': args_declare_groups(settings.Precompiler,declare_groups), prefix+'load_groups': write_loadgroups_gamY(settings.Precompiler.groups,g_endo=settings['g_endo'],gdx=gdx),
			prefix+'blocks': blocks}
	args = {k:v for k,v in args.items() if v}
	return args | standardRun_gamY(settings,prefix=prefix_run) if run else args

def standardRun(settings,db,prefix=''):
	return {prefix+'fix': settings.Compile.fixGroupsText(db,settings['g_exo']), prefix+'unfix': settings.Compile.unfixGroupsText(db,settings['g_endo']), 
			prefix+'model': args_model(settings['name'], settings['blocks']), prefix+'solve': write_solve(solve=settings['solve'],name=settings['name'])}

def standardRun_gamY(settings,prefix=''):
	return {prefix+'fix': args_fix_gamY(settings['g_exo']), prefix+'unfix': args_unfix_gamY(settings['g_endo']), 
			prefix+'model': args_model(settings['name'], settings['blocks']), prefix+'solve': write_solve(solve=settings['solve'],name=settings['name'])}

