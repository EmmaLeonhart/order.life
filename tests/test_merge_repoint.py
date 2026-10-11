"""merge_cluster.py must repoint third-party references to a merged-away qid (queue item 1d).

Runs the real merge_cluster.main() --write against a throwaway git repository in a temp dir:
  Q1 survivor, Q2 its duplicate (the loser)
  Q3 a child whose father is Q2 only           -> must be repointed to Q1
  Q4 a shadow of Q3 (redirects.tsv Q4 -> Q3)   -> must end up identical to Q3
  Q5 a child naming both Q1 and Q2 as father   -> the Q2 claim must be dropped, not doubled
stdlib only:  python -m unittest tests/test_merge_repoint.py   (from the order.life root)
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "wiki-scripts"
sys.path.insert(0, str(SCRIPTS))
import merge_cluster as mc  # noqa: E402
import repoint_vacated_qids as rv  # noqa: E402


class Captured(io.StringIO):
    def reconfigure(self, **_):  # main() reconfigures stdout to utf-8
        pass


def item(q, label, **claims):
    return {"type": "item", "id": q, "labels": {"en": {"language": "en", "value": label}},
            "claims": {p: [{"mainsnak": {"snaktype": "value", "property": p, "datavalue": {
                "value": {"entity-type": "item", "id": v, "numeric-id": int(v[1:])},
                "type": "wikibase-entityid"}}, "type": "statement", "rank": "normal"} for v in vs]
                for p, vs in claims.items()}}


def ids(d, p):
    return [c["mainsnak"]["datavalue"]["value"]["id"] for c in d.get("claims", {}).get(p, [])]


class MergeRepointsThirdParties(unittest.TestCase):
    def test_merge_repoints_and_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items, an = root / "wikibase" / "items", root / "wikibase" / "analysis"
            items.mkdir(parents=True); an.mkdir(parents=True)
            recs = {
                "Q1": item("Q1", "Marcus", P20=["Q5"]),
                "Q2": item("Q2", "Marcus", P20=["Q3", "Q5"]),
                "Q3": item("Q3", "Child A", P47=["Q2"]),
                "Q4": item("Q3", "Child A", P47=["Q2"]),  # shadow file of Q3
                "Q5": item("Q5", "Child B", P47=["Q1", "Q2"]),
            }
            for stem, d in recs.items():
                (items / f"{stem}.json").write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
            (an / "redirects.tsv").write_text("from_qid\tto_qid\nQ4\tQ3\n", encoding="utf-8")
            git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)
            git("init", "-q"); git("add", "-A")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "fixture")

            for m in (mc, rv):
                m.ROOT, m.ITEMS, m.REDIRECTS = root, items, an / "redirects.tsv"
            mc.CLUSTERS = {"fixture": [("Q1", "Q2", "fixture duplicate")]}
            argv, sys.argv = sys.argv, ["merge_cluster.py", "fixture", "--write"]
            out = Captured()
            try:
                with contextlib.redirect_stdout(out):
                    rc = mc.main()
            finally:
                sys.argv = argv
            load = lambda s: json.loads((items / f"{s}.json").read_text(encoding="utf-8"))

            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(ids(load("Q3"), "P47"), ["Q1"])
            self.assertEqual(load("Q4"), load("Q3"), "shadow not synced")
            self.assertEqual(ids(load("Q5"), "P47"), ["Q1"], "duplicate father not dropped")
            self.assertEqual(load("Q2")["id"], "Q1", "loser file not rewritten as the survivor")
            self.assertIn("no record names a vacated qid", out.getvalue())


if __name__ == "__main__":
    unittest.main()
