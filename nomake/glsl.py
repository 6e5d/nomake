from subprocess import run
def build_glsl(proj):
	for file in (proj / "src").iterdir():
		stem = file.stem
		stage = stem.split("_")[-1]
		target = proj / "build" / (stem + ".spv")
		run(["glslc", f"-fshader-stage={stage}", "-o", target, file])
