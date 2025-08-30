from tkinter import *
import random
import time

# Clear text files for a new execution
with open("data.txt", 'w') as file: pass
with open("Results.txt", 'w') as file: pass

active_processes = False  # Variable to control if there are active processes
start_time = elapsed_time = 0  # Variables for the clock
q = 5  # Quantum (q)
new = []
ready = []
blocked = []  # Ready + blocked = 7 (including ready[0], execution)
finished = []

def generate_processes(n, names, operations):
    global total_processes, elapsed_time
    process_list = []
    for i in range(1, n + 1):
        process = [
            i,                      # 0. ID
            random.choice(names),   # 1. Name
            random.randint(1, 10),  # 2. NumberA
            random.choice(operations),  # 3. Operation
            random.randint(1, 10),  # 4. NumberB
            [random.randint(5, 13)]  # 5. List of times starting with requested time
        ]                           # -1. Result or error message
        process_list.append(process)
    return process_list

def get_data(filename="Results.txt"):
    global new, finished
    with open(filename, 'a') as file:
        if filename == "Results.txt":
            for process in finished:
                file.write(f"{process[0]}. {process[1]}\n{process[2]} {process[3]} {process[4]} = {process[6]}\n")
                file.write(f"Requested time: {process[5][0]}\n")
                file.write(f"Arrival time: {process[5][1]}\n")
                file.write(f"Waiting time: {process[5][2]}\n")
                file.write(f"Service time: {process[5][3]}\n")
                file.write(f"Return time: {process[5][2] + process[5][3]}\n")  # 5(c). Return Time: Total time from process arrival until completion.
                file.write(f"Completion time: {process[5][1] + process[5][2] + process[5][3]}\n")  # 6(b). Completion Time: Time when the process finished.
            file.write("_____________________________________________________________________________\n")
            file.write("                             Time Table                                \n")
            file.write("_____________________________________________________________________________\n")
            file.write("|N\t|Requested\t|Arrival\t|Wait\t|Service\t|Return\t\t|Completion\t\t|\n")
            for process in finished:
                file.write(f"|{process[0]}\t|{process[5][0]}\t\t\t|{process[5][1]}\t\t\t|{process[5][2]}\t\t|{process[5][3]}\t\t\t|{process[5][2] + process[5][3]}\t\t\t|{process[5][1] + process[5][2] + process[5][3]}\t\t\t\t|\n")
                # 5(c). Return Time: Total time from process arrival until completion.
                # 6(b). Completion Time: Time when the process finished.
            file.write("_____________________________________________________________________________\n")
            output_finished.delete(1.0, END)
            output_finished.insert(END, f"\nData obtained")
        else:
            for process in new:
                file.write(f"{process[0]}. {process[1]}\n{process[2]} {process[3]} {process[4]}\nTME: {process[5][0]}\n\n")

def update_clock():
    global start_time, elapsed_time, active_processes
    if active_processes:
        current_time = time.time()
        elapsed_time = int(current_time - start_time)
        clock.config(text=f"Global Clock: {elapsed_time}")
        root.after(1000, update_clock)  # Schedule next update

def process():
    global ready, new, blocked, finished, active_processes, q
    while new or ready or blocked:  # Improved condition to continue the cycle
        move_queues()  # Move from new to ready
        if ready:  # Show quantum
            quantum.config(text=f"Quantum: {q}")
        else:
            quantum.config(text=f"Quantum: N/A")
            q = 5
        pending.config(text=f"# Pending processes: {len(new)}")
        if ready:
            if len(ready[0][5]) < 5:  # Condition to add response time
                ready[0][5].append(elapsed_time - ready[0][5][1])  # 4(d). Response Time: Time elapsed from arrival until first attended.
        for i, process in enumerate(ready):  # For ready processes
            if i == 0:  # Show current process
                output_execution.insert(END, f"{process[0]}. {process[1]}\n{process[2]} {process[3]} {process[4]}\nSTME: {process[5][3]}, RTME: {process[5][0] - process[5][3]}\n\n")
            else:  # Show pending processes
                output_waiting.insert(END, f"{process[0]}. {process[1]}\n{process[2]} {process[3]} {process[4]}, TME: {process[5][0]}")
                if process[5][3] > 0:
                    output_waiting.insert(END, f", RTME: {process[5][0] - process[5][3]}")
                output_waiting.insert(END, f"\n\n")
                process[5][2] += 1
        for process in blocked:  # For blocked processes
            output_blocked.insert(END, f"{process[0]}. {process[1]}. BTME: {process[6]}\n")
            process[6] -= 1
        root.after(1000, root.update())  # Wait time to clear
        if ready:
            ready[0][5][3] += 1
            if ready[0][5][0] <= ready[0][5][3]:
                finish(False)
            else:
                if q > 1:
                    q -= 1
                else:
                    interrupt()
        if blocked:
            if blocked[0][6] == 0:
                blocked[0].pop()
                ready.append(process)
                blocked.pop(0)
        output_waiting.delete(1.0, END)
        output_execution.delete(1.0, END)
        output_blocked.delete(1.0, END)
    active_processes = False

def move_queues():
    global new, ready, blocked
    while len(ready) + len(blocked) < 7 and len(new) > 0:
        ready.append(new[0])  # 0. Time requested by the process
        if elapsed_time == 0:
            ready[-1][5].append(elapsed_time)  # 1(a). Arrival Time: Time when the process enters the system.
        else:
            ready[-1][5].append(elapsed_time + 1)
        ready[-1][5].append(0)  # 2(e). Waiting Time: Time the process has been waiting to use the processor.
        ready[-1][5].append(0)  # 3(f). Service Time: Time the process has been in the processor.
        new.pop(0)

def interrupt(event=True):
    global q
    q = 5
    if ready:
        ready.append(ready[0])
        ready.pop(0)

def block():
    global q
    q = 5
    if ready:
        ready[0].append(7)
        blocked.append(ready[0])
        ready.pop(0)

def finish(event=True):
    global q
    q = 5
    if ready:
        if event:
            ready[0].append("Error")
        else:
            ready[0].append(calculate_result(ready[0][2], ready[0][3], ready[0][4]))
        output_finished.insert(END, f"{ready[0][0]}. {ready[0][1]}\n{ready[0][2]} {ready[0][3]} {ready[0][4]} = {ready[0][6]}\n\n")
        finished.append(ready[0])
        ready.pop(0)

def calculate_result(n1, op, n2):
    if op == "+":
        result = n1 + n2
    elif op == "-":
        result = n1 - n2
    elif op == "*":
        result = n1 * n2
    elif op == "/":
        result = round(n1 / n2, 2)
    return result

def main():
    global new, start_time, active_processes
    names = ["Jose", "Carlos", "Carolina", "Juan"]
    operations = ["+", "-", "*", "/"]
    n = int(n_entry.get())
    new = generate_processes(n, names, operations)  # Process generation
    get_data("data.txt")  # Write the data
    active_processes = True
    start_time = time.time()
    update_clock()  # Clock initialization
    process()  # Simulation and process resolution

# Start window
root = Tk()
root.title("BatchProcessing")
root.geometry("646x540")

# Command keys to interrupt process and terminate processes by error
root.bind("<i>", interrupt)
root.bind("<e>", finish)
root.bind("<b>", block)

bInterrupt = Button(root, text="Interrupt", command=interrupt).place(x=220, y=250)
bBlock = Button(root, text="Block", command=block).place(x=300, y=250)
bFinish = Button(root, text="Finish", command=finish).place(x=367, y=250)

# Column 1
n_label = Label(root, text="# Processes:").place(x=1, y=3)
n_entry = Entry(root, width=10)
n_entry.place(x=70, y=6)
generate = Button(root, text="Generate", command=main).place(x=153, y=1)
waiting_label = Label(root, text="WAITING:").place(x=70, y=40)
output_waiting = Text(root, width=25, height=25)
output_waiting.place(x=1, y=80)
pending = Label(root, text="# Pending processes:")
pending.place(x=15, y=500)

# Column 2
quantum = Label(root, text="Quantum:")
quantum.place(x=285, y=2)
execution_label = Label(root, text="EXECUTION:").place(x=285, y=40)
output_execution = Text(root, width=25, height=10)
output_execution.place(x=221, y=80)
blocked_label = Label(root, text="BLOCKED:").place(x=285, y=285)
output_blocked = Text(root, width=25, height=10)
output_blocked.place(x=221, y=320)

# Column 3
clock = Label(root, text="Global Clock:")
clock.place(x=500, y=3)
finished_label = Label(root, text="FINISHED:").place(x=500, y=40)
output_finished = Text(root, width=25, height=25)
output_finished.place(x=441, y=80)
results = Button(root, text="GET RESULTS", command=get_data).place(x=475, y=500)

# Start window loop
root.mainloop()