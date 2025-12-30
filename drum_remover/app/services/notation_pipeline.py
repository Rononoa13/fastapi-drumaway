from services.notation_builder import NotationBuilder
import json
from pathlib import Path

def build_notation(structured_hits, drum_path: Path):
    builder = NotationBuilder()
    measures = builder.build(structured_hits)

    out_json = drum_path.with_suffix(".notation.json")
    with open(out_json, "w") as f:
        json.dump(measures, f)
    return out_json