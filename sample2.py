import csv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

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

# UI setup
root = tk.Tk()
root.title("GreenOS Scheduler")
root.geometry("700x500")

output_text = tk.Text(root, wrap='word', bg='black', fg='lime', font=('Courier', 10))
output_text.pack(expand=True, fill='both')

def log(msg):
    output_text.insert(tk.END, msg + "\n")
    output_text.see(tk.END)

def add_task(name, at, bt, dl):
    if at < 0 or bt <= 0 or dl < at:
        log(f"Invalid input for task {name}. Skipped.")
        return
    tasks.append(Task(name, at, bt, dl))

def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_task(row['name'], int(row['arrival_time']), int(row['burst_time']), int(row['deadline']))
    log("Loaded tasks from CSV.")

def load_json():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return
    with open(file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            add_task(item['name'], item['arrival_time'], item['burst_time'], item['deadline'])
    log("Loaded tasks from JSON.")

def manual_input():
    n = simpledialog.askinteger("Manual Input", "Enter number of tasks:")
    for i in range(n):
        name = simpledialog.askstring("Task", f"Enter name of Task {i+1}:")
        at = simpledialog.askinteger("Task", f"Arrival Time for {name}:")
        bt = simpledialog.askinteger("Task", f"Burst Time for {name}:")
        dl = simpledialog.askinteger("Task", f"Deadline for {name}:")
        add_task(name, at, bt, dl)

def run_greenos():
    time = 0
    energy = 0
    completed_tasks = 0
    log("\n[GreenOS Scheduler Simulation]\n")
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
            log(f"{task.name} executes from {time} to {time + task.burst_time}")
            time += task.burst_time
            task.finish_time = time
            task.completed = True
            energy += task.burst_time * 1
            completed_tasks += 1
        else:
            log(f"Idle from {time} to {time + 1}")
            time += 1
            energy += 0.5

    log(f"\nEnergy Consumed: {energy}")
    log("Missed Deadlines:")
    missed = False
    for task in tasks:
        if task.finish_time > task.deadline:
            log(f"- {task.name}")
            missed = True
    if not missed:
        log("None")

def clear():
    tasks.clear()
    output_text.delete('1.0', tk.END)
    log("Tasks and output cleared.")

# Buttons
frame = tk.Frame(root)
frame.pack(pady=10)

btn_manual = tk.Button(frame, text="Manual Input", command=manual_input)
btn_manual.grid(row=0, column=0, padx=5)

btn_csv = tk.Button(frame, text="Load CSV", command=load_csv)
btn_csv.grid(row=0, column=1, padx=5)

btn_json = tk.Button(frame, text="Load JSON", command=load_json)
btn_json.grid(row=0, column=2, padx=5)

btn_run = tk.Button(frame, text="Run Scheduler", command=run_greenos)
btn_run.grid(row=0, column=3, padx=5)

btn_clear = tk.Button(frame, text="Clear", command=clear)
btn_clear.grid(row=0, column=4, padx=5)

root.mainloop()