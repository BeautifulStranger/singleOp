'''
To Do
At the moment the memory values are not capped to 8bits
Negative number display is broken
'''


from tkinter import *
from tkinter import ttk

def halt_execution(reason=""):
	run_button.state(['disabled'])
	step_button.state(['disabled'])
	if reason == "memory":
		message = "Ops! Access out of bounds. "
	stat_message.configure(text = message + "Halted.", foreground = "red")

def memory_read(address):
	try:
		data = memory[address]
		return data
	except IndexError:
		halt_execution("memory")
		return 0

def memory_write(address, value):
	global memory
	try:
		memory[address] = value
	except IndexError:
		halt_execution("memory")

def processor():
	global inner_step, memory, current_instruction
	k = memory_read(current_instruction)
	if inner_step == 0:
		idv_A.configure(text = "A: " + decode_binary_instruction(memory_read(k)))
		idv_B.configure(text="B:")
		idv_C.configure(text="C:")
		idv_Z.configure(text="Z:")
		inner_step += 1
	elif inner_step == 1:
		idv_B.configure(text = "B: " + decode_binary_instruction(memory_read(k)))
		inner_step += 1
	elif inner_step == 2:
		idv_C.configure(text = "C: " + decode_binary_instruction(k))
		inner_step = 0
		a = memory_read(memory_read(current_instruction - 2))
		b = memory_read(memory_read(current_instruction - 1))
		z = b - a
		idv_Z.configure(text = "Z: " + decode_binary_instruction(z))
		memory_write(memory_read(current_instruction - 1), z)
		if 0 >= z:
			current_instruction = k - 1

def encode_binary_instruction(str_instruction):
	str_base = (numerical_rep.get())[-1]
	if str_base == 'x':
		base = 16
	elif str_base == 'b':
		base = 2
	else:
		base = 10
	return int(str_instruction, base)

def decode_binary_instruction(bin_instruction):
	str_instruction = format(bin_instruction, numerical_rep.get())
	return str_instruction[0:4] + " " + str_instruction[4:8]

def update_memory_view(*args):
	for i in range(24):
		memory_position = i - highlight_pos + current_instruction
		if len(memory) > memory_position >= 0:
			memory_labels[i].configure(text = "{:04x}: ".format(memory_position) + decode_binary_instruction(memory[memory_position]) + "({})".format(memory[memory_position]))
		else:
			memory_labels[i].configure(text = "")

def increment_instruction(reverse = False):
	global current_instruction
	direction = 1
	if reverse:
		direction = -1
	check_bound = current_instruction + direction
	current_instruction = check_bound % len(memory)
	#if len(memory) > check_bound >= 0:
	#	current_instruction = check_bound
	update_memory_view()

def input_validator(text):
	is_valid = False
	pattern_switch = (numerical_rep.get())[-1]
	if pattern_switch == 'x':
		pattern = '^[0-9a-f]*$'
	elif pattern_switch == 'b':
		pattern = '^[0-1]*$'
	else:
		pattern = '^[0-9]*$'
	stripped = text.split()
	add_button.state(['disabled'])
	if len(stripped) == 1:
		if re.match(pattern, stripped[0]):
			if 256 > encode_binary_instruction(stripped[0]) >= 0:
				add_button.state(['!disabled'])
	return True

def add_instruction(*args):
	try:
		global memory, program_code
		value = new_instruction.get()
		if emulator_state != "edit":
			update_emulator("edit")
		memory[current_instruction] = encode_binary_instruction(value)
		program_code[current_instruction] = memory[current_instruction]
		if current_instruction + 1 == len(memory):
			memory.append(0)
			program_code.append(0)
		increment_instruction()
		new_instruction.delete(0, 'end')
		new_instruction.focus()

	except ValueError:
		pass

def roll_list(reverse = False):
	if emulator_state != "edit":
		update_emulator("edit")
	increment_instruction(reverse)


def run_program(*args):
	update_emulator("run")

def step_program(*args):
	if emulator_state != "step":
		update_emulator("step")
	processor()
	increment_instruction()

def reset_program(*args):
	# Reset memory viewer
	global current_instruction, memory
	current_instruction = 0
	for i in range(len(program_code)):
		memory[i] = program_code[i]
	update_memory_view()
	new_instruction.delete(0, 'end')
	# Reset buttons' states, labels and viwer color
	update_emulator("ready")

def clear_memory(*args):
	global program_code
	for i in range(len(program_code)):
		program_code[i] = 0
	# Enable representation choice
	for option in radio_numb_rep.winfo_children():
		option.state(['!disabled'])
	reset_program()

def update_emulator(state):
	if state == "step":
		emulator_state = "step"
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['disabled'])
		down_button.state(['disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		# Labels
		memory_labels[highlight_pos].configure(background = 'light pink')
		stat_message.configure(text = "Stepping", foreground = 'magenta')

	elif state == "run":
		emulator_state = "run"
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['disabled'])
		down_button.state(['disabled'])
		step_button.state(['disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		# Labels
		memory_labels[highlight_pos].configure(background= 'light gray')
		stat_message.configure(text = "Running", foreground = 'black')

	elif state == "edit":
		emulator_state = "edit"
		# Buttons
		step_button.state(['disabled'])
		run_button.state(['disabled'])
		new_instruction.state(['!disabled'])
		for option in radio_numb_rep.winfo_children():
			option.state(['disabled'])
		# Labels
		memory_labels[highlight_pos].configure(background= 'light green')
		stat_message.configure(text = "Editing", foreground = 'green')

	elif state == "ready":
		emulator_state = "ready"
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['!disabled'])
		down_button.state(['!disabled'])
		run_button.state(['!disabled'])
		step_button.state(['!disabled'])
		clear_button.state(['!disabled'])
		new_instruction.state(['!disabled'])
		# Labels
		memory_labels[highlight_pos].configure(background= 'light blue')
		idv_A.configure(text = "A:")
		idv_B.configure(text = "B:")
		idv_C.configure(text = "C:")
		idv_Z.configure(text = "Z:")
		stat_message.configure(text = "Ready", foreground = 'blue')

# Variables
global current_instruction
global memory, program_code
current_instruction = 0
emulator_state = "ready"
highlight_pos = 8
global inner_step
inner_step = 0

# Create Main Window
root = Tk()
root.title("Single Operation Computer")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, stick=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Initialize Memory
initial_memory = 30
memory = [i  for i in range(initial_memory)]
program_code = [i  for i in range(initial_memory)]

# Create memory view box
ttk.Label(mainframe, text="MEMORY", justify="center", anchor="center",  background="light blue", relief="raised").grid(column=1, row=0, stick=(W, E))
memory_view = ttk.Frame(mainframe, relief="ridge", padding="3 3 3 3")
memory_view.grid(column=1, row=1, rowspan=10, stick=(N, W, E, S))

memory_labels = []
for i in range(24):
	memory_labels.append(ttk.Label(memory_view, text = "", font = "TkFixedFont"))
	memory_labels[i].grid(column=1, row = i, stick=W)

# Instruction box
instruction = StringVar()
new_instruction = ttk.Entry(mainframe, width=7, textvariable=instruction)
new_instruction.grid(column=2, row=10, columnspan=2, stick=(W, E))
validate_input = (root.register(input_validator), '%P')
new_instruction.configure(validate = 'key', validatecommand=validate_input)

# Create buttons
add_button = ttk.Button(mainframe, text="Add Intruction", command=add_instruction)
add_button.grid(column=2, row=9, columnspan=2, stick=(W, E))

run_button = ttk.Button(mainframe, text="Run", command=run_program)
run_button.grid(column=3, row=1, stick=W)

step_button = ttk.Button(mainframe, text="Step", command=step_program)
step_button.grid(column=3, row=2, stick=W)

reset_button = ttk.Button(mainframe, text="Reset", command=reset_program)
reset_button.grid(column=3, row=3, stick=W)

clear_button = ttk.Button(mainframe, text="Clear memory", command=clear_memory)
clear_button.grid(column=3, row=4, stick=W)

up_button = ttk.Button(mainframe, text="^", command=lambda: roll_list(reverse = True))
up_button.grid(column=2, row=3, stick=W)

down_button = ttk.Button(mainframe, text="v", command=lambda: roll_list())
down_button.grid(column=2, row=4, stick=W)

# Number representation selection
radio_numb_rep = ttk.Frame(mainframe, relief = "solid", padding="2 2 2 2")
radio_numb_rep.grid(column=2, row=1, rowspan=2, stick=(W, E))
numerical_rep = StringVar(root, '08x')
numerical_rep.trace_add('write', update_memory_view) # Invoke update_memory_view  when numerical_rep is written
ttk.Radiobutton(radio_numb_rep, text = "Dec", value='08d', variable = numerical_rep).grid(column=0, row=0, stick=W)
ttk.Radiobutton(radio_numb_rep, text = "Hex", value='08x', variable = numerical_rep).grid(column=0, row=1, stick=W)
ttk.Radiobutton(radio_numb_rep, text = "Bin", value='08b', variable = numerical_rep).grid(column=0, row=2, stick=W)

# Status viewer
stat_message = ttk.Label(mainframe, text = "")
stat_message.grid(column=2, row=0, columnspan=2, stick=W)

# Instruction decoder viewer
idv_A = ttk.Label(mainframe, text="A:")
idv_A.grid(column=2, row=6, stick=W)

idv_B = ttk.Label(mainframe, text="B:")
idv_B.grid(column=2, row=7, stick=W)

idv_C = ttk.Label(mainframe, text="C:")
idv_C.grid(column=2, row=8, stick=W)

idv_Z = ttk.Label(mainframe, text="Z:")
idv_Z.grid(column=3, row=7, stick=W)

for child in mainframe.winfo_children():
	child.grid_configure(padx=5, pady=5)

# Initializes the emulator
reset_program()
new_instruction.focus()
#root.bind("<Return>", calculate)

root.mainloop()

