package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/sha256"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"syscall"
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

const(
	fileExtension = ".enc"
	dir = "C:\\Users\\win11\\Desktop\\ransomware"
	pass = "qwerty1234"
)

// Derive AES-256 key from passphrase
func deriveKey(passphrase string) []byte {
	hash := sha256.Sum256([]byte(passphrase))
	return hash[:]
}

// PKCS7 unpadding
func pkcs7Unpad(data []byte) ([]byte, error) {
	if len(data) == 0 {
		return nil, fmt.Errorf("empty data for unpadding")
	}
	padLen := int(data[len(data)-1])
	if padLen > aes.BlockSize || padLen == 0 {
		return nil, fmt.Errorf("invalid padding")
	}
	return data[:len(data)-padLen], nil
}

// AES-256-CBC file decryption
func decryptFile(encPath string, key []byte) error {
	inputFile, err := os.Open(encPath)
	if err != nil {
		return err
	}
	defer inputFile.Close()

	// Read IV from the beginning
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(inputFile, iv); err != nil {
		return err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}

	mode := cipher.NewCBCDecrypter(block, iv)

	outputPath := strings.TrimSuffix(encPath, fileExtension)
	outputFile, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	buf := make([]byte, aes.BlockSize)
	var prevDecrypted []byte

	for {
		n, err := io.ReadFull(inputFile, buf)
		if err == io.EOF {
			break
		}
		if err != nil && err != io.ErrUnexpectedEOF {
			return err
		}

		if n != aes.BlockSize {
			return fmt.Errorf("corrupt file: incomplete block")
		}

		decrypted := make([]byte, aes.BlockSize)
		mode.CryptBlocks(decrypted, buf)

		// If it's the last block
		_, peekErr := inputFile.Read(make([]byte, 1))
		if peekErr == io.EOF {
			unpadded, err := pkcs7Unpad(decrypted)
			if err != nil {
				return err
			}
			_, err = outputFile.Write(unpadded)
			if err != nil {
				return err
			}
			break
		} else {
			// Not last block, write previous
			if prevDecrypted != nil {
				if _, err := outputFile.Write(prevDecrypted); err != nil {
					return err
				}
			}
			prevDecrypted = decrypted
			// Reset file cursor back one byte (since we peeked)
			inputFile.Seek(-1, io.SeekCurrent)
		}
	}

	fmt.Printf("Decrypted: %s -> %s\n", encPath, outputPath)

	// Delete the encrypted file
	if err := os.Remove(encPath); err != nil {
		log.Printf("Failed to delete encrypted file %s: %v", encPath, err)
	} else {
		log.Printf("Deleted encrypted file: %s", encPath)
	}

	return nil
}

// Recursively decrypt all .enc files
func processDecryption(root string, key []byte) error {
	return filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}
		if !strings.HasSuffix(path, fileExtension) {
			return nil
		}

		if err := decryptFile(path, key); err != nil {
			log.Printf("Decryption failed for %s: %v", path, err)
			return nil // continue processing other files
		}

		// Extra check: make sure decrypted file was created
		originalPath := strings.TrimSuffix(path, fileExtension)
		if _, err := os.Stat(originalPath); err == nil {
			// Decrypted file exists → safe to delete .enc
			if err := os.Remove(path); err != nil {
				log.Printf("Failed to delete encrypted file %s: %v", path, err)
			} else {
				log.Printf("Deleted encrypted file: %s", path)
			}
		} else {
			log.Printf("Decrypted file not found for %s → .enc not deleted", path)
		}

		return nil
	})
}

func main() {
	//if len(os.Args) != 3 {
	//	fmt.Println("Usage: decryptor <directory> <passphrase>")
	//	return
	//}

	//dir := os.Args[1]
	//pass := os.Args[2]
	//if len(pass) < 8 {
	//	fmt.Println("Passphrase must be at least 8 characters")
	//	return
	//}

	key := deriveKey(pass)

	err := processDecryption(dir, key)
	if err != nil {
		log.Fatalf("Failed to decrypt directory: %v", err)
	}
}