"""Build offline topology candidates and exercise the original x86 selectors.

The SMU reply is a synthetic input. This does not emulate PCIe training, execute
the complete firmware, produce a flash image, or access hardware.
"""

import hashlib
import json
import struct
import zlib
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32
from unicorn.x86_const import (
    UC_X86_REG_EAX, UC_X86_REG_EBP, UC_X86_REG_EBX, UC_X86_REG_ECX,
    UC_X86_REG_EDI, UC_X86_REG_EDX, UC_X86_REG_EFLAGS, UC_X86_REG_EIP,
    UC_X86_REG_ESI, UC_X86_REG_ESP,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build'
MODULES = ROOT / 'inputs/DS1522+_7.2.2-72806'
OEM_PATH = MODULES / 'AmdCpmOemInitPeim_D617467B_early.efi'
CPM_PATH = MODULES / 'AmdCpmInitPeim_D919136E_early.efi'
OEM_SHA256 = '8a1a35e8bfa8d85d70d1831585eb6de03d7599b34a5857dc719a08af80976cbf'
CPM_SHA256 = '46701360c3fd09965346c8f5b897e6ae12b9717ca55d6c0f533fc6e8a0c434bd'

GET_CPU_CLASS = 0x09B496D1
SELECT_PLATFORM = 0x09B478B7
GET_TABLE = 0x09B47BBC
GET_PCD_SERVICE = 0x09B47B52
CPM_PPI = 0x20000000
MAIN_TABLE = 0x20001000
TABLE_LIST = 0x20002000
PCD_SERVICE = 0x20003000
CPUID_STUB = 0x20008000
PCD_GET32_STUB = 0x20008100
PCD_SET16_STUB = 0x20008200
STACK_BASE = 0x10000000
STACK_TOP = STACK_BASE + 0xFFF0
STOP = 0x30000000


def u32(blob, offset):
    return struct.unpack_from('<I', blob, offset)[0]


def pe_layout(blob):
    pe = u32(blob, 0x3C)
    assert blob[pe:pe + 4] == b'PE\0\0'
    machine, sections = struct.unpack_from('<HH', blob, pe + 4)
    optional_size = struct.unpack_from('<H', blob, pe + 20)[0]
    optional = pe + 24
    assert machine == 0x14C and struct.unpack_from('<H', blob, optional)[0] == 0x10B
    image_base = u32(blob, optional + 28)
    image_size = u32(blob, optional + 56)
    header_size = u32(blob, optional + 60)
    parts = []
    for i in range(sections):
        off = optional + optional_size + i * 40
        virtual_size, rva, raw_size, raw_offset = struct.unpack_from('<IIII', blob, off + 8)
        parts.append((rva, raw_offset, raw_size, virtual_size))
    return image_base, image_size, header_size, parts


def active_ports(uc, table_address):
    ports = []
    for i in range(16):
        data = bytes(uc.mem_read(table_address + 0x14 + i * 0x194, 24))
        flags = u32(data, 0)
        port = u32(data, 12)
        if data[4] == 1 and port & 1:
            ports.append(f'00:{(port >> 8) & 31:02x}.{(port >> 13) & 7}')
        if flags & 0x80000000:
            break
    return ports


def exercise(cpm_bytes, oem_bytes, smu_high_bits, cpuid_eax):
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    images = [(cpm_bytes, pe_layout(cpm_bytes)), (oem_bytes, pe_layout(oem_bytes))]
    map_start = min(layout[0] for _, layout in images) & ~0xFFF
    map_end = (max(layout[0] + layout[1] for _, layout in images) + 0xFFF) & ~0xFFF
    uc.mem_map(map_start, map_end - map_start)
    for blob, (image_base, _, header_size, sections) in images:
        uc.mem_write(image_base, blob[:header_size])
        for rva, raw_offset, raw_size, _ in sections:
            if raw_size:
                uc.mem_write(image_base + rva, blob[raw_offset:raw_offset + raw_size])
    uc.mem_map(STACK_BASE, 0x10000)
    uc.mem_map(CPM_PPI, 0x10000)
    uc.mem_map(STOP, 0x1000)

    def write32(address, value):
        uc.mem_write(address, struct.pack('<I', value))

    def read32(address):
        return u32(bytes(uc.mem_read(address, 4)), 0)

    # Replace only the platform-service dependency with a returning stub.
    # All CPU-classification, platform-selection, and table-lookup instructions
    # remain the original bytes from the official CPM module.
    for address in [GET_PCD_SERVICE, CPUID_STUB, PCD_GET32_STUB, PCD_SET16_STUB]:
        uc.mem_write(address, b'\xC3')
    write32(CPM_PPI + 4, MAIN_TABLE)
    write32(CPM_PPI + 0x108, CPUID_STUB)
    write32(CPM_PPI + 0x188, GET_CPU_CLASS)
    write32(CPM_PPI + 0x1A8, GET_TABLE)
    write32(MAIN_TABLE + 0x53, TABLE_LIST)
    write32(PCD_SERVICE + 0x0C, PCD_GET32_STUB)
    write32(PCD_SERVICE + 0x24, PCD_SET16_STUB)

    oem_base = pe_layout(oem_bytes)[0]
    table_offsets = [0x14C8, 0x2208, 0x22D8, 0x23A8, 0x3D30]
    write32(TABLE_LIST + 0x10, len(table_offsets))
    for i, off in enumerate(table_offsets):
        address = TABLE_LIST + 0x18 + i * 13
        uc.mem_write(address, struct.pack('<IBQ', u32(oem_bytes, off), 0, oem_base + off))

    setter_calls = []

    def hook(machine, address, _size, _data):
        sp = machine.reg_read(UC_X86_REG_ESP)
        if address == GET_PCD_SERVICE:
            machine.reg_write(UC_X86_REG_EAX, PCD_SERVICE)
        elif address == CPUID_STUB:
            assert read32(sp + 4) == CPM_PPI
            output = read32(sp + 8)
            write32(output, cpuid_eax)
            assert read32(sp + 12) == 0
            machine.reg_write(UC_X86_REG_EAX, 0)
        elif address == PCD_GET32_STUB:
            assert read32(sp + 8) == 0x4F0C4
            machine.reg_write(UC_X86_REG_EAX, smu_high_bits << 30)
        elif address == PCD_SET16_STUB:
            token, value = read32(sp + 8), read32(sp + 12)
            assert token in (0x10000000, 0x10000001)
            setter_calls.append({'token': hex(token), 'value': value})
            machine.reg_write(UC_X86_REG_EAX, 0)

    uc.hook_add(UC_HOOK_CODE, hook)

    def invoke(address, args=(), esi=0):
        for reg in [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
                    UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]:
            uc.reg_write(reg, 0)
        uc.reg_write(UC_X86_REG_ESI, esi)
        uc.reg_write(UC_X86_REG_ESP, STACK_TOP)
        uc.reg_write(UC_X86_REG_EFLAGS, 2)
        uc.mem_write(STACK_TOP, struct.pack('<' + 'I' * (1 + len(args)), STOP, *args))
        uc.emu_start(address, STOP, count=100000)
        assert uc.reg_read(UC_X86_REG_EIP) == STOP, 'Instruction bound reached before return'
        return uc.reg_read(UC_X86_REG_EAX)

    cpu_class = invoke(GET_CPU_CLASS, [CPM_PPI]) & 0xFF
    invoke(SELECT_PLATFORM, esi=CPM_PPI)
    platform = struct.unpack('<H', uc.mem_read(MAIN_TABLE + 0x31, 2))[0]
    dxio = invoke(GET_TABLE, [CPM_PPI, int.from_bytes(b'$A26', 'little')])
    clocks = invoke(GET_TABLE, [CPM_PPI, int.from_bytes(b'$A17', 'little')])
    assert dxio and clocks
    return {
        'synthetic_cpuid_eax': hex(cpuid_eax),
        'synthetic_smu_arg0_high_bits': smu_high_bits,
        'cpu_class_from_original_machine_code': cpu_class,
        'platform_from_original_machine_code': platform,
        'selected_dxio_file_offset': hex(dxio - oem_base),
        'selected_clock_table_file_offset': hex(clocks - oem_base),
        'active_pcie_ports': active_ports(uc, dxio),
        'pcd_setter_calls': setter_calls,
    }


def rebuild_code_region(original_module, candidate_module):
    firmware = MODULES
    payload = (firmware / 'bios_payload.bin').read_bytes()
    expanded = (firmware / 'early_bios.bin').read_bytes()
    assert hashlib.sha256(payload).hexdigest() == 'ac8eb91600c714bd17c7fa5bcac1e94463c8f633e7c26bd948a3b6f772415e65'
    assert hashlib.sha256(expanded).hexdigest() == '72d2ae15438d8f0b52a99bd68489bac0f37210c83657eea3e9b8a98324535432'
    region = 0x750000
    module = 0x412C0
    ffs = 0x41268
    old_packed_size = u32(payload, region + 0x14)
    assert zlib.decompress(payload[region + 0x100:region + 0x100 + old_packed_size]) == expanded
    assert expanded[module:module + len(original_module)] == original_module
    modified = expanded[:module] + candidate_module + expanded[module + len(original_module):]
    assert len(modified) == len(expanded)
    assert modified[:module] == expanded[:module]
    assert modified[module + len(original_module):] == expanded[module + len(original_module):]

    fv_header_length = struct.unpack_from('<H', modified, 0x30)[0]
    assert fv_header_length == 0x48
    assert sum(struct.unpack('<' + 'H' * (fv_header_length // 2), modified[:fv_header_length])) & 0xFFFF == 0
    ffs_header = modified[ffs:ffs + 24]
    assert ffs_header == expanded[ffs:ffs + 24]
    assert not ffs_header[19] & 0x40 and ffs_header[17] == 0xAA
    assert (sum(ffs_header) - ffs_header[17] - ffs_header[23]) & 0xFF == 0

    packed = zlib.compress(modified, 9)
    assert zlib.decompress(packed) == modified
    # This specific candidate fits inside the original compressed extent.
    # Abort rather than relocating firmware components if a future edit grows.
    assert len(packed) <= old_packed_size
    header = bytearray(payload[region:region + 0x100])
    struct.pack_into('<I', header, 0x14, len(packed))
    fragment = bytes(header) + packed + b'\xFF' * (old_packed_size - len(packed))
    hypothetical_payload = payload[:region] + fragment + payload[region + len(fragment):]
    assert len(hypothetical_payload) == len(payload)
    assert hypothetical_payload[:region] == payload[:region]
    assert hypothetical_payload[region + len(fragment):] == payload[region + len(fragment):]
    changed = [i for i, (a, b) in enumerate(zip(expanded, modified)) if a != b]
    assert len(changed) == 130
    assert all(module <= i < module + len(original_module) for i in changed)
    # The 0x62 entries still refer to the same address and expanded size.
    for directory in [0x126000, 0x285000]:
        assert hypothetical_payload[directory:directory + 0x400] == payload[directory:directory + 0x400]

    destination = OUT / 'candidate_region_only'
    destination.mkdir(exist_ok=True)
    fragment_path = destination / 'early_bios_topology.analysis_fragment.bin'
    fragment_path.write_bytes(fragment)
    report = {
        'kind': 'Offline compressed-code region rebuild; not a deployable BIOS or SPI image',
        'not_a_flash_image': True,
        'fragment': str(fragment_path),
        'fragment_sha256': hashlib.sha256(fragment).hexdigest(),
        'payload_offset': hex(region),
        'mapped_code_address': '0xfff50000',
        'fragment_size': len(fragment),
        'original_packed_size': old_packed_size,
        'candidate_packed_size': len(packed),
        'expanded_size': len(modified),
        'candidate_expanded_sha256': hashlib.sha256(modified).hexdigest(),
        'changed_expanded_bytes': len(changed),
        'ffs_header_checksum_valid': True,
        'ffs_body_checksum_present': False,
        'fv_header_checksum_valid': True,
        'compression_round_trip_exact': True,
        'amd_directory_entries_unchanged': True,
        'bytes_outside_target_region_unchanged': True,
        'hypothetical_payload_sha256': hashlib.sha256(hypothetical_payload).hexdigest(),
        'vendor_update_signatures': 'Existing BIOSCER and Authenticode signatures would be invalid; no valid replacement signature was generated.',
        'live_boot_acceptance': 'Untested and unknown.',
    }
    (OUT / 'region_rebuild_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report



def main():
    if not __debug__:
        raise SystemExit('Run without -O: assertions are part of this verification')
    OUT.mkdir(exist_ok=True)
    original = OEM_PATH.read_bytes()
    cpm = CPM_PATH.read_bytes()
    assert hashlib.sha256(original).hexdigest() == OEM_SHA256
    assert hashlib.sha256(cpm).hexdigest() == CPM_SHA256
    candidate = bytearray(original)
    patches = []
    for signature, destination, source, length in [
        (b'$A17', 0x2208, 0x22D8, 0xD0),
        (b'$A26', 0x23A8, 0x3D30, 0x1984),
    ]:
        assert original[destination:destination + 4] == signature
        assert original[source:source + 4] == signature
        assert struct.unpack_from('<H', original, destination + 4)[0] == length
        assert struct.unpack_from('<H', original, source + 4)[0] == length
        candidate[destination + 16:destination + length] = original[source + 16:source + length]
        assert candidate[destination:destination + 16] == original[destination:destination + 16]
        assert candidate[source:source + length] == original[source:source + length]
        patches.append({'signature': signature.decode(), 'destination': hex(destination),
                        'source': hex(source), 'copied_body_bytes': length - 16,
                        'headers_and_platform_masks_preserved': True})
    candidate = bytes(candidate)
    assert len(candidate) == len(original)
    _, _, _, sections = pe_layout(original)
    code_rva, code_offset, code_size, _ = sections[0]
    assert original[code_offset:code_offset + code_size] == candidate[code_offset:code_offset + code_size]
    unchanged_original_tables = [(0x22D8, 0xD0), (0x3D30, 0x1984)]
    for offset, length in unchanged_original_tables:
        assert original[offset:offset + length] == candidate[offset:offset + length]

    results = []
    expected_ports = [f'00:01.{i}' for i in range(1, 6)]
    # Family17h Model11h/stepping0 is a constructed Raven-family input,
    # not a measurement of the user's replacement V1500B. Model18h/stepping1
    # matches the installed R1600. Enumerate the unknown SMU bits for both.
    for cpuid_eax in [0x00810F10, 0x00810F81]:
        for high in range(4):
            before = exercise(cpm, original, high, cpuid_eax)
            after = exercise(cpm, candidate, high, cpuid_eax)
            expected_class, expected_platform = (11, 0) if high < 2 else (12, 8)
            for result in (before, after):
                assert result['cpu_class_from_original_machine_code'] == expected_class
                assert result['platform_from_original_machine_code'] == expected_platform
            assert after['active_pcie_ports'] == expected_ports
            if high < 2:
                assert before['active_pcie_ports'] == ['00:01.1', '00:01.2']
            else:
                assert before == after
            results.append({'original': before, 'module_candidate': after})

    candidate_dir = OUT / 'candidate_module_only'
    candidate_dir.mkdir(exist_ok=True)
    candidate_path = candidate_dir / 'AmdCpmOemInitPeim.board_topology_only.efi'
    candidate_path.write_bytes(candidate)
    region_report = rebuild_code_region(original, candidate)
    report = {
        'kind': 'Offline module candidate and original-machine-code selector emulation',
        'not_a_flash_image': True,
        'original_module': str(OEM_PATH), 'original_sha256': OEM_SHA256,
        'candidate_module': str(candidate_path), 'candidate_sha256': hashlib.sha256(candidate).hexdigest(),
        'module_size': len(candidate), 'changed_byte_count': sum(a != b for a, b in zip(original, candidate)),
        'patches': patches, 'original_code_unchanged': True,
        'original_platform8_tables_unchanged': True,
        'emulated_original_routines': [hex(GET_CPU_CLASS), hex(SELECT_PLATFORM), hex(GET_TABLE)],
        'synthetic_dependencies': ['CPUID EAX=0x00810F10 or0x00810F81; replacement-chip CPUID not measured', 'SMU argument0 high bits enumerated over0,1,2,3',
                                   'PCD service getters/setters', 'CPM table registration memory'],
        'emulation_results': results,
        'compressed_region_verification': 'region_rebuild_verification.json',
        'limits': [
            'Actual V1500B SMU response and selected platform have not been measured.',
            'PCIe lane mapping/training, physical reset and clock behavior are not emulated.',
            'This does not prove the R1600 topology is electrically and algorithmically valid for V1500B.',
            'The compressed-code region was rebuilt offline and structurally checked; no valid vendor-signed package or deployable full SPI image was produced.',
            'No firmware was written to the NAS and no hardware CPU/SMU command was executed.',
        ],
    }
    (OUT / 'candidate_emulation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'cases_passed': len(results), 'changed_bytes': report['changed_byte_count'],
                      'candidate_sha256': report['candidate_sha256'],
                      'region_rebuild_verified': region_report['compression_round_trip_exact'],
                      'not_a_flash_image': True}))


if __name__ == '__main__':
    main()
