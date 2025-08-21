package algo

import (
	"database/sql"

	_ "github.com/glebarez/go-sqlite"
)

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

func (d *DBconn) Close() {
	d.conn.Close()
}

type Assignment struct {
	TeacherID     string
	ClassID       string
	Subject       string
	Periodsneeded int
	periodsused   int
}

func (d *DBconn) getPossibleAssignments(classID string, periodno int, date string) ([]Assignment, error) {
	rows, err := d.conn.Query("SELECT * FROM assignments WHERE classid = ? AND periodsused < periodsneeded ORDER BY periodsused", classID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

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
		if c.Next() {
			err = c.Scan(&count)
			if err != nil {
				c.Close()
				return nil, err
			}
		}
		c.Close()

		if count == 0 {
			assignments = append(assignments, a)
		}
	}
	return assignments, nil
}

func (a *Assignment) NewAssignments(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO assignments (teacherid, classid, periodsneeded, subject, periodsused) VALUES (?, ?, ?, ?, ?)", a.TeacherID, a.ClassID, a.Periodsneeded, a.Subject, 0)
	return err
}

func (a *Assignment) IncrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused + 1 WHERE classid = ? AND teacherID = ?", a.ClassID, a.TeacherID)
	return err
}

func (a *Assignment) DecrementAssignments(d *DBconn) error {
	_, err := d.conn.Exec("UPDATE assignments SET periodsused = periodsused - 1 WHERE classid = ? AND teacherID = ?", a.ClassID, a.TeacherID)
	return err
}

type period struct {
	a        *Assignment
	Periodno int
	Day      string
}

func (p *period) NewPeriod(d *DBconn) error {
	err := p.a.IncrementAssignments(d)
	if err != nil {
		return err
	}
	_, err = d.conn.Exec("INSERT INTO periods (teacherid, Classid, periodno, day, subject) VALUES (?,?,?,?,?)", p.a.TeacherID, p.a.ClassID, p.Periodno, p.Day, p.a.Subject)
	return err
}

func (p *period) RemovePeriod(d *DBconn) error {
	err := p.a.DecrementAssignments(d)
	if err != nil {
		return err
	}
	_, err = d.conn.Exec("DELETE FROM periods WHERE classid = ? AND periodno = ? AND day = ?", p.a.ClassID, p.Periodno, p.Day)
	return err
}

func (d *DBconn) GenerateClass(classID string) (bool, error) {
	// Clear any existing timetable for this class
	_, err := d.conn.Exec("DELETE FROM periods WHERE classID = ?", classID)
	if err != nil {
		return false, err
	}
	// Reset used periods for this class
	_, err = d.conn.Exec("UPDATE assignments SET periodsused = 0 WHERE classID = ?", classID)
	if err != nil {
		return false, err
	}
	return d.assignPeriod(classID, "mon", 1)
}

func (d *DBconn) assignPeriod(classID string, day string, periodNo int) (bool, error) {
	// Base case: If we have successfully scheduled all periods, we are done.
	nd, np, done := next(day, periodNo)
	if done {
		// Try to fill the last period
		assignments, err := d.getPossibleAssignments(classID, periodNo, day)
		if err != nil {
			return false, err
		}
		if len(assignments) == 0 {
			return false, nil // No assignment available for the last slot
		}
		p := period{&assignments[0], periodNo, day}
		err = p.NewPeriod(d)
		if err != nil {
			return false, err
		}
		return true, nil
	}

	assignments, err := d.getPossibleAssignments(classID, periodNo, day)
	if err != nil {
		return false, err
	}

	if len(assignments) == 0 {
		// If no assignments are possible for this slot, backtrack.
		return false, nil
	}

	// Recursive step: Try each possible assignment for the current period.
	for i := range assignments {
		p := period{&assignments[i], periodNo, day}

		err = p.NewPeriod(d)
		if err != nil {
			return false, err
		}

		success, err := d.assignPeriod(classID, nd, np)
		if err != nil {
			return false, err
		}
		if success {
			return true, nil
		}

		// Backtrack
		err = p.RemovePeriod(d)
		if err != nil {
			return false, err
		}
	}

	// If no assignment leads to a solution, return false.
	return false, nil
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
