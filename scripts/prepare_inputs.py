"""Extract the exact official DS1522+ inputs used by the offline experiment.

Supply bios.ROM extracted from a package listed in sources.json.
This script does not connect to a NAS or write firmware.
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'inputs/DS1522+_7.2.2-72806'
CONTAINER_SHA256 = '09289812c93bfc184425b8db7853a56d92abd60256904aeeaa4f6249f4552b68'
PAYLOAD_SHA256 = 'ac8eb91600c714bd17c7fa5bcac1e94463c8f633e7c26bd948a3b6f772415e65'
EARLY_SHA256 = '72d2ae15438d8f0b52a99bd68489bac0f37210c83657eea3e9b8a98324535432'
MODULES = [
    ('AmdCpmOemInitPeim_D617467B_early.efi', 0x412C0, 23968,
     '8a1a35e8bfa8d85d70d1831585eb6de03d7599b34a5857dc719a08af80976cbf'),
    ('AmdCpmInitPeim_D919136E_early.efi', 0x47120, 17920,
     '46701360c3fd09965346c8f5b897e6ae12b9717ca55d6c0f533fc6e8a0c434bd'),
]


def verify(label, data, expected):
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f'{label}: expected SHA256 {expected}, got {actual}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bios_rom', type=Path, help='Official bios.ROM update container')
    args = parser.parse_args()
    container = args.bios_rom.read_bytes()
    verify('bios.ROM', container, CONTAINER_SHA256)
    payload = container[0xB08D0:0xB08D0 + 0x800000]
    verify('8 MiB payload', payload, PAYLOAD_SHA256)
    size, = struct.unpack_from('<I', payload, 0x750014)
    decoder = zlib.decompressobj()
    early = decoder.decompress(payload[0x750100:0x750100 + size], 0x300001)
    if (len(early) != 0x300000 or not decoder.eof or decoder.unused_data or
            decoder.unconsumed_tail):
        raise ValueError('The compressed stream is not the expected complete 3 MiB early BIOS')
    verify('early BIOS', early, EARLY_SHA256)
    outputs = {'bios_payload.bin': payload, 'early_bios.bin': early}
    for name, offset, length, expected in MODULES:
        module = early[offset:offset + length]
        verify(name, module, expected)
        outputs[name] = module
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        manifest[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    (OUT / 'prepared.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'prepared_files': len(outputs), 'output': str(OUT.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
