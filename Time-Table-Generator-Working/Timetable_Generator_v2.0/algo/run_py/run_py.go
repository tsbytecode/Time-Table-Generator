package main

import (
	"os"
	"os/exec"
)

func main() {
	// The path to your python executable and script
	pythonExecutable := "python3"  // Use "python3" on some systems
	pythonScript := "../../app.py" // Path to your Python script

	// Create a new command
	cmd := exec.Command(pythonExecutable, pythonScript)

	// Run the command and capture its output
	// output, err := cmd.CombinedOutput()
	// if err != nil {
	// 	fmt.Printf("Error running the Python script: %v\n", err)
	// 	return
	// }
	cmd.Stdout = os.Stdout

	// Print the output of the script
	cmd.Run()
	// Example Python script (hello.py)
	/*
		print("Hello from the Python script!")
	*/
}
