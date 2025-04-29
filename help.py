instructions = [
	"------------------------------------------------------",
	"Welcome to rezarg's Circuit Simulator!",
	"Select a logic gate from the left panel.",
	"Left Click on the canvas to place the gate.",
	"Right Click on a gate and drag to create a connection.",
	"Right Click on the canvas and drag to pan the camera.",
	"Middle Click on a gate/connection to delete it.",
	"I to import logic.",
	"O to export logic.",
	"E to pulse a logic gate.",
	"- to lower TPS.",
	"+/= to increase TPS.",
	"h to show this again.",
	"------------------------------------------------------",
]

def howtouse():
	print("\n".join(instructions))