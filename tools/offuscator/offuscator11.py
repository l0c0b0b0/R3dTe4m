import argparse
import base64
import os
import random
import string
import textwrap


def read_ps1_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


def split_and_obfuscate_string(content):
    """
    Breaks PowerShell commands into chunks and obfuscates using ASCII conversion and index-based string access.
    """
    obfuscated_lines = []
    reused_vars = ['a', 'b', 'c', 'x', 'y', 'z']
    var_index = 0

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        chars = [f"[char]{ord(c)}" for c in line]
        joined = '+'.join(chars)
        var_name = reused_vars[var_index % len(reused_vars)]
        obfuscated_line = f"${var_name} = {joined}; &${var_name}"
        obfuscated_lines.append(obfuscated_line)
        var_index += 1

    return '\n'.join(obfuscated_lines)


def write_output(output_path, content):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_one_liner(obfuscated_script):
    """
    Encodes the obfuscated PowerShell into base64 and returns a one-liner
    suitable for command line execution.
    """
    command = obfuscated_script.encode('utf-16le')
    encoded = base64.b64encode(command).decode('utf-8')
    return f"powershell -encodedCommand {encoded}"


def get_random_filename(base_name):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_name}_obf_{suffix}.ps1"


def main():
    parser = argparse.ArgumentParser(
        description='Obfuscate a PowerShell script using nested techniques.'
    )
    parser.add_argument(
        'input', type=str, help='Input .ps1 file path'
    )
    parser.add_argument(
        '-o', '--output', type=str, help='Output obfuscated .ps1 file (optional)'
    )
    parser.add_argument(
        '--one-liner', action='store_true', help='Print one-liner base64 encoded command'
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        return

    original_script = read_ps1_file(args.input)
    obfuscated_script = split_and_obfuscate_string(original_script)

    output_path = args.output or get_random_filename(os.path.splitext(os.path.basename(args.input))[0])
    write_output(output_path, obfuscated_script)

    print(f"[+] Obfuscated script written to: {output_path}")

    if args.one_liner:
        one_liner = generate_one_liner(obfuscated_script)
        print(f"\n[+] One-liner Base64 Command:\n{one_liner}")


if __name__ == '__main__':
    main()
