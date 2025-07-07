# Compile in GO:
## crypto_aes.go
```bash
~$ GOOS=windows GOARCH=amd64 go build -ldflags="-H=windowsgui" -o crypto_aes.bin crypto_aes.go
~$ GOOS=windows GOARCH=amd64 go build -ldflags="-H=windowsgui" -o crypto_aes.exe crypto_aes.go
```

## decrypto_aes.go
```bash
~$ GOOS=windows GOARCH=amd64 go build -o decrypto_aes.bin decrypto_aes.go
~$ GOOS=windows GOARCH=amd64 go build -o decrypto_aes.exe decrypto_aes.go
```
