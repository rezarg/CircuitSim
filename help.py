instructions = [
	"------------------------------------------------------",
	"Welcome to rezarg's Circuit Simulator!",
	"Select a logic gate from the left panel.",
	"Left Click on the canvas to place the gate.",
	"Right Click on a gate and drag to create a connection.",
	"Right Click on the canvas and drag to pan the camera.",
	"Middle Click on a gate/connection to delete it.",
	"I to import logic from the console.",
	"O to export logic to the console.",
	"S to save logic to a file.",
	"L to load logic from a file name.",
	"E to pulse a logic gate.",
	"T to input TPS value from the console.",
	"- to lower TPS.",
	"+/= to increase TPS.",
	"h to show this again.",
	"------------------------------------------------------",
]

def howtouse():
	print("\n".join(instructions))