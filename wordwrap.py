# Mimics the official card creator's
# weird behavior of leaving the spaces
# intact at the end of each line.
def msplit(line):
	output = [""]
	for char in line:
		if char == " ":
			if (output[-1] == ""):
				output[-2] = output[-2] + char
			else:
				output[-1] = output[-1] + char
				output.append("")
		else:
			output[-1] = output[-1] + char

	if output[-1] == "":
		del output[-1]
	return output

assert msplit("wor wro asdkjfh ") == ["wor ", "wro ", "asdkjfh "]
assert msplit("wor  wro asdkjfh ") == ["wor  ", "wro ", "asdkjfh "]


# The word wrapping function takes a list of words
# and wraps it as the official card creator would.
# Maybe.
def wrap(contents):
	width = 23
	finaloutput = []
	for hardLine in contents.split("\n"):
		output = [""]
		for word in msplit(hardLine):
			if len(output[-1]) + len(word)-2 < width:
				output[-1] = output[-1] + word
			else:
				while len(word) > width:
					if (output[-1] == ""):
						output[-1] = word[:width]
					else:
						output.append(word[:width])
					word = word[width:]
				output.append(word)
		finaloutput += output
	# print("|".join(output))
	return finaloutput

# word spacing matches template
assert wrap("Look at all this wonderful room for card one's front text!") == ["Look at all this ","wonderful room for card ","one's front text!"]
# Make sure the width isset exactly correct
assert wrap("12345678909 12345678909 12345678909") == ["12345678909 12345678909 ","12345678909"]
assert wrap("123456789090 12345678909 12345678909") == ["123456789090 ","12345678909 12345678909"]
# Make sure it doesn't loose multiple spaces
assert wrap("12345678909  12345678909 12345678909") == ["12345678909  ","12345678909 12345678909"]
# 2 line word
assert wrap("123 12345678901234567890123456789 12345678909 12345678909") == ["123 ","12345678901234567890123","456789 12345678909 ","12345678909"]
# 2 line word at start
assert wrap("12345678901234567890123456789 12345678909 12345678909") == ["12345678901234567890123","456789 12345678909 ","12345678909"]
# 4 line long word
assert wrap("0123456789012345678901234567890123456789012345678901234567890123456789 01234567890123456789") == ["01234567890123456789012","34567890123456789012345","67890123456789012345678","9 01234567890123456789"]
# Test newlines and double newlines
assert wrap("Oops I forgot\nabout\n\nnewlines") == ["Oops I forgot","about","","newlines"]