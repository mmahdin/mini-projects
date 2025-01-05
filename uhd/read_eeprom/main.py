import os
import struct
import zlib
import tempfile
from eeprom import *

# Mock EEPROM data for version 3
mock_eeprom_data_version_3 = {
    "magic": 0xABCD1234,                           # I
    "eeprom_version": 3,                          # I
    "mcu_flags": b'\x00\x00\x00\x00' * 4,         # 16s
    "pid": 0x1234,                                # H
    "rev": 0x0001,                                # H
    "serial": b"SER1234",                         # 7s
    "mac_eth0": b'\x01\x02\x03\x04\x05\x06',      # 6s
    "dt_compat": 0x1122,                          # H
    "mac_eth1": b'\x07\x08\x09\x0A\x0B\x0C',      # 6s
    "ec_compat": 0x3344,                          # H
    "mac_eth2": b'\x0D\x0E\x0F\x10\x11\x12',      # 6s
    "rev_compat": 0x5566,                         # H
}

# Create a mock EEPROM binary structure
eeprom_header_format_v3 = "!I I 16s  H H 7s 1x 6s H 6s H 6s H"  # Format for version 3

# Pack the data into binary format
eeprom_struct = struct.Struct(eeprom_header_format_v3)
data_without_crc = eeprom_struct.pack(
    mock_eeprom_data_version_3['magic'],         # I
    mock_eeprom_data_version_3['eeprom_version'],  # I
    mock_eeprom_data_version_3['mcu_flags'],     # 16s
    mock_eeprom_data_version_3['pid'],           # H
    mock_eeprom_data_version_3['rev'],           # H
    mock_eeprom_data_version_3['serial'],        # 7s
    mock_eeprom_data_version_3['mac_eth0'],      # 6s
    mock_eeprom_data_version_3['dt_compat'],     # H
    mock_eeprom_data_version_3['mac_eth1'],      # 6s
    mock_eeprom_data_version_3['ec_compat'],     # H
    mock_eeprom_data_version_3['mac_eth2'],      # 6s
    mock_eeprom_data_version_3['rev_compat']     # H
)

# Calculate CRC and append
crc = zlib.crc32(data_without_crc) & 0xffffffff
eeprom_data = data_without_crc + struct.pack("!I", crc)

# Write to a temporary file
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    temp_file.write(eeprom_data)
    eeprom_file_path = temp_file.name


def test_read_eeprom():
    eeprom_header_format = (
        None,  # For laziness, we start at version 1 and thus index 0 stays empty
        # Version 1
        "!I I 16s  H H 7s 1x 24s I",
        # Version 2 (Ignore the extra fields, it doesn't matter to MPM)
        "!I I 16s  H H 7s 1x 6s H 6s H 6s 2x I",
        # Version 3 (Ignore the extra fields, it doesn't matter to MPM)
        "!I I 16s  H H 7s 1x 6s H 6s H 6s H I",
    )
    eeprom_header_keys = (
        None,  # For laziness, we start at version 1 and thus index 0 stays empty
        ('magic', 'eeprom_version', 'mcu_flags', 'pid', 'rev',
         'serial', 'mac_addresses', 'CRC'),  # Version 1
        ('magic', 'eeprom_version', 'mcu_flags', 'pid', 'rev', 'serial', 'mac_eth0', 'dt_compat', 'mac_eth1',
         # Version 2 (Ignore the extra fields, it doesn't matter to MPM)
         'ec_compat', 'mac_eth2', 'CRC'),
        ('magic', 'eeprom_version', 'mcu_flags', 'pid', 'rev', 'serial', 'mac_eth0',
         'dt_compat', 'mac_eth1', 'ec_compat', 'mac_eth2', 'rev_compat', 'CRC'),  # Version 3
    )
    expected_magic = 0xABCD1234

    parsed_data, raw_data = read_eeprom(
        eeprom_file_path,
        offset=0,
        eeprom_header_format=eeprom_header_format,
        eeprom_header_keys=eeprom_header_keys,
        expected_magic=expected_magic,
    )
    print("Parsed Data:", parsed_data)


# Test the function
test_read_eeprom()

# Cleanup temporary file
os.remove(eeprom_file_path)
