package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
)

var wg sync.WaitGroup

const maxConcurrentGoroutines = 50 

var sem = make(chan struct{}, maxConcurrentGoroutines)

func trimWav(inputFile string) error {
	// please add logic here to trim file using ffmpeg
	return nil
}

func walkDirectory(dir string) error {
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() && (strings.HasSuffix(path, ".wav")) {
			fmt.Printf("Trimming %s to .wav...\n", path)
			wg.Add(1)

			sem <- struct{}{}

			go func() {
				defer func() {
					wg.Done()
					<-sem
				}() 
				if err := convertToWav(path); err != nil {
					log.Println(err)
				}
			}()
		}
		return nil
	})
	return err
}

func main() {
	// Check if ffmpeg is installed
	_, err := exec.LookPath("ffmpeg")
	if err != nil {
		fmt.Println("ffmpeg is not installed. Please install ffmpeg first.")
		os.Exit(1)
	}

	// Get the directory to start from (default is the current directory)
	dir := "."
	if len(os.Args) > 1 {
		dir = os.Args[1]
	}

	// Walk through the directory and process files
	err = walkDirectory(dir)
	if err != nil {
		log.Println(err)
	}

	// Wait for all goroutines to finish
	wg.Wait()
}