def gcc():
	cmd = ["gcc", "--std=c11",
		"-Wall",
		"-Wextra",
		"--allow-shlib-undefined",
	]
	return cmd

def clang():
	cmd = [
		"clang",
		"--std=c11",
		"-Wmost",
		"-Wl,-unresolved-symbols=ignore-in-shared-libs",
	]
	return cmd
