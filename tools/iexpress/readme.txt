Reference: https://www.youtube.com/watch?v=mAond4BkCfM&t=611s

# Commands:
cmd> iexpress.exe /n winrar.SED
cmd> iexpress

GUI:
[1] Welcome to IExpress 2.0
	- Create new Self Extraction Directive File
	<NEXT>

[2] Package purpose
	- Extract files and run an installation command
	<NEXT>

[3] Package title
	- Name of the output packaet: PDFReader

[4] Confirmation prompt
	- Prompt user with:
		# Its possible to change to any message, context with phishing.
		Installing Adobe Reader, please wait a few minutes.
		<NEXT>

[5] License agreement
	- Do not display a lincense.
	<NEXT>
[6] Packaged files
	# After we can change the exe program, in SED file.
	- Choose the executable file: C:\Windows\System32\calcs.exe
	<NEXT>
[7] Install Program to Launch
	- calcs.exe
	- Post Install Command: <None>
	<NEXT>
[8] Show window
	- Hidden
	<NEXT>

[9] Finished message
	- Display message
	The installation was completed.

[10] Pacakge Name and Options
	# The directory where it will be save the new EXE file.
	- Browse: C:\Users\win11\Desktop\calcs.exe
	- Options: Hide File Extracting Progress Animation from User
	<NEXT>

[11] Configure restart
	- No restart
	<NEXT>

[12] Save self Extraction
	- Save self extraction file:
	C:\users\win11\Donwloads\calcs.SED

[13] The file as template is located in ./tools/iexpress/PDFReader.SED
