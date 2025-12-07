package main

import (
	"algorithm/algo"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

// AssignmentRequest defines the structure for incoming JSON requests to create a new assignment.
// It includes the teacher's ID, the class's ID, the subject, and the number of periods required.
type AssignmentRequest struct {
	TeacherID     string `json:"teacher_id"`
	ClassID       string `json:"class_id"`
	Subject       string `json:"subject"`
	Periodsneeded int    `json:"periods_needed"`
}

// ResponseMessage defines a standard JSON response structure.
// It provides feedback to the client on the status of their request.
type ResponseMessage struct {
	Status  string `json:"status"`
	Message string `json:"message,omitempty"`
}

var dbConn *algo.DBconn

// newAssignmentHandler handles HTTP POST requests to create a new assignment.
// It decodes the JSON request body into an AssignmentRequest struct, validates the input,
// and then creates a new assignment in the database.
//
// Parameters:
//   w: http.ResponseWriter to write the HTTP response.
//   r: *http.Request representing the incoming HTTP request.
func newAssignmentHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(r)
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AssignmentRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		fmt.Println(err)
		return
	}

	// Validate required fields
	if req.TeacherID == "" || req.ClassID == "" || req.Periodsneeded <= 0 {
		http.Error(w, "Missing required fields: teacher_id, class_id, periods_needed must be provided and periods_needed > 0", http.StatusBadRequest)
		return
	}

	// Create an algo.Assignment object from the request data.
	newAssignment := algo.Assignment{
		TeacherID:     req.TeacherID,
		ClassID:       req.ClassID,
		Periodsneeded: req.Periodsneeded,
		Subject:       req.Subject,
	}

	fmt.Println(newAssignment)

	err = newAssignment.NewAssignments(dbConn)
	if err != nil {
		fmt.Print(err)
		http.Error(w, fmt.Sprintf("Error creating assignment: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(ResponseMessage{Status: "success", Message: "Assignment created successfully"})
}

// generateClassHandler handles HTTP POST requests to generate a class timetable.
// It decodes a JSON request containing a class ID and calls the GenerateClass method
// to create the timetable.
//
// Parameters:
//   w: http.ResponseWriter to write the HTTP response.
//   r: *http.Request representing the incoming HTTP request.
func generateClassHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		ClassID string `json:"class_id"`
	}

	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if req.ClassID == "" {
		http.Error(w, "Missing required field: class_id", http.StatusBadRequest)
		return
	}

	success := dbConn.GenerateClass(req.ClassID)

	w.Header().Set("Content-Type", "application/json")
	if success {
		json.NewEncoder(w).Encode(ResponseMessage{Status: "success", Message: "Timetable generated successfully"})
	} else {
		json.NewEncoder(w).Encode(ResponseMessage{Status: "failure", Message: "Could not generate timetable for the given class and assignments"})
	}
}

// main is the entry point of the application.
// It initializes the database connection, sets up the HTTP handlers,
// and starts the web server.
func main() {
	var err error
	dbConn, err = algo.NewDBconn(false, "x.db")
	if err != nil {
		log.Fatalf("Could not initialize database: %v", err)
		os.Exit(1)
	}
	defer dbConn.Close()

	http.HandleFunc("/assignments", newAssignmentHandler)
	http.HandleFunc("/generate-class", generateClassHandler)
	//	http.HandleFunc("/output-csv", outputTimetableHandler) // New endpoint

	port := "8080"
	fmt.Printf("Server starting on port %s...\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
