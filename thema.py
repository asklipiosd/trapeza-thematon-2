#!/usr/bin/env python3

# -- [imports] ----------------------------------------------------------------
from urllib.request import urlretrieve, urlcleanup
import subprocess
import argparse
from pypdf import PdfWriter
import tempfile
import shutil

# -- [check if shutils is available] ------------------------------------------
if shutil.which("tdf") is None:
	print("well tdf was not found")
	print("it's like 50 lines go edit the last one")
	exit(1)

# -- [cli parsing] ------------------------------------------------------------
parser = argparse.ArgumentParser(
	prog='thema fucking downloader',
	description='it downloads themata',
	epilog='epilogue'
)
parser.add_argument('-s', '--solutions',
	action='store_true'
)
parser.add_argument('-d', '--download',
	action='store_true'
)
parser.add_argument('files', nargs='*')
args = parser.parse_args()

# -- [state] ------------------------------------------------------------------
paths = []
solutions = []

# -- [progress] ---------------------------------------------------------------
def reporthook(block_num, block_size, total_size):
	if total_size <= 0:
		return
	done = min(block_num * block_size, total_size)
	width = 30
	filled = width * done // total_size
	print(f"\r{'█' * filled}{'░' * (width - filled)} {100 * done // total_size}%",
		end="", flush=True)
	if done >= total_size:
		print()
# -- [downloads] --------------------------------------------------------------
for id in args.files:
	try:
		path , _ = urlretrieve(f"https://trapeza.z6.web.core.windows.net/{id}.pdf",
			reporthook = reporthook)
	except:
		print(f"well you got a problem with {id}")
		exit(1)
	paths.append(path)
	if args.solutions:
		try:
			path , _ = urlretrieve(f"https://trapeza.z6.web.core.windows.net/{id}_SOLUTION.pdf",
				reporthook = reporthook)
		except:
			print(f"well you got a problem with {id} solution")
			exit(1)
		solutions.append(path)

# -- [merge] ------------------------------------------------------------------
merger = PdfWriter()
if args.solutions:
	for p, s in zip(paths, solutions):
    		merger.append(p)
    		merger.append(s)
else:
	for p in paths:
    		merger.append(p)

# -- [download or view] -------------------------------------------------------
if args.download:
	merger.write("_".join(args.files) + ".pdf")
	merger.close()
	urlcleanup()
else:
	with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
		merger.write(f)
		merger.close()
		f.flush()
		try:
			subprocess.run(["tdf","-m","1", f.name])
		finally:
			urlcleanup()
