'''
The class DropDownlist originated from OptionBox from 'https://stackoverflow.com/questions/19877900/tips-on-adding-creating-a-drop-down-selection-box-in-pygame'
	Using the original, I tinkered it to my needs

The other GUI classes were coded originally by me using inspiration from the OptionBox class
'''

import pygame as pg


# self, x, y, w, h, alignment, font, text, text_offset
class Label:
	def __init__(self, x, y, w, h, alignment, font, text, text_offset):
		self.rect = pg.Rect(x, y, w, h)
		self.alignment = alignment
		self.font = font
		self.text = text
		self.text_offset = text_offset

	def draw(self, surf):
		# pg.draw.rect(surf, (255, 255, 255), self.rect, 2)  # Test - shows borders
		msg = self.font.render(self.text, 1, (0, 0, 0)) #(text, antialias, text colour)
		if self.alignment == "center":
			# Displays text at center of rectangle
			text_rect = msg.get_rect(center = self.rect.center)	
		elif self.alignment == "right":
			# Displays at right-handside
			text_rect = msg.get_rect(midright = self.rect.midright)	
		elif self.alignment == "left":
			# Displays at left-handside
			text_rect = msg.get_rect(midleft = self.rect.midleft)
		text_rect.move_ip(self.text_offset)
		surf.blit(msg, text_rect)

	def update(self, event_list):
		pass

	def set_text(self, text):
		self.text = text


# self, x, y, w, h, colour, highlight_colour, border_colour, font, symbol_font, option_list, text_offset=(0, 0), selected=0
class DropDownList:
	def __init__(self, x, y, w, h, colour, highlight_colour, border_colour, font, symbol_font, option_list, text_offset=(0, 0), selected=0):
		self.colour = colour
		self.highlight_colour = highlight_colour
		self.border_colour = border_colour
		self.rect = pg.Rect(x, y, w, h)
		self.font = font
		self.symbol_font = symbol_font
		self.option_list = option_list
		self.selected = selected
		self.draw_menu = False
		self.menu_active = False
		self.active_option = -1
		self.text_offset = text_offset

	def draw(self, surf):
		proportion = 0.10  # Fraction of the box to be the arrow rectangle
		arrow_background_rect = self.rect.copy()
		arrow_background_rect[0] = arrow_background_rect[0] + arrow_background_rect[2] * (1-proportion)  # Changes x value
		arrow_background_rect[2] = arrow_background_rect[2] * proportion  # Changes width
		pg.draw.rect(surf, self.highlight_colour if self.menu_active else self.colour, self.rect)  # Rect background for box; different colour when active
		pg.draw.rect(surf, self.border_colour, arrow_background_rect)  # Draws rect for the arrow
		pg.draw.rect(surf, self.border_colour, self.rect, 2)  # Draws a rect with only borders
		msg = self.font.render(str(self.option_list[self.selected]), 1, (0, 0, 0))  # (text, antialias, text colour)
		arrow = self.symbol_font.render("▼", 1, (0, 0, 0))  # For the arrow in the rect
		text_rect = msg.get_rect(center=self.rect.center)  # Gets rect of the rendered message
		text_rect.move_ip(self.text_offset)  # Moves text if necessary to better fit in the rect
		arrow_rect = arrow.get_rect(center=arrow_background_rect.center)
		surf.blit(msg, text_rect)  # Displays message at the center of the rect	
		surf.blit(arrow, arrow_rect)  # Displays arrow at the center of its own rect


		if self.draw_menu:
			for i, text in enumerate(self.option_list):
				rect = self.rect.copy()
				rect.y += (i+1) * self.rect.height # Shifts copied rect down
				pg.draw.rect(surf, self.highlight_colour if i == self.active_option else self.colour, rect)
				msg = self.font.render(text, 1, (0, 0, 0))
				text_rect = msg.get_rect(center = rect.center)
				text_rect.move_ip(self.text_offset)
				surf.blit(msg, text_rect)
			outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
			pg.draw.rect(surf, self.border_colour, outer_rect, 2)

	def update(self, event_list):
		mpos = pg.mouse.get_pos()
		self.menu_active = self.rect.collidepoint(mpos)

		self.active_option = -1
		for i in range(len(self.option_list)):
			rect = self.rect.copy()
			rect.y += (i+1) * self.rect.height
			if rect.collidepoint(mpos):
				self.active_option = i
				break

		if not self.menu_active and self.active_option == -1:
			self.draw_menu = False

		for event in event_list:
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if self.menu_active:
					self.draw_menu = not self.draw_menu
				elif self.draw_menu and self.active_option >= 0:
					self.selected = self.active_option
					self.draw_menu = False
					return self.active_option
		return -1

	def getSelectedOption(self):
		return self.option_list[self.selected]

	def setSelected(self, value):
		if value not in self.option_list:
			print("Error - no value in options")
		else:
			pos = 0
			while True:
				if self.option_list[pos] == value:
					self.selected = pos
					return True
				pos += 1
					

	def get_draw_menu(self):
		return self.draw_menu


# self, x, y, w, h, colour, highlight_colour, border_colour, font, text, text_offset = (0,0), action = None
class Button:
	def __init__(self, x, y, w, h, colour, highlight_colour, border_colour, font, text, text_offset = (0,0), action = None):
		self.colour = colour
		self.highlight_colour = highlight_colour
		self.border_colour = border_colour
		self.rect = pg.Rect(x, y, w, h)
		self.font = font
		self.button_active = False
		self.text = text
		self.text_offset = text_offset
		self.action = action

	def draw(self, surf):
		pg.draw.rect(surf, self.highlight_colour if self.button_active else self.colour, self.rect) # Different colour when active
		pg.draw.rect(surf, self.border_colour, self.rect, 2) # Draws a rect with only borders
		msg = self.font.render(self.text, 1, (0, 0, 0)) # (text, antialias, text colour)
		text_rect = msg.get_rect(center = self.rect.center)
		text_rect.move_ip(self.text_offset)
		surf.blit(msg, text_rect) # Displays text at the center

	def update(self, event_list):
		# Checks if mouse is over the button
		mpos = pg.mouse.get_pos()
		self.button_active = self.rect.collidepoint(mpos)

		for event in event_list:
			# Calls functions when left mouse is clicked
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if self.button_active and self.action != None:
					self.action()


# self, x, y, r, colour, highlight_colour, border_colour, font, text, text_offset = (0,0), action = None
class CircularButton:
	def __init__(self, x, y, r, colour, highlight_colour, border_colour, font, text, text_offset = (0,0), action = None):
		self.colour = colour
		self.highlight_colour = highlight_colour
		self.border_colour = border_colour
		self.x = x
		self.y = y
		self.r = r
		self.font = font
		self.button_active = False
		self.text = text
		self.text_offset = text_offset
		self.action = action

	def collidepoint(self, mpos):
		# Using the equation for a circle
		# Checks if the mouse is over the button
		if (self.x-mpos[0])**2 + (self.y-mpos[1])**2 <= self.r**2:
			return True
		else:
			return False

	def draw(self, surf):
		pg.draw.circle(surf, self.highlight_colour if self.button_active else self.colour, (self.x, self.y), self.r)
		pg.draw.circle(surf, self.border_colour, (self.x, self.y), self.r, 2)
		msg = self.font.render(self.text, 1, (0, 0, 0)) # (text, antialias, text colour)
		text_rect = msg.get_rect(center = (self.x, self.y))
		text_rect.move_ip(self.text_offset)
		surf.blit(msg, text_rect) # Displays text at the center

	def update(self, event_list):
		# Checks if mouse is over the button
		mpos = pg.mouse.get_pos()
		self.button_active = self.collidepoint(mpos)

		for event in event_list:
			# Calls functions when left mouse is clicked
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if self.button_active and self.action != None:
					self.action()


# self, x, y, w, h, inactive_colour, inactive_highlight_colour, active_colour, active_highlight_colour, border_colour, font, text, alt_text=None, text_offset = (0,0)
class ToggleButton:
	def __init__(self, x, y, w, h, inactive_colour, inactive_highlight_colour, active_colour, active_highlight_colour, border_colour, font, text, alt_text=None, text_offset = (0,0)):
		self.toggled = False
		self.inactive_colour = inactive_colour
		self.inactive_highlight_colour = inactive_highlight_colour
		self.active_colour = active_colour
		self.active_highlight_colour = active_highlight_colour
		self.border_colour = border_colour
		self.rect = pg.Rect(x, y, w, h)
		self.font = font
		self.button_active = False
		self.text = text
		if alt_text == None:
			self.alt_text = text
		else:
			self.alt_text = alt_text
		self.text_offset = text_offset
		
	def toggle(self):
		# Switches to the alternate setting
		if self.toggled:
			self.toggled = False
		else:
			self.toggled = True

	def set_to_inactive(self):
		self.toggled = False

	def set_to_active(self):
		self.toggled = True

	def draw(self, surf):
		if self.toggled == False:  # Uses inactive colour attributes
			pg.draw.rect(surf, self.inactive_highlight_colour if self.button_active else self.inactive_colour, self.rect)  # Different colour when active
			msg = self.font.render(self.text, 1, (0, 0, 0)) # (text, antialias, text colour)
		else:  # Uses active colour attributes
			pg.draw.rect(surf, self.active_highlight_colour if self.button_active else self.active_colour, self.rect)  # Different colour when active
			msg = self.font.render(self.alt_text, 1, (0, 0, 0)) # (text, antialias, text colour)
		pg.draw.rect(surf, self.border_colour, self.rect, 2) # Draws a rect with only borders
		text_rect = msg.get_rect(center = self.rect.center)
		text_rect.move_ip(self.text_offset)
		surf.blit(msg, text_rect) # Displays text at the center

	def update(self, event_list):
		# Checks if mouse is over the button
		mpos = pg.mouse.get_pos()
		self.button_active = self.rect.collidepoint(mpos)

		for event in event_list:
			# Toggles when left mouse button is clicked and returns True if so
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if self.button_active:
					self.toggle()
					return True
		return -1


# self, x, y, w, h, colour, highlight_colour, border_colour, font, text, text_when_empty, text_offset = (0,0)
class TextEntry:
	def __init__(self, x, y, w, h, colour, highlight_colour, border_colour, font, text, text_when_empty, text_offset = (0,0)):
		self.colour = colour
		self.highlight_colour = highlight_colour
		self.border_colour = border_colour
		self.rect = pg.Rect(x, y, w, h)
		self.font = font
		self.button_active = False
		self.text = text
		self.text_when_empty = text_when_empty
		self.text_offset = text_offset
		self.highlighted = False

	def draw(self, surf):
		pg.draw.rect(surf, self.highlight_colour if self.button_active or self.highlighted else self.colour, self.rect) # Different colour when active or highlighted
		pg.draw.rect(surf, self.border_colour, self.rect, 2) # Draws a rect with only borders
		msg = self.font.render(self.text, 1, (0, 0, 0)) # (text, antialias, text colour)
		text_rect = msg.get_rect(center = self.rect.center)
		text_rect.move_ip(self.text_offset)
		surf.blit(msg, text_rect) # Displays text at the center

	def update(self, event_list):
		# Checks if mouse is over the gui element
		mpos = pg.mouse.get_pos()
		self.button_active = self.rect.collidepoint(mpos)

		for event in event_list:
			# Sets as highlighted when left mouse button clicked over element
			# Resets it when left clicked or the return key is pressed
			
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if self.button_active:
					self.setHighlighted()
					self.text = ""
				else:
					self.setNotHighlighted()
					return int(self.text)
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_RETURN:
					self.setNotHighlighted()
					return int(self.text)
		return -1

	def setHighlighted(self):
		self.highlighted = True

	def setNotHighlighted(self):
		self.highlighted = False
		# When empty, it sets the text to a default setting
		if self.text == "":
			self.text = self.text_when_empty

	def deleteLastCharacter(self):
		self.text = self.text[:-1]

	def addText(self, character):
		self.text += character
