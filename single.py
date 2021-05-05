
from tkinter import *
from tkinter import ttk

def signed_decimal(number):
	if  number >= 128:
		number -= 256
	return "{:=4d}".format(number)

#implement the wrap-around of 8bit numbers
def wrap_around(number):
	if number < 0:
		return number + 256
	elif number > 255:
		return number - 256
	else:
		return number

def halt_execution(reason=""):
	global interrupt
	interrupt = True
	run_button.state(['disabled'])
	step_button.state(['disabled'])
	reset_button.state(['!disabled'])
	message = ""
	if reason == "memory":
		message = "Ops! Access out of bounds. "
	stat_message.configure(text = message + "Halted.", foreground = "red")

def display_driver(value):
	global cursor_position
	character = display_lookup[wrap_around(256 - value)]
	current_column = cursor_position % 16
	current_line = int((cursor_position - current_column)/16)
	if character == 'NOP':
		pass
	elif character == 'CD': # Clear display
		for i in range(display_lines):
			for j in range(display_columns):
				display_characters[i][j].configure(text = '')
		cursor_position = 0
	elif character == 'LE': # Line end
		cursor_position = 16*current_line + 15
	elif character == 'CL': # Clear line
		for i in range(display_columns):
			display_characters[current_line][i].configure(text = '')
			cursor_position = 16 * current_line
	elif character == 'BS': # Back space
		cursor_position -= 1
		bs_column = cursor_position % 16
		bs_row = int((cursor_podition - bs_column)/16)
		display_characters[bs_row][bs_column].configure(text = '')
	elif character == 'LF':	# Line feed
		cursor_position = (cursor_position + 16) % 32
	elif character == 'CR': # Carriage return
		cursor_position = 16*current_line
	elif character[0:2] == 'ch': # Select character
		cursor_position = int(character[2], 16) + 16*((value % 16) - 8)
	else:
		display_characters[current_line][current_column].configure(text = character)
		cursor_position = (cursor_position + 1) % 32


def memory_read(address):
	try:
		if address != 255:
			data = memory[address]
		else:
			data = 0
		return data
	except IndexError:
		halt_execution("memory")
		return 0

def memory_write(address, value):
	global memory
	try:
		if address == 255:
			display_driver(value)
		else:
			memory[address] = value
	except IndexError:
		halt_execution("memory")

def processor():
	global inner_step, memory, current_instruction
	k = memory_read(current_instruction)
	if inner_step == 0:
		idv_A.configure(text = "A: " + decode_binary_instruction(memory_read(k)) + "(" + signed_decimal(memory_read(k))  + ")")
		idv_B.configure(text="B:")
		idv_C.configure(text="C:")
		idv_Z.configure(text="Z:")
		inner_step += 1
	elif inner_step == 1:
		idv_B.configure(text = "B: " + decode_binary_instruction(memory_read(k)) + "(" + signed_decimal(memory_read(k)) + ")")
		inner_step += 1
	elif inner_step == 2:
		idv_C.configure(text = "C: " + decode_binary_instruction(k))
		inner_step = 0
		a = memory_read(memory_read(current_instruction - 2))
		b = memory_read(memory_read(current_instruction - 1))
		z = wrap_around(b - a)
		idv_Z.configure(text = "Z: " + decode_binary_instruction(z) + "(" + signed_decimal(z) + ")")
		memory_write(memory_read(current_instruction - 1), z)
		if z >= 128 or z == 0:
			if k == 255:
				halt_execution()
			current_instruction = k - 1

def encode_binary_instruction(str_instruction):
	str_base = numerical_rep_in.get()
	if str_base == 'hex':
		base = 16
	elif str_base == 'bin':
		base = 2
	else:
		base = 10
	return int(str_instruction, base)

def decode_binary_instruction(bin_instruction):
	str_instruction = format(bin_instruction, numerical_rep_out.get())
	return str_instruction[0:4] + " " + str_instruction[4:8]

def update_memory_view(*args):
	for i in range(24):
		memory_position = i - 8 + scroll_position
		if len(memory) > memory_position >= 0:
			memory_labels[i].configure(text = "{:02x}: ".format(memory_position) + decode_binary_instruction(memory[memory_position]) + "({:03d})".format(memory[memory_position]))
		else:
			memory_labels[i].configure(text = "")
		if highlight_pos == i:
			memory_labels[i].configure(background = view_color[emulator_state])
		else:
			memory_labels[i].configure(background = 'light gray')

def increment_instruction(reverse = False):
	global current_instruction, scroll_position, highlight_pos
	direction = 1
	if reverse:
		direction = -1
	check_bound = current_instruction + direction
	current_instruction = check_bound % len(memory)
	#if len(memory) > check_bound >= 0:
	#	current_instruction = check_bound
	scroll_position = current_instruction
	highlight_pos = 8
	update_memory_view()

def input_validator(text):
	pattern_switch = numerical_rep_in.get()
	input_cap = 256
	if pattern_switch == 'hex':
		pattern = '^[0-9a-fA-F]*$'
	elif pattern_switch == 'bin':
		pattern = '^[0-1]*$'
	else:
		pattern = '^[0-9]*$|^-[0-9]*$'
		input_cap = 128
	stripped = text.split()
	add_button.state(['disabled'])
	if len(stripped) == 1:
		if re.match(pattern, stripped[0]) and stripped[0] != '-':
			if input_cap > encode_binary_instruction(stripped[0]) >= -(input_cap):
				add_button.state(['!disabled'])
	return True

def add_instruction(*args):
	try:
		global memory, program_code
		value = new_instruction.get()
		value = wrap_around(encode_binary_instruction(value))
		if emulator_state != "edit":
			update_emulator("edit")
		memory[current_instruction] = value
		program_code[current_instruction] = memory[current_instruction]
		if current_instruction + 1 == len(memory) and len(memory) < max_memory:
			memory.append(0)
			program_code.append(0)
		increment_instruction()
		new_instruction.delete(0, 'end')
		new_instruction.focus()

	except ValueError:
		pass

def scroll_view(reverse):
	global scroll_position, highlight_pos
	if reverse and scroll_position > 0:
		scroll_position -= 1
	elif scroll_position < len(memory) and not reverse:
		scroll_position += 1
	highlight_pos = 8 + current_instruction - scroll_position
	update_memory_view()


def roll_list(reverse = False):
	if emulator_state != "edit" and emulator_state != "step":
		update_emulator("edit")
	if emulator_state == "edit":
		increment_instruction(reverse)
	elif emulator_state != "run":
		scroll_view(reverse)
	else:
		pass

def catch_whell(event):
	if event.num == 4:
		roll_list()
	else:
		roll_list(True)
def run_loop():
	if (not interrupt):
		step_program()
		root.after(50, run_loop)

def run_program(*args):
	global interrupt
	interrupt = False
	if emulator_state != "run":
		update_emulator("run")
		run_loop()
	else:
		interrupt = True
		update_emulator("step")
		reset_button.state(['!disabled'])

def step_program(*args):
	if emulator_state != "step" and emulator_state != "run":
		update_emulator("step")
	processor()
	increment_instruction()

def reset_program(*args):
	# Reset memory viewer
	global current_instruction, memory, inner_step, scroll_position, highlight_pos
	inner_step = 0
	current_instruction = 0
	scroll_position = 0
	highlight_pos = 8
	for i in range(len(program_code)):
		memory[i] = program_code[i]
	update_memory_view()
	new_instruction.delete(0, 'end')
	# Reset display
	display_driver(255)
	# Reset buttons' states, labels and viwer color
	update_emulator("ready")

def clear_memory(*args):
	global program_code
	for i in range(len(program_code)):
		program_code[i] = 0
	# Enable representation choice
	'''for option in radio_numb_rep.winfo_children():
		option.state(['!disabled'])'''
	reset_program()

def update_emulator(state):
	global emulator_state
	if state == "step":
		emulator_state = state
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['!disabled'])
		down_button.state(['!disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		step_button.state(['!disabled'])
		run_button.configure(text = "Run")
		# Labels
		memory_labels[highlight_pos].configure(background = view_color[state])
		stat_message.configure(text = "Stepping", foreground = 'magenta')

	elif state == "run":
		emulator_state = state
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['disabled'])
		down_button.state(['disabled'])
		step_button.state(['disabled'])
		clear_button.state(['disabled'])
		new_instruction.state(['disabled'])
		## Attention
		run_button.configure(text = "Stop")
		reset_button.state(['disabled'])
		# Labels
		memory_labels[highlight_pos].configure(background= view_color[state])
		stat_message.configure(text = "Running", foreground = 'black')

	elif state == "edit":
		emulator_state = state
		# Buttons
		step_button.state(['disabled'])
		run_button.state(['disabled'])
		new_instruction.state(['!disabled'])
		'''for option in radio_numb_rep.winfo_children():
			option.state(['disabled'])'''
		# Labels
		memory_labels[highlight_pos].configure(background= view_color[state])
		stat_message.configure(text = "Editing", foreground = 'green')

	elif state == "ready":
		emulator_state = state
		# Buttons
		add_button.state(['disabled'])
		up_button.state(['!disabled'])
		down_button.state(['!disabled'])
		run_button.state(['!disabled'])
		step_button.state(['!disabled'])
		clear_button.state(['!disabled'])
		new_instruction.state(['!disabled'])
		run_button.configure(text = "Run")
		# Labels
		memory_labels[highlight_pos].configure(background= view_color[state])
		idv_A.configure(text = "A:")
		idv_B.configure(text = "B:")
		idv_C.configure(text = "C:")
		idv_Z.configure(text = "Z:")
		stat_message.configure(text = "Ready", foreground = 'blue')

# Variables
global current_instruction, highlight_pos, scroll_position
global memory, program_code, emulator_state
current_instruction = 0
emulator_state = "ready"
highlight_pos = 8
scroll_position = 0
global inner_step
inner_step = 0
view_color = {"step":'light pink', "run":'light gray', "edit":'light green', "ready":'light blue'}

display_lookup = ['NOP','CD',	'NOP',	'LE',	'CL',	'NOP',	'NOP',	'NOP',	'BS',	'NOP',	'LF',	'NOP',	'NOP',	'CR',	'NOP',	'NOP',	#00
		  'NOP','NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	'NOP',	#10
		  ' ',	'!',	'"',	'#',	'$',	'%',	'&',	'\'',	'(',	')',	'*',	'+',	',',	'-',	'.',	'/',	#20
		  '0',	'1',	'2',	'3',	'4',	'5',	'6',	'7',	'8',	'9',	':',	';',	'<',	'=',	'>',	'?',	#30
		  '@',	'A',	'B',	'C',	'D',	'E',	'F',	'G',	'H',	'I',	'J',	'K',	'L',	'M',	'N',	'O',	#40
		  'P',	'Q',	'R',	'S',	'T',	'U',	'V',	'W',	'X',	'Y',	'Z',	'[',	'\\',	']',	'^',	'_',	#50
		  '`',	'a',	'b',	'c',	'd',	'e',	'f',	'g',	'h',	'i',	'j',	'k',	'l',	'm',	'n',	'o',	#60
		  'p',	'q',	'r',	's',	't',	'u',	'v',	'w',	'x',	'y',	'z',	'{',	'|',	'}',	'~',	'NOP']	#70
		  #00	#01	#02	#03	#04	#05	#06	#07	#08	#09	#0a	#0b	#0c	#0d	#0e	#0f

'''
display_lookup = ['NOP','NOP',' ', '0','@','P', '`','p',  'ch0','ch0','NOP','°','À','Ð','à','ð',  	#00
		  'CD',	'NOP','!', '1','A','Q', 'a','q',  'ch1','ch1','¡',  '±','Á','Ñ','á','ñ',	#10
		  'NOP','NOP','"', '2','B','R', 'b','r',  'ch2','ch2','¢',  '²','Â','Ò','â','ò', 	#20
		  'LE',	'NOP','#', '3','C','S', 'c','s',  'ch3','ch3','£',  '³','Ã','Ó','ã','ó', 	#30
		  'CL',	'NOP','$', '4','D','T', 'd','t',  'ch4','ch4','¤',  '´','Ä','Ô','ä','ô', 	#40
		  'NOP','NOP','%', '5','E','U', 'e','u',  'ch5','ch5','¥',  'µ','Å','Õ','å','õ', 	#50
		  'NOP','NOP','&', '6','F','V', 'f','v',  'ch6','ch6','¦',  '¶','Æ','Ö','æ','ö', 	#60
		  'NOP','NOP','\'','7','G','W', 'g','w',  'ch7','ch7','§',  '·','Ç','×','ç','÷', 	#70
		  'BS',	'NOP','(', '8','H','X', 'h','x',  'ch8','ch8','¨',  '¸','È','Ø','è','ø', 	#80
		  'NOP','NOP',')', '9','I','Y', 'i','y',  'ch9','ch9','©',  '¹','É','Ù','é','ù', 	#90
		  'LF',	'NOP','*', ':','J','Z', 'j','z',  'cha','cha','ª',  'º','Ê','Ú','ê','ú', 	#a0
		  'NOP','NOP','+', ';','K','[', 'k','{',  'chb','chb','«',  '»','Ë','Û','ë','û', 	#b0
		  'NOP','NOP',',', '<','L','\\','l','|',  'chc','chc','¬',  '¼','Ì','Ü','ì','ü', 	#c0
		  'CR',	'NOP','-', '=','M',']', 'm','}',  'chd','chd','NOP','½','Í','Ý','í','ý', 	#d0
		  'NOP','NOP','.', '>','N','^', 'n','~',  'che','che','®',  '¾','Î','Þ','î','þ', 	#e0
		  'NOP','NOP','/', '?','O','_', 'o','NOP','chf','chf','¯',  '¿','Ï','ß','ï','ÿ']	#f0
		   #00,	#01,  #02, #03,#04,#05, #06,#07,  #08,  #09,  #0a,  #0b,#0c,#0d,#0e,#0f
'''




# Create Main Window
root = Tk()
root.title("Single Operation Computer")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, stick=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Initialize Memory
initial_memory = 30
max_memory = 255 # Reserved address 0xff to display
#zeros = [0 for i in range(initial_memory)]
hello_world = [12, 12, 3, 36, 37, 6, 37, 12, 9, 37, 37, 12, 0, 255, 15, 38, 36, 18, 12, 12, 21, 52, 37, 24, 37, 12, 27, 37, 37, 30, 36, 12, 255, 37, 37, 0, 39, 0, 255, 72, 101, 108, 108, 111, 44, 32, 87, 111, 114, 108, 100, 33, 52]
program_code = hello_world.copy()
memory = []
for i in range(len(program_code)):
	memory.append(program_code[i])

# Create memory view box
ttk.Label(mainframe, text="MEMORY", justify="center", anchor="center",  background="light blue", relief="raised").grid(column=0, row=0, stick=(W, E))
memory_view = ttk.Frame(mainframe, relief="ridge", padding="3 3 3 3")
memory_view.grid(column=0, row=1, rowspan=9, stick=(N, W, E, S))
memory_view.bind_all("<Button-4>", catch_whell)
memory_view.bind_all("<Button-5>", catch_whell)

memory_labels = []
for i in range(24):
	memory_labels.append(ttk.Label(memory_view, text = "", font = "TkFixedFont"))
	memory_labels[i].grid(column=0, row = i, stick=W)

# Instruction box
instruction = StringVar()
new_instruction = ttk.Entry(mainframe, width=7, textvariable=instruction)
new_instruction.grid(column=1, row=9, columnspan=2, stick=(W, E))
validate_input = (root.register(input_validator), '%P')
new_instruction.configure(validate = 'key', validatecommand=validate_input)

# Create buttons
add_button = ttk.Button(mainframe, text="Add Intruction", command=add_instruction)
add_button.grid(column=1, row=10, columnspan=2, stick=(W, E))

run_button = ttk.Button(mainframe, text="Run", command=run_program)
run_button.grid(column=2, row=3, stick=W)

step_button = ttk.Button(mainframe, text="Step", command=step_program)
step_button.grid(column=2, row=4, stick=W)

reset_button = ttk.Button(mainframe, text="Reset", command=reset_program)
reset_button.grid(column=1, row=5, stick=W)

clear_button = ttk.Button(mainframe, text="Clear memory", command=clear_memory)
clear_button.grid(column=2, row=5, stick=W)

up_button = ttk.Button(mainframe, text="^", command=lambda: roll_list(reverse = True))
up_button.grid(column=1, row=3, stick=W)

down_button = ttk.Button(mainframe, text="v", command=lambda: roll_list())
down_button.grid(column=1, row=4, stick=W)

# Number representation selection
# Input
radio_numb_rep_in = ttk.Frame(mainframe, relief = "solid", padding="2 2 2 2")
radio_numb_rep_in.grid(column=1, row=8, columnspan=2, stick=(W, E))
radio_numb_rep_in.columnconfigure(0, weight=1)
radio_numb_rep_in.columnconfigure(1, weight=1)
radio_numb_rep_in.columnconfigure(2, weight=1)
radio_numb_rep_in.columnconfigure(3, weight=1)

numerical_rep_in = StringVar(root, 'hex')
ttk.Radiobutton(radio_numb_rep_in, text = "Dec", value='dec', variable = numerical_rep_in).grid(column=1, row=0, stick=W)
ttk.Radiobutton(radio_numb_rep_in, text = "Hex", value='hex', variable = numerical_rep_in).grid(column=2, row=0, stick=W)
ttk.Radiobutton(radio_numb_rep_in, text = "Bin", value='bin', variable = numerical_rep_in).grid(column=3, row=0, stick=W)
ttk.Label(radio_numb_rep_in, text = "Input:").grid(column=0, row=0, stick=W)
# Output
radio_numb_rep_out = ttk.Frame(mainframe, relief = "solid", padding="2 2 2 2")
radio_numb_rep_out.grid(column=0, row=10, stick=(W, E))
numerical_rep_out = StringVar(root, '08x')
numerical_rep_out.trace_add('write', update_memory_view) # Invoke update_memory_view  when numerical_rep is written
ttk.Radiobutton(radio_numb_rep_out, text = "Hex", value='08x', variable = numerical_rep_out).grid(column=1, row=0, stick=E)
ttk.Radiobutton(radio_numb_rep_out, text = "Bin", value='08b', variable = numerical_rep_out).grid(column=2, row=0, stick=W)
ttk.Label(radio_numb_rep_out, text = "Output:").grid(column=0, row=0, stick=W)


# Status viewer
stat_message = ttk.Label(mainframe, text = "")
stat_message.grid(column=1, row=0, columnspan=2, stick=W)

# Instruction decoder viewer
idv_A = ttk.Label(mainframe, text="A:", font="TkFixedFont", width=18)
idv_A.grid(column=1, row=6, stick=W)

idv_B = ttk.Label(mainframe, text="B:", font="TkFixedFont", width=18)
idv_B.grid(column=1, row=7, stick=W)

idv_C = ttk.Label(mainframe, text="C:", font="TkFixedFont", width=18)
idv_C.grid(column=2, row=6, stick=W)

idv_Z = ttk.Label(mainframe, text="Z:", font="TkFixedFont", width=18)
idv_Z.grid(column=2, row=7, stick=W)

for child in mainframe.winfo_children():
	child.grid_configure(padx=5, pady=5)

# Alphanumerical display
display = ttk.Frame(mainframe, relief = 'ridge', padding="2 2 2 2")
display.grid(column=1, row=1, columnspan=2, rowspan=2, stick=(W, E, N, S))
display_characters = []
display_lines = 2
display_columns = 16
for i in range(display_lines):
	display_characters.append([])
	for j in range(display_columns):
		display_characters[i].append(ttk.Label(display, text = format(j, 'x'), font="TKFixedFont"))
		display_characters[i][j].grid(column=j, row=i, stick=W)

global cursor_position
cursor_position = 0

# Initializes the emulator
reset_program()
new_instruction.focus()
#root.bind("<Return>", calculate)

root.mainloop()

