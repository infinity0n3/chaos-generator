import os

def create_dir(f):
	if not os.path.exists(f):
		os.makedirs(f)
		print( 'mkdir {:s}'.format(f) )

def create_link(src, dst, overwrite = False):
	if os.path.lexists(dst):
		if overwrite:
			os.remove(dst)
			os.symlink(src, dst)
			print( 'softlink {:s} -> {:s}'.format(dst,src) )
	else:
		os.symlink(src, dst)
		print( 'softlink {:s} -> {:s}'.format(dst,src) )

def build_path(*args):
	return os.path.join(*args)
