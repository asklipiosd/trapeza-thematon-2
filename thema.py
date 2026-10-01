#!/usr/bin/env python3

# -- [suppress warnings] ------------------------------------------------------
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# -- [imports] ----------------------------------------------------------------
from urllib.request import urlretrieve, urlcleanup
from pypdf import PdfWriter
import pypdf
import subprocess
import argparse
import tempfile
import shutil

# -- [cli parsing] ------------------------------------------------------------
parser = argparse.ArgumentParser(
	prog='thema downloader',
)
parser.add_argument('-s', '--solutions',
	action='store_true',
	help = "query for solutions too"
)
parser.add_argument('-d', '--download',
	action='store_true',
	help = "download instead of opening tdf"
)
parser.add_argument('-o', '--outputFile',
	help = "specify an output name"
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
	if args.outputFile is not None:
		name = args.outputFile
	else:
		name = "_".join(args.files) + ".pdf"
	merger.write(name)
	merger.close()
	urlcleanup()
else:
	with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
		# -- [check if tdf is available] ----------------------------------------------
		if shutil.which("tdf") is None:
			print("well tdf was not found")
			print("it's like 50 lines go edit the last one")
			exit(1)
		else:
			merger.write(f)
			merger.close()
			f.flush()
			try:
				subprocess.run(["tdf","-m","1", f.name])
			finally:
				urlcleanup()
