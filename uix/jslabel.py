from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp, sp
from kivymd.label import MDLabel
from jscolor import *

class ContentLabel(MDLabel, ButtonBehavior):
	bcolor = ListProperty(white)
	asc = True
	def __init__(self, **kwargs):
		super(ContentLabel, self).__init__(**kwargs)

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			touch.grab(self)
			try:
				# CHANGE COLOR
				for b in self.parent.parent.children:
					for lbl in b.children:
						lbl.bcolor = white
				for lbl in self.parent.children:
					lbl.bcolor = primarylight
			except:
				pass

class TitleLabel(MDLabel, ButtonBehavior):
	bcolor = ListProperty(sunglow)
	def __init__(self, **kwargs):
		super(TitleLabel, self).__init__(**kwargs)