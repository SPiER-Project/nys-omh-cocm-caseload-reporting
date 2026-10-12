"""Build calculator/schema.py, the calculator's copy of the data contract's columns.

    python3 scripts/build_schema.py           write calculator/schema.py
    python3 scripts/build_schema.py --check   exit non-zero if it's out of date

The calculator checks its input against the contract (calculator/checks.py), and it runs
in the browser, where it can't read docs/reference/data-contract.md. So the columns are
copied into Python from the contract page, which stays the source of truth.
"""

import os
import pprint
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contract  # noqa: E402

OUT = os.path.join(contract.ROOT, "calculator", "schema.py")


def build():
    instruments = contract.instrument_values()
    schema = {}
    for name, _, columns in contract.tables():
        cols = []
        for c in columns:
            allowed = c["allowed"]
            if c["name"] == "primary_scale":  # "one of the T5 instruments other than phq2"
                allowed = [i for i in instruments if i != "phq2"]
            cols.append((c["name"], c["type"], c["required"], tuple(allowed) if allowed else None))
        schema[name] = cols
    body = pprint.pformat(schema, width=100, sort_dicts=False)
    return ('"""The data contract\'s columns: (name, type, required, allowed values).\n\n'
            "Generated from docs/reference/data-contract.md by scripts/build_schema.py.\n"
            'Don\'t edit it; change the contract and rebuild.\n"""\n\n'
            f"SCHEMA = {body}\n")


def main(argv):
    text = build()
    if "--check" in argv:
        current = open(OUT).read() if os.path.exists(OUT) else ""
        if current != text:
            print("calculator/schema.py is out of date; run python3 scripts/build_schema.py")
            return 1
        print("calculator/schema.py is up to date")
        return 0
    with open(OUT, "w") as f:
        f.write(text)
    print("wrote calculator/schema.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
