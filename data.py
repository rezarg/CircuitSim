from logic import Block

blocks = None

def init(blocks_: list):
	global blocks
	blocks = blocks_

def encodeData():
	outputStr = ""
	for block in blocks:
		inputsStr = ",".join([f"{input.x},{input.y}" for input in block.inputs])
		outputStr += f"{block.type},{block.x},{block.y},{block.value},{inputsStr};"
	print("Exported Logic:")
	print(outputStr[:-1])
	return outputStr[:-1]

def decodeData(inputStr: str):
	if inputStr.strip() == "": return
	inputStr = inputStr.split(";")
	for blockData in inputStr:
		blockData = blockData.split(",")
		blockType = blockData[0]
		blockX = int(blockData[1])
		blockY = int(blockData[2])
		blockValue = bool(blockData[3])
		newBlock = Block(blockType, blockX, blockY)
		newBlock.value = blockValue
	for blockData in inputStr:
		blockData = blockData.split(",")
		blockX = int(blockData[1])
		blockY = int(blockData[2])
		thisBlock = None
		for block in blocks:
			if block.x == blockX and block.y == blockY:
				thisBlock = block
		if thisBlock is None: continue
		inputsStr = blockData[4:]
		inputs = []
		x, y = 0, 0
		for i in range(len(inputsStr)):
			inputStr = inputsStr[i]
			if inputStr == "": continue
			if i%2 == 0:
				x = int(inputStr)
			else:
				y = int(inputStr)
				for block in blocks:
					if block.x == x and block.y == y:
						inputs.append(block)
						break
		thisBlock.inputs = inputs
	print("Imported logic!")