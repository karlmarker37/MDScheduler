main_widget_kv='''
#:import Toolbar kivymd.toolbar.Toolbar
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import NavigationDrawerToolbar kivymd.navigationdrawer.NavigationDrawerToolbar
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import MDTextField kivymd.textfields.MDTextField
#:import MDProgressBar kivymd.progressbar.MDProgressBar
#:import MDBottomNavigation kivymd.tabs.MDBottomNavigation
#:import MDBottomNavigationItem kivymd.tabs.MDBottomNavigationItem
#:import MDIconButton kivymd.button.MDIconButton
#:import MDDropdownMenu kivymd.menu.MDDropdownMenu
#:import FloatInput uix.floatinput.FloatInput

<Button>:
    markup: True
<Label>:
    markup: True
<MDLabel>:
	halign: 'center'
<ContentLabel>:
	font_size: sp(16)
	canvas.before:
		Color:
			rgba: self.bcolor
		Rectangle:
			pos: self.pos
			size: self.size
<TitleLabel>:
	font_size: sp(16)
	canvas.before:
		Color:
			rgba: self.bcolor
		Rectangle:
			pos: self.pos
			size: self.size

NavigationLayout:
	id: nav_layout
	MDNavigationDrawer:
		id: nav_drawer
		##NavigationDrawerToolbar:
		##	MDIconButton:
		##		icon: 'home'
		NavigationDrawerIconButton:
			icon: 'home'
			text: "Home"
			on_release: app.root.ids.scr_mngr.current = 'main'
		NavigationDrawerIconButton:
			icon: 'forward'
			text: "Scheduling Results"
			on_release: app.root.ids.scr_mngr.current = 'result'
		NavigationDrawerIconButton:
			icon: 'plus'
			text: "Insert Order(s)"
			on_release: app.root.ids.scr_mngr.current = 'main'
			on_release: app.UpdateInsert()
		NavigationDrawerIconButton:
			icon: 'delete'
			text: "Remove Order(s)"
			on_release: app.root.ids.scr_mngr.current = 'remove'
			on_release: app.UpdateRemove()
		NavigationDrawerIconButton:
			icon: 'file-find'
			text: "Import"
			on_release: app.SelectFile()
		NavigationDrawerIconButton:
			icon: 'file-export'
			text: "Export Results"
			on_release: app.root.ids.scr_mngr.current = 'export'
		NavigationDrawerIconButton:
			icon: 'settings'
			text: "Settings"
			on_release: app.root.ids.scr_mngr.current = 'settings'
	BoxLayout:
		orientation: 'vertical'
		Toolbar:
			id: toolbar
			title: 'Intelligent Job Scheduler'
			md_bg_color: app.theme_cls.primary_color
			background_palette: 'Primary'
			background_hue: '500'
			left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
			right_action_items: [['play', lambda x: app.StartTH()]] ##, ['camera', lambda x: None]]
		ScreenManager:
			id: scr_mngr
			Screen:
				name: 'main'
				BoxLayout:
					id: mainbox
					orientation: 'vertical'
					BoxLayout:
						size_hint_y: .1
						TitleLabel:
							text: 'JO#'
						TitleLabel:
							text: 'Qty.'
						TitleLabel:
							text: 'Section'
						TitleLabel:
							text: 'Sheets'
						TitleLabel:
							text: 'RAP Date'
						TitleLabel:
							text: 'Due Time'
						TitleLabel:
							text: 'Progress'
						TitleLabel:
							text: 'Status'
					ScrollView:
						id: mainscroll
						size: self.size
						GridLayout:
							id: maingrid
							cols: 1
							size_hint_y: None
							height: self.minimum_height
							row_default_height: dp(50)
							row_force_default: True
			Screen:
				name: 'result'
                MDBottomNavigation:
					orientation: 'vertical'
					MDBottomNavigationItem:
						name: 'prepressnpress'
						text: "Pre-Press & Press"
						icon: "printer"
						BoxLayout:
							orientation: 'vertical'
							BoxLayout:
								size_hint_y: .1
								TitleLabel:
									text: 'JO#'
									size_hint_x: .5
								TitleLabel:
									text: 'Sheet'
								TitleLabel:
									text: 'Print'
								TitleLabel:
									text: 'Dry'
							ScrollView:
								do_scroll_x: False
								GridLayout:
									id: prepressnpressgrid
									cols: 1
									size_hint_y: None
									height: self.minimum_height
									row_default_height: dp(50)
									row_force_default: True
					MDBottomNavigationItem:
						name: 'postpress1'
						text: "Post Press 1"
						icon: "book-open"
						BoxLayout:
							orientation: 'vertical'
							BoxLayout:
								size_hint_y: .1
								TitleLabel:
									text: 'JO#'
									size_hint_x: .5
								TitleLabel:
									text: 'Fold'
								TitleLabel:
									text: 'FoldNip'
								TitleLabel:
									text: 'Nip'
							ScrollView:
								do_scroll_x: False
								GridLayout:
									id: postpress1grid
									cols: 1
									size_hint_y: None
									height: self.minimum_height
									row_default_height: dp(50)
									row_force_default: True
					MDBottomNavigationItem:
						name: 'postpress2'
						text: "Post Press 2"
						icon: "book-open-page-variant"
						BoxLayout:
							orientation: 'vertical'
							BoxLayout:
								size_hint_y: .1
								TitleLabel:
									text: 'JO#'
									size_hint_x: .5
								TitleLabel:
									text: 'Collate'
								TitleLabel:
									text: 'Sew'
								TitleLabel:
									text: 'Case-in'
							ScrollView:
								do_scroll_x: False
								GridLayout:
									id: postpress2grid
									cols: 1
									size_hint_y: None
									height: self.minimum_height
									row_default_height: dp(50)
									row_force_default: True
			Screen:
				name: 'remove'
				BoxLayout:
					orientation: 'vertical'
					BoxLayout:
						size_hint_y: .1
						TitleLabel:
							text: 'JO#'
						TitleLabel:
							text: 'Qty.'
						TitleLabel:
							text: 'Section'
						TitleLabel:
							text: 'Sheets'
						TitleLabel:
							text: 'RAP Date'
						TitleLabel:
							text: 'Status'
						MDCheckbox:
							id: removeallcheck
							state: 'normal'
					ScrollView:
						size: self.size
						GridLayout:
							id: removegrid
							cols: 1
							size_hint_y: None
							height: self.minimum_height
							row_default_height: dp(50)
							row_force_default: True
			Screen:
				name: 'export'
			Screen:
				name: 'settings'
				orientation: 'vertical'
				BoxLayout:
					orientation: 'vertical'
					padding: 30
					spacing: 20
					BoxLayout:
						spacing: 10
						FloatInput:
							id: setjbuffer
							hint_text: "Job Buffer (hr)"
							text: str(app.jbuffer)
							helper_text: "extra make-ready time"
							helper_text_mode: "on_focus"
							required: True
						FloatInput:
							id: setpbuffer
							hint_text: "Procedural Buffer (hr)"
							text: str(app.pbuffer)
							helper_text: "the transportation time between stations"
							helper_text_mode: "on_focus"
							required: True
					BoxLayout:
						spacing: 10
						FloatInput:
							id: setqoffset
							hint_text: "Qty. Offset"
							text: str(app.qoffset)
							helper_text: "the max difference of qty. to be similar"
							helper_text_mode: "on_focus"
							required: True
						FloatInput:
							id: setsoffset
							hint_text: "Sections Offset"
							text: str(app.soffset)
							helper_text: "the max difference of sections to be similar"
							helper_text_mode: "on_focus"
							required: True
					BoxLayout:
						spacing: 10
						FloatInput:
							id: setroffset
							hint_text: "RAP Date Offset (days)"
							text: str(app.roffset)
							helper_text: "the max difference of RAP date to be similar"
							helper_text_mode: "on_focus"
							required: True
						FloatInput:
							disabled: True
					BoxLayout:
						spacing: 10
						FloatInput:
							id: setlnsmax
							hint_text: "LNS Max"
							text: str(app.LNSmax)
							helper_text: "the upper limit of LNS search"
							helper_text_mode: "on_focus"
							required: True
						FloatInput:
							id: setswapmax
							hint_text: "Swapping Max"
							text: str(app.swapmax)
							helper_text: "the upper limit of basic swapping search"
							helper_text_mode: "on_focus"
							required: True
					BoxLayout:
						spacing: 10
						FloatInput:
							id: settimelimit
							hint_text: "Time Limit (mins)"
							text: str(app.timelimit)
							helper_text: "the running time of bat algorithm"
							helper_text_mode: "on_focus"
							required: True
						FloatInput:
							disabled: True
					BoxLayout:
						spacing: 10
						MDLabel:
							size_hint: 5,1
							font_style: 'Subhead'
							text: 'Export Permutations: '
						MDLabel:
							size_hint: 2,1
							text: 'None'
						MDCheckbox:
							size_hint: 1,1
							id: setexportperms_none
							group: 'setexportperms'
							state: 'down' if app.exportperms=='none' else 'normal'
						Label:
						MDLabel:
							size_hint: 2,1
							text: 'Best Only'
						MDCheckbox:
							size_hint: 1,1
							id: setexportperms_best
							group: 'setexportperms'
							state: 'down' if app.exportperms=='best' else 'normal'
						Label:
						MDLabel:
							size_hint: 2,1
							text: 'All'
						MDCheckbox:
							size_hint: 1,1
							id: setexportperms_all
							group: 'setexportperms'
							state: 'down' if app.exportperms=='all' else 'normal'
						Label:
							size_hint:5,1

					MDRaisedButton:
						text: 'Apply'
						size_hint: 1,1
						on_release: app.ApplySettings()
'''

removeconfirmbox_kv = '''
BoxLayout:
	MDRaisedButton:
		id: removecancelbtn
		text: 'Cancel'
		size_hint: 1,1
		md_bg_color: [.25,.25,.25, .8]
	MDRaisedButton:
		id: removeconfirmbtn
		text: 'Confirm'
		size_hint: 1,1
		md_bg_color: [ .25,  .75,  .25, .8]

'''

insertbox_kv = '''
BoxLayout:
	size_hint_y: .2
	orientation: 'vertical'
	BoxLayout:
		spacing: 5
		padding: (10,0,0,0)
		canvas.before:
			Color:
				rgba: [.75,.75,.75,.5]
			Rectangle:
				size: self.size
				pos: self.pos
		FloatInput:
			id: insertjo
			hint_text: 'JO#'
			required: True
		FloatInput:
			id: insertqty
			hint_text: 'Qty.'
			required: True
		FloatInput:
			id: insertsection
			hint_text: 'Section'
			required: True
		Label:
		FloatLayout:
			NavigationDrawerIconButton:
				id: insertrapdate
				icon: 'calendar'
				pos_hint: {'center_x':.5,'center_y':.5}
		Label:
		Label:
		Label:
	BoxLayout:
		MDRaisedButton:
			id: cancelbtn
			size_hint: 1,1
			text: 'Cancel'
			md_bg_color: [.25,.25,.25, .8]
		MDRaisedButton:
			id: insertbtn
			size_hint: 1,1
			text: 'Insert'
'''

mainostatus_kv = '''
FloatLayout:
	canvas.before:
		Color:
			rgba: [1,1,1,1]
		Rectangle:
			size: self.size
			pos: self.pos
	MDIconButton:
		icon: 'dots-horizontal'
		pos_hint: {'center_x':.5,'center_y':.5}
'''