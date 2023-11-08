def gcc():
	cmd = ["gcc", "--std=gnu17",
		"-Wall",
		"-Wextra",
		"-Wconversion",
		"--allow-shlib-undefined",
	]
	return cmd

def clang():
	cmd = [
		"clang",
		"--std=gnu17",
		"-Wmost",
		"-Wconversion",
		"-Wl,-unresolved-symbols=ignore-in-shared-libs",
	]
	return cmd
