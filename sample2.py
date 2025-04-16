import csv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Treeview, Style, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
scheduler_ran = False

# UI setup
root = tk.Tk()
root.title("GreenOS Scheduler Pro")
root.geometry("1100x800")
root.configure(bg="#121212")

# Style
style = Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#1e1e1e",
                foreground="#00FF00",
                rowheight=30,
                fieldbackground="#1e1e1e",
                font=('Consolas', 11))
style.configure("Treeview.Heading", background="#333333", foreground="#00FF00", font=('Consolas', 12, 'bold'))

main_canvas = tk.Canvas(root, bg="#121212")
main_scrollbar = Scrollbar(root, orient="vertical", command=main_canvas.yview)
main_scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)
main_canvas.configure(yscrollcommand=main_scrollbar.set)

main_frame = tk.Frame(main_canvas, bg="#121212")
main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

def configure_scroll(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

main_frame.bind("<Configure>", configure_scroll)

# Output log box with scroll
output_frame = tk.Frame(main_frame)
output_frame.pack(padx=20, pady=(20, 10), fill='x')

output_scrollbar = Scrollbar(output_frame)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(output_frame, wrap='word', bg='#1e1e1e', fg='#00FF00', font=('Consolas', 11), height=12, insertbackground='white', yscrollcommand=output_scrollbar.set)
output_text.pack(side=tk.LEFT, fill='x', expand=True)
output_scrollbar.config(command=output_text.yview)

chart_frame = tk.Frame(main_frame, bg="#121212")
chart_frame.pack(padx=10, pady=10, fill='both', expand=False)

chart_canvas = None


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
    global scheduler_ran
    if scheduler_ran:
        clear()
    if not tasks:
        log("No tasks to schedule.")
        return

    scheduler_ran = True
    time = 0
    energy = 0
    cpu_energy = 0
    gpu_energy = 0
    memory_energy = 0
    screen_energy = 0
    completed_tasks = 0

    log("\n[GreenOS Scheduler Simulation]\n")
    tasks.sort(key=lambda t: (t.deadline / t.burst_time, t.arrival_time))
    while completed_tasks < len(tasks):
        idx = -1
        for i, task in enumerate(tasks):
            if not task.completed and task.arrival_time <= time:
                idx = i
                break

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

    conventional_energy = calculate_conventional_energy()
    energy_saved = conventional_energy - energy
    log(f"\nTotal Energy Consumed by GreenOS: {energy:.2f}")
    log(f"  - CPU Energy: {cpu_energy:.2f}")
    log(f"  - GPU Energy: {gpu_energy:.2f}")
    log(f"  - Memory Energy: {memory_energy:.2f}")
    log(f"  - Screen Energy: {screen_energy:.2f}")
    log(f"Estimated Energy by Conventional OS: {conventional_energy:.2f}")
    log(f"Energy Saved by GreenOS: {energy_saved:.2f}")

    log("Missed Deadlines:")
    missed = False
    for task in tasks:
        if task.finish_time > task.deadline:
            log(f"- {task.name}")
            missed = True
    if not missed:
        log("None")
    update_task_table()
    display_energy_chart(cpu_energy, gpu_energy, memory_energy, screen_energy)


def calculate_conventional_energy():
    time = 0
    energy = 0
    sorted_tasks = sorted(tasks, key=lambda t: t.arrival_time)
    for task in sorted_tasks:
        if task.arrival_time > time:
            time = task.arrival_time
        energy += task.burst_time * 1.5
        time += task.burst_time
    return energy


def clear():
    global scheduler_ran, chart_canvas
    scheduler_ran = False
    output_text.delete('1.0', tk.END)
    for row in task_table.get_children():
        task_table.delete(row)
    for task in tasks:
        task.reset()
    if chart_canvas:
        chart_canvas.get_tk_widget().destroy()
        chart_canvas = None
    log("Tasks and output cleared.")
    update_task_table()


def update_task_table():
    for row in task_table.get_children():
        task_table.delete(row)
    for task in tasks:
        task_table.insert('', 'end', values=(task.name, task.arrival_time, task.burst_time, task.deadline, task.start_time, task.finish_time, "Yes" if task.completed else "No"))

frame = tk.Frame(main_frame, bg="#121212")
frame.pack(pady=10)

btn_manual = tk.Button(frame, text="Manual Input", command=manual_input, bg="#03DAC5", fg="black", font=('Consolas', 10, 'bold'), width=15)
btn_manual.grid(row=0, column=0, padx=10)

btn_csv = tk.Button(frame, text="Load CSV", command=load_csv, bg="#BB86FC", fg="black", font=('Consolas', 10, 'bold'), width=15)
btn_csv.grid(row=0, column=1, padx=10)

btn_json = tk.Button(frame, text="Load JSON", command=load_json, bg="#FFB74D", fg="black", font=('Consolas', 10, 'bold'), width=15)
btn_json.grid(row=0, column=2, padx=10)

btn_run = tk.Button(frame, text="Run Scheduler", command=run_greenos, bg="#4CAF50", fg="white", font=('Consolas', 10, 'bold'), width=15)
btn_run.grid(row=0, column=3, padx=10)

btn_clear = tk.Button(frame, text="Clear All", command=clear, bg="#CF6679", fg="white", font=('Consolas', 10, 'bold'), width=15)
btn_clear.grid(row=0, column=4, padx=10)

columns = ("Name", "Arrival", "Burst", "Deadline", "Start", "Finish", "Done")
task_table = Treeview(main_frame, columns=columns, show='headings', style="Treeview")
for col in columns:
    task_table.heading(col, text=col)
    task_table.column(col, width=130, anchor='center')
task_table.pack(padx=20, pady=20, fill='both', expand=True)

root.mainloop()
