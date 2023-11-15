from subprocess import run

checks = [
	# I don't want to rely on compilers optimizations to eliminate init
	"-cppcoreguidelines-init-variables",
	"-cppcoreguidelines-avoid-magic-numbers",
	# NOTE: needs more discussion
	"-cert-err34-c",
	"-hicpp-uppercase-literal-suffix",
	# i don't use this style
	"-llvm-header-guard",
	"-google-readability-todo",
	"-clang-analyzer-security.insecureAPI.DeprecatedOrUnsafeBufferHandling",
	# clang-tidy failed to detect NULL check after realloc
	"-bugprone-suspicious-realloc-usage",
	# we don't use llvmlibc
	"-llvmlibc-restrict-system-libc-headers",
	# we don't do fpga
	"-altera-*",
	# more work handling exceptions than debugging bugs it may cause
	"-bugprone-easily-swappable-parameters",
	# unavoidable in callback
	"-misc-unused-parameters",
	# nonsense
	"-readability-uppercase-literal-suffix",
	"-readability-identifier-length",
	"-readability-isolate-declaration",
	"-readability-magic-numbers",
]
checks = ",".join(checks)
def nomake_check(path):
	run([f"clang-tidy -checks=*,{checks} "
		f"{path}/src/*.c {path}/include/*.h"],
		shell = True,
		check = True,
	)
