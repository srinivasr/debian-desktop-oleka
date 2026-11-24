import os, tempfile, unittest, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from olekalauncher.apps import App, parse_desktop_file, load_apps, command_for, split_command
from olekalauncher.search import score, rank


def write(dirname, name, text):
    path = os.path.join(dirname, name)
    with open(path, "w") as f:
        f.write(text)
    return path


class AppsTest(unittest.TestCase):
    def test_parse_and_hidden(self):
        with tempfile.TemporaryDirectory() as d:
            ok = write(d, "a.desktop", "[Desktop Entry]\nType=Application\nName=Foo\nExec=foo %U\nIcon=foo\n")
            hid = write(d, "b.desktop", "[Desktop Entry]\nName=Bar\nExec=bar\nNoDisplay=true\n")
            act = write(d, "c.desktop", "[Desktop Entry]\nName=Baz\nExec=baz\n[Desktop Action x]\nName=Other\nExec=other\n")
            self.assertEqual(parse_desktop_file(ok).name, "Foo")
            self.assertIsNone(parse_desktop_file(hid))
            self.assertEqual(parse_desktop_file(act).exec, "baz")

    def test_user_dir_overrides(self):
        with tempfile.TemporaryDirectory() as u, tempfile.TemporaryDirectory() as s:
            write(u, "x.desktop", "[Desktop Entry]\nName=Mine\nExec=m\n")
            write(s, "x.desktop", "[Desktop Entry]\nName=System\nExec=s\n")
            self.assertEqual([a.name for a in load_apps([u, s])], ["Mine"])

    def test_command(self):
        app = App("n", 'sh -c "echo hi" %U %%', "", "", "")
        self.assertEqual(command_for(app), ["sh", "-c", "echo hi", "%"])
        self.assertEqual(split_command("a  b"), ["a", "b"])


class SearchTest(unittest.TestCase):
    def test_order(self):
        self.assertGreater(score("fire", "Firefox"), score("fox", "Firefox"))
        self.assertGreater(score("fox", "Firefox"), score("ffx", "Firefox"))
        self.assertIsNone(score("zzz", "Firefox"))

    def test_rank(self):
        apps = [App(n, "x", "", c, "") for n, c in
                [("Files", ""), ("Files and Folders", ""), ("Terminal", "Run commands"), ("Firefox", "")]]
        self.assertEqual([a.name for a in rank("files", apps)], ["Files", "Files and Folders"])
        self.assertEqual(rank("ffx", apps)[0].name, "Firefox")
        self.assertEqual(rank("commands", apps)[0].name, "Terminal")
        self.assertEqual(len(rank("", apps, limit=2)), 2)


class RecentsTest(unittest.TestCase):
    def test_record_and_boost(self):
        from olekalauncher import recents
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "r.json")
            a = App("Alpha Edit", "x", "", "", "/u/alpha.desktop")
            b = App("Alpha Draw", "x", "", "", "/u/beta.desktop")
            recents.record(b, path); recents.record(b, path)
            counts = recents.load(path)
            self.assertEqual(counts, {"beta.desktop": 2})
            self.assertEqual(rank("alpha", [a, b], counts=counts)[0].name, "Alpha Draw")
            self.assertEqual(rank("", [a, b], counts=counts)[0].name, "Alpha Draw")
            self.assertEqual(recents.load(os.path.join(d, "missing")), {})


if __name__ == "__main__":
    unittest.main()
