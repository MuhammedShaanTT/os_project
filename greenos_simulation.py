import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Task:
    def __init__(self, name, arrival_time, burst_time, deadline):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.deadline = deadline
        self.start_time = None
        self.finish_time = None

# Scheduling algorithms
def fcfs_scheduler(tasks):
    time = 0
    energy = 0
    timeline = []
    missed = []

    for task in sorted(tasks, key=lambda x: x.arrival_time):
        if time < task.arrival_time:
            energy += (task.arrival_time - time) * 0.5  # Sleep state energy
            time = task.arrival_time
        task.start_time = time
        time += task.burst_time
        task.finish_time = time
        timeline.append((task.name, task.start_time, task.finish_time))
        energy += task.burst_time * 2
        if task.finish_time > task.deadline:
            missed.append(task.name)
    return timeline, energy, missed

def round_robin_scheduler(tasks, quantum=2):
    time = 0
    energy = 0
    timeline = []
    queue = []
    tasks = sorted(tasks, key=lambda x: x.arrival_time)
    missed = []

    while tasks or queue:
        while tasks and tasks[0].arrival_time <= time:
            queue.append(tasks.pop(0))

        if queue:
            current = queue.pop(0)
            exec_time = min(current.remaining_time, quantum)
            if current.start_time is None:
                current.start_time = time
            timeline.append((current.name, time, time + exec_time))
            time += exec_time
            current.remaining_time -= exec_time
            energy += exec_time * 1.5

            while tasks and tasks[0].arrival_time <= time:
                queue.append(tasks.pop(0))

            if current.remaining_time > 0:
                queue.append(current)
            else:
                current.finish_time = time
                if current.finish_time > current.deadline:
                    missed.append(current.name)
        else:
            time += 1
            energy += 0.5

    return timeline, energy, missed

def edf_scheduler(tasks):
    time = 0
    energy = 0
    timeline = []
    ready_queue = []
    tasks = sorted(tasks, key=lambda x: x.arrival_time)
    missed = []

    while tasks or ready_queue:
        while tasks and tasks[0].arrival_time <= time:
            ready_queue.append(tasks.pop(0))

        if ready_queue:
            ready_queue.sort(key=lambda x: x.deadline)
            current = ready_queue.pop(0)
            current.start_time = time
            time += current.burst_time
            current.finish_time = time
            timeline.append((current.name, current.start_time, current.finish_time))
            energy += current.burst_time * 1.2
            if current.finish_time > current.deadline:
                missed.append(current.name)
        else:
            time += 1
            energy += 0.5

    return timeline, energy, missed

def greenos_scheduler(tasks):
    time = 0
    energy = 0
    timeline = []
    ready_queue = []
    tasks = sorted(tasks, key=lambda x: x.arrival_time)
    missed = []

    while tasks or ready_queue:
        while tasks and tasks[0].arrival_time <= time:
            ready_queue.append(tasks.pop(0))

        if ready_queue:
            ready_queue.sort(key=lambda x: (x.deadline / x.burst_time))
            current = ready_queue.pop(0)
            current.start_time = time
            time += current.burst_time
            current.finish_time = time
            timeline.append((current.name, current.start_time, current.finish_time))
            energy += current.burst_time * 1.0
            if current.finish_time > current.deadline:
                missed.append(current.name)
        else:
            time += 1
            energy += 0.5

    return timeline, energy, missed

def draw_gantt(timeline, title, root):
    fig, ax = plt.subplots()
    for i, (task, start, end) in enumerate(timeline):
        ax.broken_barh([(start, end - start)], (i * 10, 9), facecolors='tab:green')
        ax.text(start + (end - start) / 2, i * 10 + 4, task, ha='center', va='center', color='white')
    ax.set_xlabel('Time')
    ax.set_yticks([i * 10 + 4 for i in range(len(timeline))])
    ax.set_yticklabels([task for task, _, _ in timeline])
    ax.set_title(title)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

# GUI App
def run_scheduler(algorithm):
    try:
        tasks = [
            Task("T1", 0, 4, 10),
            Task("T2", 1, 3, 8),
            Task("T3", 2, 2, 5),
            Task("T4", 3, 1, 6),
        ]

        algo_map = {
            "FCFS": fcfs_scheduler,
            "Round Robin": round_robin_scheduler,
            "EDF": edf_scheduler,
            "GreenOS": greenos_scheduler
        }

        func = algo_map[algorithm]
        timeline, energy, missed = func([Task(t.name, t.arrival_time, t.burst_time, t.deadline) for t in tasks])
        result_text.set(f"Energy Consumed: {energy:.2f}\nMissed Deadlines: {', '.join(missed) if missed else 'None'}")
        draw_gantt(timeline, f"{algorithm} Scheduling", gantt_frame)
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("GreenOS: Energy-Efficient Scheduler")

mainframe = ttk.Frame(root, padding="10")
mainframe.pack(fill=tk.BOTH, expand=True)

algo_label = ttk.Label(mainframe, text="Choose Scheduling Algorithm:")
algo_label.pack()

algo_choice = ttk.Combobox(mainframe, values=["FCFS", "Round Robin", "EDF", "GreenOS"])
algo_choice.set("GreenOS")
algo_choice.pack()

run_btn = ttk.Button(mainframe, text="Run Simulation", command=lambda: run_scheduler(algo_choice.get()))
run_btn.pack(pady=10)

result_text = tk.StringVar()
result_label = ttk.Label(mainframe, textvariable=result_text)
result_label.pack()

gantt_frame = ttk.Frame(root)
gantt_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
