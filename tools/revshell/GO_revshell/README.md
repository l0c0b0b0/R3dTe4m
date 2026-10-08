# Compile in GO:
## reev.go

Change the IP address and PORT on line: 18

```bash
~$ GOOS=windows GOARCH=amd64 go build -o reev.exe reev.go
~$ GOOS=windows GOARCH=amd64 go build -ldflags="-H=windowsgui" -o reev.exe reev.go
```
