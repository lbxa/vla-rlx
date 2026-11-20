---
name: editor
description: Write, revise, and review VLA-RLX research text in the thesis, results, and project website. Use for methods, results, captions, statistical interpretation, and evidence-backed conclusions.
---

# Editor

Write for an independent research reader. Explain what makes the argument work in complete sentences and connected paragraphs. State the research question, approach, and supported result early. Define notation, units, and the observation unit before using them.

## Locate the evidence

- Start with the [reproduction and evidence record](../../../docs/reproduction-status.md) for unresolved discrepancies, source revisions, rollout conditions, and limits on physical reproduction.
- Use the [analysis README](../../../results/README.md) for metric definitions, intervals, and reproduction commands. Treat `results/results_section.tex` as historical prose and verify numbers against the intended source before reuse.
- Use the [website README](../../../website/README.md) to identify the site source and its deployment workflow. Check the actual version and protocol before carrying a claim across the site, local results, or the separate manuscript repository linked from the [project README](../../../README.md).

## Write the reasoning in full

- Explain the role of the frozen base policy and the learned residual as needed for the comparison. Spell out which task, method, and trial condition the evidence covers.
- Name the measured outcome and its denominator. Distinguish mean discretized task progress from binary success, evaluation rollouts from independent training runs, and manuscript-assigned trial conditions from verified rollout records.
- Keep results from the supplied CSV traceable to that file. Consult the evidence record before describing scores as reconciled with the manuscript or assigning results to a checkpoint, seed, or code revision.
- Report the observation unit and interval assumptions. Use causal language only for a supported comparison. Explain where the evidence ends before drawing a broader conclusion.
- Verify citations and preserve author metadata and established notation. Use a worked example or diagram only when it resolves a concrete obstacle for the reader.

## Verify the edited artifact

Generate updated numerical tables and figures from the versioned source using the documented analysis commands. Give each figure a caption and a nearby reference. Include the setting, units, sample size, and any uncertainty that the figure displays.

Read the edited passage in context and check that the abstract, methods, figures, and results agree. Use the relevant local build or reproduction check. For layout changes, inspect the built page or document for legibility, overflow, captions, and references.
