"""Regression checks for the released score analysis, without robot dependencies."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

from analysis import DATA_DIR, calculate_ci, load_trial_data, summarize_results


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.trials = load_trial_data()

    def test_protocol_boundaries_and_observation_counts(self):
        conditions = self.trials.set_index("Trial")["Condition"]
        for trial, condition in [(1, "ID"), (5, "ID"), (6, "DP"), (10, "DP"), (11, "OOD"), (20, "OOD")]:
            with self.subTest(trial=trial):
                self.assertTrue(conditions.loc[trial].eq(condition).all())
        result = summarize_results(self.trials)
        self.assertEqual(len(self.trials), 140)
        self.assertEqual(len(result), 119)
        self.assertTrue(result.loc[result.Metric == "MeanProgress", "N"].eq(20).all())
        self.assertTrue(result.loc[result.Metric != "MeanProgress", "N"].eq(10).all())

    def test_reproduces_historical_summary(self):
        expected = pd.read_csv(DATA_DIR / "results_with_ci.csv")
        actual = summarize_results(self.trials)[expected.columns]
        pd.testing.assert_frame_equal(actual, expected, rtol=1e-12, atol=1e-12)

    def test_row_order_does_not_change_metrics_or_pairing(self):
        def ordered(df):
            return summarize_results(df).sort_values(["Task", "Metric", "Method"]).reset_index(drop=True)
        pd.testing.assert_frame_equal(ordered(self.trials), ordered(self.trials.sample(frac=1, random_state=19)))

    def test_progress_is_not_binary_success(self):
        # All nominal/DP scores are partial; OOD scores are successes. Mean DTP
        # must include fractional progress rather than count only successes.
        self.trials["Base"] = np.where(self.trials.Condition == "OOD", 1.0, 0.5)
        result = summarize_results(self.trials)
        base = result[(result.Task == "rubix-stack-v1") & (result.Method == "Base")].set_index("Metric")
        self.assertEqual(base.loc["MeanProgress", "Mean"], 0.75)
        self.assertEqual(base.loc["Generalization", "Mean"], 1.0)

    def test_t_interval_and_insufficient_sample(self):
        # For [0, 1], sample SE = 0.5 and t(0.975, df=1) = 12.706204736.
        self.assertAlmostEqual(calculate_ci(np.array([0.0, 1.0])), 6.353102368, places=7)
        self.assertTrue(np.isnan(calculate_ci(np.array([0.5]))))

    def test_invalid_scores_or_trials_are_rejected(self):
        raw = self.trials.drop(columns="Condition")
        cases = {
            "missing trial": raw.drop(index=0),
            "duplicate trial": pd.concat([raw, raw.iloc[[0]]]),
            "missing task": raw[raw.Task != "rubix-stack-v1"],
        }
        for name, column, value in [
            ("missing score", "Base", np.nan),
            ("off ladder", "Base", 0.3),
            ("out of range score", "Base", 1.25),
            ("noninteger trial", "Trial", 1.5),
            ("extra trial", "Trial", 21),
            ("nonnumeric trial", "Trial", "bad"),
        ]:
            modified = raw.astype({column: object}).copy()
            modified.loc[0, column] = value
            cases[name] = modified
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.csv"
            for name, frame in cases.items():
                with self.subTest(name=name):
                    frame.to_csv(path, index=False)
                    with self.assertRaises(ValueError):
                        load_trial_data(path)

    def test_condition_drift_is_rejected(self):
        conditions = pd.read_csv(DATA_DIR / "trial_conditions.csv")
        conditions.loc[conditions.Trial == 6, "Condition"] = "ID"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conditions.csv"
            conditions.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "5–5–10"):
                load_trial_data(conditions_path=path)

    def test_export_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested/summary.csv"
            result = subprocess.run(
                [sys.executable, str(DATA_DIR / "main.py"), "--output", str(output)],
                cwd=directory, check=True, capture_output=True, text=True,
            )
            self.assertIn("not reconciled", result.stdout)
            self.assertEqual(len(pd.read_csv(output)), 119)


if __name__ == "__main__":
    unittest.main()
