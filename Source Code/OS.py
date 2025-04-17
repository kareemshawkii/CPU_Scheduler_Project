import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import time
import random
import copy # Import copy for deep copying process list
import traceback # For detailed error logging

class Process:
    def __init__(self, pid, arrival, burst, priority=None):
        self.pid = pid
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.remaining = int(burst)
        self.priority = int(priority) if priority is not None else None
        self.start_time = None
        self.finish_time = None
        # Assign a random visually distinct color on init
        self.color = f"#{random.randint(50, 200):02x}{random.randint(50, 200):02x}{random.randint(50, 200):02x}"
        self.wait_time = 0
        self.turnaround_time = 0
        self.status = "Waiting" # Add status attribute

    # Add __deepcopy__ for proper copying if needed later, though simple copy works here
    def __deepcopy__(self, memodict={}):
        # Create a new instance
        new_copy = Process(self.pid, self.arrival, self.burst, self.priority)
        # Copy relevant simulation state attributes
        new_copy.remaining = self.remaining
        new_copy.start_time = self.start_time
        new_copy.finish_time = self.finish_time
        new_copy.color = self.color # Keep the same color for consistency
        new_copy.wait_time = self.wait_time
        new_copy.turnaround_time = self.turnaround_time
        new_copy.status = self.status
        return new_copy

    def reset(self):
        """Resets process state for a new simulation run."""
        self.remaining = self.burst
        self.start_time = None
        self.finish_time = None
        self.wait_time = 0
        self.turnaround_time = 0
        self.status = "Waiting"


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("1000x700") # Adjusted size
        self.input_processes = [] # Store user inputs
        self.active_processes = [] # Processes used in simulation run
        self.completed_processes = [] # Store completed processes for stats
        self.running = False
        self.paused = False
        self.scheduler_thread = None
        self.current_time = 0
        self.gantt_data = []
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg="#e0f7fa") # Light cyan background

        # Title
        tk.Label(self.root, text="CPU Scheduler Simulator", font=("Helvetica", 20, "bold"),
                 bg="#e0f7fa", fg="#00695c").pack(pady=10) # Teal title

        # --- Main PanedWindow for Layout Flexibility ---
        main_pane = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="#e0f7fa")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Top Frame for Controls ---
        controls_frame = tk.Frame(main_pane, bg="#b2ebf2", bd=2, relief=tk.GROOVE) # Light blue controls frame
        main_pane.add(controls_frame, height=180) # Initial height, adjustable sash

        # Scheduler Selection Frame
        scheduler_frame = tk.Frame(controls_frame, bg="#b2ebf2")
        scheduler_frame.pack(pady=5, padx=10, fill=tk.X)

        self.scheduler_type = tk.StringVar(value="FCFS")
        options = ["FCFS", "SJF Non-Preemptive", "SJF Preemptive",
                   "Priority Non-Preemptive", "Priority Preemptive", "Round Robin"]

        tk.Label(scheduler_frame, text="Select Scheduler:", font=("Helvetica", 12),
                 bg="#b2ebf2").pack(side=tk.LEFT, padx=5, pady=5)
        # Use ttk.Combobox for better look & feel
        self.scheduler_combo = ttk.Combobox(scheduler_frame, textvariable=self.scheduler_type, values=options, state="readonly", font=("Helvetica", 11))
        self.scheduler_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.scheduler_combo.bind("<<ComboboxSelected>>", lambda e: self.change_inputs(self.scheduler_type.get()))


        # Input Frame
        self.input_frame = tk.Frame(controls_frame, bg="#b2ebf2")
        self.input_frame.pack(pady=5, padx=10, fill=tk.X)

        self.entries = {}
        labels = ["PID", "Arrival Time", "Burst Time"]
        entry_frame = tk.Frame(self.input_frame, bg="#b2ebf2") # Frame to hold entries side-by-side
        entry_frame.pack(fill=tk.X, pady=5)
        for label in labels:
            col_frame = tk.Frame(entry_frame, bg="#b2ebf2") # Frame for Label+Entry pair
            tk.Label(col_frame, text=label + ":", font=("Helvetica", 11), bg="#b2ebf2").pack(side=tk.TOP, padx=5)
            entry = ttk.Entry(col_frame, font=("Helvetica", 11), width=10) # Use ttk.Entry
            entry.pack(side=tk.TOP, padx=5)
            col_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2, padx=5)
            self.entries[label] = entry

        # Dynamic Input Rows Frame
        self.dynamic_input_frame = tk.Frame(controls_frame, bg="#b2ebf2")
        self.dynamic_input_frame.pack(pady=5, padx=10, fill=tk.X)


        # Priority and Quantum rows (Managed within dynamic_input_frame)
        self.priority_row = tk.Frame(self.dynamic_input_frame, bg="#b2ebf2")
        tk.Label(self.priority_row, text="Priority:", font=("Helvetica", 11), bg="#b2ebf2").pack(side=tk.LEFT, padx=5)
        self.priority_entry = ttk.Entry(self.priority_row, font=("Helvetica", 11), width=10) # Use ttk.Entry
        self.priority_entry.pack(side=tk.LEFT, padx=5)

        self.quantum_row = tk.Frame(self.dynamic_input_frame, bg="#b2ebf2")
        tk.Label(self.quantum_row, text="Quantum:", font=("Helvetica", 11), bg="#b2ebf2").pack(side=tk.LEFT, padx=5)
        self.quantum_entry = ttk.Entry(self.quantum_row, font=("Helvetica", 11), width=10) # Use ttk.Entry
        self.quantum_entry.insert(0, "2")
        self.quantum_entry.pack(side=tk.LEFT, padx=5)


        # Button Frame
        button_frame = tk.Frame(controls_frame, bg="#b2ebf2")
        button_frame.pack(pady=10, padx=10)

        # Define button styles
        style = ttk.Style()
        style.configure("Green.TButton", foreground="white", background="#4CAF50", font=("Helvetica", 10))
        style.map("Green.TButton", background=[('active', '#388E3C')]) # Darker green on hover/press
        style.configure("Orange.TButton", foreground="white", background="#FF9800", font=("Helvetica", 10))
        style.map("Orange.TButton", background=[('active', '#F57C00')])
        style.configure("Red.TButton", foreground="white", background="#F44336", font=("Helvetica", 10))
        style.map("Red.TButton", background=[('active', '#D32F2F')])
        style.configure("Blue.TButton", foreground="white", background="#2196F3", font=("Helvetica", 10))
        style.map("Blue.TButton", background=[('active', '#1976D2')])
        style.configure("Teal.TButton", foreground="white", background="#008CBA", font=("Helvetica", 10))
        style.map("Teal.TButton", background=[('active', '#006064')])


        def create_button(parent, text, style_name, command, width=12):
              btn = ttk.Button(parent, text=text, command=command, style=style_name, width=width)
              btn.pack(side=tk.LEFT, padx=5)
              return btn

        buttons_config = [
            ("Add Process", "Green.TButton", self.add_process),
            ("Delete Last", "Orange.TButton", self.delete_last_process),
            ("Clear All", "Red.TButton", self.delete_all_processes),
            ("Start Live", "Teal.TButton", self.start_live),
            ("Pause/Resume", "Orange.TButton", self.toggle_pause),
            ("Run Static", "Blue.TButton", self.run_static)
        ]

        for text, style_name, command in buttons_config:
            create_button(button_frame, text, style_name, command)


        # --- Middle Frame for Gantt Chart ---
        gantt_outer_frame = tk.Frame(main_pane, bg="#e0f7fa") # Use main background color
        gantt_label = tk.Label(gantt_outer_frame, text="Gantt Chart", font=("Helvetica", 14, "bold"), bg="#e0f7fa", fg="#00695c")
        gantt_label.pack(pady=(5,0))
        self.gantt_frame = tk.Frame(gantt_outer_frame, bg="#ffffff", bd=2, relief=tk.SUNKEN)
        self.gantt_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.gantt_chart = tk.Canvas(self.gantt_frame, bg="white", height=80, scrollregion=(0,0,1000,80)) # Initial scroll region
        # Add horizontal scrollbar for Gantt
        gantt_hsb = ttk.Scrollbar(self.gantt_frame, orient=tk.HORIZONTAL, command=self.gantt_chart.xview)
        self.gantt_chart.configure(xscrollcommand=gantt_hsb.set)
        gantt_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.gantt_chart.pack(fill=tk.X, expand=True) # Fill available horizontal space

        main_pane.add(gantt_outer_frame, height=120) # Initial height, adjustable


        # --- Bottom Frame for Process Table and Stats ---
        results_frame = tk.Frame(main_pane, bg="#e0f7fa")
        main_pane.add(results_frame) # Takes remaining space

        table_label = tk.Label(results_frame, text="Process Details", font=("Helvetica", 14, "bold"), bg="#e0f7fa", fg="#00695c")
        table_label.pack(pady=(5,0))
        # Process Table Frame with Scrollbars
        table_frame = tk.Frame(results_frame, bg="#e0f7fa")
        table_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        cols = ("PID", "Arrival", "Burst", "Priority", "Remaining", "Status", "Start", "Finish", "Wait", "Turnaround")
        self.process_table = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)

        col_widths = {"PID": 50, "Arrival": 60, "Burst": 60, "Priority": 60, "Remaining": 70,
                      "Status": 90, "Start": 60, "Finish": 60, "Wait": 70, "Turnaround": 70}
        col_anchors = {"PID": tk.CENTER, "Arrival": tk.CENTER, "Burst": tk.CENTER, "Priority": tk.CENTER, "Remaining": tk.CENTER,
                       "Status": tk.W, "Start": tk.CENTER, "Finish": tk.CENTER, "Wait": tk.CENTER, "Turnaround": tk.CENTER}

        for col in cols:
             self.process_table.heading(col, text=col, anchor=tk.CENTER)
             self.process_table.column(col, width=col_widths.get(col, 85), anchor=col_anchors.get(col, tk.CENTER), stretch=tk.NO)

        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.process_table.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.process_table.xview)
        self.process_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.process_table.pack(fill=tk.BOTH, expand=True)

        # Stats Label
        self.stats = tk.Label(results_frame, text="Avg Waiting Time: - | Avg Turnaround Time: -", font=("Helvetica", 12, "bold"),
                              bg="#e0f7fa", fg="#d81b60", height=2) # Pinkish color for stats, fixed height
        self.stats.pack(pady=5, fill=tk.X, padx=10)

        self.change_inputs("FCFS") # Initial UI setup
        self.display_processes_in_table() # Display initially empty table
        # Set initial PID
        self.entries["PID"].insert(0, "1")


    def change_inputs(self, value):
        """Shows/hides Priority and Quantum inputs based on selected scheduler."""
        # Hide both first
        self.priority_row.pack_forget()
        self.quantum_row.pack_forget()
        # Show based on selection
        if "Priority" in value:
            self.priority_row.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2, padx=10) # Use pack side=LEFT
        if "Round Robin" in value:
            self.quantum_row.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2, padx=10) # Use pack side=LEFT

    def add_process(self):
        """Adds a process from the input fields to the input_processes list."""
        try:
            pid_str = self.entries["PID"].get()
            arrival_str = self.entries["Arrival Time"].get()
            burst_str = self.entries["Burst Time"].get()

            if not all([pid_str, arrival_str, burst_str]):
                 messagebox.showerror("Input Error", "PID, Arrival Time, and Burst Time are required.")
                 return

            pid = int(pid_str)
            arrival = int(arrival_str)
            burst = int(burst_str)

            # Validate inputs
            if arrival < 0 or burst <= 0:
                 messagebox.showerror("Input Error", "Arrival time must be >= 0 and Burst time must be > 0.")
                 return
            if any(p.pid == pid for p in self.input_processes):
                 messagebox.showerror("Input Error", f"Process with PID {pid} already exists.")
                 return

            priority = None
            if "Priority" in self.scheduler_type.get():
                p_str = self.priority_entry.get()
                if not p_str:
                     messagebox.showerror("Input Error", "Priority value is required for Priority Scheduling.")
                     return
                priority = int(p_str)
                if priority < 0: # Assuming lower number means higher priority, non-negative
                     messagebox.showerror("Input Error", "Priority must be a non-negative integer.")
                     return

            process = Process(pid, arrival, burst, priority)
            self.input_processes.append(process)
            self.display_processes_in_table() # Update the main table

            # Clear entries except PID
            self.entries["Arrival Time"].delete(0, tk.END)
            self.entries["Burst Time"].delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)

            # Auto-increment PID suggestion
            next_pid = pid + 1
            self.entries["PID"].delete(0, tk.END)
            self.entries["PID"].insert(0, str(next_pid))
            # Set focus to Arrival Time for next entry
            self.entries["Arrival Time"].focus_set()


        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for PID, Arrival, and Burst Time (and Priority if applicable).")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error adding process: {str(e)}")
            traceback.print_exc()

    def delete_last_process(self):
        """Removes the most recently added process."""
        if self.input_processes:
            self.input_processes.pop()
            self.display_processes_in_table()
            self.clear_results(clear_input=False) # Clear only results, not input list
        else:
            messagebox.showinfo("Info", "No processes to delete.")

    def delete_all_processes(self):
        """Clears all input processes and simulation results."""
        self.input_processes.clear()
        self.display_processes_in_table()
        self.clear_results(clear_input=True)
        self.entries["PID"].delete(0, tk.END) # Reset PID entry
        self.entries["PID"].insert(0, "1")

    def clear_results(self, clear_input=False):
        """Clears Gantt chart and stats, resets simulation state."""
        if self.running:
            self.running = False # Signal thread to stop if running
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                 try:
                     self.scheduler_thread.join(timeout=0.5) # Wait briefly
                 except RuntimeError:
                     pass # Ignore if thread already finished
        self.running = False
        self.paused = False
        self.gantt_chart.delete("all")
        self.stats.config(text="Avg Waiting Time: - | Avg Turnaround Time: -")
        self.completed_processes.clear()
        self.active_processes.clear()
        self.gantt_data.clear()
        self.current_time = 0

        if clear_input:
             self.input_processes.clear()

        # Reset status in the original input list if not clearing it
        if not clear_input:
             for p in self.input_processes:
                 p.reset()

        self.display_processes_in_table() # Refresh table

    def display_processes_in_table(self, processes_to_display=None):
        """Updates the main table with process details."""
        self.process_table.delete(*self.process_table.get_children())

        # Decide which list of processes to show (active during simulation, input otherwise)
        display_list = processes_to_display if processes_to_display is not None else self.input_processes

        # Sort by PID for consistent display order
        display_list_sorted = sorted(display_list, key=lambda p: p.pid)

        for p in display_list_sorted:
            # Format values, handling None or initial state
            priority_val = p.priority if p.priority is not None else "-"
            start_val = p.start_time if p.start_time is not None else "-"
            finish_val = p.finish_time if p.finish_time is not None else "-"
            # Show calculated wait/turnaround only when finished
            wait_val = f"{p.wait_time:.2f}" if p.finish_time is not None else "-"
            turnaround_val = f"{p.turnaround_time:.2f}" if p.finish_time is not None else "-"
            # Show remaining time during run, or burst time initially/after completion
            remaining_val = p.remaining if p.status in ["Running", "Ready"] else (0 if p.status == "Completed" else p.burst)

            values = (p.pid, p.arrival, p.burst, priority_val, remaining_val, p.status,
                      start_val, finish_val, wait_val, turnaround_val)
            self.process_table.insert("", tk.END, values=values)

    def toggle_pause(self):
        """Toggles the paused state of the simulation."""
        if self.running:
            self.paused = not self.paused
            state = "Paused" if self.paused else "Resumed"
            print(f"Simulation {state}") # Optional console feedback
        else:
             messagebox.showinfo("Info", "Simulation is not running.")


    def start_simulation(self, live):
        """Prepares and starts the simulation thread."""
        if self.running:
            messagebox.showwarning("Warning", "Simulation is already running.")
            return
        if not self.input_processes:
            messagebox.showerror("Error", "No processes added to simulate.")
            return

        # Validate Quantum for RR just before starting
        if self.scheduler_type.get() == "Round Robin":
             try:
                 q = int(self.quantum_entry.get())
                 if q <= 0:
                     messagebox.showerror("Input Error", "Quantum must be a positive integer for Round Robin.")
                     return
             except ValueError:
                 messagebox.showerror("Input Error", "Invalid Quantum value for Round Robin.")
                 return

        self.clear_results(clear_input=False) # Clear previous run results, keep input list

        # Create deep copies of processes for the simulation run
        self.active_processes = copy.deepcopy(self.input_processes)
        for p in self.active_processes: # Ensure reset state for the run
             p.reset()

        self.running = True
        self.paused = False
        self.scheduler_thread = Thread(target=self.run_scheduler, args=(live,), daemon=True)
        self.scheduler_thread.start()

    def start_live(self):
        """Starts the simulation in live (step-by-step) mode."""
        self.start_simulation(live=True)

    def run_static(self):
        """Starts the simulation in static (instant results) mode."""
        self.start_simulation(live=False)

    # ==========================================================================
    # CORE SCHEDULER LOGIC 
    # ==========================================================================
    def run_scheduler(self, live=True):
        try:
            scheduler_type = self.scheduler_type.get()
            quantum = None
            if scheduler_type == "Round Robin":
                try:
                    # Quantum already validated in start_simulation, but get value here
                    quantum = int(self.quantum_entry.get())
                except ValueError: # Should not happen if validated before
                    self.root.after(0, lambda: messagebox.showerror("Input Error", "Invalid Quantum value."))
                    self.running = False
                    return

            # Use the copied list for the simulation
            processes_to_schedule = self.active_processes
            self.completed_processes = []
            ready_queue = []
            self.current_time = 0
            self.gantt_data = [] # Stores (pid_str, start_time, duration, color)

            current_process = None

            n_processes = len(processes_to_schedule)

            # Main simulation loop: Continue while not all processes are completed OR there are still ready/waiting processes
            while len(self.completed_processes) < n_processes:
                # Check for pause/stop signals
                while self.paused and self.running:
                    time.sleep(0.1)
                if not self.running: # Check if stop was requested externally
                     print("Simulation stopped externally.")
                     # Update UI one last time with current state before exiting thread
                     self.root.after(0, self.update_ui, self.gantt_data, self.active_processes)
                     return # Exit the thread

                # 1. Add newly arrived processes to the ready queue
                newly_arrived = [p for p in processes_to_schedule
                                 if p.arrival <= self.current_time and p.status == "Waiting"]
                if newly_arrived:
                    for p in newly_arrived:
                        p.status = "Ready"
                        ready_queue.append(p)
                    # Re-sort ready queue if a preemptive algorithm is used and new processes arrived
                    if ready_queue and "Preemptive" in scheduler_type:
                        if "SJF" in scheduler_type:
                            ready_queue.sort(key=lambda p: p.remaining)
                        elif "Priority" in scheduler_type:
                            ready_queue.sort(key=lambda p: (p.priority, p.arrival))

                # Check if CPU is idle AND there are no more processes waiting to arrive BUT queue is empty
                # This means we might have finished all processes but loop condition hasn't updated
                if not current_process and not ready_queue and all(p.status == "Completed" or p.arrival > self.current_time for p in processes_to_schedule):
                     # If there are processes that haven't arrived yet, advance time to next arrival
                     future_arrivals = [p.arrival for p in processes_to_schedule if p.arrival > self.current_time]
                     if future_arrivals:
                           next_arrival_time = min(future_arrivals)
                           idle_duration = next_arrival_time - self.current_time
                           # Add Idle block to Gantt
                           if self.gantt_data and self.gantt_data[-1][0] == "Idle":
                               last_entry = self.gantt_data[-1]
                               self.gantt_data[-1] = (last_entry[0], last_entry[1], last_entry[2] + idle_duration, last_entry[3])
                           else:
                               self.gantt_data.append(("Idle", self.current_time, idle_duration, "#E0E0E0")) # Grey for idle
                           self.current_time = next_arrival_time
                           if live: # Update UI if live during idle skip
                               self.root.after(0, self.update_ui, self.gantt_data, self.active_processes)
                               time.sleep(0.1) # Small sleep to allow UI update
                           continue # Skip to next iteration to add the newly arrived process
                     else:
                           # No future arrivals, and queue is empty, must be done
                           break # Exit the main simulation loop

                # 2. Decide which process runs next (or if CPU is idle)

                # Add the previously running process back to ready queue if it was preempted (Preemptive SJF/Priority only)
                # RR handles its own requeueing after its quantum block.
                if current_process and current_process.status == "Running" and current_process.remaining > 0:
                    if "Preemptive" in scheduler_type: # Check if a preemptive algorithm is running
                        current_process.status = "Ready"
                        ready_queue.append(current_process)
                        # Re-sort after adding back
                        if "SJF" in scheduler_type:
                            ready_queue.sort(key=lambda p: p.remaining)
                        elif "Priority" in scheduler_type:
                            ready_queue.sort(key=lambda p: (p.priority, p.arrival))
                        current_process = None # Clear current process as it needs re-selection/confirmation

                # --- Sort the ready queue based on the algorithm (if needed and not RR) ---
                # Sorting for preemptive done above or when selecting. Non-preemptive selects once.
                # FCFS relies on arrival order (often implicit by append order if checked correctly)
                if ready_queue and not current_process: # Only sort/select if CPU is idle
                     if scheduler_type == "FCFS":
                         ready_queue.sort(key=lambda p: p.arrival) # Ensure FCFS order
                     elif scheduler_type == "SJF Non-Preemptive":
                          ready_queue.sort(key=lambda p: p.burst) # Non-preemptive uses original burst
                     elif scheduler_type == "Priority Non-Preemptive":
                          ready_queue.sort(key=lambda p: (p.priority, p.arrival))
                     # Preemptive sorting already happened if needed. RR is FIFO (pop(0)).

                # --- Select the next process to run ---
                if not current_process and ready_queue: # Select only if CPU is free
                    current_process = ready_queue.pop(0) # Take from front (works for FCFS, RR, and sorted P/SJF)
                    current_process.status = "Running"
                    if current_process.start_time is None:
                        current_process.start_time = self.current_time

                # 3. Execute a time slice or unit
                if current_process:
                    pid_str = f"P{current_process.pid}"
                    color = current_process.color

                    # --- Branch execution logic based on RR or other algorithms ---
                    if scheduler_type == "Round Robin":
                        # --- RR Execution Logic (Quantum Block) ---
                        run_duration = min(current_process.remaining, quantum)

                        # --- Gantt Chart Update for the block ---
                        self.gantt_data.append((pid_str, self.current_time, run_duration, color))

                        # --- Simulate Block Execution ---
                        if live:
                            # In live mode, simulate step-by-step for visualization
                            for i in range(run_duration):
                                while self.paused and self.running: time.sleep(0.1) # Allow pause within block
                                if not self.running: return # Allow stop within block

                                current_process.remaining -= 1
                                self.current_time += 1

                                # Check for new arrivals *during* the quantum slice in live mode
                                live_newly_arrived = [p for p in processes_to_schedule
                                                  if p.arrival == self.current_time and p.status == "Waiting"]
                                for p in live_newly_arrived:
                                      p.status = "Ready"
                                      ready_queue.append(p) # Add arrivals immediately in live

                                # Update UI every step in live mode
                                # Update Gantt data duration for live display step by step
                                current_gantt_block = list(self.gantt_data[-1])
                                current_gantt_block[2] = i + 1 # Update duration visually
                                self.gantt_data[-1] = tuple(current_gantt_block)
                                self.root.after(0, self.update_ui, self.gantt_data, self.active_processes)
                                time.sleep(1)

                                if current_process.remaining == 0: break # Exit block early if finished

                        else: # Static mode: Execute block instantly
                            # Need to check for arrivals during the block even in static mode
                            block_end_time = self.current_time + run_duration
                            arrivals_during_block = [p for p in processes_to_schedule
                                                     if p.arrival > self.current_time and p.arrival <= block_end_time and p.status == "Waiting"]
                            for p in arrivals_during_block:
                                 p.status = "Ready"
                                 ready_queue.append(p)

                            current_process.remaining -= run_duration
                            self.current_time = block_end_time # Advance time by full duration

                        # --- Post-Quantum Check ---
                        if current_process.remaining == 0:
                            # Process completed
                            current_process.finish_time = self.current_time # Finish time is end of block
                            current_process.turnaround_time = current_process.finish_time - current_process.arrival
                            current_process.wait_time = current_process.turnaround_time - current_process.burst
                            current_process.status = "Completed"
                            self.completed_processes.append(current_process)
                            for p in self.active_processes: # Update status in display list
                                if p.pid == current_process.pid:
                                     p.status = "Completed"; p.finish_time = current_process.finish_time
                                     p.wait_time = current_process.wait_time; p.turnaround_time = current_process.turnaround_time
                                     p.start_time = current_process.start_time; p.remaining = 0; break # Set remaining to 0
                            current_process = None # CPU becomes free

                        else:
                            # Quantum expired (or finished exactly on quantum), process not finished
                            current_process.status = "Ready"
                            # Check for new arrivals at the exact end time of the quantum slice, before appending back
                            exact_end_arrivals = [p for p in processes_to_schedule
                                                  if p.arrival == self.current_time and p.status == "Waiting"]
                            for p in exact_end_arrivals:
                                p.status = "Ready"
                                ready_queue.append(p)
                            # Now append the current RR process to the end
                            ready_queue.append(current_process)
                            current_process = None # CPU becomes free

                    else:
                        # --- Execution Logic for FCFS, SJF, Priority (One Time Unit) ---
                        # --- Gantt Chart Update ---
                        if self.gantt_data and self.gantt_data[-1][0] == pid_str:
                             last_entry = self.gantt_data[-1]
                             self.gantt_data[-1] = (last_entry[0], last_entry[1], last_entry[2] + 1, last_entry[3])
                        else:
                             self.gantt_data.append((pid_str, self.current_time, 1, color))

                        # --- Execute One Unit ---
                        current_process.remaining -= 1

                        # Advance time by one unit *before* checking completion for consistency
                        self.current_time += 1

                        # --- Check for Completion ---
                        if current_process.remaining == 0:
                            current_process.finish_time = self.current_time # Finish time is *now*
                            current_process.turnaround_time = current_process.finish_time - current_process.arrival
                            current_process.wait_time = current_process.turnaround_time - current_process.burst
                            current_process.status = "Completed"
                            self.completed_processes.append(current_process)
                            for p in self.active_processes: # Update status in display list
                                if p.pid == current_process.pid:
                                     p.status = "Completed"; p.finish_time = current_process.finish_time
                                     p.wait_time = current_process.wait_time; p.turnaround_time = current_process.turnaround_time
                                     p.start_time = current_process.start_time; p.remaining = 0; break # Set remaining to 0
                            current_process = None # CPU becomes free
                        # No quantum check needed for non-RR algorithms
                        # Preemption check happens implicitly at the start of the next loop iteration


                else: # CPU is Idle (and no process could be selected from ready queue)
                    # If we got here, it means ready_queue was empty, but maybe processes will arrive later.
                    # Advance time by 1 unit and add Idle block. The check at the start of the loop handles jumping ahead.
                    if self.gantt_data and self.gantt_data[-1][0] == "Idle":
                         last_entry = self.gantt_data[-1]
                         self.gantt_data[-1] = (last_entry[0], last_entry[1], last_entry[2] + 1, last_entry[3])
                    else:
                         self.gantt_data.append(("Idle", self.current_time, 1, "#E0E0E0"))
                    self.current_time += 1


                # 5. Update UI (if live and NOT RR, as RR updates within its block)
                if live and scheduler_type != "Round Robin":
                    self.root.after(0, self.update_ui, self.gantt_data, self.active_processes)
                    time.sleep(1)


            # Simulation finished
            # One final UI update for static mode or if live mode ended abruptly
            self.root.after(0, self.finalize_simulation)

        except Exception as e:
             print(f"Error during simulation: {e}")
             traceback.print_exc()
             self.root.after(0, lambda: messagebox.showerror("Runtime Error", f"An error occurred during simulation: {e}\n\n{traceback.format_exc()}"))
        finally:
            # Ensure running flag is reset even if errors occur
             self.running = False


    def finalize_simulation(self):
        """Called after the simulation loop finishes to update UI finally."""
        print("Simulation finished.")
        # Ensure the final state is accurately displayed
        self.update_ui(self.gantt_data, self.active_processes)
        self.show_stats()
        self.running = False # Ensure flag is reset
        messagebox.showinfo("Simulation Complete", f"Simulation finished at time {self.current_time}.")


    def update_ui(self, gantt_data, process_list):
        """Updates Gantt chart and process table. Called from scheduler thread via root.after."""
        # Check if root window still exists
        if not self.root.winfo_exists():
            self.running = False # Stop simulation if window closed
            return

        # --- Update Gantt Chart ---
        self.gantt_chart.delete("all")
        if not gantt_data:
            self.gantt_chart.xview_moveto(0) # Reset scroll
            self.gantt_chart.config(scrollregion=(0,0,100,80))
            self.display_processes_in_table(process_list) # Update table even if gantt empty
            return

        max_time = 0
        if gantt_data:
             max_time = gantt_data[-1][1] + gantt_data[-1][2] # End time of the last block

        # Use a reasonable minimum width for the canvas content
        min_canvas_width = max(max_time * 15, 500) # Ensure at least 500px or 15px per time unit
        self.gantt_chart.config(scrollregion=(0, 0, min_canvas_width + 20, 80)) # Update scroll region (+20 padding)

        canvas_width = min_canvas_width # Use calculated content width for scale
        scale = canvas_width / max_time if max_time > 0 else 1
        bar_height = 45 # Slightly smaller bar
        y_offset = 10
        x_offset = 10

        last_time_label_pos = -100 # Initialize to ensure first label draws
        min_label_spacing_pixels = 25 # Minimum pixels between time labels

        for pid_str, start_time, duration, color in gantt_data:
            x1 = x_offset + start_time * scale
            x2 = x_offset + (start_time + duration) * scale
            # Ensure minimum width for visibility, especially for duration 1 at small scales
            display_width = max(x2 - x1, 1.5)
            self.gantt_chart.create_rectangle(x1, y_offset, x1 + display_width, y_offset + bar_height,
                                              fill=color, outline="#333333", width=1) # Darker outline
            # Add text only if bar is wide enough
            if display_width > 15: # Only add text if width is > 15 pixels
                 # Center text vertically
                 text_y = y_offset + bar_height / 2
                 self.gantt_chart.create_text((x1 + x1 + display_width) / 2, text_y,
                                            text=pid_str, fill="black", font=("Helvetica", 9, "bold")) # Bold text


        # Draw time markers more sparsely if needed
        time_marker_y = y_offset + bar_height + 5
        time_label_y = time_marker_y + 5
        for t in range(max_time + 1):
             x = x_offset + t * scale
             # Draw tick mark
             self.gantt_chart.create_line(x, y_offset + bar_height, x, time_marker_y, fill="#666666")
             # Draw time label conditionally based on spacing
             if x >= last_time_label_pos + min_label_spacing_pixels or t == 0 or t == max_time:
                 self.gantt_chart.create_text(x, time_label_y, text=str(t),
                                            anchor=tk.N, font=("Helvetica", 8), fill="#333333")
                 last_time_label_pos = x


        # --- Update Process Table ---
        # Pass the currently active list which has updated statuses and times
        self.display_processes_in_table(process_list)


    def show_stats(self):
        """Calculates and displays average waiting and turnaround times."""
        # Use completed_processes list which should have final calculated values
        if not self.completed_processes:
            self.stats.config(text="Avg Waiting Time: - | Avg Turnaround Time: -")
            return

        # Filter just in case (should not be needed if logic is correct)
        actually_completed = [p for p in self.completed_processes if p.finish_time is not None]
        if not actually_completed:
             self.stats.config(text="Avg Waiting Time: - | Avg Turnaround Time: -")
             return

        total_wt = sum(p.wait_time for p in actually_completed)
        total_tt = sum(p.turnaround_time for p in actually_completed)
        n = len(actually_completed)

        if n > 0:
            avg_wt = total_wt / n
            avg_tt = total_tt / n
            self.stats.config(text=f"Avg Waiting Time: {avg_wt:.2f} | Avg Turnaround Time: {avg_tt:.2f}")
        else:
            self.stats.config(text="Avg Waiting Time: 0.00 | Avg Turnaround Time: 0.00")

# ==========================================================================
# Main execution
# ==========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    # Apply a theme for better widget appearance
    try:
        style = ttk.Style(root)
        # ('clam', 'alt', 'default', 'classic')
        available_themes = style.theme_names()
        # print(f"Available themes: {available_themes}")
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
    except Exception as e:
        print(f"Could not set ttk theme: {e}")

    app = SchedulerApp(root)
    root.mainloop()