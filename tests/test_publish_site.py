"""Unit tests for the static download site: staging, pruning, page, embed."""
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from publish_site import (build_embed, file_changes,  # noqa: E402
                          load_versions, prune, render_index,
                          resolve_version, sig_snapshot, stage_version,
                          write_index)


class Site(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = os.path.join(self.tmp.name, "site")
        os.makedirs(self.dest)
        self.so = os.path.join(self.tmp.name, "libserver.so")
        with open(self.so, "wb") as fh:
            fh.write(b"\x7fELF fake")

    def tearDown(self):
        self.tmp.cleanup()

    def publish(self, version):
        meta = stage_version(self.dest, version, {"ClientVersion": "2000939",
                                                  "PatchVersion": version},
                             [("linux", self.so)])
        time.sleep(1.01)  # published has second resolution; keep order stable
        return meta

    def test_stage_writes_files_sums_and_meta(self):
        meta = self.publish("1.41.9.4")
        vdir = os.path.join(self.dest, "1.41.9.4")
        self.assertEqual(sorted(os.listdir(vdir)),
                         ["SHA256SUMS", "cs2-1.41.9.4-linux.zip",
                          "libserver.so", "meta.json"])
        import zipfile
        with zipfile.ZipFile(os.path.join(vdir, "cs2-1.41.9.4-linux.zip")) as zf:
            self.assertEqual(zf.namelist(), ["libserver.so"])
        self.assertEqual(meta["files"][0]["platform"], "linux")
        with open(os.path.join(vdir, "SHA256SUMS")) as fh:
            self.assertIn(meta["files"][0]["sha256"] + "  libserver.so", fh.read())
        self.assertFalse([n for n in os.listdir(self.dest) if n.startswith(".")])

    def test_republish_replaces_in_place(self):
        self.publish("1.41.9.4")
        with open(self.so, "wb") as fh:
            fh.write(b"new bytes")
        meta = self.publish("1.41.9.4")
        self.assertEqual(len(load_versions(self.dest)), 1)
        self.assertEqual(meta["files"][0]["size"], len(b"new bytes"))

    def test_prune_keeps_newest(self):
        for v in ("1.0", "1.1", "1.2"):
            self.publish(v)
        self.assertEqual(prune(self.dest, 2, "1.2"), ["1.0"])
        self.assertEqual([m["version"] for m in load_versions(self.dest)],
                         ["1.2", "1.1"])

    def test_index_and_versions_json(self):
        self.publish("1.0")
        self.publish("1.1")
        write_index(self.dest, 5)
        with open(os.path.join(self.dest, "versions.json")) as fh:
            self.assertEqual(json.load(fh)["latest"], "1.1")
        with open(os.path.join(self.dest, "index.html")) as fh:
            page = fh.read()
        self.assertIn('href="1.1/libserver.so"', page)
        self.assertEqual(page.count('class="hero"'), 1)
        self.assertEqual(page.count("<details"), 1)
        self.assertIn('href="1.1/cs2-1.1-linux.zip"', page)
        self.assertIn("gameVersion", render_index(load_versions(self.dest), 5))
        self.assertIn("unchanged since 1.0", page)

    def test_sig_snapshot_pill_and_projects(self):
        reports = os.path.join(self.tmp.name, "reports")
        os.makedirs(os.path.join(reports, "Foo"))
        with open(os.path.join(reports, "badge.json"), "w") as fh:
            json.dump({"message": "3 broken", "color": "red"}, fh)
        with open(os.path.join(reports, "Foo", "status.json"), "w") as fh:
            json.dump({"tally": {"ok": 7, "broken": 3}}, fh)
        sigs = sig_snapshot(os.path.join(reports, "badge.json"))
        self.assertFalse(sigs["ok"])
        self.assertEqual(sigs["projects"], [{"name": "Foo", "ok": 7, "total": 10}])
        stage_version(self.dest, "1.0", {}, [("linux", self.so)], sigs)
        write_index(self.dest, 5)
        with open(os.path.join(self.dest, "index.html")) as fh:
            page = fh.read()
        self.assertIn('class="pill bad"', page)
        self.assertIn("signatures: 3 broken", page)
        self.assertIn("Foo <b>7/10</b>", page)

    def test_file_changes(self):
        self.publish("1.0")
        self.publish("1.1")                      # same bytes
        with open(self.so, "wb") as fh:
            fh.write(b"\x7fELF fake but longer")
        self.publish("1.2")                      # changed
        self.publish("1.3")                      # same as 1.2
        ch = file_changes(load_versions(self.dest))
        self.assertNotIn("1.0", ch)
        self.assertEqual(ch["1.1"]["libserver.so"], ("same", "1.0"))
        self.assertEqual(ch["1.2"]["libserver.so"], ("changed", 11))
        self.assertEqual(ch["1.3"]["libserver.so"], ("same", "1.2"))

    def test_latest_links(self):
        self.publish("1.0")
        self.publish("1.1")
        write_index(self.dest, 5)
        latest = os.path.join(self.dest, "latest")
        self.assertEqual(os.readlink(os.path.join(latest, "libserver.so")),
                         os.path.join("..", "1.1", "libserver.so"))
        with open(os.path.join(latest, "cs2-linux.zip"), "rb") as fh:
            self.assertEqual(fh.read(2), b"PK")
        with open(os.path.join(latest, "SHA256SUMS")) as fh:
            self.assertIn("  cs2-linux.zip", fh.read())
        # latest/ never counts as a version and never gets pruned
        self.assertEqual([m["version"] for m in load_versions(self.dest)], ["1.1", "1.0"])

    def test_og_tags(self):
        self.publish("1.41.9.4")
        page = render_index(load_versions(self.dest), 5, "https://bins.example")
        self.assertIn('property="og:title" content="CS2 1.41.9.4 binaries"', page)
        self.assertIn("gameVersion 14194", page)
        self.assertIn('content="https://bins.example/"', page)
        self.assertIn("Valve Corporation", page)

    def test_rss_feed(self):
        import xml.etree.ElementTree as ET
        self.publish("1.0")
        self.publish("1.1")
        write_index(self.dest, 5, "https://bins.example")
        root = ET.parse(os.path.join(self.dest, "releases.rss")).getroot()
        items = root.findall("channel/item")
        self.assertEqual([i.findtext("guid") for i in items],
                         ["bins-1.1", "bins-1.0"])
        self.assertEqual(items[0].findtext("link"), "https://bins.example/#v1.1")
        self.assertIn("https://bins.example/1.1/libserver.so",
                      items[0].findtext("description"))

    def test_stray_dirs_ignored(self):
        os.makedirs(os.path.join(self.dest, "junk"))
        self.assertEqual(load_versions(self.dest), [])
        self.assertIn("Nothing published", render_index([], 5))

    def test_version_resolution(self):
        self.assertEqual(resolve_version("x", {"PatchVersion": "1"}, None), "x")
        self.assertEqual(resolve_version(None, {"PatchVersion": "1.41.9.4",
                                                "ClientVersion": "2"}, None),
                         "1.41.9.4")
        self.assertEqual(resolve_version(None, {}, "2026-11-02"), "2026-11-02")

    def test_embed_links(self):
        meta = self.publish("1.41.9.4")
        e = build_embed(meta, "https://bins.example/")
        self.assertIn("https://bins.example/1.41.9.4/libserver.so",
                      e["description"])
        self.assertEqual(e["url"], "https://bins.example/#v1.41.9.4")


if __name__ == "__main__":
    unittest.main()
