import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os

class AdvancedTimetableGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Advanced School Timetable Manager")
        master.geometry("1000x700")
        master.configure(bg='#f0f4f9')

        # Application state
        self.subjects = {}
        self.teachers = {}
        self.classrooms = []
        self.time_slots = []
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.current_timetable = []

        # Load initial data
        self.load_default_data()

        # Create main UI
        self.create_main_interface()

    def load_default_data(self):
        # Default subjects with credit hours
        self.subjects = {
            "Mathematics": {"teachers": ["Mr. Smith", "Ms. Johnson"], "credits": 5},
            "English": {"teachers": ["Mrs. Williams", "Mr. Brown"], "credits": 4},
            "Science": {"teachers": ["Dr. Garcia", "Ms. Lee"], "credits": 5},
            "History": {"teachers": ["Mr. Thompson", "Mrs. Davis"], "credits": 3},
            "Computer Science": {"teachers": ["Dr. Chen", "Ms. Kumar"], "credits": 4},
            "Physical Education": {"teachers": ["Coach Martinez", "Mr. Anderson"], "credits": 2},
            "Art": {"teachers": ["Ms. Parker", "Mr. Roberts"], "credits": 2},
            "Music": {"teachers": ["Mr. Taylor", "Mrs. Moore"], "credits": 2},
            "Biology": {"teachers": ["Dr. White", "Ms. Green"], "credits": 4}
        }

        # Default classrooms
        self.classrooms = [
            "Room 101", "Room 102", "Room 103", 
            "Room 201", "Room 202", "Room 203", 
            "Gym", "Art Studio", "Computer Lab"
        ]

        # Default time slots
        self.time_slots = [
            "8:00 - 9:00", "9:00 - 10:00", "10:00 - 11:00", 
            "11:00 - 12:00", "12:00 - 1:00", "1:00 - 2:00", 
            "2:00 - 3:00"
        ]

    def create_main_interface(self):
        # Main frame
        main_frame = tk.Frame(self.master, bg='#f0f4f9')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame, 
            text="Advanced School Timetable Manager", 
            font=("Segoe UI", 18, "bold"), 
            bg='#f0f4f9',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)

        # Control Frame
        control_frame = tk.Frame(main_frame, bg='#f0f4f9')
        control_frame.pack(fill=tk.X, pady=10)

        # Buttons
        btn_style = {
            'font': ("Segoe UI", 10),
            'bg': '#3498db', 
            'fg': 'white',
            'activebackground': '#2980b9',
            'relief': tk.FLAT
        }

        generate_btn = tk.Button(
            control_frame, 
            text="Generate Timetable", 
            command=self.generate_timetable,
            **btn_style
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        manage_subjects_btn = tk.Button(
            control_frame, 
            text="Manage Subjects", 
            command=self.manage_subjects,
            **btn_style
        )
        manage_subjects_btn.pack(side=tk.LEFT, padx=5)

        manage_teachers_btn = tk.Button(
            control_frame, 
            text="Manage Teachers", 
            command=self.manage_teachers,
            **btn_style
        )
        manage_teachers_btn.pack(side=tk.LEFT, padx=5)

        # Timetable Treeview
        timetable_frame = tk.Frame(main_frame, bg='white', borderwidth=1, relief=tk.SOLID)
        timetable_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.timetable_tree = ttk.Treeview(
            timetable_frame, 
            columns=("Day", "Time", "Subject", "Teacher", "Room", "Credits"), 
            show="headings"
        )
        
        # Define headings
        headings = [
            ("Day", 80), 
            ("Time", 100), 
            ("Subject", 150), 
            ("Teacher", 150), 
            ("Room", 100),
            ("Credits", 70)
        ]
        
        for heading, width in headings:
            self.timetable_tree.heading(heading, text=heading)
            self.timetable_tree.column(heading, width=width, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(timetable_frame, orient=tk.VERTICAL, command=self.timetable_tree.yview)
        self.timetable_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timetable_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg='#ecf0f1'
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var.set("Ready to generate timetable")

    def generate_timetable(self):
        # Clear existing timetable
        for i in self.timetable_tree.get_children():
            self.timetable_tree.delete(i)

        # Reset current timetable
        self.current_timetable = []

        try:
            # Generate timetable
            for day in self.days:
                used_subjects = set()
                used_teachers = set()
                used_rooms = set()

                for time_slot in self.time_slots:
                    # Select a subject not used in this day
                    available_subjects = [
                        subj for subj, details in self.subjects.items() 
                        if subj not in used_subjects
                    ]
                    
                    if not available_subjects:
                        break

                    subject = random.choice(available_subjects)
                    used_subjects.add(subject)

                    # Select an available teacher for the subject
                    available_teachers = [
                        teacher for teacher in self.subjects[subject]['teachers'] 
                        if teacher not in used_teachers
                    ]
                    
                    if not available_teachers:
                        continue

                    teacher = random.choice(available_teachers)
                    used_teachers.add(teacher)

                    # Select an available room
                    available_rooms = [
                        room for room in self.classrooms 
                        if room not in used_rooms
                    ]
                    
                    if not available_rooms:
                        continue

                    room = random.choice(available_rooms)
                    used_rooms.add(room)

                    # Get credits for the subject
                    credits = self.subjects[subject]['credits']

                    # Create timetable entry
                    entry = {
                        'day': day,
                        'time': time_slot,
                        'subject': subject,
                        'teacher': teacher,
                        'room': room,
                        'credits': credits
                    }

                    # Insert into timetable view and internal list
                    self.timetable_tree.insert("", "end", values=(
                        day, time_slot, subject, teacher, room, credits
                    ))
                    self.current_timetable.append(entry)

            # Update status
            self.status_var.set(f"Timetable generated for {len(self.current_timetable)} slots")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate timetable: {str(e)}")

    def manage_subjects(self):
        # Create a new window for subject management
        subject_window = tk.Toplevel(self.master)
        subject_window.title("Manage Subjects")
        subject_window.geometry("500x400")

        # Subjects Treeview
        columns = ("Subject", "Teachers", "Credits")
        subject_tree = ttk.Treeview(subject_window, columns=columns, show="headings")
        
        for col in columns:
            subject_tree.heading(col, text=col)
            subject_tree.column(col, width=150, anchor='center')

        # Populate subjects
        for subject, details in self.subjects.items():
            subject_tree.insert("", "end", values=(
                subject, 
                ", ".join(details['teachers']), 
                details['credits']
            ))

        subject_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = tk.Frame(subject_window)
        btn_frame.pack(pady=10)

        def add_subject():
            subject = simpledialog.askstring("Add Subject", "Enter subject name:")
            if subject:
                teachers = simpledialog.askstring("Add Subject", "Enter teachers (comma-separated):")
                credits = simpledialog.askinteger("Add Subject", "Enter credits:")
                
                if subject and teachers and credits:
                    self.subjects[subject] = {
                        'teachers': [t.strip() for t in teachers.split(',')],
                        'credits': credits
                    }
                    subject_tree.insert("", "end", values=(
                        subject, 
                        teachers, 
                        credits
                    ))

        def remove_subject():
            selected = subject_tree.selection()
            if selected:
                subject = subject_tree.item(selected[0])['values'][0]
                del self.subjects[subject]
                subject_tree.delete(selected[0])

        add_btn = tk.Button(btn_frame, text="Add Subject", command=add_subject)
        remove_btn = tk.Button(btn_frame, text="Remove Subject", command=remove_subject)
        
        add_btn.pack(side=tk.LEFT, padx=5)
        remove_btn.pack(side=tk.LEFT, padx=5)

    def manage_teachers(self):
        # Similar to manage_subjects, but for teachers
        teacher_window = tk.Toplevel(self.master)
        teacher_window.title("Manage Teachers")
        teacher_window.geometry("400x300")

        # Implement teacher management logic here
        label = tk.Label(teacher_window, text="Teacher Management Coming Soon!")
        label.pack(padx=20, pady=20)

def main():
    root = tk.Tk()
    app = AdvancedTimetableGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()