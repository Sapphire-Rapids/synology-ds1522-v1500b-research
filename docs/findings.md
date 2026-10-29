# Technical findings

**This project has an offline candidate, not a verified DS1522+ CPU upgrade or a ready-to-flash image.** The objective is to explain the failed R1600-to-V1500B replacement and complete useful preparation before another costly CPU replacement. No failed V1500B boot trace establishes its CPU classification, selected board table, or final executed stage.

The primary baseline is DSM 7.2.2-72806 Update 4, with the corresponding official DS1525+ package used for comparison. The analysis uses official firmware, static code inspection, bounded emulation, and evidence from the working R1600 configuration. Those methods answer different questions. Code can establish what a branch does; synthetic inputs can exercise that branch; neither establishes what the replacement processor actually did.

**Board topology is the strongest concrete hypothesis.** The firmware classifies the processor using CPUID and information from its management controller, the SMU. That classification selects tables describing how PCIe links and clocks should be configured. In the studied DS1522+ firmware, platform 8 enables five PCIe roots. Platform 0 enables only two and assigns other logical lanes to Ethernet engines.

The working R1600 layout puts the onboard network switch behind root `00:01.4` and the JMB585 SATA controller behind `00:01.5`. Those roots are absent from the original platform-0 PCIe table. If the V1500B selects that table, the mismatch could affect both onboard networking and system-disk discovery. This is a specific mechanism supported by the firmware, with an unobserved selection step in the failed boot. [Topology evidence](../evidence/pcie_followup/pcie_table_analysis.json)

The DS1525+ provides a useful comparison because it officially uses V1500B. Several relevant parts match:

| Compared part | Result | What it establishes |
| --- | --- | --- |
| Family/package gate | The matcher and candidate-construction code are byte-identical. | These checks give the same result for the same inputs. |
| PMU memory-training firmware | Eight code/data entry extents are byte-identical. | These stored training programs are shared. |
| CPU microcode | Three of four listed entries are byte-identical. | Several patch payloads are shared; applicability to the failed chip remains unmeasured. |
| Selected table interpreters | CPM Init, GPIO Init, and PCIe Init PEIM text matches after normalizing image relocations. | The compared interpretation code is shared; table contents still matter. |

Both BIOSes also contain an executable V1500B power-policy branch with a 16 W path. DS1525+ adds a conditional higher-power option; its presence does not establish that the product normally selects it. No specific missing basic CPU-initialization prerequisite was identified in DS1522+. PSP, SMU, ABL, and other modules still differ, so this is a bounded conclusion rather than whole-firmware equivalence. [CPU comparison](../evidence/ds1525_comparison/cpu/evidence.json), [board comparison](../evidence/ds1525_comparison/board/evidence.json)

The boards also differ in onboard network hardware and expansion interfaces. DS1525+ has different lane and root-port assignments. Its working design therefore supports studying board-specific configuration, without establishing that its tables can be copied onto DS1522+.

The candidate reuses the DS1522+ board's topology and clock settings in the alternative classification path. It changes 130 data bytes in `AmdCpmOemInitPeim`, within the existing PCIe layout and clock tables. Original instructions, table headers, platform masks, and the existing platform-8 tables remain unchanged.

Eight selector cases passed, covering two constructed CPUID inputs (`0x00810f10` and `0x00810f81`) and all four values of SMU response bits 31:30. The original selector machine code chose the expected candidate tables. These are synthetic cases: the replacement chip's CPUID and SMU response were not measured. PCIe training, electrical routing, resets, and clock behavior were not emulated. Rebuilding and checking the compressed code region establishes structural consistency only. [Candidate evidence](../evidence/boot_enablement/candidate_emulation.json)

**An official same-CPU split precedent has now been found.** The RS1221+ V1500B firmware configures logical lanes 0 and 1 as independent x1 engines. The board table is registered and reachable through the original CPU-class/platform selector. Its seven-port layout also matches the disk-controller and expansion-slot roots required by the shipped device tree. The reviewed OEM callback does not explicitly replace or merge those two descriptors.

| Official V1500B model | Logical lanes 0 and 1 | Requested roots |
| --- | --- | --- |
| DS1621+ | One x2 engine, assigned to NVMe slot 1 | `00:01.3` |
| DS1821+ | One x2 engine, assigned to NVMe slot 1 | `00:01.3` |
| DS1525+ | One x2 engine | `00:01.6` |
| RS1221+ | Two independent x1 engines | lane 0 → `00:01.2`; lane 1 → `00:01.3` |

This closes the earlier lack of an applicable V1500B split example. It is static factory-design evidence; no donor-model trained-link trace was collected. The DS1522+ candidate requests lane 0 → `00:01.5` and lane 1 → `00:01.4`, preserves native SATA on lanes 2/3, and uses different clock/reset definitions. Its complete combination and final mapping remain untested. [Same-CPU comparison](../evidence/same_cpu_reference/summary.json), [RS1221+ selection review](../evidence/same_cpu_reference/rs1221/selection_review.json)

A published Picasso descriptor rule relates lane order to root-port order. Its applicability to full-I/O Raven/V1500B has not been established. The actual target mapper accepts unique requested bus/device/function assignments, but it depends on the earlier SMU initialization producing valid engines. The RS1221+ precedent narrows the remaining question to the DS1522+ combination, mapping and hardware behavior. [Earlier lane investigation and follow-up](../evidence/ds1525_comparison/board/lane_split_support.json), [mapper check](../evidence/boot_enablement/port_mapping_check.json)

The absence of an IP address on both onboard and expansion ports does not identify a single boot stage. The studied diskless recovery environment can start onboard networking, so missing system disks alone do not explain loss of an onboard IP. If the onboard PCIe path is unavailable, however, those ports cannot work.

The same recovery kernel and ramdisk lack the Atlantic driver needed by the studied expansion NIC. An expansion endpoint could still enumerate without producing a usable network interface. Its DHCP configuration would then have nothing to configure. The later JuniorExpansionPack download requires an existing network connection. This gives a conditional explanation for both kinds of port having no IP, without proving that the failed boot reached recovery. [Network evidence](../evidence/network_followup/evidence.json)

Firmware acceptance is a separate unresolved issue. Editing the covered payload invalidates the vendor's BIOSCER and outer PE Authenticode signatures. Repairing ordinary checksums does not restore those signatures. Whether this platform would boot the modified raw payload remains unknown. A read-only status attempt returned raw `0x2`, but the register's validity bit was unset. That value proves neither acceptance nor rejection. [Signature analysis](../evidence/patch_feasibility/evidence.json), [readiness decision](../evidence/go_no_go/decision.json)

Further CPU rework remains on hold. Preparation still needs a qualified image-write/restore path that preserves board-specific data, acceptance and boot verification of the candidate on R1600, and a working capture path that can reveal a later failure. Any eventual V1500B test must observe classification, table selection, PCIe endpoints, and recovery networking. The offline checks do not replace those observations.

An additional model-specific branch recognizes V1404I during early initialization, sets token `0x4140d`, and passes the resulting byte into the later SMU power table's `itemp` field. This identifies another handled SKU; DS1522+ operation with that CPU has not been tested. [V1404I evidence](../evidence/additional_cpu_support/evidence.json)

This public repository excludes proprietary firmware binaries and machine-specific captures. [sources.json](../sources.json) identifies official inputs and their hashes. The [reproduction guide](reproduce.md) describes the supported offline workflow. The included evidence records state their scope and limits so that another researcher can distinguish a repeatable static result from an unresolved hardware question.
