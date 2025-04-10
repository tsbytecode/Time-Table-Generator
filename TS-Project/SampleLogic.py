from constraint import Problem, Variable, Domain

class Subject:
    def __init__(self, name, teacher, duration=1):
        self.name = name
        self.teacher = teacher
        self.duration = duration

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

class TimeSlot:
    def __init__(self, day, hour):
        self.day = day
        self.hour = hour

def generate_timetable_csp(subjects, rooms, time_slots):
    problem = Problem()

    # Define variables: (subject_name, day, hour, room_name)
    subject_vars = {}
    days = sorted(list(set(ts.day for ts in time_slots)))
    hours = sorted(list(set(ts.hour for ts in time_slots)))
    room_names = [room.name for room in rooms]

    for subject in subjects:
        subject_vars[subject.name] = (
            Variable(Domain(days), name=f"{subject.name}_day"),
            Variable(Domain(hours), name=f"{subject.name}_hour"),
            Variable(Domain(room_names), name=f"{subject.name}_room")
        )
        problem.addVariables(subject_vars[subject.name], domain=None) # Domain is handled by constraints

    # Constraint: No two subjects in the same room at the same time
    def room_occupied(s1, d1, h1, r1, s2, d2, h2, r2):
        if r1 == r2 and d1 == d2 and h1 == h2 and s1 != s2:
            return False
        return True

    subject_names = list(subject_vars.keys())
    for i in range(len(subject_names)):
        for j in range(i + 1, len(subject_names)):
            vars1 = [subject_names[i]] + list(subject_vars[subject_names[i]])
            vars2 = [subject_names[j]] + list(subject_vars[subject_names[j]])
            problem.addConstraint(room_occupied, (*vars1,))

    # Constraint: No teacher clashes (a teacher can't teach two subjects at the same time)
    def teacher_available(s1, t1, d1, h1, s2, t2, d2, h2):
        if t1 == t2 and d1 == d2 and h1 == h2 and s1 != s2:
            return False
        return True

    subject_teachers = {sub.name: sub.teacher for sub in subjects}
    for i in range(len(subject_names)):
        for j in range(i + 1, len(subject_names)):
            name1 = subject_names[i]
            name2 = subject_names[j]
            vars1 = [name1, subject_teachers[name1]] + list(subject_vars[name1])[:2]
            vars2 = [name2, subject_teachers[name2]] + list(subject_vars[name2])[:2]
            problem.addConstraint(teacher_available, (*vars1,))

    # Constraint: Subject duration (a subject occupies consecutive time slots)
    def subject_duration(day, start_hour, room, duration):
        occupied_slots = [(day, h, room) for h in range(start_hour, start_hour + duration)]
        # We need to ensure these slots are free for the current subject
        # This is harder to directly enforce as a binary constraint between two subjects.
        # We'll handle this in the solution processing.
        return True # Placeholder for now

    for name, vars in subject_vars.items():
        duration = next(sub.duration for sub in subjects if sub.name == name)
        problem.addConstraint(subject_duration, (*vars[:2], vars[2], duration))

    solutions = problem.getSolutions()

    if not solutions:
        return None

    timetable = {}
    for sol in solutions:
        for subject_name, (day, hour, room_name) in sol.items():
            duration = next(sub.duration for sub in subjects if sub.name == subject_name)
            for i in range(duration):
                slot = (day, hour + i, room_name)
                if slot in timetable and timetable[slot] != subject_name:
                    # Conflict due to duration, try next solution
                    timetable = {}
                    break
                timetable[slot] = subject_name
            if not timetable:
                break # Move to the next solution if conflict found
        if timetable:
            break # Found a valid timetable

    return timetable

def get_user_input():
    subjects = []
    rooms = []
    time_slots = []

    # Get Subjects
    num_subjects = int(input("Enter the number of subjects: "))
    for _ in range(num_subjects):
        name = input("Enter subject name: ")
        teacher = input(f"Enter teacher for {name}: ")
        duration = int(input(f"Enter duration (in hours) for {name}: "))
        subjects.append(Subject(name, teacher, duration))

    # Get Rooms
    num_rooms = int(input("Enter the number of rooms: "))
    for _ in range(num_rooms):
        name = input("Enter room name: ")
        capacity = int(input(f"Enter capacity for {name}: "))
        rooms.append(Room(name, capacity))

    # Get Time Slots
    days_input = input("Enter days of the week (e.g., Mon,Tue,Wed): ").split(',')
    start_hour = int(input("Enter the starting hour (e.g., 9): "))
    end_hour = int(input("Enter the ending hour (e.g., 16): "))

    for day in [d.strip() for d in days_input]:
        for hour in range(start_hour, end_hour):
            time_slots.append(TimeSlot(day, hour))

    return subjects, rooms, time_slots

def print_timetable(timetable, all_time_slots, all_rooms):
    if not timetable:
        print("No feasible timetable could be generated with the given constraints.")
        return

    days = sorted(list(set(slot.day for slot in all_time_slots)))
    hours = sorted(list(set(slot.hour for slot in all_time_slots)))
    room_names = sorted([room.name for room in all_rooms])

    print("\n--- Timetable ---")
    print("Time \\ Room | " + " | ".join(room_names))
    print("-" * (15 + 5 * len(room_names)))

    for day in days:
        for hour in hours:
            row = f"{day} - {hour:02d}:00 |"
            for room_name in room_names:
                subject = timetable.get((day, hour, room_name))
                if subject:
                    row += f" {subject:<10} |"
                else:
                    row += " {:<10} |".format("")
            print(row)
        print("-" * (15 + 5 * len(room_names)))

if __name__ == "__main__":
    subjects_data, rooms_data, time_slots_data = get_user_input()
    generated_timetable = generate_timetable_csp(subjects_data, rooms_data, time_slots_data)
    print_timetable(generated_timetable, time_slots_data, rooms_data)