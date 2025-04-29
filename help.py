instructions = [
	"------------------------------------------------------",
	"Welcome to rezarg's Circuit Simulator!",
	"I to import logic from the console.",
	"O to export logic to the console.",
	"S to save logic to a file.",
	"L to load logic from a file name.",
	"T to input TPS value from the console.",
	"- to lower TPS.",
	"+/= to increase TPS.",
	"h to show this again.",
	"Ctrl+C to copy selection.",
	"Ctrl+V to paste selection.",
	"1 to activate Normal rendering mode.",
	"2 to activate Wireless rendering mode.",
	"3 to activate LED-Exclusive rendering mode.",
	"------------------------------------------------------",
]

def howtouse():
	print("\n".join(instructions))