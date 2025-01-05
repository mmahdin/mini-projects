import struct
import zlib

EEPROM_DEFAULT_HEADER = struct.Struct("!I I")


def read_eeprom(
        nvmem_path,
        offset,
        eeprom_header_format,
        eeprom_header_keys,
        expected_magic,
        max_size=None
):
    """
    Read the EEPROM located at nvmem_path and return a tuple (header, data)
    Header is already parsed in the common header fields
    Data contains the full eeprom data structure

    nvmem_path -- Path to readable file (typically something in sysfs)
    eeprom_header_format -- List of header formats, by version
    eeprom_header_keys -- List of keys for the entries in the EEPROM
    expected_magic -- The magic value that is expected
    max_size -- Max number of bytes to be read. If omitted, will read the full file.
    """
    assert len(eeprom_header_format) == len(eeprom_header_keys)

    def _parse_eeprom_data(
        data,
        version,
    ):
        """
        Parses the raw 'data' according to the version.
        This also parses the CRC and assumes CRC is the last 4 bytes of each data.
        Returns a dictionary.
        """
        eeprom_parser = struct.Struct(eeprom_header_format[version])
        eeprom_keys = eeprom_header_keys[version]
        parsed_data = eeprom_parser.unpack_from(data)
        read_crc = parsed_data[-1]
        rawdata_without_crc = data[:eeprom_parser.size-4]
        expected_crc = zlib.crc32(rawdata_without_crc) & 0xffffffff
        if read_crc != expected_crc:
            raise RuntimeError(
                "Received incorrect CRC."
                "Read: {:08X} Expected: {:08X}".format(
                    read_crc, expected_crc))
        return dict(list(zip(eeprom_keys, parsed_data)))
    # Dawaj, dawaj
    max_size = max_size or -1
    with open(nvmem_path, "rb") as nvmem_file:
        data = nvmem_file.read(max_size)[offset:]
    eeprom_magic, eeprom_version = EEPROM_DEFAULT_HEADER.unpack_from(data)
    if eeprom_magic != expected_magic:
        raise RuntimeError(
            "Received incorrect EEPROM magic. "
            "Read: {:08X} Expected: {:08X}".format(
                eeprom_magic, expected_magic))
    if eeprom_version >= len(eeprom_header_format):
        raise RuntimeError(
            "Unexpected EEPROM version: `{}'".format(eeprom_version))
    return (_parse_eeprom_data(data, eeprom_version), data)
