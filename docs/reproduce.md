# Reproduce the offline candidate

The scripts reproduce the DS1522+ table modification and execute the original x86 selection routines under Unicorn. They do not contact a NAS, change hardware, emulate a complete boot, or produce a qualified SPI programming image.

## Obtain the exact input

Download the [official DS1522+ DSM 7.2.2-72806 package](https://global.synologydownload.com/download/DSM/release/7.2.2/72806/DSM_DS1522%2B_72806.pat). Its SHA-256 is:

```text
428a896511849bc0971b9d3e4fcdcbb29c48dae65ae46e7c757a9f585412e2dd
```

Extract `bios.ROM` from that package. The original investigation used [patology](https://github.com/sud0woodo/patology), which verifies the package signature and encrypted-block hashes. Follow its installation instructions and run its `--dump` command in an empty working directory. Its extraction writes package files into the current directory.

The required `bios.ROM` is a 9,158,376-byte update container, with SHA-256:

```text
09289812c93bfc184425b8db7853a56d92abd60256904aeeaa4f6249f4552b68
```

[sources.json](../sources.json) records the comparison packages, input hashes and analysis tools. No vendor firmware is bundled here. The separate Update 4 package was also examined for incident-era OS behavior; the candidate reproducer uses the base package's BIOS bytes.

## Run

From the repository root, with Python 3.10 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/prepare_inputs.py /path/to/extracted/bios.ROM
python scripts/validate_candidate.py
```

Input preparation checks the container hash, extracts its 8 MiB payload, decompresses the 3 MiB early BIOS, and verifies both extracted modules. It rejects a different BIOS revision instead of guessing offsets.

Run the verifier without Python's `-O` option because its assertions are part of the experiment. On the development Mac, Unicorn terminated with `SIGILL` inside the agent sandbox and completed normally outside that sandbox. The reported verification was run outside that sandbox.

## Expected result

The verifier reports eight passing cases and 130 changed module bytes. The deterministic module candidate SHA-256 is:

```text
19536f87b29917839457311c0acdba61aee96c0bb90054b6a530fb15f97e4e28
```

Generated files are under the ignored `build/` directory:

- `candidate_emulation.json`: original and modified selection results.
- `candidate_module_only/`: the modified OEM module.
- `candidate_region_only/`: the rebuilt compressed-code fragment.
- `region_rebuild_verification.json`: decompression, size and firmware-structure checks.

The decompressed candidate early-BIOS hash is `f8a72eff02448c583646a2d95b91be8b4b6e6c298b3a2a204d6e2892003022c1`. Compressed bytes can depend on the zlib version; the script verifies their decoded contents and that they fit the original extent.

The eight cases combine two constructed CPUID inputs with four synthetic SMU high-bit values. They test the original classifier, platform selector and table lookup. They do not measure the replacement processor, initialize memory, train PCIe links, enforce boot signatures, or run DSM.

The original investigation also assembled an 8 MiB candidate from a private live capture. That machine-specific image is excluded. Its deidentified construction result is in [live_candidate_verification.json](../evidence/go_no_go/live_candidate_verification.json); it is not required by these scripts.

## Evidence coverage

The broader study used UEFIExtract A76, PSPTool 3.7, Ghidra 12.1.2 through REA, LLVM disassembly, official Synology OS sources, and read-only observations from the original R1600 system. The published JSON files preserve code addresses, hashes, source URLs and the limits of each finding.

The portable scripts reproduce the central table experiment. They do not automatically rerun every decompilation, donor comparison or historical observation. Raw device dumps, system-log archives, credentials and machine-specific configuration are excluded from the public corpus.
