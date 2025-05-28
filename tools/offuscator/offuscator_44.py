import argparse
import random
import string
import sys
import re
from pathlib import Path


def encode_string_as_char_array(text: str) -> str:
    """Encode a string as a PowerShell expression using ASCII values."""
    ascii_values = ",".join(str(ord(c)) for c in text)
    return (
        f"([string]::join('', (({ascii_values}) |%{{;$_;}} |"
        f"%{{ ([char][int] $_)}})))"
    )


def create_indexed_reconstruction(command: str) -> str:
    """Reconstruct a string using indexes in a shuffled character pool."""
    base = ''.join(random.choices(string.ascii_letters + string.digits + "-.:/\\", k=64))
    indices = []

    for char in command:
        if char not in base:
            base += char
        indices.append(base.index(char))

    index_expr = ",".join(map(str, indices))
    return f'("{base}"[{index_expr}] -join "")'


def obfuscate_string_literals(line: str) -> str:
    """Find all quoted strings and obfuscate them."""
    def replacer(match):
        content = match.group(1)
        return encode_string_as_char_array(content)
    return re.sub(r'"([^"]+)"', replacer, line)


def obfuscate_command_keywords(line: str) -> str:
    """Obfuscate command keywords like Start-BitsTransfer using indexed reconstruction."""
    powershell_cmds = [
        "Start-BitsTransfer",
        "Invoke-WebRequest",
        "New-Object",
        "System.Net.WebClient"
    ]

    for cmd in powershell_cmds:
        if cmd in line:
            indexed = create_indexed_reconstruction(cmd)
            line = line.replace(cmd, f"& {indexed}")

    return line


def obfuscate_env_variables(line: str) -> str:
    """Encode paths like $env:temp\file.exe"""
    matches = re.findall(r"\$env:[\w\\\/\.\-]+", line)
    for m in matches:
        encoded = encode_string_as_char_array(m)
        line = line.replace(m, encoded)
    return line


def obfuscate_script_line(line: str) -> str:
    """Orchestrate the obfuscation of a single line."""
    line = obfuscate_command_keywords(line)
    line = obfuscate_string_literals(line)
    line = obfuscate_env_variables(line)
    return line


def obfuscate_script(input_path: Path) -> str:
    """Obfuscate an entire PowerShell script."""
    try:
        with input_path.open("r", encoding="utf-8") as file:
            lines = file.readlines()

        obfuscated_lines = [
            obfuscate_script_line(line.strip()) for line in lines if line.strip()
        ]
        return "\n".join(obfuscated_lines)

    except Exception as e:
        print(f"[!] Error reading or obfuscating file: {e}", file=sys.stderr)
        sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="PowerShell Obfuscator - Encodes PowerShell payloads including URLs, commands, and variables."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input PowerShell .ps1 file"
    )
    parser.add_argument(
        "-o", "--output", help="Path to save obfuscated output (optional)"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    input_path = Path(args.input)

    if not input_path.exists() or not input_path.is_file():
        print(f"[!] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = obfuscate_script(input_path)

    if args.output:
        output_path = Path(args.output)
        try:
            output_path.write_text(result, encoding="utf-8")
            print(f"[+] Obfuscated script saved to {output_path}")
        except Exception as e:
            print(f"[!] Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result)


if __name__ == "__main__":
    main()
