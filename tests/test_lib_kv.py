"""Unit tests for lib_kv: KeyValues gamedata -> tracker JSON shape."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
import lib_kv  # noqa: E402

SAMPLE = r'''"Games"
{
	"csgo"
	{
		"Signatures"
		{
			// "Kicking user %s (sv_kick_players_with_cooldown=%d)\n"
			"GameSystem_Think_CheckSteamBan"
			{
				"library"		"server"
				"windows"		"41 54 48 81 EC ? ? ? ?"
				"linux"			"\x55\x48\x89\xE5\x2A\x2a"
			}
		}
		"Offsets"
		{
			"Slot"
			{
				"linux"		"12"
				"windows"	"11"
			}
		}
	}
}
'''


class TestToGamedata(unittest.TestCase):
    def test_signatures_and_offsets(self):
        gd = lib_kv.to_gamedata(SAMPLE)
        self.assertEqual(gd["GameSystem_Think_CheckSteamBan"], {"signatures": {
            "library": "server",
            "windows": "41 54 48 81 EC ? ? ? ?",
            "linux": "55 48 89 E5 ? ?",
        }})
        self.assertEqual(gd["Slot"], {"offsets": {"linux": 12, "windows": 11}})

    def test_comment_words_are_not_keys(self):
        gd = lib_kv.to_gamedata(SAMPLE)
        self.assertEqual(sorted(gd), ["GameSystem_Think_CheckSteamBan", "Slot"])

    def test_other_game_is_empty(self):
        self.assertEqual(lib_kv.to_gamedata(SAMPLE, game="dota"), {})

    def test_double_question_marks(self):
        self.assertEqual(lib_kv.normalize_sig("48 ?? 8D"), "48 ? 8D")


if __name__ == "__main__":
    unittest.main()
