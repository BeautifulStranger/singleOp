from tkinter import *
from tkinter import ttk

def processor(instruction_addr):
	pass

def encode_binary_instruction(str_instruction):
	str_base = (numerical_rep.get())[-1]
	if str_base == 'x':
		base = 16
	elif str_base == 'b':
		base = 2
	else:
		base = 10
	a,b,c = str_instruction.split()
	a = a + '00000000'
	b = b + '0000'
	return int(a, base) + int(b, base) + int(c, base)

def decode_binary_instruction(bin_instruction):
	str_instruction = format(bin_instruction, numerical_rep.get())
	return ' '.join(str_instruction[i:i+4] for i in (0,4,8))

def update_memory_view(*args):
	for i in range(24):
		memory_position = i - highlight_pos + current_instruction
		if len(memory) > memory_position >= 0:
			memory_labels[i].configure(text = "{:04x}: ".format(memory_position) + decode_binary_instruction(memory[memory_position]))
		else:
			memory_labels[i].configure(text = "")
	value_A, value_B, value_C = decode_binary_instruction(memory[current_instruction]).split()
	idv_A.configure(text = "A: " + value_A)
	idv_B.configure(text = "B: " + value_B)
	idv_C.configure(text = "C: " + value_C)

def increment_instruction(reverse = False):
	global current_instruction
	direction = 1
	if reverse:
		direction = -1
	check_bound = current_instruction + direction
	if len(memory) > check_bound >= 0:
		current_instruction = check_bound
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
	if len(stripped) == 3:
		if re.match(pattern, stripped[0]) and re.match(pattern, stripped[1]) and re.match(pattern, stripped[2]):
			add_button.state(['!disabled'])
	return True

def add_instruction(*args):
	try:
		global memory
		value = new_instruction.get()
		if emulator_state != "edit":
			update_emulator("edit")
		memory[current_instruction] = encode_binary_instruction(value)
		increment_instruction()
		new_instruction.delete(0, 'end')

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
	processor(current_instruction)
	increment_instruction()

def reset_program(*args):
	# Reset memory viewer
	global current_instruction
	current_instruction = 0
	update_memory_view()
	new_instruction.delete(0, 'end')
	# Reset buttons' states and viwer color
	update_emulator("ready")

def clear_memory(*args):
	for i in range(len(memory)):
		memory[i] = 0
	for option in radio_numb_rep.winfo_children():
		option.state(['!disabled'])
	reset_program()

def update_emulator(state):
	if state == "step":
		add_button.state(['disabled'])
		up_button.state(['disabled'])
		down_button.state(['disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		memory_labels[highlight_pos].configure(background = 'light pink')
		emulator_state = "step"

	elif state == "run":
		add_button.state(['disabled'])
		up_button.state(['disabled'])
		down_button.state(['disabled'])
		step_button.state(['disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		memory_labels[highlight_pos].configure(background= 'light gray')
		emulator_state = "run"

	elif state == "edit":
		step_button.state(['disabled'])
		run_button.state(['disabled'])
		new_instruction.state(['!disabled'])
		memory_labels[highlight_pos].configure(background= 'light green')
		emulator_state = "edit"
		for option in radio_numb_rep.winfo_children():
			option.state(['disabled'])

	elif state == "ready":
		add_button.state(['disabled'])
		up_button.state(['!disabled'])
		down_button.state(['!disabled'])
		run_button.state(['!disabled'])
		step_button.state(['!disabled'])
		clear_button.state(['!disabled'])
		new_instruction.state(['!disabled'])
		memory_labels[highlight_pos].configure(background= 'light blue')
		emulator_state = "ready"


# Variables
global current_instruction
global memory
current_instruction = 0
emulator_state = "ready"
highlight_pos = 8

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
numerical_rep = StringVar(root, '012x')
numerical_rep.trace_add('write', update_memory_view) # Invoke update_memory_view  when numerical_rep is written
radio_dec = ttk.Radiobutton(radio_numb_rep, text = "Dec", value='012d', variable = numerical_rep)
radio_dec.grid(column=0, row=0, stick=W)
radio_hex = ttk.Radiobutton(radio_numb_rep, text = "Hex", value='012x', variable = numerical_rep)
radio_hex.grid(column=0, row=1, stick=W)
radio_bin = ttk.Radiobutton(radio_numb_rep, text = "Bin", value='012b', variable = numerical_rep)
radio_bin.grid(column=0, row=2, stick=W)


# Instruction decoder viewer
idv_A = ttk.Label(mainframe, text="")
idv_A.grid(column=3, row=6, stick=W)

idv_B = ttk.Label(mainframe, text="")
idv_B.grid(column=3, row=7, stick=W)

idv_C = ttk.Label(mainframe, text="")
idv_C.grid(column=3, row=8, stick=W)

for child in mainframe.winfo_children():
	child.grid_configure(padx=5, pady=5)

# Initializes the emulator
reset_program()
new_instruction.focus()
#root.bind("<Return>", calculate)

root.mainloop()

