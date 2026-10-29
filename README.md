# Synology DS1522+ / V1500B research

[简体中文](README.zh-CN.md)

Research into a DS1522+ that did not complete startup after replacing its Ryzen Embedded R1600 with a V1500B.

**Status: an offline candidate exists. A successful CPU upgrade has not been verified, and this repository provides no ready-to-flash image.**

The firmware already contains executable V1500B handling. The strongest hypothesis is that CPU classification selects a PCIe layout that does not match the DS1522+ board. There is no failed V1500B boot trace to confirm that path.

- The candidate changes **130 table-data bytes** for PCIe topology and clocks. Eight synthetic selector cases passed: two constructed CPUID inputs × four SMU high-bit values. These checks do not test physical link training.
- Comparison with the V1500B-based DS1525+ found the same family/package gate, eight identical PMU firmware entries, and common table interpreters. The complete firmware stacks differ.
- **RS1221+ supplies a same-CPU split precedent:** its official V1500B firmware configures logical lanes 0 and 1 as independent x1 links. The complete DS1522+ layout and resulting port mapping remain untested. [Comparison](evidence/same_cpu_reference/summary.json)
- Editing the firmware invalidates vendor update signatures. Acceptance of a modified raw image remains unknown.

Start with the [findings](docs/findings.md) and [reproduction guide](docs/reproduce.md). Further CPU rework remains on hold pending a qualified deployment/restore path and useful boot diagnostics.

The public corpus contains analysis, source references, and reproduction scripts. Proprietary firmware binaries and machine-specific captures are excluded. Official download references and input hashes are listed in [sources.json](sources.json).
