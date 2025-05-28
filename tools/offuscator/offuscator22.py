#!/usr/bin/env python3
"""
Advanced PowerShell Obfuscator
Author: Senior Python Programmer with 10+ years in TI
Description: Applies multiple nested obfuscation techniques to PowerShell scripts
"""

import argparse
import random
import string
import re
from typing import List, Tuple, Optional

class PowerShellObfuscator:
    def __init__(self):
        self.var_pool = []
        self.used_names = set()
        self.technique_map = {
            'string_split': self._apply_string_splitting,
            'ascii_char': self._apply_ascii_conversion,
            'dynamic_invoke': self._apply_dynamic_invocation,
            'variable_reuse': self._apply_variable_reuse
        }

    def _generate_random_var(self, prefix: Optional[str] = None) -> str:
        """Generate a random variable name with optional prefix"""
        prefix = prefix or '$'
        while True:
            suffix = ''.join(random.choices(string.ascii_letters, k=random.randint(4, 8)))
            var_name = f"{prefix}{suffix}"
            if var_name not in self.used_names:
                self.used_names.add(var_name)
                return var_name

    def _apply_string_splitting(self, code: str) -> str:
        """Technique 1: Advanced string splitting with nested reconstruction"""
        lines = []
        for line in code.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                lines.append(line)
                continue

            # Find all strings in the line
            strings = re.findall(r'\"([^\"]*)\"', line)
            if not strings:
                lines.append(line)
                continue

            modified_line = line
            for s in strings:
                if len(s) < 2:  # Skip very short strings
                    continue

                # Create multi-level string reconstruction
                parts = [s[i:i+random.randint(1,3)] for i in range(0, len(s), random.randint(1,3))]
                parts_vars = []
                
                # First level obfuscation
                reconstruction = []
                for i, part in enumerate(parts):
                    part_var = self._generate_random_var()
                    self.var_pool.append((part_var, part))
                    parts_vars.append(part_var)
                    modified_line = f"{part_var}=\"{part}\";{modified_line}"
                
                # Second level obfuscation (nested joins)
                join_var = self._generate_random_var()
                nested_join = f"{join_var}=({'+'.join(parts_vars)});"
                modified_line = nested_join + modified_line.replace(f'"{s}"', join_var)

            lines.append(modified_line)
        return '\n'.join(lines)

    def _apply_ascii_conversion(self, code: str) -> str:
        """Technique 2: Multi-layer ASCII conversion with random encoding"""
        lines = []
        for line in code.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                lines.append(line)
                continue

            strings = re.findall(r'\"([^\"]*)\"', line)
            if not strings:
                lines.append(line)
                continue

            modified_line = line
            for s in strings:
                if len(s) < 3:  # Skip short strings
                    continue

                # Create multi-stage ASCII conversion
                ascii_vars = []
                chunk_size = random.randint(1, 3)
                chunks = [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]
                
                for chunk in chunks:
                    ascii_codes = [f"[char]{ord(c)}" for c in chunk]
                    if random.random() > 0.5:  # Randomly add math operations
                        ascii_codes = [f"({code}+{random.randint(0,9)}-{random.randint(0,9)})" for code in ascii_codes]
                    
                    chunk_var = self._generate_random_var()
                    ascii_vars.append(chunk_var)
                    modified_line = f"{chunk_var}=$(-join({','.join(ascii_codes)}));{modified_line}"
                
                # Combine all chunks
                final_var = self._generate_random_var()
                modified_line = f"{final_var}=$(-join({','.join(ascii_vars)}));{modified_line}"
                modified_line = modified_line.replace(f'"{s}"', final_var)

            lines.append(modified_line)
        return '\n'.join(lines)

    def _apply_dynamic_invocation(self, code: str) -> str:
        """Technique 3: Dynamic invocation with nested command generation"""
        lines = []
        for line in code.split('\n'):
            if not line.strip() or line.strip().startswith('#') or '=' in line:
                lines.append(line)
                continue

            # Find commands to obfuscate
            commands = re.findall(r'^\s*([a-zA-Z-]+)\s', line)
            if not commands:
                lines.append(line)
                continue

            cmd = commands[0]
            if len(cmd) < 3:  # Skip very short commands
                lines.append(line)
                continue

            # Create multi-level command generation
            cmd_var1 = self._generate_random_var()
            cmd_var2 = self._generate_random_var()
            
            # Split command into parts
            split_pos = random.randint(1, len(cmd)-1)
            cmd_part1 = cmd[:split_pos]
            cmd_part2 = cmd[split_pos:]
            
            modified_line = (
                f"{cmd_var1}=\"{cmd_part1}\";"
                f"{cmd_var2}=\"{cmd_part2}\";"
                f"{self._generate_random_var()}=$({cmd_var1}+{cmd_var2});"
                f"{line.replace(cmd, f'& {cmd_var1}{cmd_var2}', 1)}"
            )
            lines.append(modified_line)
        return '\n'.join(lines)

    def _apply_variable_reuse(self, code: str) -> str:
        """Technique 4: Advanced variable reuse with garbage insertion"""
        # Add garbage variables with random operations
        garbage_lines = []
        for _ in range(random.randint(5, 10)):
            var1 = self._generate_random_var()
            var2 = self._generate_random_var()
            garbage_value = ''.join(random.choices(
                string.ascii_letters + string.digits + ' ', 
                k=random.randint(10, 20)
            ))
            operation = random.choice([
                f"{var1}=\"{garbage_value}\";",
                f"{var1}=\"{garbage_value[:len(garbage_value)//2]}\";{var2}=\"{garbage_value[len(garbage_value)//2:]}\";{var1}+={var2};",
                f"{var1}=[string]::join('',({','.join([str(ord(c)) for c in garbage_value])}|%{{[char]$_}}));"
            ])
            garbage_lines.append(operation)

        # Insert garbage at random positions
        lines = code.split('\n')
        for i in range(len(lines)):
            if random.random() > 0.5 and lines[i].strip() and not lines[i].strip().startswith('#'):
                lines[i] = random.choice(garbage_lines) + lines[i]
                
        # Randomly reuse variables from the pool
        if self.var_pool:
            for i in range(len(lines)):
                if random.random() > 0.7 and lines[i].strip():
                    var, value = random.choice(self.var_pool)
                    lines[i] = f"{var}=\"{value}\";" + lines[i]
        
        return '\n'.join(lines)

    def _convert_to_oneliner(self, code: str) -> str:
        """Convert the script to a one-liner without using base64"""
        # Remove comments and empty lines
        lines = [line for line in code.split('\n') 
                if line.strip() and not line.strip().startswith('#')]
        
        # Join with semicolons and random whitespace
        oneliner = ''
        for line in lines:
            separator = ';' + ''.join(random.choices([' ', '\t'], k=random.randint(1, 3)))
            oneliner += line.strip() + separator
        
        # Remove trailing semicolon
        oneliner = oneliner.rstrip('; \t')
        
        # Add random whitespace
        oneliner = ''.join(
            c + ''.join(random.choices([' ', '\t'], k=random.randint(0, 2)))
            for c in oneliner
        )
        
        return f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"{oneliner}\""

    def obfuscate(self, code: str, techniques: List[str], output_format: str) -> str:
        """Apply selected obfuscation techniques with chained execution"""
        # Apply techniques in random order for better obfuscation
        random.shuffle(techniques)
        
        for technique in techniques:
            if technique in self.technique_map:
                code = self.technique_map[technique](code)
        
        if output_format == 'oneliner':
            return self._convert_to_oneliner(code)
        return code

def parse_arguments():
    """Parse command line arguments with detailed help"""
    parser = argparse.ArgumentParser(
        description="Advanced PowerShell Script Obfuscator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input', 
        required=True,
        help='Path to the input PowerShell script file (.ps1)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to save the obfuscated output'
    )
    
    parser.add_argument(
        '-t', '--techniques',
        nargs='+',
        choices=['string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse', 'all'],
        default=['all'],
        help="""Obfuscation techniques to apply (choose one or more):
  string_split    : String splitting & index obfuscation
  ascii_char      : ASCII-to-char conversion with random encoding
  dynamic_invoke  : Dynamic Invocation with command fragmentation
  variable_reuse   : Advanced variable reuse with garbage insertion
  all             : All techniques combined in random order"""
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['script', 'oneliner'],
        default='script',
        help="""Output format:
  script    : Regular PowerShell script file
  oneliner  : One-line PowerShell command (without base64)"""
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Handle 'all' option
    if 'all' in args.techniques:
        args.techniques = ['string_split', 'ascii_char', 'dynamic_invoke', 'variable_reuse']
    
    try:
        # Read input file
        with open(args.input, 'r', encoding='utf-8') as f:
            ps_code = f.read()
        
        # Obfuscate the code
        obfuscator = PowerShellObfuscator()
        obfuscated_code = obfuscator.obfuscate(ps_code, args.techniques, args.format)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)
        
        print(f"[+] Successfully obfuscated script saved to: {args.output}")
        if args.format == 'oneliner':
            print("[+] One-liner command generated without base64 encoding")
        
    except Exception as e:
        print(f"[-] Error during obfuscation: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()