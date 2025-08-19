package algo

import (
	"database/sql"
	"encoding/csv"
	"os"

	_ "github.com/glebarez/go-sqlite"
)

// class = {grade int , section char , teachers [string], assignments {}}

type DBconn struct {
	conn     *sql.DB
	path     string
	isMemory bool
}

func NewDBconn(isMemory bool, path string) (*DBconn, error) {
	d := DBconn{}
	d.isMemory = isMemory
	if isMemory {
		d.path = ":memory:"
	} else {
		d.path = path
	}

	conn, err := sql.Open("sqlite", d.path)
	if err != nil {
		return nil, err
	}
	err = conn.Ping()
	if err != nil {
		return nil, err
	}

	d.conn = conn

	_, err = d.conn.Exec("CREATE TABLE IF NOT EXISTS teachers (id TEXT , name TEXT, subject TEXT, PRIMARY KEY(id,subject))")
	if err != nil {
		return nil, err
	}

	_, err = d.conn.Exec("CREATE TABLE IF NOT EXISTS assignments (teacherid TEXT , classID TEXT, periodsneeded INT, periodsused INT, PRIMARY KEY(teacherid,classid))")
	if err != nil {
		return nil, err
	}

	_, err = d.conn.Exec("CREATE TABLE IF NOT EXISTS periods (teacherid TEXT , classID TEXT, periodno INT, day TEXT, PRIMARY KEY(classid,periodno,day))")
	if err != nil {
		return nil, err
	}
	return &d, err
}

func (d *DBconn) Close() {
	d.conn.Close()
}

// type Teacher struct {
// 	id      string
// 	name    string
// 	subject string
// 	d       *DBconn
// }

// func (t *Teacher) AddTeachers() error {
// 	_, err := t.d.conn.Exec("INSERT INTO teachers (?,?,?)", t.id, t.name, t.subject)
// 	return err
// }

// OutputClassTimetableCSV generates a CSV file for a given class timetable.
func (d *DBconn) OutputClassTimetableCSV(classID string, filename string) error {
	// Time slot mapping based on your provided example
	timeSlots := map[int]string{
		1: "8:50 - 9:30",
		2: "9:30 - 10:10",
		3: "10:20 - 11:00",
		4: "11:00 - 11:40",
		5: "11:40 - 12:20",
		6: "12:50 - 13:30",
		7: "13:30 - 14:10",
		8: "14:10 - 14:50",
		9: "14:50 - 15:30",
	}

	// Open the file for writing. Create it if it doesn't exist, and truncate it if it does.
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	// Perform a JOIN to get the teacher's name and subject from the 'teachers' table
	rows, err := d.conn.Query("SELECT T1.day, T1.periodno, T2.subject, T2.name FROM periods AS T1 JOIN teachers AS T2 ON T1.teacherid = T2.id WHERE T1.classID = ? ORDER BY T1.day, T1.periodno", classID)
	if err != nil {
		return err
	}
	defer rows.Close()

	writer := csv.NewWriter(file)

	// Write CSV header in the requested format
	headers := []string{"Day", "Time Slot", "Subject", "Teacher"}
	if err := writer.Write(headers); err != nil {
		return err
	}

	for rows.Next() {
		var day string
		var periodNo int
		var subject string
		var teacherName string
		if err := rows.Scan(&day, &periodNo, &subject, &teacherName); err != nil {
			return err
		}

		// Use the map to get the time slot string
		timeSlot, ok := timeSlots[periodNo]
		if !ok {
			timeSlot = "Unknown"
		}

		record := []string{day, timeSlot, subject, teacherName}
		if err := writer.Write(record); err != nil {
			return err
		}
	}

	writer.Flush()
	if err := writer.Error(); err != nil {
		return err
	}

	return nil
}

type Assignment struct {
	TeacherID     string
	ClassID       string
	Periodsneeded int
	periodsused   int
}

func (d *DBconn) getPossibleAssignments(classID string, periodno int, date string) ([]Assignment, error) {
	rows, err := d.conn.Query("SELECT * FROM assignments WHERE classid = ? AND periodsused != periodsneeded ORDER BY periodsused", classID)
	if err != nil {
		return nil, err
	}

	var assignments []Assignment
	for rows.Next() {
		a := Assignment{}
		err := rows.Scan(&a.TeacherID, &a.ClassID, &a.Periodsneeded, &a.periodsused)
		if err != nil {
			return nil, err
		}

		var count int
		c, err := d.conn.Query("SELECT COUNT(*) FROM periods WHERE periodno = ? AND day = ? AND teacherID = ?", periodno, date, a.TeacherID)
		if err != nil {
			return nil, err
		}
		c.Scan(&count)
		if count != 0 {
			continue
		}

		assignments = append(assignments, a)
	}
	return assignments, nil
}

func (a *Assignment) NewAssignments(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO assignments (teacherid, classid, periodsneeded, periodsused) VALUES (?, ?, ?, 0)", a.TeacherID, a.ClassID, a.Periodsneeded)
	return err
}

func (a *Assignment) IncrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused + 1 WHERE classid = ? AND teacherID = ?", a.ClassID, a.TeacherID)
	return err
}

func (a *Assignment) DecrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused - 1 WHERE classid = ? AND teacherID = ?", a.TeacherID, a.ClassID)
	return err
}

type period struct {
	a        *Assignment
	Periodno int
	Day      string
}

func (p *period) NewPeriod(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO periods (teacherid, Classid, periodno, day) VALUES (?,?,?,?)", p.a.TeacherID, p.a.ClassID, p.Periodno, p.Day)
	if err == nil {
		p.a.IncrementAssignments(d)
	}
	return err
}

func (p *period) RemovePeriod(d *DBconn) error {
	_, err := d.conn.Exec("DELETE FROM periods WHERE classid = ? AND periodno = ? AND day = ?", p.a.ClassID, p.Periodno, p.Day)
	if err == nil {
		p.a.DecrementAssignments(d)
	}
	return err
}

func GenerateTimetable(d *DBconn) {

}

func (d *DBconn) GenerateClass(classID string) bool {
	return d.Assignperiod(classID, "mon", 1, false)
}

func (d *DBconn) Assignperiod(classID string, day string, periodNo int, islast bool) bool {
	a, err := d.getPossibleAssignments(classID, periodNo, day)
	if err != nil {
		panic(err)
	}

	if len(a) == 0 {
		return false
	}
	if islast {
		p := period{&a[0], periodNo, day}

		err := p.NewPeriod(d)
		if err != nil {
			panic(err)
		}
	}

	nd, np, done := next(day, periodNo)
	if done {
		d.Assignperiod(classID, nd, np, true)
		return true
	}

	for loop := 0; loop < len(a); loop++ {
		p := period{&a[loop], periodNo, day}

		err := p.NewPeriod(d)
		if err != nil {
			panic(err)
		}

		if d.Assignperiod(classID, nd, np, false) {
			return true
		} else {
			p.RemovePeriod(d)
		}
	}
	return false

}

func next(day string, periodno int) (string, int, bool) {
	days := []string{"mon", "tue", "wed", "thu", "fri"}
	if periodno == 9 {
		loop := 0
		for loop = 0; loop < 5; loop++ {
			if days[loop] == day {
				break
			}
		}

		if loop == 4 {
			return days[loop], 9, true
		} else {
			return days[loop+1], 1, false
		}
	}

	return day, periodno + 1, false

}

func prev(day string, periodno int) (string, int, bool) {
	days := []string{"mon", "tue", "wed", "thu", "fri"}
	if periodno == 1 {
		loop := 1
		for loop = 1; loop < 6; loop++ {
			if days[loop] == day {
				break
			}
		}

		if loop == 1 {
			return "", 0, true
		} else {
			return days[loop-1], 1, false
		}
	}

	return day, periodno - 1, false

}
