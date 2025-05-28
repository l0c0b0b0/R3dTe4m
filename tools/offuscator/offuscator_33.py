#!/usr/bin/env python3
"""
Fixed PowerShell Obfuscator
Author: Security Engineer
Description: Generates properly formatted obfuscated PowerShell code
"""

import argparse
import random
import string
import re
import os
from typing import List, Tuple

class PowerShellObfuscator:
    def __init__(self):
        self.used_vars = set()
        self.string_pool = []
        
    def _random_var(self) -> str:
        """Generate valid PowerShell variable name"""
        while True:
            var = '$' + ''.join(random.choices(string.ascii_letters, k=random.randint(6,10)))
            if var not in self.used_vars:
                self.used_vars.add(var)
                return var

    def _string_index_obfuscation(self, s: str) -> str:
        """Generate valid string index syntax"""
        if len(s) < 3:
            return f'"{s}"'
            
        # Create random string with embedded target
        chars = list(string.ascii_letters + string.digits + '-_')
        random.shuffle(chars)
        padding = ''.join(chars[:random.randint(30,60)])
        
        # Insert target at random position
        insert_pos = random.randint(10, len(padding)-10)
        mixed_str = padding[:insert_pos] + s + padding[insert_pos:]
        
        # Generate correct indices
        indices = list(range(insert_pos, insert_pos + len(s)))
        # Add some decoys
        for _ in range(random.randint(2,5)):
            indices.append(random.randint(0, len(mixed_str)-1))
        random.shuffle(indices)
        
        # Store for potential reuse
        var_name = self._random_var()
        self.string_pool.append((var_name, mixed_str))
        
        return f"(('{mixed_str}')[{','.join(map(str, indices))}] -join '')"

    def _ascii_obfuscation(self, s: str) -> str:
        """Generate valid ASCII conversion syntax"""
        if len(s) < 3:
            return f'"{s}"'
            
        parts = []
        for c in s:
            code = ord(c)
            if random.random() > 0.5:  # 50% chance to add math obfuscation
                delta = random.randint(1,5)
                op = random.choice(['+','-'])
                parts.append(f"[char]({code}{op}{delta})")
            else:
                parts.append(f"[char]{code}")
        
        return f"(-join({','.join(parts)}))"

    def _obfuscate_command(self, cmd: str) -> str:
        """Obfuscate command names safely"""
        if random.random() > 0.5:
            return self._string_index_obfuscation(cmd)
        else:
            return self._ascii_obfuscation(cmd)

    def _add_garbage(self) -> str:
        """Generate valid PowerShell garbage code"""
        patterns = [
            lambda: f"{self._random_var()}=$null",
            lambda: f"{self._random_var()}=\"{''.join(random.choices(string.ascii_letters, k=8))}\"",
            lambda: f"{self._random_var()}={random.randint(1,100)}"
        ]
        return random.choice(patterns)()

    def obfuscate_file(self, input_file: str, output_file: str):
        """Process file with proper syntax handling"""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        output = []
        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                output.append(line)
                continue
                
            # Obfuscate strings
            line = re.sub(r'"([^"]*)"', 
                         lambda m: self._string_index_obfuscation(m.group(1)) if random.random() > 0.3 
                                  else self._ascii_obfuscation(m.group(1)),
                         line)
            
            # Obfuscate commands (but not method calls)
            line = re.sub(r'\b([A-Za-z-]{3,})\b(?![\'"\.\(])',
                         lambda m: f"& {self._obfuscate_command(m.group(1))}" if random.random() > 0.5 
                                  else m.group(0),
                         line)
            
            # Add garbage
            if random.random() > 0.7:
                line = f"{self._add_garbage()};{line}"
            
            output.append(line)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(output)

def main():
    parser = argparse.ArgumentParser(description="PowerShell Obfuscator")
    parser.add_argument('-i', '--input', required=True, help='Input PS1 file')
    parser.add_argument('-o', '--output', required=True, help='Output file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        exit(1)
        
    try:
        obfuscator = PowerShellObfuscator()
        obfuscator.obfuscate_file(args.input, args.output)
        print(f"Successfully obfuscated file saved to: {args.output}")
    except Exception as e:
        print(f"Error during obfuscation: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()