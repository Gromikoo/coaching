# Builds index.html from template.html + messages.json. Run: python3 build.py
import json, pathlib
here = pathlib.Path(__file__).parent
CAL = "https://calendly.com/gromiko-mikooai/busy-woman-s-weight-loss-strategy-call"
data = json.loads((here/"messages.json").read_text())
data.pop("_note", None)
html = (here/"template.html").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__CAL__", CAL)
(here/"index.html").write_text(html)
print("built index.html", len(html), "bytes")
