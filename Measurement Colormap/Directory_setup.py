import os
#path = os.path.join("C:\\","tmp")

def check_for_dir(path, silent = True):
	if os.path.exists(path):
		if not silent:
			print(path + ' : exists')
		if os.path.isdir(path):
			if not silent:
				print(path + ' : is a directory') 
			return True
	return False

def create_new_dir(location, dir_name, silent = True):
	path = os.path.join(location,dir_name)
	if not check_for_dir(path):
		os.mkdir(path)
		if not silent:
			print('Directory', path,'created') 
	else:
		if not silent:
			print('Directory', path,'already exists') 
	return path

if __name__ == '__main__':
	cwd = os.getcwd()
	print(cwd)
	create_new_dir(cwd,"TEST2")
