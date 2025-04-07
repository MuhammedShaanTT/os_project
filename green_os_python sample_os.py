import csv
import json

class Task:
    def __init__(self, name, arrival_time, burst_time, deadline):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.deadline = deadline
        self.start_time = -1
        self.finish_time = 0
        self.completed = False

tasks = []

def add_task(name, at, bt, dl):
    if at < 0 or bt <= 0 or dl < at:
        print(f"Invalid input for task {name}. Skipping.")
        return
    tasks.append(Task(name, at, bt, dl))

def load_tasks_from_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_task(row['name'], int(row['arrival_time']), int(row['burst_time']), int(row['deadline']))

def load_tasks_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        for item in data:
            add_task(item['name'], item['arrival_time'], item['burst_time'], item['deadline'])

def manual_input():
    n = int(input("Enter number of tasks: "))
    for i in range(n):
        print(f"\nTask {i+1}")
        name = input("Name: ")
        at = int(input("Arrival Time: "))
        bt = int(input("Burst Time: "))
        dl = int(input("Deadline: "))
        add_task(name, at, bt, dl)

def run_greenos():
    time = 0
    energy = 0
    completed_tasks = 0
    print("\n[GreenOS Scheduler Simulation]\n")
    while completed_tasks < len(tasks):
        idx = -1
        best_ratio = float('inf')

        for i, task in enumerate(tasks):
            if not task.completed and task.arrival_time <= time:
                ratio = task.deadline / task.burst_time
                if ratio < best_ratio:
                    best_ratio = ratio
                    idx = i

        if idx != -1:
            task = tasks[idx]
            if task.start_time == -1:
                task.start_time = time
            print(f"{task.name} executes from {time} to {time + task.burst_time}")
            time += task.burst_time
            task.finish_time = time
            task.completed = True
            energy += task.burst_time * 1
            completed_tasks += 1
        else:
            print(f"Idle from {time} to {time + 1}")
            time += 1
            energy += 0.5

    print(f"\nEnergy Consumed: {energy}")
    print("Missed Deadlines:", end=' ')
    missed = False
    for task in tasks:
        if task.finish_time > task.deadline:
            print(task.name, end=' ')
            missed = True
    if not missed:
        print("None")
    print()

def main():
    while True:
        print("\n=== GreenOS Menu ===")
        print("1. Manual Input")
        print("2. Load Tasks from CSV")
        print("3. Load Tasks from JSON")
        print("4. Run Scheduler")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            manual_input()
        elif choice == '2':
            filename = input("Enter CSV filename: ")
            load_tasks_from_csv(filename)
        elif choice == '3':
            filename = input("Enter JSON filename: ")
            load_tasks_from_json(filename)
        elif choice == '4':
            run_greenos()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == '__main__':
    main()