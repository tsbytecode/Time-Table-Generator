package main

import "fmt"

func generateTimetable() map[string]map[string]string {
        classes := []string{"a1", "a2", "a3"}
        teachers := map[string]string{
                "x1": "Physics",
                "x2": "Chemistry",
                "x3": "Math",
                "x4": "Math", // Added x4
        }
        days := []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}

        classRequirements := map[string]map[string]int{
                "a1": {"Physics": 2, "Chemistry": 2, "Math": 2},
                "a2": {"Physics": 2, "Chemistry": 2, "Math": 2},
                "a3": {"Physics": 1, "Chemistry": 2, "Math": 3},
        }

        classCounts := map[string]map[string]int{
                "a1": {"Physics": 0, "Chemistry": 0, "Math": 0},
                "a2": {"Physics": 0, "Chemistry": 0, "Math": 0},
                "a3": {"Physics": 0, "Chemistry": 0, "Math": 0},
        }

        timetable := make(map[string]map[string]string)
        for _, day := range days {
                timetable[day] = make(map[string]string)
        }

        teacherAvailability := make(map[string]map[string]bool)
        for _, teacher := range teachers {
                teacherAvailability[teacher] = make(map[string]bool)
                for _, day := range days {
                        teacherAvailability[teacher][day] = true // Initially, all teachers are available
                }
        }

        for _, day := range days {
                for _, class := range classes {
                        assigned := false
                        for teacher, subject := range teachers {
                                if classCounts[class][subject] < classRequirements[class][subject] && teacherAvailability[teacher][day] {
                                        timetable[day][class] = teacher
                                        classCounts[class][subject]++
                                        teacherAvailability[teacher][day] = false // Teacher is now unavailable
                                        assigned = true
                                        break
                                }
                        }
                        if !assigned {
                                fmt.Println("could not assign all classes")
                                return timetable
                        }
                }
                //reset teacher availability for the next day.
                for teacher := range teachers {
                        teacherAvailability[teacher][day] = true
                }
        }

        return timetable
}

func main() {
        timetable := generateTimetable()

        days := []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
        classes := []string{"a1", "a2", "a3"}

        for _, day := range days {
                fmt.Printf("%s:\n", day)
                for _, class := range classes {
                        fmt.Printf("  %s: %s\n", class, timetable[day][class])
                }
        }
}
