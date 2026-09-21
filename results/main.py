"""Recompute the supplied CSV; see README.md for provenance and interval limits."""

import argparse
from pathlib import Path

from analysis import DATA_DIR, PROVENANCE_NOTICE, load_trial_data, summarize_results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DATA_DIR / "results.csv")
    parser.add_argument("--conditions", type=Path, default=DATA_DIR / "trial_conditions.csv")
    parser.add_argument("--output", type=Path, default=DATA_DIR / "reproduced/results_with_ci.csv")
    args = parser.parse_args()
    df_trials = load_trial_data(args.input, args.conditions)
    results_df = summarize_results(df_trials)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(args.output, index=False)
    print(PROVENANCE_NOTICE)
    print(f"Input: {args.input.resolve()}; conditions: {args.conditions.resolve()}")
    print(f"Validated {len(df_trials)} task/trial rows; {len(results_df)} summary rows.")

    # Print formatted tables to console
    print("=" * 80)
    print("SUPPLIED CSV: MEAN DTP AND 95% t INTERVAL HALF-WIDTHS")
    print("=" * 80)

    for task in df_trials["Task"].unique():
        print(f"\n{'=' * 80}")
        print(f"TASK: {task}")
        print("=" * 80)

        task_results = results_df[results_df["Task"] == task]

        # Mean Progress
        print("\n--- Mean Progress (all 20 trials) ---")
        mp = task_results[task_results["Metric"] == "MeanProgress"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in mp.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

        # Generalization
        print("\n--- Generalization (trials 11-20) ---")
        gen = task_results[task_results["Metric"] == "Generalization"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in gen.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

        # Transfer Gap
        print("\n--- Transfer Gap (Res - Base, trials 11-20) ---")
        tg = task_results[task_results["Metric"] == "TransferGap"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in tg.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

    print(f"\n{'=' * 80}")
    print(f"Results saved to: {args.output}")
    print("=" * 80)


if __name__ == "__main__":
    main()
