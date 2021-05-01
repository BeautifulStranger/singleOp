from tkinter import *
from tkinter import ttk

def add_instruction(*args):
	try:
		for i in range(len(memory)):
			if arrow_labels[i]['text'] == arrow_symbols[1] or arrow_labels[i]['text'] == arrow_symbols[2]:
				value = new_instruction.get()
				memory[i] = value
				memory_labels[i].configure(text = value)
				arrow_labels[i].configure(text = arrow_symbols[2])
				step_button.state(['disabled'])
				move_cursor(2)
				break
	except ValueError:
		pass

def run_program(*args):
	move_cursor(2)
	step_button.state(['disabled'])

def move_cursor(mode):
	for i in range(len(memory)):
		if arrow_labels[i]['text'] != arrow_symbols[0]:
			arrow_labels[i].configure(text=arrow_symbols[0])
			arrow_labels[(i+1)%len(memory)].configure(text=arrow_symbols[mode])
			break

def step_program(*args):
	move_cursor(1)
	edit_button.state(['disabled'])
	run_button.state(['disabled'])

def reset_program(*args):
	for i in range(len(memory)):
		memory_labels[i].configure(text = memory[i])
		arrow_labels[i].configure(text = arrow_symbols[0])
	arrow_labels[0].configure(text = arrow_symbols[1])
	edit_button.state(['!disabled'])
	step_button.state(['!disabled'])
	run_button.state(['!disabled'])

def clear_memory(*args):
	for i in range(len(memory)):
		memory[i] = "0000 0000 0000"
	reset_program()

root = Tk()
root.title("Single Operation Computer")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, stick=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
memory_view=ttk.Frame(mainframe, relief="ridge", padding="3 3 3 3")
memory_view.grid(column=1, row=1, rowspan=10, stick=(N, W, E, S))
#memory_view.rowconfigure(0, weight=1)

instruction = StringVar()
new_instruction = ttk.Entry(mainframe, width=7, textvariable=instruction)
new_instruction.grid(column=3, row=10, stick=(W, E))

ttk.Label(mainframe, text="MEMORY", justify="center", anchor="center",  background="light blue", relief="raised").grid(column=1, row=0, stick=(W, E))

initial_memory = 30
memory = ["0000 0000 0000"  for i in range(initial_memory)]
memory_labels = []
arrow_labels = []
arrow_symbols = ["|", "|<--", "|<<-"]
for i in range(len(memory)):
	memory_labels.append(ttk.Label(memory_view, text = memory[i]))
	memory_labels[i].grid(column=1, row = i, stick=W)
	arrow_labels.append(ttk.Label(memory_view, text=arrow_symbols[0]))
	arrow_labels[i].grid(column=2, row=i, stick=W)

arrow_labels[0].configure(text=arrow_symbols[1])

edit_button = ttk.Button(mainframe, text="Add Intruction", command=add_instruction)
edit_button.grid(column=3, row=9, stick=W)
run_button = ttk.Button(mainframe, text="Run", command=run_program)
run_button.grid(column=3, row=1, stick=W)
step_button = ttk.Button(mainframe, text="Step", command=step_program)
step_button.grid(column=3, row=2, stick=W)
ttk.Button(mainframe, text="Reset", command=reset_program).grid(column=3, row=3, stick=W)
ttk.Button(mainframe, text="Clear memory", command=clear_memory).grid(column=3, row=4, stick=W)

ttk.Label(mainframe, text="A: 0").grid(column=3, row=6, stick=W)
ttk.Label(mainframe, text="B: 0").grid(column=3, row=7, stick=W)
ttk.Label(mainframe, text="C: 0").grid(column=3, row=8, stick=W)

for child in mainframe.winfo_children():
	child.grid_configure(padx=5, pady=5)

new_instruction.focus()
#root.bind("<Return>", calculate)

root.mainloop()

