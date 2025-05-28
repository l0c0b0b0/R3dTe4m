import argparse
import random
import string
import base64
import re

def split_string(s):
    """Split a string into random-length segments."""
    segments = []
    while s:
        length = random.randint(1, len(s))
        segments.append(s[:length])
        s = s[length:]
    return segments

def ascii_to_char(s):
    """Convert a string to ASCII character codes."""
    return ''.join(f'[{ord(c)}]' for c in s)

def dynamic_invocation(cmd):
    """Wrap a command in dynamic invocation."""
    return f'& ({cmd})'

def obfuscate_line(line):
    """Apply obfuscation techniques to a single line."""
    line = re.sub(r'([a-zA-Z]+)', lambda m: ''.join(random.sample(m.group(0), len(m.group(0)))), line)
    line = re.sub(r'(["\'])', lambda m: f'`{m.group(0)}`', line)
    return line

def obfuscate_script(script):
    """Obfuscate the entire script."""
    lines = script.splitlines()
    obfuscated_lines = []
    for line in lines:
        line = obfuscate_line(line)
        line = dynamic_invocation(line)
        obfuscated_lines.append(line)
    return '\n'.join(obfuscated_lines)

def encode_script(script):
    """Encode the script to Base64."""
    encoded_bytes = base64.b64encode(script.encode('utf-16le'))
    return encoded_bytes.decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description='Obfuscate a PowerShell script.')
    parser.add_argument('input_file', help='Path to the input PowerShell script (.ps1)')
    parser.add_argument('output_file', help='Path to save the obfuscated PowerShell script')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as f:
        script = f.read()

    obfuscated_script = obfuscate_script(script)
    encoded_script = encode_script(script)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(obfuscated_script)

    print(f'Obfuscated script saved to {args.output_file}')
    print(f'Encoded script: {encoded_script}')

if __name__ == '__main__':
    main()

