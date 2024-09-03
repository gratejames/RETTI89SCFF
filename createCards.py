from wordwrap import wrap


# Converts integers to strings of characters
def intToStr2L(num):
	return chr(num%0x0100) + chr(num//0x0100)
def intToStr4L(num):
	return chr(num%0x0100) + chr((num//0x0100)%0x0100) + chr((num//0x010000)%0x0100) + chr((num//0x01000000)%0x0100)
def intToStr2B(num):
	return chr(num//0x0100) + chr(num%0x0100)




class card:
	def __init__(self, name, frontLines, backLines):
		self.name = name
		# Written so that you could move the wrap function in here if you wanted,
		# to provide a smoother but less extensible interface.
		# Or it can be left like this and modified to parse inputted text positions as well
		self.frontLines = frontLines
		self.backLines = backLines

		# Quick bit of a header
		FrontPtr           = intToStr2L(len(self.name)+5)					#   2 bytes: Distance from card start to front of card
		BackPtr            = intToStr2L(0)									#   2 bytes: Distance from card start to back of card
		Name               = self.name + "\x00"								#   n bytes: zero terminated card name

		# Card front
		FrontHeader        = "\x01\x03\x00"									#   3 bytes: Unknown
		FrontLines         = chr(len(self.frontLines))						#   1 byte : Lines of text on the front
		FrontData          = ""

		# Text entries
		xPos = 0
		yPos = 0
		for line in self.frontLines:
			FrontData += "\x01" + chr(yPos) + chr(xPos) + line + "\x00"
			yPos += 9
		FrontFooter        = "\x50\x01\x01\x01"								#   4 bytes: Unknown
		FrontFace = FrontHeader + FrontLines + FrontData + FrontFooter

		# Fill in the back pointer now that we know where it is
		BackPtr = intToStr2L(len(FrontPtr + BackPtr + Name + FrontFace))

		# Card back
		BackHeader         = "\x01\x03\x00"									#   3 bytes: Unknown
		BackLines          = chr(len(self.backLines))						#   1 byte : Lines of text on the front
		BackData           = ""

		# Text entries
		xPos = 0
		yPos = 0
		for line in self.backLines:
			BackData += "\x01" + chr(yPos) + chr(xPos) + line + "\x00"
			yPos += 9
		BackFooter         = "\x50\x01\x01"									#   3 bytes: Unknown
		BackFace = BackHeader + BackLines + BackData + BackFooter

		# Combine and save!
		# Could be a function, but the length is need to fill
		# in the card pointer table. Because we don't need
		# any of the fields to change, we can just compile it all
		# on initialization.
		self.content = FrontPtr + BackPtr + Name + FrontFace + BackFace


class stack:
	def __init__(self, StackTitle, VariableName, VersionNum, CreatorName, CreationDate, Points, Cards):
		# Just a quick bit of sanitization on the variable name
		VariableName = (VariableName + "\x00\x00\x00\x00\x00\x00\x00").lower()[:8]

		# The appvar file header
		Signature          = "**TI89**\x01\x00"														#  8 bytes: Constant signature
		DefaultFolder      = "MAIN\x00\x00\x00\x00"													#  8 bytes: Zero padded
		Comment            = f"AppVariable file 08/31/24, 18:08\x00\x00\x00\x00\x00\x00\x00\x00"	# 40 bytes: Zero padded
		Entries            = intToStr2L(1)															#  2 bytes: Amount of entries
		Header             = Signature + DefaultFolder + Comment + Entries
		assert len(Header) == 0x3C

		# The variable entry, up until the file length
		# which needs to be substituted at the end
		VariableOffset     = intToStr4L(0x52)														#  4 bytes: Offset from the beginning of the file to variable
		VariableName       = VariableName															#  8 bytes: Zero padded
		VariableTypeID     = "\x1c"																	#  1 byte : Type ID of the variable
		VariableAttributes = "\x00"																	#  1 byte : Attirbutes (0: none, 1: locked, 2: archived)
		VariableUnused     = "\x00\x00"																#  2 bytes: Unused, 0
		VariableEntry      = VariableOffset + VariableName + VariableTypeID + VariableAttributes + VariableUnused
		assert len(VariableEntry) == 0x10

		FileLength         = intToStr4L(0)															#  4 bytes: File size, fixed later
		FileSignature      = "\xa5\x5a"																#  2 bytes: Signature
		StackNull          = "\x00\x00\x00\x00"														#  4 bytes: Null prefix
		StackSize          = "\x00\x00"																#  2 bytes: Fixed later
		StackMagic         = "\xf3\x47\xbf\xa7"														#  4 bytes: Reference position for many later calculations
		StackUnknown       = intToStr4L(1)															#  4 bytes: A one? not sure
		position = 0x15 + len(Cards)*2	
		StackTitlePtr      = intToStr2L(position)													#  2 bytes: Distance from Magic to Title
		position += 1+len(StackTitle)
		StackCreatorPtr    = intToStr2L(position)													#  2 bytes: Distance from Magic to Creator
		position += 1+len(CreatorName)
		StackDatePtr       = intToStr2L(position)													#  2 bytes: Distance from Magic to Date
		position += 1+len(CreationDate)
		StackVersionPtr    = intToStr2L(position)													#  2 bytes: Distance from Magic to Version
		position += 1+len(VersionNum)
		StackPointsRight   = chr(Points[0])															#  1 byte : Points for right answer (+)
		StackPointsWrong   = chr(Points[1])															#  1 byte : Points for wrong answer (-)
		StackPointsSkip    = chr(Points[2])															#  1 byte : Points for skipped answer (-)
		StackNumCards      = chr(len(Cards))														#  1 byte : Amount of cards
		CardPtrTable = ""
		for i in range(len(Cards)):
			CardPtrTable += intToStr2L(position)													#  2 bytes: Distance from Magic to first card
			position += len(Cards[i].content)

		# Combine all the collected data this far into the stack data.
		# Don't combine with size because it needs to be filled in below
		StackHeader = StackMagic + StackUnknown + \
		StackTitlePtr + StackCreatorPtr + StackDatePtr + StackVersionPtr + \
		StackPointsRight + StackPointsWrong + StackPointsSkip + \
		StackNumCards + CardPtrTable + \
		f"\x02{StackTitle}\x00{CreatorName}\x00{CreationDate}\x00{VersionNum}\x00"

		# Combine all the cards. For some reason, this extra null
		# character needs to be included in the card size, but doesn't make
		# sense to shift into the card structure for no reason.
		CompiledCards = "".join([Card.content for Card in Cards]) + "\x00"

		StackFooter = "STDY\x00\xF8"

		# Combine all the variable data so far, minus the stack footer,
		# and find the length. Then, recombine it with the right length
		VariableData = StackNull + StackSize + StackHeader + CompiledCards
		StackSize = intToStr2B(len(VariableData))
		VariableData = StackNull + StackSize + StackHeader + CompiledCards + StackFooter

		# The checksum is calculated by adding up every byte in the variable data.
		checksum = intToStr2L(sum([ord(char) for char in VariableData]))

		# Similar to the above, but with the whole file length
		self.file = Header + VariableEntry + FileLength + FileSignature + VariableData + checksum
		FileLength = intToStr4L(len(self.file))
		self.file = Header + VariableEntry + FileLength + FileSignature + VariableData + checksum





if __name__ == '__main__':
	stack1 = stack(
		"StackTitle2",
		"stackti3",
		"vn0101",
		"creatorName",
		"CreateDate",
		[99, 55, 22],
		[
			card("cardName1",
				wrap("Look at all this wonderful room for card one's front text!"),
				wrap("And so much on the back as well!"),
			),
			card("cardName22",
				wrap("Look at all this wonderful room for card two's front text!~!"),
				wrap("And so much on the back as well!~!"),
			),
			card("cardName333",
				wrap("Look at all this wonderful room for card tre's front text!~!~!"),
				wrap("And so much on the back as well!~!~!"),
			),
		],
	)

	# Written as binary instead of just text for fear of
	# python messing with line-ending localization.
	# I changed it to this at some point and can't remember
	# if it fixed an issue, and am too afraid to go back
	with open("gen3.89y", "wb") as f:
		for char in stack1.file:
			f.write(ord(char).to_bytes(1))