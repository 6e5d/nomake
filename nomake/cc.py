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
		"-Weverything",

		"-Wno-unused-parameter", # too much for template functions
		"-Wno-switch-enum", # it disallows default
		# common lib cannot pass: project/dependency
		"-Wno-cast-function-type-strict", # vkhelper/vulkan
		"-Wno-cast-qual", # wlbasic/wayland-scanner
		"-Wno-missing-variable-declarations", # wlbasic/wayland-scanner
		# too common for c
		"-Wno-padded",
		"-Wno-unsafe-buffer-usage",
		"-Wno-gnu-pointer-arith",
		# c99
		"-Wno-declaration-after-statement",

		"-Wl,-unresolved-symbols=ignore-in-shared-libs",
	]
	return cmd
