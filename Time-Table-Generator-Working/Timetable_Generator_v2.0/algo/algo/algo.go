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

func (a *Assignment) NewAssignments(d *DBconn) error {
	_, err := d.conn.Exec("INSERT INTO assignments (teacherid, classid, periodsneeded, subject, periodsused) VALUES (?, ?, ?, ?, ?)", a.TeacherID, a.ClassID, a.Periodsneeded, a.Subject, int(0))
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
	_, err := d.conn.Exec("INSERT INTO periods (teacherid, Classid, periodno, day, subject) VALUES (?,?,?,?,?)", p.a.TeacherID, p.a.ClassID, p.Periodno, p.Day, p.a.Subject)
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
