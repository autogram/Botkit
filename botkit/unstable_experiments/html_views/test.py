from pathlib import Path

from botkit.unstable.html import sample_lib

path = str(Path(__file__).parent / "experiment.xml")

res = sample_lib.parse(path, print_warnings=True)
print(res)

