package main

import (
	"algorithm/algo"
	"fmt"
)

func main() {

	d, err := algo.NewDBconn(false, "example.db")
	if err != nil {
		panic(err)
	}

	fmt.Println(d.GenerateClass("11A"))
	fmt.Println(d.GenerateClass("12B"))
	fmt.Println(d.GenerateClass("12A"))
	fmt.Println(d.GenerateClass("11B"))

}

// package main

// import (
// 	"algorithm/algo"
// 	"encoding/json"
// 	"fmt"
// 	"log"
// 	"net/http"
// 	"os"
// )

// // The AssignmentRequest struct is used to decode the JSON request body.
// // It uses exported fields and JSON tags so that it can be handled by the
// // `encoding/json` package. This is necessary because the `algo.Assignment`
// // struct has an unexported field (`periodsused`), which cannot be accessed
// // by the JSON decoder.
// type AssignmentRequest struct {
// 	TeacherID     string `json:"teacher_id"`
// 	ClassID       string `json:"class_id"`
// 	Periodsneeded int    `json:"periods_needed"`
// }

// // The OutputTimetableRequest struct is used for the new CSV output API.
// type OutputTimetableRequest struct {
// 	ClassID  string `json:"class_id"`
// 	Filename string `json:"filename"`
// }

// // The ResponseMessage struct is a standard way to send a JSON response
// // back to the client.
// type ResponseMessage struct {
// 	Status  string `json:"status"`
// 	Message string `json:"message,omitempty"`
// }

// var dbConn *algo.DBconn

// // newAssignmentHandler handles POST requests to create a new assignment.
// // It decodes the JSON request, creates an `algo.Assignment` instance,
// // and calls the appropriate method on the `algo.DBconn` object.
// func newAssignmentHandler(w http.ResponseWriter, r *http.Request) {
// 	fmt.Println(r)
// 	if r.Method != "POST" {
// 		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
// 		return
// 	}

// 	var req AssignmentRequest
// 	err := json.NewDecoder(r.Body).Decode(&req)
// 	if err != nil {
// 		http.Error(w, err.Error(), http.StatusBadRequest)
// 		fmt.Println(err)
// 		return
// 	}

// 	// Validate required fields
// 	if req.TeacherID == "" || req.ClassID == "" || req.Periodsneeded <= 0 {
// 		http.Error(w, "Missing required fields: teacher_id, class_id, periods_needed must be provided and periods_needed > 0", http.StatusBadRequest)
// 		return
// 	}

// 	// Create an algo.Assignment object from the request data.
// 	newAssignment := algo.Assignment{
// 		TeacherID:     req.TeacherID,
// 		ClassID:       req.ClassID,
// 		Periodsneeded: req.Periodsneeded,
// 	}

// 	fmt.Println(newAssignment)

// 	err = newAssignment.NewAssignments(dbConn)
// 	if err != nil {
// 		http.Error(w, fmt.Sprintf("Error creating assignment: %v", err), http.StatusInternalServerError)
// 		return
// 	}

// 	w.Header().Set("Content-Type", "application/json")
// 	json.NewEncoder(w).Encode(ResponseMessage{Status: "success", Message: "Assignment created successfully"})
// }

// // generateClassHandler handles POST requests to generate a class timetable.
// // It decodes the JSON request and calls the `GenerateClass` method from
// // the `algo` package.
// func generateClassHandler(w http.ResponseWriter, r *http.Request) {
// 	if r.Method != "POST" {
// 		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
// 		return
// 	}

// 	var req struct {
// 		ClassID string `json:"class_id"`
// 	}

// 	err := json.NewDecoder(r.Body).Decode(&req)
// 	if err != nil {
// 		http.Error(w, err.Error(), http.StatusBadRequest)
// 		return
// 	}

// 	if req.ClassID == "" {
// 		http.Error(w, "Missing required field: class_id", http.StatusBadRequest)
// 		return
// 	}

// 	success := dbConn.GenerateClass(req.ClassID)

// 	w.Header().Set("Content-Type", "application/json")
// 	if success {
// 		json.NewEncoder(w).Encode(ResponseMessage{Status: "success", Message: "Timetable generated successfully"})
// 	} else {
// 		json.NewEncoder(w).Encode(ResponseMessage{Status: "failure", Message: "Could not generate timetable for the given class and assignments"})
// 	}
// }

// // outputTimetableHandler handles POST requests to output a timetable to a CSV file.
// func outputTimetableHandler(w http.ResponseWriter, r *http.Request) {
// 	if r.Method != "POST" {
// 		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
// 		return
// 	}

// 	var req OutputTimetableRequest
// 	err := json.NewDecoder(r.Body).Decode(&req)
// 	if err != nil {
// 		http.Error(w, err.Error(), http.StatusBadRequest)
// 		return
// 	}

// 	if req.ClassID == "" || req.Filename == "" {
// 		http.Error(w, "Missing required fields: class_id, filename", http.StatusBadRequest)
// 		return
// 	}

// 	err = dbConn.OutputClassTimetableCSV(req.ClassID, req.Filename)
// 	if err != nil {
// 		http.Error(w, fmt.Sprintf("Error generating CSV file: %v", err), http.StatusInternalServerError)
// 		return
// 	}

// 	w.Header().Set("Content-Type", "application/json")
// 	json.NewEncoder(w).Encode(ResponseMessage{Status: "success", Message: "Timetable successfully written to " + req.Filename})
// }

// func main() {
// 	var err error
// 	dbConn, err = algo.NewDBconn(false, "x.db")
// 	if err != nil {
// 		log.Fatalf("Could not initialize database: %v", err)
// 		os.Exit(1)
// 	}
// 	defer dbConn.Close()

// 	http.HandleFunc("/assignments", newAssignmentHandler)
// 	http.HandleFunc("/generate-class", generateClassHandler)
// 	http.HandleFunc("/output-csv", outputTimetableHandler) // New endpoint

// 	port := "8080"
// 	fmt.Printf("Server starting on port %s...\n", port)
// 	log.Fatal(http.ListenAndServe(":"+port, nil))
// }
