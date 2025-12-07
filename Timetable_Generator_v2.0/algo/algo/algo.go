package algo

import (
	"database/sql"

	_ "github.com/glebarez/go-sqlite"
)

// DBconn represents a connection to the SQLite database.
type DBconn struct {
	conn     *sql.DB
	path     string
	isMemory bool
}

// NewDBconn creates a new database connection.
//
// Parameters:
//   isMemory: A boolean indicating whether to use an in-memory database.
//   path: The path to the database file if not an in-memory database.
//
// Returns:
//   *DBconn: A pointer to the DBconn struct.
//   error: An error if the connection fails.
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

	_, err = d.conn.Exec("CREATE TABLE IF NOT EXISTS assignments (teacherid TEXT , classID TEXT, periodsneeded INT, periodsused INT, subject TEXT, PRIMARY KEY(teacherid,classid))")
	if err != nil {
		return nil, err
	}

	_, err = d.conn.Exec("CREATE TABLE IF NOT EXISTS periods (teacherid TEXT , classID TEXT, periodno INT, day TEXT, subject TEXT,PRIMARY KEY(classid,periodno,day))")
	if err != nil {
		return nil, err
	}
	return &d, err
}

// Close closes the database connection.
func (d *DBconn) Close() {
	d.conn.Close()
}

// Assignment represents a teaching assignment.
type Assignment struct {
	TeacherID     string
	ClassID       string
	Subject       string
	Periodsneeded int
	periodsused   int
}

// getPossibleAssignments retrieves a list of possible assignments for a given class, period, and date.
//
// Parameters:
//   classID: The ID of the class.
//   periodno: The period number.
//   date: The date.
//
// Returns:
//   []Assignment: A slice of possible assignments.
//   error: An error if the query fails.
func (d *DBconn) getPossibleAssignments(classID string, periodno int, date string) ([]Assignment, error) {
	rows, err := d.conn.Query("SELECT * FROM assignments WHERE classid = ? AND periodsused != periodsneeded ORDER BY periodsused", classID)
	if err != nil {
		return nil, err
	}

	var assignments []Assignment
	for rows.Next() {
		a := Assignment{}
		err := rows.Scan(&a.TeacherID, &a.ClassID, &a.Periodsneeded, &a.periodsused, &a.Subject)
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

// NewAssignments adds a new assignment to the database.
//
// Parameters:
//   d: A pointer to the DBconn struct.
//
// Returns:
//   error: An error if the insertion fails.
func (a *Assignment) NewAssignments(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO assignments (teacherid, classid, periodsneeded, subject, periodsused) VALUES (?, ?, ?, ?, ?)", a.TeacherID, a.ClassID, a.Periodsneeded, a.Subject, int(0))
	return err
}

// IncrementAssignments increments the number of periods used for an assignment.
//
// Parameters:
//   d: A pointer to the DBconn struct.
//
// Returns:
//   error: An error if the update fails.
func (a *Assignment) IncrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused + 1 WHERE classid = ? AND teacherID = ?", a.ClassID, a.TeacherID)
	return err
}

// DecrementAssignments decrements the number of periods used for an assignment.
//
// Parameters:
//   d: A pointer to the DBconn struct.
//
// Returns:
//   error: An error if the update fails.
func (a *Assignment) DecrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused - 1 WHERE classid = ? AND teacherID = ?", a.TeacherID, a.ClassID)
	return err
}

// period represents a single period in the timetable.
type period struct {
	a        *Assignment
	Periodno int
	Day      string
}

// NewPeriod adds a new period to the database.
//
// Parameters:
//   d: A pointer to the DBconn struct.
//
// Returns:
//   error: An error if the insertion fails.
func (p *period) NewPeriod(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO periods (teacherid, Classid, periodno, day, subject) VALUES (?,?,?,?,?)", p.a.TeacherID, p.a.ClassID, p.Periodno, p.Day, p.a.Subject)
	if err == nil {
		p.a.IncrementAssignments(d)
	}
	return err
}

// RemovePeriod removes a period from the database.
//
// Parameters:
//   d: A pointer to the DBconn struct.
//
// Returns:
//   error: An error if the deletion fails.
func (p *period) RemovePeriod(d *DBconn) error {
	_, err := d.conn.Exec("DELETE FROM periods WHERE classid = ? AND periodno = ? AND day = ?", p.a.ClassID, p.Periodno, p.Day)
	if err == nil {
		p.a.DecrementAssignments(d)
	}
	return err
}

// GenerateTimetable generates a timetable for all classes.
//
// Parameters:
//   d: A pointer to the DBconn struct.
func GenerateTimetable(d *DBconn) {

}

// GenerateClass generates a timetable for a specific class.
//
// Parameters:
//   classID: The ID of the class.
//
// Returns:
//   bool: True if the timetable was generated successfully, false otherwise.
func (d *DBconn) GenerateClass(classID string) bool {
	_, err := d.conn.Exec("DELETE FROM periods WHERE classid = ?", classID)
	if err != nil {
		panic(err)
	}
	return d.Assignperiod(classID, "mon", 1, false)
}

// Assignperiod recursively assigns periods for a class.
//
// Parameters:
//   classID: The ID of the class.
//   day: The day of the week.
//   periodNo: The period number.
//   islast: A boolean indicating whether this is the last period.
//
// Returns:
//   bool: True if the period was assigned successfully, false otherwise.
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

// next calculates the next day and period number.
//
// Parameters:
//   day: The current day.
//   periodno: The current period number.
//
// Returns:
//   string: The next day.
//   int: The next period number.
//   bool: True if this is the last period of the week.
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
