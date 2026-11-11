import tempfile
import unittest
from pathlib import Path
import sys
import os
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.candidates import select_diverse
from src.parser import format_time, parse_episode, parse_text, to_seconds
from src.pipeline import analyze, export
from src.schemas import Promo
from src.reviewer import review
from src.scoring import audit_cold_viewer_risk
from src.schemas import Beat
from src.evaluation import evaluate, promo_key
from src.brief import build_presentation_brief


ROOT = Path(__file__).parents[1]
DATA = ROOT / "I Married a Broken Soldier. He was a Duke-scripts (2)"


class PromoFinderTests(unittest.TestCase):
    def test_timestamp_round_trip(self):
        self.assertEqual(to_seconds("01:02.50"), 62.5)
        self.assertEqual(format_time(62.5), "01:02.50")

    def test_parser_reads_episode_one(self):
        path = next(DATA.rglob("episode-001-*.txt"))
        episode = parse_episode(path)
        self.assertEqual(episode.number, 1)
        self.assertGreater(len(episode.beats), 10)
        self.assertEqual(episode.beats, sorted(episode.beats, key=lambda beat: (beat.start, beat.end)))

    def test_full_dataset_produces_valid_diverse_promos(self):
        episodes, promos, info = analyze(DATA, limit=15)
        self.assertEqual(len(episodes), 50)
        self.assertGreater(info["candidates"], 100)
        self.assertTrue(promos)
        for promo in promos:
            self.assertGreaterEqual(promo.duration, 20)
            self.assertLessEqual(promo.duration, 60)
            self.assertLess(promo.start, promo.end)

    def test_export(self):
        _, promos, _ = analyze(DATA, limit=3)
        with tempfile.TemporaryDirectory() as directory:
            json_path, csv_path = export(promos, directory)
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())

    def test_overlap_suppression(self):
        make = lambda start, end, score: Promo(0, 1, start, end, end-start, score, "h", "c", "w", {}, [], False)
        chosen = select_diverse([make(0, 40, 90), make(5, 45, 89), make(60, 100, 80)])
        self.assertEqual(len(chosen), 2)

    def test_model_review_failure_keeps_heuristic_result(self):
        promo = Promo(1, 1, 0, 30, 30, 72, "hook", "cliff", "why", {}, [], False)
        with patch.dict(os.environ, {"PROMO_API_BASE_URL": "https://example.test", "PROMO_API_KEY": "test", "PROMO_MODEL": "test"}), patch("src.reviewer.request.urlopen", side_effect=OSError("offline")):
            reviewed, mode = review([promo])
        self.assertEqual(mode, "heuristic (model review unavailable)")
        self.assertEqual(reviewed[0].score, 72)

    def test_cold_viewer_audit_flags_late_payoff_language(self):
        beats = [Beat(20, 1, "dialogue", 0, 3, "The truth is revealed: he is dead.", "JULIANA"), Beat(20, 1, "dialogue", 25, 30, "What will happen now?", "GERALD")]
        risk, status, notes = audit_cold_viewer_risk(beats, 0, 30, 20)
        self.assertGreaterEqual(risk, 40)
        self.assertIn(status, {"REVIEW", "HIGH RISK"})
        self.assertTrue(notes)

    def test_uploaded_text_parser_and_evaluation_metrics(self):
        raw = "EPISODE NUMBER: Episode 8\n\nSCENE 01\n\n**MAYA:**\nStart: (00:00.00) | End: (00:03.00)\n\"Stop!\"\n\n--- SCRIPT END ---"
        self.assertEqual(parse_text(raw, "upload.txt").number, 8)
        promo = Promo(1, 8, 0, 30, 30, 80, "h", "c", "w", {}, [], False)
        labels = {promo_key(8, 0, 30): {"verdict": "good", "spoiler_verdict": "safe"}}
        metrics = evaluate([promo], labels)
        self.assertEqual(metrics["precision_at_k"], 1.0)
        self.assertEqual(metrics["spoiler_safety_rate"], 1.0)

    def test_presentation_brief_contains_shortlist(self):
        promo = Promo(1, 8, 0, 30, 30, 80, "Hook line", "Cliff line", "Why", {}, [], False, spoiler_risk=10, cold_viewer_status="SAFE")
        brief = build_presentation_brief([promo], [])
        self.assertIn("Episode 08", brief)
        self.assertIn("Cold-viewer risk: 10/100", brief)


if __name__ == "__main__":
    unittest.main()
