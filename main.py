# -*- coding: utf-8 -*-
import sys, time, copy, datetime, threading, random, multiprocessing
from operator import attrgetter
from functools import partial
from collections import OrderedDict, defaultdict
from itertools import permutations, product, combinations
from os.path import sep, expanduser, isdir, dirname

import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.logger import Logger

from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import *
from kivy.uix.behaviors import ButtonBehavior
# from kivy.garden.filebrowser import FileBrowser
from filebrowser import FileBrowser

from kivy.properties import StringProperty,BooleanProperty,ListProperty,ObjectProperty,NumericProperty
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.config import Config
Config.set('kivy','log_level', 'warning')
Config.write()

from machine import *
import datentime
from datentime import HourstoDate, DatetoHours, DateAbbr, AbbrtoDate, NextWorkingDate, proceduralbuffer, jobbuffer, workingweek
from exporter import Exporter
from orderm import PrintInformation, OrderInfoPanel, Order
from db import ReadOrders
from forschedule import ForSchedule, CalUT

###################################################################### MP EVAL ######################################################################
def Evaluate(*args):
	candidate = args[0]
	fororders = ForSchedule(copy.deepcopy(candidate))
	avgut = CalUT(fororders)
	print '.',
	return (avgut, candidate)

def MP(i):
	print '-'*35,app.neighbourhoods[i][0],'-'*35

	# MP.PROCESS
	# perms = app.neighbourhoods[i][1]()
	# head,tail = 0,0
	# jobs = []
	# cpus = multiprocessing.cpu_count()
	# for process in range(cpus-1):
	# 	tail+=int(len(perms)/cpus)
	# 	jobs.append(multiprocessing.Process(target=Evaluate, args=(perms[head:tail],)))
	# 	head=tail
	# jobs.append(multiprocessing.Process(target=Evaluate, args=(perms[head:],)))
	# for j in jobs:
	# 	j.start()
	# for j in jobs:
	# 	j.join()

	# MP.POOL
	avgut = 0.0
	bestperm = []
	error = 0
	workers = multiprocessing.Pool(multiprocessing.cpu_count())
	try:
		(avgut,bestperm) = max(workers.map(Evaluate,app.neighbourhoods[i][1]()))
	except:
		error=1
	workers.close()
	workers.join()
	if error:
		return
	print
	if str(avgut)[:10]>str(app.bestut)[:10]:
		app.selectedorders = [copy.deepcopy(bestperm)]
		app.bestut=avgut
		print 'best', [o.jo if len(o.jo)<5 else o.jo[-4:] for o in bestperm], round(app.bestut*100,4),'%'
	elif str(avgut)[:10]==str(app.bestut)[:10]:
		app.selectedorders.append(copy.deepcopy(bestperm))
		for perm in app.selectedorders:
			print 'bests', [o.jo if len(o.jo)<5 else o.jo[-4:] for o in perm], round(app.bestut*100,4),'%'
	app.orders = app.selectedorders[0]

###################################################################### MAIN INIT ######################################################################
class MDScheduler(App):
	def build(self):
		self.PreBuildInit()
		self.ReBuildInit()
		self.root = Builder.load_string(main_widget_kv)
		self.UpdateMain()
		self.UpdateResult(self.orders)
		self.PostBuildInit()
		return self.root

	def PreBuildInit(self):
		# BASICS
		self.theme_cls = ThemeManager()
		self.title = "Intelligent Job Scheduler"
		self.orderpath = './orders/ORDERS_15.txt'

		# CALCULATIONS PARA
		self.jbuffer = jobbuffer
		self.pbuffer = proceduralbuffer
		self.drydays = 2
		self.qoffset = 2000
		self.soffset = 2
		self.roffset = 7
		self.LNSmax = 500
		self.swapmax = 1000
		self.exportperms = 'none'

		# CALCULATIONS VAR
		self.neighbourhoods = [
		(' Random ',	partial(self.neighbours_random, num=100)),
		('Swapping', 	self.neighbours_swap),
		('LNS (3) ', 	partial(self.neighbours_LNS, size=3)),
		# ('LNS (4) ', 	partial(self.neighbours_LNS, size=4)),
		('Idle (4)', 	partial(self.neighbours_idle, size=4)),
		('Idle (5)', 	partial(self.neighbours_idle, size=5))
		]

	def ReBuildInit(self):
		self.orders = ReadOrders(self.orderpath)
		self.timelimit = round(len(self.orders)**2/15.0,4) #mins

		self.signal = 'run'
		self.strategytime = [0.0 for i in range(len(self.neighbourhoods))]
		self.strategyimpr = [0.0 for i in range(len(self.neighbourhoods))]
		self.pausetime = 0.0
		self.bestut = 0.0
		self.selectedorders = []
		self.UpdateSettings()

	def PostBuildInit(self):
		pass
	###################################################################### MAIN LAYOUT ######################################################################
	def UpdateMain(self):
		self.root.ids.maingrid.clear_widgets()
		for o in self.orders:
			b = BoxLayout()
			b.add_widget(ContentLabel(text=o.jo))
			b.add_widget(ContentLabel(text=str(o.qty)))
			b.add_widget(ContentLabel(text=str(o.sections)))
			b.add_widget(ContentLabel(text=str(o.sheets)))
			b.add_widget(ContentLabel(text=str(o.rapdate)[:10]))
			b.add_widget(ContentLabel(text=str(round(o.timetodue,2))))
			b.add_widget(ContentLabel(text='-'))
			b.add_widget(Builder.load_string(mainostatus_kv))		
			b.children[0].children[0].bind(on_release=partial(self.OrderStatus,disable=False))
			self.root.ids.maingrid.add_widget(b)

	def OrderStatus(self, btn, disable, *args):
		def SelectAll(checkbox, value):
			for b in statuspanel.children:
				if type(b).__name__=='BoxLayout':
					b.children[0].state = value

		def ApplyChange(btn):
			for b in statuspanel.children:
				if type(b).__name__=='BoxLayout':
					check = b.children[0]
					proc = b.children[1].text.lower()
					if proc=='':
						continue
					if check.state=='down':
						o.ES[proc] = 0.0
						o.EE[proc] = 0.0
						o.CopytoSuborders(proc)
					else:
						o.ES[proc] = -1.0
						o.EE[proc] = -1.0
						o.CopytoSuborders(proc)
			self.UpdateResult(self.orders)
			statuspopup.dismiss()

		jo = btn.parent.parent.children[-1].text
		o = [o for o in self.orders if o.jo==jo][0]
		statuspanel = BoxLayout(orientation='vertical')
		b = BoxLayout()
		b.add_widget(Label(text=''))
		selectall = MDCheckbox(state='down' if not [proc for proc in machines if o.EE[proc]<0] else 'normal', disabled=disable)
		selectall.bind(state=SelectAll)
		b.add_widget(selectall)
		statuspanel.add_widget(b)
		for key in machines:
			b = BoxLayout()
			b.add_widget(Label(text=key.upper()))
			b.add_widget(MDCheckbox(state='down' if o.EE[key]>=0 else 'normal', disabled=disable))
			statuspanel.add_widget(b)
		statuspopup = Popup(title='JO#'+jo+' Status',
							title_size=sp(20),
							content=statuspanel,
							size_hint=(.3,.8))
		if not disable:
			statuspanel.add_widget(MDRaisedButton(text='Apply', on_release=ApplyChange, size_hint=(1,1)))
			statuspopup.background = 'atlas://data/images/defaulttheme/button'
		statuspopup.open()

	def UpdateResult(self, orders):
		self.root.ids.prepressnpressgrid.clear_widgets()
		self.root.ids.postpress1grid.clear_widgets()
		self.root.ids.postpress2grid.clear_widgets()
		for j,tab in enumerate([self.root.ids.prepressnpressgrid, self.root.ids.postpress1grid, self.root.ids.postpress2grid]):
			for o in orders:
				b = BoxLayout()
				b.add_widget(ContentLabel(text=o.jo))
				for i,key in enumerate(o.ES):
					if j*3<=i<(j+1)*3:
						if o.ES[key]<0:
							txt1 = '-'
						elif o.ES[key]>datentime.timeframe:
							txt1 = '> timeframe'
						else:
							txt1 = DateAbbr(HourstoDate(o.ES[key]))
						if o.EE[key]<0:
							txt2 = '-'
						elif o.EE[key]==0:
							txt2 = txt1 = 'done'
						elif o.EE[key]>datentime.timeframe:
							txt2 = '> timeframe'
						else:
							txt2 = DateAbbr(HourstoDate(o.EE[key]))
						b.add_widget(ContentLabel(text=txt1))
						b.add_widget(ContentLabel(text=txt2))
				tab.add_widget(b)
	
	def UpdateInsert(self):
		def Insert(btn):
			if not self.selecteddate:
				return
			try:
				kwargs = {'jo':			str(box.ids.insertjo.text),
						'qty':			int(box.ids.insertqty.text),
						'sections':		int(box.ids.insertsection.text),
						'sheets':		int(box.ids.insertqty.text)*int(box.ids.insertsection.text),
						'incomedate':	datetime.date.today(),
						'rapdate':		datetime.datetime.strptime(self.selecteddate, '%Y-%m-%d'),
						'pldate':		datetime.datetime.strptime(self.selecteddate, '%Y-%m-%d')}
			except:
				return
			o = Order(**kwargs)
			self.orders.append(o)
			self.UpdateMain()
			self.UpdateResult(self.orders)
			self.root.ids.mainscroll.scroll_to(self.root.ids.mainscroll.children[0].children[0])
			box.ids.insertjo.text = ''
			box.ids.insertqty.text = ''
			box.ids.insertsection.text = ''
			Snackbar(text="Insert Successful").show()

		def Cancel(btn):
			self.root.ids.mainbox.remove_widget(box)
			self.root.ids.mainscroll.size_hint_y=1

		def InsertDatePicker(btn):
			def Setrapdate(date_obj):
				# box.ids.insertrapdate.text = str(date_obj)
				self.selecteddate = str(date_obj)
			MDDatePicker(Setrapdate).open()

		if not type(self.root.ids.mainbox.children[0]).__name__=='ScrollView':
			return

		box = Builder.load_string(insertbox_kv)	
		self.selecteddate = ''
		box.ids.insertrapdate.bind(on_release=InsertDatePicker)
		box.ids.insertbtn.bind(on_release=Insert)
		box.ids.cancelbtn.bind(on_release=Cancel)
		self.root.ids.mainbox.add_widget(box)
		self.root.ids.mainscroll.size_hint_y=.8

	def UpdateRemove(self):
		def RemoveConfirm(btn):
			def DisableAll(boolean):
				self.root.ids.removeallcheck.disabled = boolean
				for b in self.root.ids.removegrid.children:
					b.children[0].disabled = boolean

			def Remove(btn):
				count = 0
				for b in self.root.ids.removegrid.children:
					if type(b).__name__ == 'MDRaisedButton':
						continue
					if b.children[0].state=='down':
						jo = b.children[-1].text
						self.orders.remove([o for o in self.orders if o.jo==jo][0])
						count += 1
					self.UpdateMain()
					self.UpdateResult(self.orders)
					self.root.ids.scr_mngr.current = 'main'
				Snackbar(text=str(count)+" Order(s) Removed").show()

			def Cancel(btn):
				self.root.ids.removegrid.remove_widget(confirmbox)
				rbtn.disabled = False
				rbtn.md_bg_color = elite
				DisableAll(False)

			if not [b for b in self.root.ids.removegrid.children if type(b).__name__=='BoxLayout' and b.children[0].state=='down']:
				return
			DisableAll(True)
			rbtn.disabled = True
			rbtn.md_bg_color = transparent
			confirmbox = Builder.load_string(removeconfirmbox_kv)
			confirmbox.ids.removeconfirmbtn.bind(on_release=Remove)
			confirmbox.ids.removecancelbtn.bind(on_release=Cancel)
			self.root.ids.removegrid.add_widget(confirmbox)
					
		def RemoveAll(checkbox, value):
			for b in self.root.ids.removegrid.children:
				b.children[0].state=value
		self.root.ids.removegrid.clear_widgets()
		self.root.ids.removeallcheck.bind(state=RemoveAll)
		for o in self.orders:
			b=BoxLayout()
			b.add_widget(ContentLabel(text=str(o.jo)))
			b.add_widget(ContentLabel(text=str(o.qty)))
			b.add_widget(ContentLabel(text=str(o.sections)))
			b.add_widget(ContentLabel(text=str(o.sheets)))
			b.add_widget(ContentLabel(text=str(o.rapdate)[:10]))
			f = FloatLayout()
			f.add_widget(MDIconButton(icon='dots-horizontal', on_release=partial(self.OrderStatus,disable=True), pos_hint={'center_x':.5,'center_y':.5}))
			b.add_widget(f)
			b.add_widget(MDCheckbox(state='normal'))
			self.root.ids.removegrid.add_widget(b)
		rbtn = MDRaisedButton(text='Remove',on_release=RemoveConfirm,size_hint=(1,1))
		rbtn.md_bg_color=elite
		self.root.ids.removegrid.add_widget(rbtn)
		

	def SelectFile(self):
		def _fbrowser_canceled(instance):
			popup.dismiss()
		def _fbrowser_success(instance):
			try:
				self.orderpath = instance.selection[0]
				self.ReBuildInit()
				self.UpdateMain()
				self.UpdateResult(self.orders)
				popup.dismiss()
			except:
				popup.title = 'Please Select a Correct File'
			
		if platform == 'win':
			user_path = dirname(expanduser('~')) + sep + 'Documents'
		else:
			user_path = expanduser('~') + sep + 'Documents'
		browser = FileBrowser(select_string='Select',
							favorites=[(user_path, 'Documents')])
		browser.bind(on_success=_fbrowser_success,
					on_canceled=_fbrowser_canceled)
		popup = Popup(title='Select a file',
					title_size=sp(20),
					size_hint=(1,.75),
					content=browser,
					background='atlas://data/images/defaulttheme/button')
		popup.open()

	def ApplySettings(self):
		self.jbuffer 		= float(self.root.ids.setjbuffer.text)
		self.pbuffer 		= float(self.root.ids.setpbuffer.text)
		self.permsreport	= 'none'
		if self.root.ids.setexportperms_best.state=='down':
			self.permsreport	= 'best'
		elif self.root.ids.setexportperms_all.state=='down':
			self.permsreport	= 'all'
		self.qoffset		= int(self.root.ids.setqoffset.text)
		self.soffset		= int(self.root.ids.setsoffset.text)
		self.roffset		= int(self.root.ids.setroffset.text)
		self.LNSmax			= int(self.root.ids.setlnsmax.text)
		self.swapmax		= int(self.root.ids.setswapmax.text)
		self.timelimit 		= float(self.root.ids.settimelimit.text)
		self.root.ids.scr_mngr.current = 'main'
		Snackbar(text="Settings Updated").show()

	def UpdateSettings(self):
		try:
			self.root.ids.settimelimit.text = str(self.timelimit)
		except:
			pass
	###################################################################### THREADING ######################################################################
	def StartTH(self):
		def pauseTH(instance):
			if self.signal == 'pause':
				self.signal = 'run'
				self.THcontroller.children[-1].icon = 'pause'
			else:
				self.signal = 'pause'
				self.THcontroller.children[-1].icon = 'play'

		def killTH(instance):
			if not self.signal=='stop':
				print '*'*80
				print '*'*34,'Forced End','*'*34
				print '*'*80
			self.signal = 'stop'
			self.THcontroller.children[-1].disabled = True
			self.THcontroller.children[0].icon = 'reply'
			self.THpopup.dismiss()

		def isProcessing(instance):
			if self.th.isAlive():
				return True
			else:
				self.UpdateResult(ForSchedule(copy.deepcopy(self.orders)))

		self.th = threading.Thread(target=self.RunTH)
		self.th.start()

		self.THpanel = BoxLayout(orientation='vertical')
		self.THpanelpb = MDProgressBar(size_hint_y=5, max=self.timelimit*60.0)
		self.THcontroller = BoxLayout()
		self.THcontroller.add_widget(MDIconButton(icon='pause', on_release=pauseTH))
		self.THcontroller.add_widget(MDIconButton(icon='stop', on_release=killTH))
		self.THpanel.add_widget(self.THpanelpb)
		self.THpanel.add_widget(self.THcontroller)
		self.THpopup = Popup(title='Initializing...',
							title_size=sp(20),
							size_hint=(.5,.5),
							content=self.THpanel,
							on_dismiss=isProcessing,
							background='atlas://data/images/defaulttheme/vkeyboard_key_normal')
		self.THpopup.open()

	def RunTH(self):
		print '*'*80
		print '*'*35,' Start  ','*'*35
		print '*'*80
		print
		print 'no. orders\t:',len(self.orders)
		print 'timeframe\t:',datentime.timeframe/(sum(workingweek)+0.0),'week(s)'
		print 'processor(s)\t:',multiprocessing.cpu_count()
		print 'est. time\t:', self.timelimit,'min(s)'
		print 
		self.signal = 'run'
		self.t0  = time.time()
		while time.time()-self.t0 < self.timelimit*60:
			t = time.time()
			self.pausetime = 0.0
			MP(random.randint(0,len(self.neighbourhoods)-1))
			if not self.signal=='stop':
				print 'time taken',round(time.time()-t-self.pausetime,4),'seconds'
				print
				self.t0+=self.pausetime
			else:
				return
		ex.Export(ForSchedule(copy.deepcopy(self.orders)))
		self.signal = 'stop'
		self.UpdateTHpanel()
		self.THcontroller.children[-1].disabled = True
		self.THcontroller.children[0].icon = 'reply'

		print '*'*80
		print '*'*35,' Ended  ','*'*35
		print '*'*80

	def SignalCheck(self):
		t = time.time()
		while self.signal=='pause':
			time.sleep(1)
			print '.',
			if self.signal=='stop':
				return False
		if self.signal=='stop':
			return False
		self.pausetime+=time.time()-t
		self.THpanelpb.max+=self.pausetime
		return True

	def UpdateTHpanel(self):
		self.THpanelpb.value = time.time()-self.t0
		self.THpopup.title = 'Processing Permutations... '+str(round(self.THpanelpb.value/self.THpanelpb.max*100,2))+'%'
	###################################################################### CALCULATIONS ######################################################################
	def neighbours_random(self, num):
		candidates = []
		for i in range(num):
			if not self.SignalCheck():
				return []
			self.UpdateTHpanel()
			candidate = copy.deepcopy(self.orders)
			random.shuffle(candidate)
			candidates.append(candidate)
		return candidates

	def neighbours_swap(self):
		candidates = []
		for i,j in combinations(range(len(self.orders)),2):
			self.UpdateTHpanel()
			candidate = copy.deepcopy(self.orders)
			if not self.SignalCheck():
				return []
			candidate[i],candidate[j] = candidate[j],candidate[i]
			candidates.append(candidate)
		return candidates

	def neighbours_LNS(self, size):
		approach = 'UT'
		candidates = []
		neighbourhoods = list(combinations(self.orders,size))
		random.shuffle(neighbourhoods)

		for subset in neighbourhoods[:self.LNSmax]:
			if not self.SignalCheck():
				return []
			self.UpdateTHpanel()

			bestsubperm = list(subset)
			bestsubut = CalUT(ForSchedule(copy.deepcopy(subset)))
			for perm in permutations(subset):
				# Method 1: SPT
				if approach=='SPT': 
					pass
				# Method 2: Highest Utilization
				elif approach=='UT':
					avgsubut = CalUT(ForSchedule(copy.deepcopy(perm)))
					if avgsubut > bestsubut:
						bestsubut = avgsubut
						bestsubperm = list(perm)
			# if another ordering or the subset has a better performance
			if not bestsubperm==list(subset):
				candidate = copy.deepcopy(self.orders)
				# copy back the bestsubperm to fullperm
				i=0
				for j,o in enumerate(candidate):
					if o.jo in [r.jo for r in bestsubperm]:
						candidate[j] = bestsubperm[i]
						i+=1
				candidates.append(candidate)
		return candidates

	def neighbours_idle(self, size):
		candidates = []
		fororders = ForSchedule()
		self.UpdateTHpanel()
		if not self.SignalCheck():
			return []
		return [self.orders]

if __name__ == '__main__':
	from kivymd.button import *
	from kivymd.snackbar import Snackbar
	from kivymd.theming import ThemeManager
	from kivymd.progressbar import MDProgressBar
	from kivymd.selectioncontrols import MDCheckbox
	from kivymd.navigationdrawer import NavigationDrawerIconButton
	from kivymd.date_picker import MDDatePicker
	from uix.jscolor import *
	from uix.jslabel import ContentLabel, TitleLabel
	from allkv import *

	multiprocessing.freeze_support()
	ex = Exporter()
	app = MDScheduler()
	app.run()