# Evidence index

The records distinguish observed bytes and runtime facts from hypotheses and untested behavior.

| Area | Entry point |
| --- | --- |
| Overall findings | [findings.json](findings.json) |
| CPU-dependent board configuration | [pcie_table_analysis.json](pcie_followup/pcie_table_analysis.json) |
| DS1525+ comparison | [summary.json](ds1525_comparison/summary.json) |
| Exact lane-split uncertainty | [lane_split_support.json](ds1525_comparison/board/lane_split_support.json) |
| Candidate selection experiment | [candidate_emulation.json](boot_enablement/candidate_emulation.json) |
| Update signatures and raw boot limits | [evidence.json](patch_feasibility/evidence.json) |
| Authentication-state observation | [live_preflight.json](go_no_go/live_preflight.json) |
| Diskless networking | [evidence.json](network_followup/evidence.json) |
| Boot-stage markers | [evidence.json](boot_diagnostics/evidence.json) |
| Historical symptoms and recovered diagnostic | [historical_observations.json](historical_observations.json) |
| Preparation before another CPU rework | [decision.json](go_no_go/decision.json) |

Machine names, connection information and personal filesystem paths have been removed. Live-observation summaries retain relevant hardware facts; their raw captures and unique full-image fingerprints are not published.

Paths inside the records describe the original analysis layout. References to firmware, extracted modules, OS files, raw logs or tool-evidence archives are provenance labels, not promises that those files are distributed. Official input URLs and hashes are in [sources.json](../sources.json). Static code excerpts are attributed to their original firmware or upstream source; this repository does not claim ownership of vendor code.
