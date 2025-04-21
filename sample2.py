import csv
import json
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter.ttk import Treeview, Style

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

    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = -1
        self.finish_time = 0
        self.completed = False

tasks = []

root = tk.Tk()
root.title("GreenOS Scheduler Pro")
root.geometry("1100x800")
root.configure(bg="#121212")

style = Style()
style.theme_use("clam")
style.configure("Treeview", background="#1e1e1e", foreground="#00FF00", rowheight=30,
                fieldbackground="#1e1e1e", font=('Consolas', 11))
style.configure("Treeview.Heading", background="#333333", foreground="#00FF00", font=('Consolas', 12, 'bold'))

main_frame = tk.Frame(root, bg="#121212")
main_frame.pack(fill="both", expand=True)

output_frame = tk.Frame(main_frame)
output_frame.pack(padx=20, pady=(20, 10), fill='x')

output_text = tk.Text(output_frame, wrap='word', bg='#1e1e1e', fg='#00FF00', font=('Consolas', 11), height=12, insertbackground='white')
output_text.pack(side=tk.LEFT, fill='x', expand=True)

output_scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=output_scrollbar.set)

def log(msg):
    output_text.insert(tk.END, msg + "\n")
    output_text.see(tk.END)

def add_task(name, at, bt, dl):
    if at < 0 or bt <= 0 or dl < at:
        log(f"Invalid input for task {name}. Skipped.")
        return
    tasks.append(Task(name, at, bt, dl))
    update_task_table()

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
    if not tasks:
        log("No tasks to schedule.")
        return

    time = 0
    energy = cpu_energy = gpu_energy = memory_energy = screen_energy = completed_tasks = 0

    log("\n[GreenOS Scheduler Simulation]\n")
    tasks.sort(key=lambda t: (t.deadline / t.burst_time, t.arrival_time))
    while completed_tasks < len(tasks):
        idx = next((i for i, t in enumerate(tasks) if not t.completed and t.arrival_time <= time), -1)
        if idx != -1:
            task = tasks[idx]
            if task.start_time == -1:
                task.start_time = time
            log(f"{task.name} executes from {time} to {time + task.burst_time}")
            time += task.burst_time
            task.finish_time = time
            task.completed = True
            cpu_energy += task.burst_time * 0.5
            gpu_energy += task.burst_time * 0.2
            memory_energy += task.burst_time * 0.15
            screen_energy += task.burst_time * 0.1
            energy += task.burst_time * 1
            completed_tasks += 1
        else:
            log(f"Idle from {time} to {time + 1}")
            time += 1
            cpu_energy += 0.3
            gpu_energy += 0.1
            memory_energy += 0.1
            screen_energy += 0.05
            energy += 0.5

    conventional_energy = sum(t.burst_time * 1.5 for t in sorted(tasks, key=lambda t: t.arrival_time))
    energy_saved = conventional_energy - energy
    log(f"\nTotal Energy Consumed by GreenOS: {energy:.2f}")
    log(f"  - CPU Energy: {cpu_energy:.2f}")
    log(f"  - GPU Energy: {gpu_energy:.2f}")
    log(f"  - Memory Energy: {memory_energy:.2f}")
    log(f"  - Screen Energy: {screen_energy:.2f}")
    log(f"Estimated Energy by Conventional OS: {conventional_energy:.2f}")
    log(f"Energy Saved by GreenOS: {energy_saved:.2f}")

    log("Missed Deadlines:")
    missed_any = False
    for task in tasks:
        if task.finish_time > task.deadline:
            log(f"- {task.name}")
            missed_any = True
    if not missed_any:
        log("None")

    update_task_table()

def clear():
    output_text.delete('1.0', tk.END)
    for task in tasks:
        task.reset()
    log("Tasks and output cleared.")
    update_task_table()

def update_task_table():
    for row in task_table.get_children():
        task_table.delete(row)
    for task in tasks:
        task_table.insert('', 'end', values=(
            task.name, task.arrival_time, task.burst_time, task.deadline,
            task.start_time, task.finish_time, "Yes" if task.completed else "No"
        ))

frame = tk.Frame(main_frame, bg="#121212")
frame.pack(pady=10)

btns = [
    ("Manual Input", manual_input, "#03DAC5"),
    ("Load CSV", load_csv, "#BB86FC"),
    ("Load JSON", load_json, "#FFB74D"),
    ("Run Scheduler", run_greenos, "#4CAF50"),
    ("Clear All", clear, "#CF6679")
]

for idx, (text, cmd, color) in enumerate(btns):
    tk.Button(frame, text=text, command=cmd, bg=color, fg="black" if "Clear" not in text else "white",
              font=('Consolas', 10, 'bold'), width=15).grid(row=0, column=idx, padx=10)

columns = ("Name", "Arrival", "Burst", "Deadline", "Start", "Finish", "Done")
task_table = Treeview(main_frame, columns=columns, show='headings', style="Treeview")
for col in columns:
    task_table.heading(col, text=col)
    task_table.column(col, width=130, anchor='center')
task_table.pack(padx=20, pady=20, fill='both', expand=True)

root.mainloop()
