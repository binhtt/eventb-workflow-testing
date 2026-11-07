#!/usr/bin/env python3
"""Export manuscript tables from recorded data without modifying that data."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from analyse import eligible, found

METHODS = {
    "nominal": "Nominal",
    "random": "Random",
    "model_conflicts": "Model-derived",
    "canonical_independence": "Conservative sleep-set DFS",
}


def write_csv(folder, name, rows):
    with (folder / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/paper-tables")
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.exists():
        parser.error(f"Output directory already exists: {destination}")

    plan = json.loads((ROOT / "plan.json").read_text())
    with (ROOT / "results/trials.csv").open(newline="", encoding="utf-8") as stream:
        trials = list(csv.DictReader(stream))
    destination.mkdir(parents=True)

    statuses = list(ET.parse(ROOT / "proof/SharedWorkflow/Resource.bps").getroot())
    kinds = Counter(row.attrib["name"].rsplit("/", 1)[-1] for row in statuses)
    write_csv(destination, "table4_proof_obligations.csv", [
        {"obligation": kind, "generated": kinds[kind], "discharged": sum(
            row.attrib["name"].endswith("/" + kind)
            and int(row.attrib["org.eventb.core.confidence"]) > 0
            for row in statuses)}
        for kind in ("INV", "THM", "WD")
    ])
    finite = json.loads((ROOT / "results/model_conformance.json").read_text())
    write_csv(destination, "table5_finite_conformance.csv", finite)

    faults = plan["development_faults"] + plan["evaluation_faults"]
    raw = []
    for index, fault in enumerate(faults):
        row = {"id": f"D{index+1}" if index < 3 else f"E{index-2}", "mutant": fault}
        for method, label in METHODS.items():
            subset = [r for r in trials if r["mutant"] == fault and r["method"] == method]
            row[label] = sum(found(r, 16) for r in subset)
            row[label + " denominator"] = len(subset)
        raw.append(row)
    write_csv(destination, "table6_raw_mutant_detections.csv", raw)

    curve = []
    summary = []
    for method, label in METHODS.items():
        subset = [r for r in trials if r["method"] == method and eligible(r, plan)]
        assert len(subset) == 550, (method, len(subset))
        summary.append({"method": label, "eligible_trials": len(subset),
                        "budget4": sum(found(r, 4) for r in subset),
                        "budget16": sum(found(r, 16) for r in subset)})
        for budget in range(1, 17):
            detected = sum(found(r, budget) for r in subset)
            curve.append({"method": label, "budget": budget, "detected": detected,
                          "eligible_trials": len(subset), "percent": 100*detected/len(subset)})
    write_csv(destination, "table7_qualified_detection.csv", summary)
    write_csv(destination, "figure4_detection_curve.csv", curve)
    witnesses = json.loads((ROOT / "results/witnesses.json").read_text())
    witness = next(w for w in witnesses if w["method"] == "model_conflicts"
                   and w["requests"] == 4 and w["capacity"] == 2
                   and w["mutant"] == "reserve_lost_update" and w["seed"] == 0)
    prefix = []
    for index, entry in enumerate(witness["log"], 1):
        state = entry["snapshot"]
        request, operation, phase = entry["hook"]
        prefix.append({"step": index, "request": request, "operation": operation,
                       "phase": phase, "free": state["free"], "held_count": len(state["held"]),
                       "free_plus_held": state["free"] + len(state["held"]),
                       "failures": ";".join(entry["failures"])})
        if entry["failures"]:
            break
    write_csv(destination, "table8_first_failing_prefix.csv", prefix)
    shutil.copy2(ROOT / "results/paired_bootstrap.csv", destination / "table9_paired_bootstrap.csv")
    shutil.copy2(ROOT / "results/standalone_timing_summary.csv", destination / "table10_suite_timing.csv")
    (destination / "README.md").write_text(
        "# Paper table exports\n\n"
        "Generated from the recorded raw data and native proof status files.\n"
        "Table numbers refer to IEEE_ACCESS_Agent.pdf supplied on 2026-11-07.\n"
        "Table 8 is an execution-prefix extract from results/witnesses.json; "
        "see docs/PAPER_RESULTS.md for its selection.\n"
        "The 550 denominator counts repeated seed-mutant-configuration trials, "
        "not independent defects. Timings are the recorded measurements, not a new run.\n",
        encoding="utf-8",
    )
    print(f"Exported paper tables and detection-curve data to {destination}")


if __name__ == "__main__":
    main()
