def gcc():
	cmd = ["gcc", "--std=c11",
		"-Wall",
		"-Wextra",
		"-Wconversion",
		"--allow-shlib-undefined",
	]
	return cmd

def clang():
	cmd = [
		"clang",
		"--std=c11",
		"-Wmost",
		"-Wconversion",
		"-Wl,-unresolved-symbols=ignore-in-shared-libs",
	]
	return cmd
