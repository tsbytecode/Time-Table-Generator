import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import random
import json
import os

class AdvancedTimetableManager:
    def __init__(self, master):
        self.master = master
        master.title("Advanced School Timetable Manager")
        master.geometry("1200x800")
        master.configure(bg='#f0f0f0')

        # Application State
        self.subjects = {}
        self.teachers = {}
        self.classrooms = []
        self.constraints = {}

        # Initialize default data
        self.load_default_data()

        # Create UI Components
        self.create_main_interface()

    def load_default_data(self):
        # Default Subject Configuration
        self.subjects = {
            "Mathematics": {
                "teachers": ["Dr. Emily Rodriguez", "Prof. Alex Chen"],
                "credits": 5,
                "color": "#1abc9c",
                "difficulty": "Advanced"
            },
            "Computer Science": {
                "teachers": ["Ms. Sarah Kim", "Mr. Michael Wong"],
                "credits": 4,
                "color": "#3498db",
                "difficulty": "Advanced"
            },
            "English": {
                "teachers": ["Mrs. Rachel Green", "Mr. David Thompson"],
                "credits": 3,
                "color": "#e74c3c",
                "difficulty": "Intermediate"
            },
            "Physics": {
                "teachers": ["Dr. John Parker", "Prof. Linda Zhang"],
                "credits": 4,
                "color": "#9b59b6",
                "difficulty": "Advanced"
            },
            "History": {
                "teachers": ["Ms. Emma Wilson", "Mr. Ryan Garcia"],
                "credits": 3,
                "color": "#f39c12",
                "difficulty": "Intermediate"
            }
        }

        # Default Classrooms
        self.classrooms = [
            "Science Lab A", 
            "Computer Lab", 
            "Lecture Hall 1", 
            "Seminar Room", 
            "Digital Classroom",
            "Art Studio"
        ]

        # Predefined Time Slots
        self.time_slots = [
            "08:00 - 09:30", 
            "09:45 - 11:15", 
            "11:30 - 13:00", 
            "14:00 - 15:30", 
            "15:45 - 17:15"
        ]

        # Days of the Week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def create_main_interface(self):
        # Main Frame
        main_frame = tk.Frame(self.master, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(
            main_frame, 
            text="Advanced Timetable Management System", 
            font=('Arial', 18, 'bold'), 
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)

        # Control Frame
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=10)

        # Buttons
        buttons = [
            ("Generate Timetable", self.generate_timetable),
            ("Manage Subjects", self.manage_subjects),
            ("Manage Classrooms", self.manage_classrooms),
            ("Export Timetable", self.export_timetable),
            ("Import Timetable", self.import_timetable)
        ]

        for text, command in buttons:
            btn = tk.Button(
                control_frame, 
                text=text, 
                command=command,
                bg='#3498db',
                fg='white',
                font=('Arial', 10)
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Timetable Treeview
        self.timetable_tree = ttk.Treeview(
            main_frame, 
            columns=("Day", "Time", "Subject", "Teacher", "Room", "Credits"),
            show="headings"
        )

        # Configure Columns
        columns = [
            ("Day", 100), 
            ("Time", 150), 
            ("Subject", 200), 
            ("Teacher", 200), 
            ("Room", 150), 
            ("Credits", 100)
        ]

        for col, width in columns:
            self.timetable_tree.heading(col, text=col)
            self.timetable_tree.column(col, width=width, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            main_frame, 
            orient=tk.VERTICAL, 
            command=self.timetable_tree.yview
        )
        self.timetable_tree.configure(yscroll=scrollbar.set)

        self.timetable_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready to generate timetable")
        status_label = tk.Label(
            main_frame, 
            textvariable=self.status_var,
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def generate_timetable(self):
        # Clear existing entries
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)

        try:
            for day in self.days:
                day_schedule = []
                used_subjects = set()
                used_teachers = set()
                used_rooms = set()

                for time_slot in self.time_slots:
                    # Select subject
                    available_subjects = [
                        subj for subj in self.subjects.keys() 
                        if subj not in used_subjects
                    ]
                    
                    if not available_subjects:
                        break

                    subject = random.choice(available_subjects)
                    used_subjects.add(subject)

                    # Select teacher
                    available_teachers = [
                        teacher for teacher in self.subjects[subject]['teachers'] 
                        if teacher not in used_teachers
                    ]
                    
                    if not available_teachers:
                        continue

                    teacher = random.choice(available_teachers)
                    used_teachers.add(teacher)

                    # Select room
                    available_rooms = [
                        room for room in self.classrooms 
                        if room not in used_rooms
                    ]
                    
                    if not available_rooms:
                        continue

                    room = random.choice(available_rooms)
                    used_rooms.add(room)

                    # Get subject details
                    subject_details = self.subjects[subject]

                    # Insert into treeview
                    entry = self.timetable_tree.insert("", "end", values=(
                        day, time_slot, subject, teacher, room, subject_details['credits']
                    ))

                    # Store for potential export
                    day_schedule.append({
                        'day': day,
                        'time': time_slot,
                        'subject': subject,
                        'teacher': teacher,
                        'room': room,
                        'credits': subject_details['credits']
                    })

            self.status_var.set(f"Timetable generated for {len(self.days)} days")

        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

    def manage_subjects(self):
        # Subject Management Window
        subject_window = tk.Toplevel(self.master)
        subject_window.title("Subject Management")
        subject_window.geometry("600x400")

        # Treeview for Subjects
        subject_tree = ttk.Treeview(
            subject_window, 
            columns=("Subject", "Teachers", "Credits", "Difficulty"),
            show="headings"
        )

        # Configure Columns
        for col in ("Subject", "Teachers", "Credits", "Difficulty"):
            subject_tree.heading(col, text=col)
            subject_tree.column(col, width=120, anchor='center')

        # Populate Subjects
        for subject, details in self.subjects.items():
            subject_tree.insert("", "end", values=(
                subject, 
                ", ".join(details['teachers']), 
                details['credits'],
                details['difficulty']
            ))

        subject_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add/Remove Buttons
        btn_frame = tk.Frame(subject_window)
        btn_frame.pack(pady=10)

        def add_subject():
            subject = simpledialog.askstring("Add Subject", "Enter subject name:")
            if subject:
                teachers = simpledialog.askstring("Teachers", "Enter teachers (comma-separated):")
                credits = simpledialog.askinteger("Credits", "Enter credits:")
                difficulty = simpledialog.askstring("Difficulty", "Enter difficulty level:")
                
                if subject and teachers and credits and difficulty:
                    self.subjects[subject] = {
                        'teachers': [t.strip() for t in teachers.split(',')],
                        'credits': credits,
                        'difficulty': difficulty,
                        'color': '#3498db'  # Default color
                    }
                    subject_tree.insert("", "end", values=(
                        subject, teachers, credits, difficulty
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

    def manage_classrooms(self):
        # Classroom Management Window
        classroom_window = tk.Toplevel(self.master)
        classroom_window.title("Classroom Management")
        classroom_window.geometry("400x300")

        # Listbox for Classrooms
        classroom_listbox = tk.Listbox(classroom_window)
        for room in self.classrooms:
            classroom_listbox.insert(tk.END, room)
        classroom_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add/Remove Buttons
        def add_classroom():
            room = simpledialog.askstring("Add Classroom", "Enter classroom name:")
            if room and room not in self.classrooms:
                self.classrooms.append(room)
                classroom_listbox.insert(tk.END, room)

        def remove_classroom():
            selected = classroom_listbox.curselection()
            if selected:
                index = selected[0]
                del self.classrooms[index]
                classroom_listbox.delete(index)

        btn_frame = tk.Frame(classroom_window)
        btn_frame.pack(pady=10)

        add_btn = tk.Button(btn_frame, text="Add Classroom", command=add_classroom)
        remove_btn = tk.Button(btn_frame, text="Remove Classroom", command=remove_classroom)
        
        add_btn.pack(side=tk.LEFT, padx=5)
        remove_btn.pack(side=tk.LEFT, padx=5)

    def export_timetable(self):
        # Export timetable to JSON
        try:
            timetable_data = []
            for item in self.timetable_tree.get_children():
                values = self.timetable_tree.item(item)['values']
                timetable_data.append({
                    'day': values[0],
                    'time': values[1],
                    'subject': values[2],
                    'teacher': values[3],
                    'room': values[4],
                    'credits': values[5]
                })

            filename = f"timetable_{random.randint(1000, 9999)}.json"
            with open(filename, 'w') as f:
                json.dump(timetable_data, f, indent=4)

            messagebox.showinfo("Export Successful", f"Timetable exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def import_timetable(self):
        # Import timetable from JSON
        try:
            filename = simpledialog.askstring("Import Timetable", "Enter filename:")
            if filename:
                with open(filename, 'r') as f:
                    timetable_data = json.load(f)

                # Clear existing timetable
                for item in self.timetable_tree.get_children():
                    self.timetable_tree.delete(item)

                # Insert imported data
                for entry in timetable_data:
                    self.timetable_tree.insert("", "end", values=(
                        entry['day'], entry['time'], entry['subject'], 
                        entry['teacher'], entry['room'], entry['credits']
                    ))

                messagebox.showinfo("Import Successful", f"Timetable imported from {filename}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

def main():
    root = tk.Tk()
    app = AdvancedTimetableManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()