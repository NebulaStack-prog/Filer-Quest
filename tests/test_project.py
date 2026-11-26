import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("filer", Path(__file__).resolve().parents[1] / "FilerQuest-New.py")
game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)

class VirtualFSTests(unittest.TestCase):
    def test_quest_hints(self):
        self.assertEqual(len(game.QUESTS), 25)
        for q in game.QUESTS:
            with self.subTest(quest=q["title"]):
                fs = game.VirtualFS(q["extras"], q["cwd"])
                ok, message, event = fs.run(q["hint"])
                self.assertTrue(ok, message)
                self.assertEqual(event, q["expected"])

    def test_path_normalization(self):
        fs = game.VirtualFS(cwd="/home")
        self.assertEqual(fs.path("../etc/./config.ini"), "/etc/config.ini")
        self.assertEqual(fs.path("~/readme.txt"), "/home/readme.txt")

    def test_virtual_creation(self):
        fs = game.VirtualFS()
        self.assertTrue(fs.run("mkdir /home/test")[0])
        self.assertTrue(fs.run("touch /home/test/note.txt")[0])
        self.assertEqual(fs.nodes["/home/test/note.txt"], "")

    def test_unknown_command(self):
        fs = game.VirtualFS()
        self.assertFalse(fs.run("not_a_command")[0])

    def test_progress(self):
        original_root, original_save = game.ROOT, game.SAVE
        self.addCleanup(setattr, game, "ROOT", original_root)
        self.addCleanup(setattr, game, "SAVE", original_save)
        with tempfile.TemporaryDirectory() as tmp:
            game.ROOT = Path(tmp)
            game.SAVE = game.ROOT / "progress.json"
            self.assertEqual(game.load_progress(), 0)
            self.assertTrue(game.save_progress(12))
            self.assertEqual(game.load_progress(), 12)
            game.SAVE.write_text("invalid", encoding="utf-8")
            self.assertEqual(game.load_progress(), 0)
