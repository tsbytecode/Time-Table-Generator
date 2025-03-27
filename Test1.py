import tkinter as tk
from tkinter import ttk
import random

class SchoolTimetableGenerator:
    def __init__(self, master):
        self.master = master
        master.title("School Timetable Generator")
        master.geometry("800x600")
        master.configure(bg='#f0f0f0')

        # Subjects
        self.subjects = [
            "Mathematics", "English", "Science", "History", 
            "Geography", "Physical Education", "Art", 
            "Computer Science", "Music", "Biology"
        ]

        # Teachers
        self.teachers = {
            "Mathematics": ["Mr. Smith", "Ms. Johnson"],
            "English": ["Mrs. Williams", "Mr. Brown"],
            "Science": ["Dr. Garcia", "Ms. Lee"],
            "History": ["Mr. Thompson", "Mrs. Davis"],
            "Geography": ["Ms. Rodriguez", "Mr. Wilson"],
            "Physical Education": ["Coach Martinez", "Mr. Anderson"],
            "Art": ["Ms. Parker", "Mr. Roberts"],
            "Computer Science": ["Dr. Chen", "Ms. Kumar"],
            "Music": ["Mr. Taylor", "Mrs. Moore"],
            "Biology": ["Dr. White", "Ms. Green"]
        }

        # Classrooms
        self.classrooms = ["Room 101", "Room 102", "Room 103", 
                            "Room 201", "Room 202", "Room 203", 
                            "Gym", "Art Studio", "Computer Lab"]

        # Time slots
        self.time_slots = [
            "8:00 - 9:00", "9:00 - 10:00", "10:00 - 11:00", 
            "11:00 - 12:00", "12:00 - 1:00", "1:00 - 2:00", 
            "2:00 - 3:00"
        ]

        # Days of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.master, 
            text="School Timetable Generator", 
            font=("Helvetica", 16, "bold"), 
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)

        # Timetable Frame
        timetable_frame = tk.Frame(self.master, bg='white')
        timetable_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Create Treeview
        self.timetable_tree = ttk.Treeview(
            timetable_frame, 
            columns=("Day", "Time", "Subject", "Teacher", "Room"), 
            show="headings"
        )
        
        # Define headings
        self.timetable_tree.heading("Day", text="Day")
        self.timetable_tree.heading("Time", text="Time")
        self.timetable_tree.heading("Subject", text="Subject")
        self.timetable_tree.heading("Teacher", text="Teacher")
        self.timetable_tree.heading("Room", text="Room")

        # Column widths
        for col in ("Day", "Time", "Subject", "Teacher", "Room"):
            self.timetable_tree.column(col, width=120, anchor='center')

        self.timetable_tree.pack(fill=tk.BOTH, expand=True)

        # Generate Button
        generate_btn = tk.Button(
            self.master, 
            text="Generate Timetable", 
            command=self.generate_timetable,
            bg='#4CAF50', 
            fg='white', 
            font=("Helvetica", 12)
        )
        generate_btn.pack(pady=10)

    def generate_timetable(self):
        # Clear existing timetable
        for i in self.timetable_tree.get_children():
            self.timetable_tree.delete(i)

        # Generate timetable
        for day in self.days:
            used_subjects = set()
            used_teachers = set()
            used_rooms = set()

            for time_slot in self.time_slots:
                # Select a subject not used in this day
                available_subjects = [
                    subj for subj in self.subjects 
                    if subj not in used_subjects
                ]
                
                if not available_subjects:
                    break

                subject = random.choice(available_subjects)
                used_subjects.add(subject)

                # Select an available teacher for the subject
                available_teachers = [
                    teacher for teacher in self.teachers[subject] 
                    if teacher not in used_teachers
                ]
                teacher = random.choice(available_teachers)
                used_teachers.add(teacher)

                # Select an available room
                available_rooms = [
                    room for room in self.classrooms 
                    if room not in used_rooms
                ]
                room = random.choice(available_rooms)
                used_rooms.add(room)

                # Insert into timetable
                self.timetable_tree.insert("", "end", values=(
                    day, time_slot, subject, teacher, room
                ))

def main():
    root = tk.Tk()
    app = SchoolTimetableGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()