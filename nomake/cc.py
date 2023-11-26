def common():
	return ["-O3",
		"--std=c17", "-D", "_POSIX_C_SOURCE=200809L",
		# warning should block, or mtime gets skipped in second build
		"-Werror",
		"-Wl,--no-undefined",
		"-Wl,--no-allow-shlib-undefined",
	]

def gcc():
	cmd = ["gcc"] + common() + [
		"-Wall",
		"-Wextra",
		"-Wconversion",
		"-Wpedantic",
		"-Wno-unused-parameter",
	]
	return cmd

def clang():
	cmd = ["clang"] + common() + [
		"-Weverything",
		"-Wno-unused-parameter", # too much for template functions
		"-Wno-switch-enum", # it disallows default
		# common lib cannot pass: project/dependency
		"-Wno-cast-function-type-strict", # vkhelper/vulkan
		"-Wno-cast-qual", # wlbasic/xdg
		"-Wno-bad-function-cast", # not good for floor/round/ceil
		# too common for c
		"-Wno-padded",
		"-Wno-unsafe-buffer-usage",
		# c99
		"-Wno-declaration-after-statement",
	]
	return cmd
