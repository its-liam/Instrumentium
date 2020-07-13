from win32api import GetSystemMetrics
import math

import tkinter as tk
import tkinter.font as font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from lines import Option, Asset, Futures, ProfitLine, updateSmallestX, updateLargestX, updateInstruments



class Instrumentium():
	""" A finance visualisation tool """
	def __init__(self, master):
		self.master = master
		self.master.update() # update the root to calibrate size values

		# define lines list (IP and graph derive values from here)
		self.lines = []
		self.profit = None
		self.FONT_FAMILY = "Cascadia Code"

		# colors
		self.GREY_THEME = "#262626"
		self.MONEY_GREEN = "#89b05d"#"#81a658"
		self.MONEY_GREEN_RGB = (137/255, 176/255, 93/255)
		self.DIM_GREEN = "#475c30"#"#5b753e"#"#617d42"#"#708f4d"
		self.WHITE_THEME = "#f5f5f5"
		self.LIGHTER_GREY = "#424242"
		self.RED_MONEY = "#ff3a2f"
		self.AQUA = "#5abeb6"
		self.AQUA_DIM = "#3c7d78"
		self.PLACEHOLDER_WHITE = "#737373"
		self.DARKER_GREY = "#7a7a7a"
		self.DISABLED_PLACEHOLDER = "#3d3d3d"

		# create master frame - everything must be packed onto master frame to enable menus
		self.masterFrame = tk.Frame(master=self.master,
			width=self.master.winfo_width(),
			height=self.master.winfo_height(),
			background=self.GREY_THEME)
		self.masterFrame.pack()
		self.masterFrame.place(relx=0.5, rely=0.5, anchor="center")

		# menu constants
		self.MENU_WIDTH = 435
		self.MENU_HEIGHT = 520
		self.menuExitCrossFont = font.Font(family=self.FONT_FAMILY, size=18, weight="bold")
		self.menuTitleFont = font.Font(family=self.FONT_FAMILY, size=15, weight="bold")
		self.menuBtnFont = font.Font(family=self.FONT_FAMILY, size=13)

		# menu box flag list
		self.presetMenu = False
		self.instMenu = False
		self.posMenu = False
		self.helpMenu = False

		# special characters
		self.ARROW = "▼"
		self.UNCLICKED, self.CLICKED = "⚪", "⚫"
		self.EXIT_CROSS = "✕"
		self.RESET = "⟳"

		# create screen size constants
		self.SCREEN_WIDTH = GetSystemMetrics(0)
		self.SCREEN_HEIGHT = GetSystemMetrics(1)

		# define window panel constants
		self.HEADER_PANEL_MULTIPLIER = 0.06 	# header panel % of window height

		# create winow panels
		self.drawPanels()

		# header panel fonts
		self.headerTitleFont = font.Font(family=self.FONT_FAMILY, size=24, weight="bold")
		self.headerBtnFont = font.Font(family=self.FONT_FAMILY, size=14, weight="bold")

		# draw the header
		self.drawHeader()

		# create window constants
		self.IP_WIDTH_MULTIPLIER = 0.4		# % of body panel width which IP occupies

		# draw the IP (Instrument Panel) and graph windows
		self.drawWindows()

		# IP fonts
		self.ipHeaderTitleFont = font.Font(family=self.FONT_FAMILY, size=17, weight="bold",
			underline=True)
		self.ipAnalysisTitleFont = font.Font(family=self.FONT_FAMILY, size=17, weight="bold")
		self.ipColHeaderFont = font.Font(family=self.FONT_FAMILY, size=13, weight="bold")
		self.ipAddInstBtnFont = font.Font(family=self.FONT_FAMILY, size=12, weight="bold")
		self.ipSelectorFont = font.Font(family=self.FONT_FAMILY, size=9, weight="bold")
		self.ipRowFont = font.Font(family=self.FONT_FAMILY, size=11, weight="bold")
		self.ipArrowFont = font.Font(family=self.FONT_FAMILY, size=10)
		self.ipResetFont = font.Font(family=self.FONT_FAMILY, size=10, weight="bold")

		# define IP constants
		self.SELECT_REMOVE_COL_WIDTH = int(0.01979167 * self.SCREEN_WIDTH)		# % of screen width for selector/remove columns
		self.IP_TITLE_FRAME_HEIGHT = int(0.085 * self.SCREEN_HEIGHT)			# % of screen height for IP title frame
		self.IP_COLUMN_HEADER_HEIGHT = int(0.05 * self.SCREEN_HEIGHT)			# % of screen height for IP column headers
		self.NUMBER_OF_ROWS = 5
		self.GRAPH_WINDOW_MULTIPLIER = 0.72
		self.ANALYSIS_TITLE_FRAME_HEIGHT = 50
		

		# draw the instrument panel
		self.drawIP()

		# create row list for future reference
		self.rows = []

		# define row height so that, regardless of the number of instruments, they always align with the base of the graph panel
		self.IP_ROW_HEIGHT = self._generateRowHeight()
		self.ANALYSIS_FRAMES_HEIGHT = self._generateAnalysisFramesHeight()

		# draw the IP rows
		self.drawRows()

		# define IP entry font
		self.entryFont = font.Font(family=self.FONT_FAMILY, size=13, weight="bold")

		# define IP entry constants
		self.ENTRY_HEIGHT = int(self.IP_config_header_frame["height"]/2 * 0.85)

		# define analysis panel multipliers
		self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER = 0.35
		self.ANALYSIS_BREAKEVEN_RESULT_FRAME_WIDTH_MULTIPLIER = 1 - self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER
		self.ANALYSIS_POSITION_ENTRY_FRAME_WIDTH_MULTIPLIER = 0.27
		self.ANALYSIS_POSITION_BTN_FRAME_WIDTH_MULTIPLIER = 0.19

		# define analysis panel fonts
		self.analysisPanelLabelFont = font.Font(family=self.FONT_FAMILY, size=14, weight="bold")
		self.analysisPanelButtonFont = font.Font(family=self.FONT_FAMILY, size=15, weight="bold")

		# define position value attribute which is referenced in determine overall position at certain S_T
		self.calculatable_position = None

		# draw the IP analysis panel
		self.drawAnalysisPanel()

		# draw the graph panel windows
		self.drawGraphPanel()

		# define graph constants
		self.FIGURE_SIZE = (7.5, 4.5) 
		self.TICK_SIZE_MULTIPLIER = 0.07 # % of y_max lim which tick occupies

		# draw the graph
		self.drawFigure()

		# define scale fonts
		self.scaleLabelFont = font.Font(family=self.FONT_FAMILY, size=15, weight="bold")
		self.scaleFont = font.Font(family=self.FONT_FAMILY, size=15)

		# define scale constants
		self.SCALE_FRAME_WIDTH_MULTIPLIER = 0.725
		self.SCALE_LENGTH = 375
		self.scale1 = None
		self.scale2 = None


	def drawPanels(self):
		""" draw the main window panels """
		# create the panel frames
		self.headerPanel = tk.Frame(master=self.masterFrame,
			width=self.master.winfo_width(),
			height=int(self.SCREEN_HEIGHT * self.HEADER_PANEL_MULTIPLIER),
			padx=10,
			background=self.GREY_THEME)
		self.windowDividerFrame = tk.Frame(master=self.masterFrame,
			width=self.master.winfo_width(),
			height=2,
			background=self.MONEY_GREEN)
		self.bodyPanel = tk.Frame(master=self.masterFrame,
			width=self.master.winfo_width(),
			height=self.master.winfo_height() - self.headerPanel["height"] - self.windowDividerFrame["height"],
			background=self.GREY_THEME)

		# grid the panel frames
		self.headerPanel.grid(row=0, column=1)
		self.windowDividerFrame.grid(row=1, column=1)
		self.bodyPanel.grid(row=2, column=1)


	def drawHeader(self):
		""" draw the header's contents """
		# create header labels
		instrumentiumTitle = tk.Label(master=self.headerPanel,
			text="Instrumentium",
			font=self.headerTitleFont,
			background=self.GREY_THEME,
			foreground=self.WHITE_THEME)
		helpBtn = tk.Button(master=self.headerPanel,
			text="HELP",
			border=0,
			font=self.headerBtnFont,
			background=self.GREY_THEME,
			foreground=self.MONEY_GREEN,
			command= lambda: self.openHelpMenu__())

		# pack the header contents
		instrumentiumTitle.pack(side=tk.LEFT)
		helpBtn.pack(side=tk.RIGHT)


	def drawWindows(self):
		""" draw the body's windows """
		# create the window frames
		self.ipWindow = tk.Frame(master=self.bodyPanel,
			width=int(self.bodyPanel["width"] * self.IP_WIDTH_MULTIPLIER),
			height=self.bodyPanel["height"],
			background=self.GREY_THEME)
		self.bodyDividerFrame = tk.Frame(master=self.bodyPanel,
			width=2,
			height=self.bodyPanel["height"],
			background=self.LIGHTER_GREY)
		self.graphWindow = tk.Frame(master=self.bodyPanel,
			width=self.bodyPanel["width"] - self.ipWindow["width"],
			height=self.bodyPanel["height"],
			background=self.GREY_THEME)

		# grid_propagate() so grid children don't resize frame
		self.ipWindow.grid_propagate(0)

		# grid the windows
		self.ipWindow.grid(row=0, column=0)
		self.bodyDividerFrame.grid(row=0, column=1)
		self.graphWindow.grid(row=0, column=2)


	def drawIP(self):
		""" create the head of the IP grid """
		# create the IP window title, header and button frames
		self.IP_title_frame = tk.Frame(master=self.ipWindow,
			width=self.ipWindow["width"],
			height=self.IP_TITLE_FRAME_HEIGHT,
			background=self.GREY_THEME)

		# grid the IP window title and header frames
		self.IP_title_frame.grid(row=0, column=0, columnspan=5)

		# create the column header frames: "", "Instrument", "Position", "Configuration", ""
		self.IP_sel_header_frame = tk.Frame(master=self.ipWindow,
			width=self._getColumnWidths(0),
			height=self.IP_COLUMN_HEADER_HEIGHT,
			background=self.GREY_THEME)
		self.IP_type_header_frame = tk.Frame(master=self.ipWindow,
			width=self._getColumnWidths(1),
			height=self.IP_COLUMN_HEADER_HEIGHT,
			background=self.GREY_THEME)
		self.IP_pos_header_frame = tk.Frame(master=self.ipWindow,
			width=self._getColumnWidths(2),
			height=self.IP_COLUMN_HEADER_HEIGHT,
			background=self.GREY_THEME)
		self.IP_config_header_frame = tk.Frame(master=self.ipWindow,
			width=self._getColumnWidths(3),
			height=self.IP_COLUMN_HEADER_HEIGHT,
			background=self.GREY_THEME)
		self.IP_reset_header_frame = tk.Frame(master=self.ipWindow,
			width=self._getColumnWidths(4),
			height=self.IP_COLUMN_HEADER_HEIGHT,
			background=self.GREY_THEME)

		# grid column header frames (master is self.IP_column_header_frame)
		self.IP_sel_header_frame.grid(row=1, column=0, sticky="nesw")
		self.IP_type_header_frame.grid(row=1, column=1, sticky="nesw")
		self.IP_pos_header_frame.grid(row=1, column=2, sticky="nesw")
		self.IP_config_header_frame.grid(row=1, column=3, sticky="nesw")
		self.IP_reset_header_frame.grid(row=1, column=4, sticky="nesw")

		# pack_propagate() the header frames
		self.IP_sel_header_frame.pack_propagate(0)
		self.IP_type_header_frame.pack_propagate(0)
		self.IP_pos_header_frame.pack_propagate(0)
		self.IP_config_header_frame.pack_propagate(0)
		self.IP_reset_header_frame.pack_propagate(0)

		# first, create the IP title
		IP_title_label = tk.Label(master=self.IP_title_frame,
			text=(f"INSTRUMENT PANEL {self.ARROW}"),
			font=self.ipHeaderTitleFont,
			background=self.GREY_THEME,
			foreground=self.RED_MONEY)

		# pack the IP title
		IP_title_label.pack()
		IP_title_label.place(relx=0.5, rely=0.5, anchor="center")
		
		# create column header labels
		IP_type_col_label = tk.Label(master=self.IP_type_header_frame,
			text="Instrument",
			font=self.ipColHeaderFont,
			background=self.GREY_THEME,
			foreground=self.WHITE_THEME)
		IP_pos_col_label = tk.Label(master=self.IP_pos_header_frame,
			text="Position",
			font=self.ipColHeaderFont,
			background=self.GREY_THEME,
			foreground=self.WHITE_THEME)
		IP_config_col_label = tk.Label(master=self.IP_config_header_frame,
			text="Configuration",
			font=self.ipColHeaderFont,
			background=self.GREY_THEME,
			foreground=self.WHITE_THEME)

		# pack column header labels
		IP_type_col_label.pack(side=tk.LEFT)
		IP_pos_col_label.pack(side=tk.LEFT)
		IP_config_col_label.pack(side=tk.LEFT)

		# bind the title and button labels to functions
		IP_title_label.bind("<Button-1>", self.openStrategyPresetMenu__)


	def drawRows(self):
		""" draw five rows of empty instruments """
		for i in range(self.NUMBER_OF_ROWS):
			# the rows position (row) in the IP grid is (i + 2)
			grid_row = i + 2

			# we create 5 rows of empty instruments, all composed of 5 frames
			instRow = []

			# we make 5 frames for each row
			# create the frames
			rowHeight = self.IP_ROW_HEIGHT
			rowSelFrame = tk.Frame(master=self.ipWindow,
				width=self.IP_sel_header_frame["width"],
				height=rowHeight,
				background=self.GREY_THEME)
			rowTypeFrame = tk.Frame(master=self.ipWindow,
				width=self.IP_type_header_frame["width"],
				height=rowHeight,
				background=self.GREY_THEME)
			rowPosFrame = tk.Frame(master=self.ipWindow,
				width=self.IP_pos_header_frame["width"],
				height=rowHeight,
				background=self.GREY_THEME)
			rowConfigFrame = tk.Frame(master=self.ipWindow,
				width=self.IP_config_header_frame["width"],
				height=rowHeight,
				background=self.GREY_THEME)
			rowResetFrame = tk.Frame(master=self.ipWindow,
				width=self.IP_reset_header_frame["width"],
				height=rowHeight,
				background=self.GREY_THEME)

			rowSelFrame.pack_propagate(0)
			rowTypeFrame.pack_propagate(0)
			rowPosFrame.pack_propagate(0)
			rowConfigFrame.pack_propagate(0)
			rowResetFrame.pack_propagate(0)

			# create the row for the IP
			instRow.append(rowSelFrame)
			instRow.append(rowTypeFrame)
			instRow.append(rowPosFrame)
			instRow.append(rowConfigFrame)
			instRow.append(rowResetFrame)

			# store the row of frames
			self.rows.append(instRow)

			# grid the frames
			rowSelFrame.grid(row=grid_row, column=0)
			rowTypeFrame.grid(row=grid_row, column=1)
			rowPosFrame.grid(row=grid_row, column=2)
			rowConfigFrame.grid(row=grid_row, column=3)
			rowResetFrame.grid(row=grid_row, column=4)

			# create the selector label
			selector = tk.Label(master=rowSelFrame,
				text=self.UNCLICKED,
				font=self.ipSelectorFont,
				background=self.GREY_THEME,
				foreground=self.DIM_GREEN)

			# pack and place the selector label
			selector.pack()
			selector.place(relx=0.5, rely=0.5, anchor="center")

			# bind the selector
			selector.bind("<Button-1>", lambda event, row=i: self.selectorClick(event, row))

			# create the type label
			selectLabel = tk.Label(master=rowTypeFrame,
				text="Select",
				font=self.ipRowFont,
				background=self.GREY_THEME,
				foreground=self.DIM_GREEN)
			arrowLabel = tk.Label(master=rowTypeFrame,
				text=self.ARROW,
				font=self.ipArrowFont,
				background=self.GREY_THEME,
				foreground=self.DIM_GREEN)

			# pack both labels
			selectLabel.pack(side=tk.LEFT)
			arrowLabel.pack(side=tk.LEFT)

			# create the reset label
			reset = tk.Label(master=rowResetFrame,
				text=self.RESET,
				font=self.ipResetFont,
				background=self.GREY_THEME,
				foreground=self.AQUA_DIM)

			# pack and place the reset label
			reset.pack()
			reset.place(relx=0.5, rely=0.5, anchor="center")

			# bind the reset to a row reset
			reset.bind("<Button-1>", lambda event, row=i: self.rowReset(event, row))

			# add an empty instrument to $self.lines
			emptyInst = {"inst": None, "inst_config": None}
			self.lines.append(emptyInst)

			# bind the type labels
			selectLabel.bind("<Button-1>", lambda event, row=i: self.openInstMenu__(event, row))


	def drawAnalysisPanel(self):
		""" 
		draw the IP analysis panel and it's divider
		note: the analysis panel will essentially have the same height as the 
			master scale frame at any time
		"""
		IP_last_row = 2 + self.NUMBER_OF_ROWS

		# create divider panel
		self.IP_divider_frame = tk.Frame(master=self.ipWindow,
			width=self.ipWindow["width"],
			height=2,
			background=self.LIGHTER_GREY)

		# grid the divider frame
		self.IP_divider_frame.grid(row=IP_last_row, column=0, columnspan=5)
		IP_last_row += 1

		# create the analysis panel title frame
		self.analysis_title_frame = tk.Frame(master=self.ipWindow,
			width=self.ipWindow["width"],
			height=self.ANALYSIS_TITLE_FRAME_HEIGHT,
			background=self.GREY_THEME)

		# grid the analysis panel title frame
		self.analysis_title_frame.grid(row=IP_last_row, column=0, columnspan=5)
		IP_last_row += 1

		# create the analysis panel title label
		analysisPanelTitle = tk.Label(master=self.analysis_title_frame,
			text="ANALYSIS",
			font=self.ipAnalysisTitleFont,
			background=self.GREY_THEME,
			foreground=self.RED_MONEY)

		# pack and place the analysis panel title
		analysisPanelTitle.pack()
		analysisPanelTitle.place(relx=0.5, rely=0.5, anchor="center")

		# create and grid "Overall Position" row frame
		self.analysis_overall_position_frame = tk.Frame(master=self.ipWindow,
			width=self.ipWindow["width"],
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)

		# grid "Overall Position" frame
		self.analysis_overall_position_frame.grid(row=IP_last_row, column=0, columnspan=5)

		# create the "Overall Position" analysis row
		self.analysis_position_label_frame = tk.Frame(master=self.analysis_overall_position_frame,
			width=int(self.analysis_overall_position_frame["width"] * self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)
		self.analysis_position_entry_frame = tk.Frame(master=self.analysis_overall_position_frame,
			width=int(self.analysis_overall_position_frame["width"] * self.ANALYSIS_POSITION_ENTRY_FRAME_WIDTH_MULTIPLIER),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)
		self.analysis_position_enter_btn_frame = tk.Frame(master=self.analysis_overall_position_frame,
			width=int(self.analysis_overall_position_frame["width"] * self.ANALYSIS_POSITION_BTN_FRAME_WIDTH_MULTIPLIER),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)
		self.analysis_position_clear_btn_frame = tk.Frame(master=self.analysis_overall_position_frame,
			width=(self.analysis_overall_position_frame["width"] - self.analysis_position_label_frame["width"] -
					self.analysis_position_entry_frame["width"] - self.analysis_position_enter_btn_frame["width"]),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)

		# grid the "Overall Position" row frames
		self.analysis_position_label_frame.grid(row=0, column=0)
		self.analysis_position_entry_frame.grid(row=0, column=1)
		self.analysis_position_enter_btn_frame.grid(row=0, column=2)
		self.analysis_position_clear_btn_frame.grid(row=0, column=3)

		# increment last row
		IP_last_row += 1

		# create and grid "Overall Position" row frame
		self.analysis_breakeven_point_frame = tk.Frame(master=self.ipWindow,
			width=self.ipWindow["width"],
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)

		# grid "Overall Position" frame
		self.analysis_breakeven_point_frame.grid(row=IP_last_row, column=0, columnspan=5)

		# create the "Breakeven Point" analysis rows
		self.analysis_breakeven_label_frame = tk.Frame(master=self.analysis_breakeven_point_frame,
			width=int(self.analysis_breakeven_point_frame["width"] * self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)
		self.analysis_breakeven_result_frame = tk.Frame(master=self.analysis_breakeven_point_frame,
			width=int(self.analysis_breakeven_point_frame["width"] * self.ANALYSIS_BREAKEVEN_RESULT_FRAME_WIDTH_MULTIPLIER),
			height=self.ANALYSIS_FRAMES_HEIGHT,
			background=self.GREY_THEME)

		# grid the "Breakeven Point" row frames
		self.analysis_breakeven_label_frame.grid(row=0, column=0)
		self.analysis_breakeven_result_frame.grid(row=0, column=1, columnspan=3)

		# draw the "Overall Position" and "Breakeven Point" labels onto the analysis frames
		self.drawOverallPosition()
		self.disableOverallPosition() 	# the "Overall Position" row is always displayed, but when there are no active instruments, it is faded
		self.drawBreakevenPoint()		# even though, upon instantiation of the app, this is not displayed, we create the elements now


	def drawOverallPosition(self):
		""" this frame content must be drawn separately because they must wrap """
		# create "Overall Position" label 
		self.analysis_position_label = tk.Label(master=self.analysis_position_label_frame,
			text="Overall Position",
			font=self.analysisPanelLabelFont,
			justify=tk.RIGHT,
			background=self.GREY_THEME,
			foreground=self.AQUA)

		# pack and place "Overall Position" label
		self.analysis_position_label.pack()
		self.analysis_position_label.place(relx=0.95, rely=0.5, anchor="e")

		# create Overall Position "price entry"
		self.analysis_position_entry = tk.Entry(master=self.analysis_position_entry_frame,
			width=self._generatePositionEntryWidth(),
			background=self.GREY_THEME, 
			highlightbackground=self.MONEY_GREEN,
			highlightthickness=1,
			foreground=self.WHITE_THEME,
			font=self.entryFont,
			insertbackground=self.WHITE_THEME)

		# define entry placeholder
		self._printPlaceholder(self.analysis_position_entry, "price")

		# pack the entry
		self.analysis_position_entry.pack()
		self.analysis_position_entry.place(relx=0.15, rely=0.52, anchor="w")

		# bind the entry to events
		self.analysis_position_entry.bind("<Button-1>", self.entryWidgetFocus)
		self.analysis_position_entry.bind("<FocusIn>", self.entryWidgetFocus)
		self.analysis_position_entry.bind("<FocusOut>", self.positionEntryFocusOut)

		# create enter button
		self.analysis_position_enter_btn = tk.Button(master=self.analysis_position_enter_btn_frame,
			text="ENTER",
			borderwidth=0,
			font=self.analysisPanelButtonFont,
			background=self.GREY_THEME,
			foreground=self.MONEY_GREEN)

		# pack and place enter button
		self.analysis_position_enter_btn.pack()
		self.analysis_position_enter_btn.place(relx=0.5, rely=0.5, anchor="center")

		# create clear button
		self.analysis_position_clear_btn = tk.Button(master=self.analysis_position_clear_btn_frame,
			text="CLEAR",
			borderwidth=0,
			font=self.analysisPanelButtonFont,
			background=self.GREY_THEME,
			foreground=self.MONEY_GREEN)


		# pack and place clear button
		self.analysis_position_clear_btn.pack()
		self.analysis_position_clear_btn.place(relx=0.5, rely=0.5, anchor="center")

		# bind buttons to events
		self.analysis_position_enter_btn.bind("<Button-1>", self.analysisEnterBtnClick)
		self.analysis_position_clear_btn.bind("<Button-1>", self.analysisClearBtnClick)


	def disableOverallPosition(self):
		""" when no instruments are active, the overall position tool will be unusable """
		# set the "Overall Position" label to a dim colour
		self.analysis_position_label.configure(foreground=self.AQUA_DIM)

		# dim the entry
		self.analysis_position_entry.configure(highlightbackground=self.DIM_GREEN,
			foreground=self.DISABLED_PLACEHOLDER)

		# dim the buttons
		self.analysis_position_enter_btn.configure(foreground=self.DIM_GREEN)
		self.analysis_position_clear_btn.configure(foreground=self.DIM_GREEN)


	def enableOverallPosition(self):
		""" when no instruments are active, the overall position tool will be unusable """
		# set the "Overall Position" label to a dim colour
		self.analysis_position_label.configure(foreground=self.AQUA)

		# dim the entry
		self.analysis_position_entry.configure(highlightbackground=self.MONEY_GREEN)

		# fix bug of entry foreground not converting to white when there are active instruments
		if self.analysis_position_entry.get() == "price":
			self.analysis_position_entry.configure(foreground=self.PLACEHOLDER_WHITE)

		# dim the buttons
		self.analysis_position_enter_btn.configure(foreground=self.MONEY_GREEN)
		self.analysis_position_clear_btn.configure(foreground=self.MONEY_GREEN)


	def _generatePositionEntryWidth(self):
		""" 
		generate a reasonable entry width 
		importantly, entry width is sized in inches, so it's size must be a function of it's master frame, and be in inches
		hint: it's 11 at master_frame=165 pixels (~7%)
		"""
		return int(0.07 * self.analysis_position_entry_frame["width"])


	def positionEntryFocusOut(self, event):
		""" handle blur event of "Overall Position" entry """
		entryInput = self.analysis_position_entry.get()

		if entryInput == "price":
			entryInput = ""

		if len(entryInput.strip()) == 0:
			# entry is empty, add the placeholder
			self._printPlaceholder(self.analysis_position_entry, "price")
		else:
			# entry isn't empty, handle value
			if self._isNumber(entryInput):
				# the value in the input is a number
				# make the sure the color is set to white
				self.analysis_position_entry.configure(foreground=self.WHITE_THEME)

				entryInput = self._returnIntOrFloat(entryInput)
				if entryInput < min(self.profit.x) or entryInput > max(self.profit.x):
					# number input to the entry is less than zero or twice the graph's x-limit (infeasible)
					self.analysis_position_entry.configure(foreground=self.RED_MONEY)

					# ensure $self.calculatable_position is set to None
					self.calculatable_position = None
				else:
					# entered number is within acceptable range
					# make sure the colour is set to white
					self.analysis_position_entry.configure(foreground=self.WHITE_THEME)

					# delete whatever is in the entry input
					self.analysis_position_entry.delete(0, len(self.analysis_position_entry.get()))

					# round the entered value to 2 places and set it in the entry
					entryInput = round(entryInput, 2)
					self.analysis_position_entry.insert(0, entryInput)
					
					# set $self.calculatable_position, which self.updateGraph() uses to determine overall position at chosen price
					self.calculatable_position = entryInput

				# call self.updateGraph() to update the graph with the desired calculated position
				self.updateGraph()
			else:
				# the value in the input is not a number
				self.analysis_position_entry.configure(foreground=self.RED_MONEY)

				# ensure $self.calculatable_position is set to none
				self.calculatable_position = None


	def analysisEnterBtnClick(self, event):
		""" handle "enter" button click in analysis panel """
		# focus master to execute blur event function
		self.master.focus()
		self.positionEntryFocusOut(None)


	def analysisClearBtnClick(self, event):
		""" handle "clear" button click in analysis panel """
		# clear the overall position entry
		self.analysis_position_entry.delete(0, len(self.analysis_position_entry.get()))

		# focus the master to execute blur event function
		self.master.focus()

		# set $self.calculatable_position to None
		self.calculatable_position = None
		
		# self.updateGraph() has no position to calculate, remove it from the graph
		self.positionEntryFocusOut(None)

		# update the graph
		self.updateGraph()


	def drawBreakevenPoint(self):
		""" must be drawn separately because must wrap """
		# create "Breakeven Point" row label
		self.analysis_breakeven_label = tk.Label(master=self.analysis_breakeven_label_frame,
			text="Breakeven Point",
			font=self.analysisPanelLabelFont,
			justify=tk.RIGHT,
			background=self.GREY_THEME,
			foreground=self.GREY_THEME)

		# pack and place "Breakeven Point" label
		self.analysis_breakeven_label.pack()
		self.analysis_breakeven_label.place(relx=0.95, rely=0.5, anchor="e")

		# create, pack and place a test result value
		self.analysis_breakeven_result = tk.Label(master=self.analysis_breakeven_result_frame,
			text="",
			font=self.analysisPanelLabelFont,
			background=self.GREY_THEME,
			foreground=self.WHITE_THEME)
		self.analysis_breakeven_result.pack()
		self.analysis_breakeven_result.place(relx=0.075, rely=0.5, anchor="w")
		

	def selectorClick(self, event, row):
		""" handle a selector click """
		scaleRow = row

		if not self._isMenuOpen() and event.widget["foreground"] == self.MONEY_GREEN:
			if event.widget["text"] == self.CLICKED:
				event.widget.configure(text=self.UNCLICKED)

				# manage scales
				self.removeScales()

				# reset analysis panel breakeven info
				self.analysis_breakeven_label.configure(foreground=self.GREY_THEME)
				self.analysis_breakeven_result.configure(text="")
			else:
				# unclick all other selectors
				for row in self.rows:
					selector = list(row[0].children.values())[0]
					selector.configure(text=self.UNCLICKED)

				# update the clicked selector
				event.widget.configure(text=self.CLICKED)

				# manage scales
				self.removeScales()
				self.generateScales(scaleRow)

				# empty breakeven point from analysis
				self.analysis_breakeven_result.configure(text="")

				# set the breakeven point label to grey. if it is an option, it will be reset to self.AQUA
				self.analysis_breakeven_label.configure(foreground=self.GREY_THEME)

				# add the breakeven point to the analysis panel
				inst = self.lines[scaleRow]
				inst_config = inst["inst_config"]
				if inst["inst"] == "option" and (self._isNumber(inst_config["strike"]) and self._isNumber(inst_config["price"])):
					# display breakeven point text
					self.analysis_breakeven_label.configure(foreground=self.AQUA)

					if inst_config["option_type"] == "call":
						# calculate and display breakeven point for this call option
						breakeven = float(inst_config["strike"]) + float(inst_config["price"])
						self.analysis_breakeven_result.configure(text=breakeven)
					else:
						# calculate and display breakeven point for this call option
						breakeven = float(inst_config["strike"]) - float(inst_config["price"])
						self.analysis_breakeven_result.configure(text=breakeven)


	def rowReset(self, event, i):
		""" reset a given row at i """
		if not self._isMenuOpen() and event.widget["foreground"] == self.AQUA:
			# reset all frames in that row
			# we are reseting the selector frame
			# reset it's colour
			selector = list(self.rows[i][0].children.values())[0]
			selector.configure(foreground=self.DIM_GREEN)

			# if this row is selected, it may have active scales. if it is selected, call self.removeScales
			if self._selectedRow() == i:
				# remove the scales assigned to the selected row
				self.removeScales()

				# remove the breakeven point section of the analysis panel
				self.analysis_breakeven_label.configure(foreground=self.GREY_THEME)
				self.analysis_breakeven_result.configure(text="")

			# if the row is selected, unselect it
			if selector["text"] == self.CLICKED:
				selector.configure(text=self.UNCLICKED) 

			# reset the type frame
			typeFrameChildren = list(self.rows[i][1].children.values())
			selectLabel = typeFrameChildren[0]
			arrowLabel = typeFrameChildren[1]

			selectLabel.configure(text="Select", foreground=self.DIM_GREEN)
			arrowLabel.configure(foreground=self.DIM_GREEN)

			# if there are any labels in the position frame, destroy() them
			posFrameChildren = list(self.rows[i][2].children.values())
			posFrameChildren[0].destroy()
			posFrameChildren[1].destroy()

			# if there are any frames in the config frame, destroy() them
			configFrameChilren = list(self.rows[i][3].children.values())
			for frame in configFrameChilren:
				frame.destroy()

			# reset the reset label colour
			event.widget.configure(foreground=self.AQUA_DIM)

			# reset the row in $self.lines
			newInst = {"inst": None, "inst_config": None}
			self.lines[i] = newInst

			# update the graph
			self.updateGraph()


	def openInstMenu__(self, event, row):
		""" open the instrument menu """
		if not self._isMenuOpen():
			# activate menu flag
			self.instMenu = True

			# focus the root window (if an entry is focused, this will blur it)
			self.master.focus()

			# create the menu frames
			instMenuBorder = tk.Frame(master=self.master,
				width=self.MENU_WIDTH + 5,
				height=self.MENU_HEIGHT + 5,
				background=self.MONEY_GREEN)
			instMenu = tk.Frame(master=self.master,
				width=self.MENU_WIDTH,
				height=self.MENU_HEIGHT,
				background=self.LIGHTER_GREY)

			# pack and place the menu and it's border
			instMenuBorder.pack()
			instMenuBorder.place(relx=0.5, rely=0.5, anchor="center")
			instMenu.pack()
			instMenu.place(relx=0.5, rely=0.5, anchor="center")

			# create the exit cross label
			exitCross = tk.Label(master=instMenu,
				text=self.EXIT_CROSS,
				font=self.menuExitCrossFont,
				background=self.LIGHTER_GREY,
				foreground=self.RED_MONEY)

			# pack and place the exit cross
			exitCross.pack()
			exitCross.place(relx=0.96, rely=0.03, anchor="center")

			# bind the exit cross to a method which closes the menu
			exitCross.bind("<Button-1>", 
				lambda event, menuBorder=instMenuBorder, menu=instMenu, menuType="inst": self.closeMenu(event, menuBorder, menu, menuType))

			# create menu title
			instMenuTitle = tk.Label(master=instMenu,
				text="--- SELECT INSTRUMENT ---",
				font=self.menuTitleFont,
				background=self.LIGHTER_GREY,
				foreground=self.MONEY_GREEN)

			# pack and place the title
			instMenuTitle.pack()
			instMenuTitle.place(relx=0.5, rely=0.075, anchor="center")

			# create the menu buttons
			optionsBtn = tk.Button(master=instMenu,
				text="Option",
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				border=0,
				command= lambda: self.selectedInstType("option", row, instMenuBorder, instMenu))
			stockBtn = tk.Button(master=instMenu,
				text="Stock",
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				border=0,
				command= lambda: self.selectedInstType("stock", row, instMenuBorder, instMenu))
			futuresBtn = tk.Button(master=instMenu,
				text="Futures",
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				border=0,
				command= lambda: self.selectedInstType("futures", row, instMenuBorder, instMenu))

			# pack and place the menu buttons
			optionsBtn.pack()
			stockBtn.pack()
			futuresBtn.pack()
			optionsBtn.place(relx=0.5, rely=0.25, anchor="center")
			stockBtn.place(relx=0.5, rely=0.32, anchor="center")
			futuresBtn.place(relx=0.5, rely=0.39, anchor="center")


	def selectedInstType(self, chosenInst, row, instMenuBorder, instMenu):
		""" 
		change the row of the selected, and it's respective $self.lines item, 
		depending on the choice 

		chosenInst = string of chosen instrument type;
		row = the (grid) row of the instrument which was selected
		"""
		# first, store access to the type column of the selected row
		rowSelFrame = self.rows[row][0]
		rowTypeFrame = self.rows[row][1]
		rowPosFrame = self.rows[row][2]
		rowResetFrame = self.rows[row][4]
		
		# store frame children to alter later
		typeFrameChildren = list(rowTypeFrame.children.values())
		selectLabel = typeFrameChildren[0]
		arrowLabel = typeFrameChildren[1]

		# reconfigure selector color
		selector = list(rowSelFrame.children.values())[0]
		selector.configure(foreground=self.MONEY_GREEN)

		# reconfigure reset color
		reset = list(rowResetFrame.children.values())[0]
		reset.configure(foreground=self.AQUA)

		# change the select label to the chosen instrument
		selectLabel.configure(text=f"{chosenInst.title()}", foreground=self.MONEY_GREEN)
		arrowLabel.configure(foreground=self.MONEY_GREEN)

		# close the inst menu
		self.closeMenu(event=None, menuBorder=instMenuBorder, menu=instMenu, menuType="inst")

		# depending on the chosen instrument, configure $self.lines
		if chosenInst == "option":
			self.lines[row] = {"inst": "option", "inst_config": {"option_type": None, "position": None, "price": None, "strike": None }}
		elif chosenInst == "stock":
			self.lines[row] = {"inst": "stock", "inst_config": {"position": None, "price": None}}
		elif chosenInst == "futures":
			self.lines[row] = {"inst": "futures", "inst_config": {"position": None, "delivery_price": None}}

		# update the position column of the row to allow for the position menu
		# create the labels
		if len(rowPosFrame.children) != 2:
			inst_pos_label = tk.Label(master=rowPosFrame,
				text="Select", 
				font=self.ipRowFont,
				background=self.GREY_THEME,
				foreground=self.DIM_GREEN)
			inst_pos_arrow = tk.Label(master=rowPosFrame,
				text=self.ARROW,
				font=self.ipArrowFont,
				background=self.GREY_THEME,
				foreground=self.DIM_GREEN)

			# pack the labels
			inst_pos_label.pack(side=tk.LEFT)
			inst_pos_arrow.pack(side=tk.LEFT)
		
			# bind the position labels
			inst_pos_label.bind("<Button-1>", lambda event, inst=chosenInst, row=row: self.openPosMenu__(event, row))
			inst_pos_arrow.bind("<Button-1>", lambda event, inst=chosenInst, row=row: self.openPosMenu__(event, row))
		else:
			# the instrument type has been changed when one was already selected
			# bind the position labels to the new instrument type
			posSelectLabel = list(rowPosFrame.children.values())[0]
			posArrowLabel = list(rowPosFrame.children.values())[1]

			# make sure the select label has "select" text (otherwise it'll hold previous position val)
			posSelectLabel.configure(text="Select", foreground=self.DIM_GREEN)
			posArrowLabel.configure(foreground=self.DIM_GREEN)

			# rebind the position labels
			posSelectLabel.bind("<Button-1>", 
				lambda event, inst=chosenInst, row=row: self.openPosMenu__(event, row))
			posArrowLabel.bind("<Button-1>", 
				lambda event, inst=chosenInst, row=row: self.openPosMenu__(event, row))

		# destroy any entries, if they exist
		configFrameChildren = list(self.rows[row][3].children.values())
		for frame in configFrameChildren:
			frame.destroy()
		
		# update the graph
		self.updateGraph()

		# if this is the selected row, remove the scales
		if self._selectedRow() == row:
			self.removeScales()


	def openHelpMenu__(self):
		""" open the help menu """
		if not self._isMenuOpen():
			# there are no other menus open, opening this is allowable
			self.helpMenu = True

			# create menu frames
			helpMenuBorder = tk.Frame(master=self.master,
				width=self.MENU_WIDTH + 20,
				height=self.MENU_HEIGHT + 20,
				background=self.MONEY_GREEN)
			helpMenu = tk.Frame(master=self.master,
				width=self.MENU_WIDTH + 15,
				height=self.MENU_HEIGHT + 15,
				background=self.LIGHTER_GREY)

			# pack and place the menu frames
			helpMenuBorder.pack()
			helpMenuBorder.place(relx=0.5, rely=0.5, anchor="center")
			helpMenu.pack()
			helpMenu.place(relx=0.5, rely=0.5, anchor="center")

			# create exit cross label
			exitCross = tk.Label(master=helpMenu,
				text=self.EXIT_CROSS,
				font=self.menuExitCrossFont,
				background=self.LIGHTER_GREY,
				foreground=self.RED_MONEY)

			# pack and place the exit cross
			exitCross.pack()
			exitCross.place(relx=0.96, rely=0.03, anchor="center")

			# bind the exit cross
			exitCross.bind("<Button-1>", 
				lambda event, menuBorder=helpMenuBorder, menu=helpMenu, menuType="help": self.closeMenu(event, menuBorder, menu, menuType))

			# create the OK button
			okayButton = tk.Button(master=helpMenu,
				text="OK",
				border=0,
				font=font.Font(family=self.FONT_FAMILY, size=30, weight="bold"),
				background=self.LIGHTER_GREY,
				foreground=self.MONEY_GREEN,
				command= lambda: self.closeMenu(event=None, menuBorder=helpMenuBorder, menu=helpMenu, menuType="help"))

			# pack and place the okay button
			okayButton.pack()
			okayButton.place(relx=0.5, rely=0.88, anchor="center")

			# create the title
			title = tk.Label(master=helpMenu,
				text="--- HELP ---",
				font=font.Font(family=self.FONT_FAMILY, size=25, weight="bold"),
				background=self.LIGHTER_GREY,
				foreground=self.MONEY_GREEN)

			# pack and place the title
			title.pack()
			title.place(relx=0.5, rely=0.075, anchor="center")

			# create the instructional labels
			helpMenuFont = font.Font(family=self.FONT_FAMILY, size=10)
			line1 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"To create an Instrument in the Instrument Panel:",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line2 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"1. Go to the Instrument Panel, and select an \ninstrument type by opening the \"Select {self.ARROW}\" menu, and \nchoosing from the options.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line3 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"2. To choose a position in the Instrument, open the \nInstrument's position \"Select {self.ARROW}\" menu, and choose \nfrom the options.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line4 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=(f"3. To configure the values of the Instrument, add \nvalues to it's configuration entries. Click the \"{self.UNCLICKED}\" \nbutton to open the slider menu"
						" and interact with the \nInstrument values."),
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line5 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"TIP: Press the Enter button to confirm entry changes.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line6 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"TIP: Use the \"Overall Position\" tool to calculate \nthe payoff at a given price.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)
			line7 = tk.Label(master=helpMenu,
				justify=tk.LEFT,
				text=f"TIP: Click the \"INSTRUMENT PANEL {self.ARROW}\" button to open \npreset configurations.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA)

			# pack and place the first label
			line1.pack()
			line1.place(relx=0.04, rely=0.17, anchor="w")

			# pack and place the second label
			line2.pack()
			line2.place(relx=0.04, rely=0.265, anchor="w")

			# pack and place the third label
			line3.pack()
			line3.place(relx=0.04, rely=0.38, anchor="w")

			# pack and place the fourth label
			line4.pack()
			line4.place(relx=0.04, rely=0.51, anchor="w")

			# pack and place the fourth label
			line5.pack()
			line5.place(relx=0.04, rely=0.63, anchor="w")

			# pack and place the fifth label
			line6.pack()
			line6.place(relx=0.04, rely=0.69, anchor="w")

			# pack and place the sixth label
			line7.pack()
			line7.place(relx=0.04, rely=0.77, anchor="w")

			# add copyright label
			copyright = tk.Label(master=helpMenu,
				text="© 2020, Liam Dyer. All rights reserved.",
				font=helpMenuFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA_DIM)

			# pack and place the copyright label
			copyright.pack()
			copyright.place(relx=0.5, rely=0.97, anchor="center")


	def openPosMenu__(self, event, row):
		""" handle the position menu being opened """
		if not self._isMenuOpen():
			# determine the chosen instrument for this row
			chosenInst = self.lines[row]["inst"]

			# set the position menu flag
			self.posMenu = True

			# focus the master to blur anu potential entries
			self.master.focus()
			
			# create the menu frames
			posMenuBorder = tk.Frame(master=self.master,
				width=self.MENU_WIDTH + 5,
				height=self.MENU_HEIGHT + 5,
				background=self.MONEY_GREEN)
			posMenu = tk.Frame(master=self.master,
				width=self.MENU_WIDTH,
				height=self.MENU_HEIGHT,
				background=self.LIGHTER_GREY)

			# pack and place the menus
			posMenuBorder.pack()
			posMenu.pack()
			posMenuBorder.place(relx=0.5, rely=0.5, anchor="center")
			posMenu.place(relx=0.5, rely=0.5, anchor="center")

			# create the exit cross
			exitCross = tk.Label(master=posMenu,
				text=self.EXIT_CROSS,
				font=self.menuExitCrossFont,
				background=self.LIGHTER_GREY,
				foreground=self.RED_MONEY)

			# pack and place the exit cross
			exitCross.pack()
			exitCross.place(relx=0.96, rely=0.03, anchor="center")

			# bind the exit cross to close the menu
			exitCross.bind("<Button-1>", 
				lambda event, menuBorder=posMenuBorder, menu=posMenu, menuType="pos": self.closeMenu(event, menuBorder, menu, menuType))

			# create the menu buttons, dependent on the chosen instrument of the row
			if chosenInst == "option":
				# create the option position menu title
				optionPosMenuTitle = tk.Label(master=posMenu,
					text="--- Select Option Position ---",
					font=self.menuTitleFont,
					background=self.LIGHTER_GREY,
					foreground=self.MONEY_GREEN)

				# pack and place the menu title
				optionPosMenuTitle.pack()
				optionPosMenuTitle.place(relx=0.5, rely=0.08, anchor="center")

				# create the option position menu
				longCall = tk.Button(master=posMenu,
					text="Long Call",
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					border=0,
					command= lambda: self.selectedPos(row, chosenInst, "lc", posMenuBorder, posMenu))
				shortCall = tk.Button(master=posMenu,
					text="Short Call",
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					border=0,
					command= lambda: self.selectedPos(row, chosenInst, "sc", posMenuBorder, posMenu))
				longPut = tk.Button(master=posMenu,
					text="Long Put",
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					border=0,
					command= lambda: self.selectedPos(row, chosenInst, "lp", posMenuBorder, posMenu))
				shortPut = tk.Button(master=posMenu,
					text="Short Put",
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					border=0,
					command= lambda: self.selectedPos(row, chosenInst, "sp", posMenuBorder, posMenu))

				# pack and place the options position menu buttons
				longCall.pack()
				shortCall.pack()
				longPut.pack()
				shortPut.pack()
				longCall.place(relx=0.5, rely=0.25, anchor="center")
				shortCall.place(relx=0.5, rely=0.32, anchor="center")
				longPut.place(relx=0.5, rely=0.39, anchor="center")
				shortPut.place(relx=0.5, rely=0.46, anchor="center")
			elif chosenInst == "stock":
				# create stock position menu title
				stockPosMenuTitle = tk.Label(master=posMenu,
					text="--- Select Stock Position ---",
					font=self.menuTitleFont,
					background=self.LIGHTER_GREY,
					foreground=self.MONEY_GREEN)

				# pack and place stock position menu title
				stockPosMenuTitle.pack()
				stockPosMenuTitle.place(relx=0.5, rely=0.075, anchor="center")

				# create stock position menu buttons
				longStock = tk.Button(master=posMenu,
					text="Long",
					border=0,
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					command= lambda: self.selectedPos(row, chosenInst, "long", posMenuBorder, posMenu))
				shortStock = tk.Button(master=posMenu,
					text="Short",
					border=0,
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					command= lambda: self.selectedPos(row, chosenInst, "short", posMenuBorder, posMenu))

				# pack and place the stock pos menu buttons
				longStock.pack()
				shortStock.pack()
				longStock.place(relx=0.5, rely=0.25, anchor="center")
				shortStock.place(relx=0.5, rely=0.32, anchor="center")
			elif chosenInst == "futures":
				# create stock position menu title
				futuresPosMenuTitle = tk.Label(master=posMenu,
					text="--- Select Futures Position ---",
					font=self.menuTitleFont,
					background=self.LIGHTER_GREY,
					foreground=self.MONEY_GREEN)

				# pack and place stock position menu title
				futuresPosMenuTitle.pack()
				futuresPosMenuTitle.place(relx=0.5, rely=0.08, anchor="center")

				# create stock position menu buttons
				longFutures = tk.Button(master=posMenu,
					text="Long",
					border=0,
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					command= lambda: self.selectedPos(row, chosenInst, "long", posMenuBorder, posMenu))
				shortFutures = tk.Button(master=posMenu,
					text="Short",
					border=0,
					font=self.menuBtnFont,
					background=self.LIGHTER_GREY,
					foreground=self.AQUA,
					command= lambda: self.selectedPos(row, chosenInst, "short", posMenuBorder, posMenu))

				# pack and place the stock pos menu buttons
				longFutures.pack()
				shortFutures.pack()
				longFutures.place(relx=0.5, rely=0.25, anchor="center")
				shortFutures.place(relx=0.5, rely=0.32, anchor="center")


	def selectedPos(self, row, inst, pos, posMenuBorder, posMenu):
		""" handle a selected position on a instrument row """
		# access the position frame of the row
		posFrame = self.rows[row][2]

		# the position chosen must be displayed to the IP
		selectedPos = None

		# depending on the instrument and position, we need to change the rows value in $self.lines
		if inst == "option":
			# we need to change the $self.lines value for this row
			if pos == "lc":
				self.lines[row]["inst_config"]["option_type"] 	= "call"
				self.lines[row]["inst_config"]["position"]		= "long"
				selectedPos = "Long Call"
			elif pos == "sc":
				self.lines[row]["inst_config"]["option_type"] 	= "call"
				self.lines[row]["inst_config"]["position"]		= "short"
				selectedPos = "Short Call"
			elif pos == "lp":
				self.lines[row]["inst_config"]["option_type"] 	= "put"
				self.lines[row]["inst_config"]["position"]		= "long"
				selectedPos = "Long Put"
			elif pos == "sp":
				self.lines[row]["inst_config"]["option_type"] 	= "put"
				self.lines[row]["inst_config"]["position"]		= "short"
				selectedPos = "Short Put"
		elif inst == "stock":
			# update the stock value in $self.lines for this row
			if pos == "long":
				self.lines[row]["inst_config"]["position"]		= "long"
				selectedPos = "Long"
			elif pos == "short":
				self.lines[row]["inst_config"]["position"]		= "short"
				selectedPos = "Short"
		elif inst == "futures":
			# update the futures value in $self.lines for this row
			if pos == "long":
				self.lines[row]["inst_config"]["position"]		= "long"
				selectedPos = "Long"
			elif pos == "short":
				self.lines[row]["inst_config"]["position"]		= "short"
				selectedPos = "Short"

		# update the IP row for the instrument to display the updated value
		posFrameChildren = list(posFrame.children.values())
		selectLabel = posFrameChildren[0]
		arrowLabel = posFrameChildren[1]
		selectLabel.configure(text=selectedPos, foreground=self.MONEY_GREEN)
		arrowLabel.configure(foreground=self.MONEY_GREEN)

		# destroy any entries in the row if they exist
		configFrameChildren = list(self.rows[row][3].children.values())
		if len(configFrameChildren) > 0:
			for child in configFrameChildren:
				child.destroy()

		# draw the required entries
		self.drawEntries(row, inst)

		# if this row is selected, generate scales for it
		if self._selectedRow() == row:
			self.generateScales(row)

		self.updateGraph()
		
		# close the menu
		self.closeMenu(event=None, menuBorder=posMenuBorder, menu=posMenu, menuType="pos")


	def openStrategyPresetMenu__(self, event):
		""" 
		open a preset menu for strategies using the given financial instruments 

		the selected choice will override $self.lines
		"""
		if not self._isMenuOpen():
			# set the position menu flag
			self.presetMenu = True
			
			# set the focus to the root window to blur any active entries
			self.master.focus()

			# create the menu frames
			presetMenuBorder = tk.Frame(master=self.master,
				width=self.MENU_WIDTH + 5,
				height=self.MENU_HEIGHT + 5,
				background=self.RED_MONEY)
			presetMenu = tk.Frame(master=self.master,
				width=self.MENU_WIDTH,
				height=self.MENU_HEIGHT,
				background=self.LIGHTER_GREY)

			# pack and place the menu frames
			presetMenuBorder.pack()
			presetMenuBorder.place(relx=0.5, rely=0.5, anchor="center")
			presetMenu.pack()
			presetMenu.place(relx=0.5, rely=0.5, anchor="center")

			# create the menu exit cross label
			exitCross = tk.Label(master=presetMenu,
				text=self.EXIT_CROSS,
				font=self.menuExitCrossFont,
				background=self.LIGHTER_GREY,
				foreground=self.RED_MONEY)

			# pack and place the exit cross
			exitCross.pack()
			exitCross.place(relx=0.96, rely=0.03, anchor="center")

			# bind the exit cross # event, menuBorder, menu, menuType
			exitCross.bind("<Button-1>", 
				lambda event, menuBorder=presetMenuBorder, menu=presetMenu, menuType="preset": self.closeMenu(event, menuBorder, menu, menuType)) 

			# create the preset menu title
			title = tk.Label(master=presetMenu,
				text="--- Examples ---",
				font=font.Font(family=self.FONT_FAMILY, size=25, weight="bold"),
				background=self.LIGHTER_GREY,
				foreground=self.RED_MONEY)

			# pack and place the title
			title.pack()
			title.place(relx=0.5, rely=0.075, anchor="center")

			# create preset menu buttons
			bearPutSpread = tk.Button(master=presetMenu,
				text="Bear Put",
				border=0,
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				command= lambda: self.drawPreset(1, presetMenuBorder, presetMenu))
			longStraddle = tk.Button(master=presetMenu,
				text="Long Straddle",
				border=0,
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				command= lambda: self.drawPreset(2, presetMenuBorder, presetMenu))
			shortStrangle = tk.Button(master=presetMenu,
				text="Short Strangle",
				border=0,
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				command= lambda: self.drawPreset(3, presetMenuBorder, presetMenu))
			collar = tk.Button(master=presetMenu,
				text="Collar",
				border=0,
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				command= lambda: self.drawPreset(4, presetMenuBorder, presetMenu))
			protectivePut = tk.Button(master=presetMenu,
				text="Protective Put",
				border=0,
				font=self.menuBtnFont,
				background=self.LIGHTER_GREY,
				foreground=self.AQUA,
				command= lambda: self.drawPreset(5, presetMenuBorder, presetMenu))

			# pack and place the buttons
			bearPutSpread.pack()
			bearPutSpread.place(relx=0.5, rely=0.25, anchor="center")
			longStraddle.pack()
			longStraddle.place(relx=0.5, rely=0.32, anchor="center")
			shortStrangle.pack()
			shortStrangle.place(relx=0.5, rely=0.39, anchor="center")
			collar.pack()
			collar.place(relx=0.5, rely=0.46, anchor="center")
			protectivePut.pack()
			protectivePut.place(relx=0.5, rely=0.52, anchor="center")


	def drawPreset(self, strategy, menuBorder, menu):
		""" 
		dependent on a given strategy, draw it to the IP 

		option dictionary format:
		{"inst": "option", "inst_config": {"option_type": type, "position": position, "price": price, "strike": strike}}

		stock dictionary format:
		{"inst": "stock", "inst_config": {"position": position, "price": price}}
		"""
		# reset the IP
		for i in range(self.NUMBER_OF_ROWS):
			self.lines[i] = {"inst": None, "inst_config": None}

		if strategy == 1:
			# bear put strategy selected
			# create the instruments
			shortPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "short", "price": 2.5, "strike": 30}}
			longPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "long", "price": 7, "strike": 40}}

			# store the instruments into $self.lines
			self.lines[0] = shortPut
			self.lines[1] = longPut
		elif strategy == 2:
			# long straddle strategy selected
			# create the instruments
			longCall = {"inst": "option", "inst_config": {"option_type": "call", "position": "long", "price": 4, "strike": 55}}
			longPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "long", "price": 5.5, "strike": 55}}

			# store the instruments in $self.lines
			self.lines[0] = longCall
			self.lines[1] = longPut
		elif strategy == 3:
			# short strangle strategy selected
			# create the instruments
			longCall = {"inst": "option", "inst_config": {"option_type": "call", "position": "short", "price": 2.75, "strike": 45}}
			longPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "short", "price": 2.75, "strike": 35}}

			# store the instruments in $self.lines
			self.lines[0] = longCall
			self.lines[1] = longPut
		elif strategy == 4:
			# collar strategy selected
			# create the instruments
			shortCall = {"inst": "option", "inst_config": {"option_type": "call", "position": "short", "price": 5, "strike": 60}}
			longPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "long", "price": 5, "strike": 50}}
			longStock = {"inst": "stock", "inst_config": {"position": "long", "price": 55}}
		
			# store the instruments in $self.lines
			self.lines[0] = longPut
			self.lines[1] = shortCall
			self.lines[2] = longStock
		else:
			# protective put strategy selected
			# create the instruments
			longPut = {"inst": "option", "inst_config": {"option_type": "put", "position": "long", "price": 10, "strike": 62}}
			longStock = {"inst": "stock", "inst_config": {"position": "long", "price": 68}}

			# store the instruments in $self.lines
			self.lines[0] = longPut
			self.lines[1] = longStock

		# reset the IP grid
		self.resetRows()

		# update the IP to represent the selected strategy
		self.drawPresetIP()

		# unselect all rows
		for row in self.rows:
			selector = list(row[0].children.values())[0]
			selector.configure(text=self.UNCLICKED)

		# remove all scales
		self.removeScales()

		# (ultimately) update the graph
		self.updateGraph()

		# close the menu
		self.closeMenu(event=None, menuBorder=menuBorder, menu=menu, menuType="preset")


	def resetRows(self):
		""" reset every row """

		for row in self.rows:
			# reset the selector
			selector = list(row[0].children.values())[0]
			selector.configure(foreground=self.DIM_GREEN)

			# reset the type frame
			typeFrameChildren = list(row[1].children.values())
			selectLabel = typeFrameChildren[0]
			arrowLabel = typeFrameChildren[1]

			selectLabel.configure(foreground=self.DIM_GREEN,
				text="Select")
			arrowLabel.configure(foreground=self.DIM_GREEN)

			# destroy all potential frames in the position frame
			posFrameChildren = list(row[2].children.values())
			for frame in posFrameChildren:
				frame.destroy()

			# destroy all potential frames in the config frame
			configFrameChildren = list(row[3].children.values())
			for frame in configFrameChildren:
				frame.destroy()

			# reset the reset label
			reset = list(row[4].children.values())[0]
			reset.configure(foreground=self.AQUA_DIM)

		# ensure the overall position calculator is empty and $self.calculatable_position is None
		self.analysisClearBtnClick(None)

		# reset analysis panel breakeven point info
		self.analysis_breakeven_label.configure(foreground=self.GREY_THEME)
		self.analysis_breakeven_result.configure(text="")


	def drawPresetIP(self):
		""" 
		this is only called when a preset is selected. loops through self.lines 
		to create a preset strategy 
		"""
		for i in range(len(self.lines)):
			if self.lines[i]["inst"]:
				# if the line at i has a value in it, draw it to the IP grid
				# set the selector to active
				selector = list(self.rows[i][0].children.values())[0]
				selector.configure(foreground=self.MONEY_GREEN)

				# update the type frame
				instType = self.lines[i]["inst"]
				typeFrameChildren = list(self.rows[i][1].children.values())
				typeSelectLabel = typeFrameChildren[0]
				typeArrowLabel = typeFrameChildren[1]

				typeSelectLabel.configure(foreground=self.MONEY_GREEN,
					text=f"{instType.title()}")
				typeArrowLabel.configure(foreground=self.MONEY_GREEN)

				# update the position frame
				if instType == "option":
					# update the position frame for an option -- the pos menu must be correctly bound
					optionPosition = self.lines[i]["inst_config"]["position"]
					optionType = self.lines[i]["inst_config"]["option_type"]
					position = f"{optionPosition.title()} {optionType.title()}"

					# create the position labels
					positionLabel = tk.Label(master=self.rows[i][2],
						text=position,
						font=self.ipRowFont,
						background=self.GREY_THEME,
						foreground=self.MONEY_GREEN)
					arrowLabel = tk.Label(master=self.rows[i][2],
						text=self.ARROW,
						font=self.ipArrowFont,
						background=self.GREY_THEME,
						foreground=self.MONEY_GREEN)

					# pack the labels
					positionLabel.pack(side=tk.LEFT)
					arrowLabel.pack(side=tk.LEFT)

					# bind the labels
					positionLabel.bind("<Button-1>", 
						lambda event, row=i: self.openPosMenu__(event, row))
					arrowLabel.bind("<Button-1>", 
						lambda event, row=i: self.openPosMenu__(event, row))

					# draw the entries for the instrument
					self.drawEntries(row=i, inst="option")
				elif instType == "stock": 
					# update the position frame for an option
					position = self.lines[i]["inst_config"]["position"]

					# create the position labels
					positionLabel = tk.Label(master=self.rows[i][2],
						text=f"{position.title()}",
						font=self.ipRowFont,
						background=self.GREY_THEME,
						foreground=self.MONEY_GREEN)
					arrowLabel = tk.Label(master=self.rows[i][2],
						text=self.ARROW,
						font=self.ipArrowFont,
						background=self.GREY_THEME,
						foreground=self.MONEY_GREEN)

					# pack the labels
					positionLabel.pack(side=tk.LEFT)
					arrowLabel.pack(side=tk.LEFT)

					# bind the labels
					positionLabel.bind("<Button-1>", 
						lambda event, row=i: self.openPosMenu__(event, row))
					arrowLabel.bind("<Button-1>", 
						lambda event, row=i: self.openPosMenu__(event, row))

					# draw the entries for the instrument
					self.drawEntries(row=i, inst="stock")

				# update the reset label
				reset = list(self.rows[i][4].children.values())[0]
				reset.configure(foreground=self.AQUA)


	def drawEntries(self, row, inst):
		""" 
		draws responsive entries to the row 

		the way we draw entries changes depending on the inst type
		"""
		# store the config frame in a variable
		configFrame = self.rows[row][3]

		if inst == "option":
			# we are creating two entries: price and strike
			# create the entry frames
			priceEntryFrame = tk.Frame(master=configFrame,
				width=int(configFrame["width"] * 0.485),
				height=self.ENTRY_HEIGHT,
				highlightbackground=self.MONEY_GREEN,
				highlightcolor=self.MONEY_GREEN,
				highlightthickness=1,
				background=self.GREY_THEME)
			fillerEntryFrame = tk.Frame(master=configFrame,
				width=int(configFrame["width"] * 0.03),
				background=self.GREY_THEME)
			strikeEntryFrame = tk.Frame(master=configFrame,
				width=int(configFrame["width"] * 0.485),
				height=self.ENTRY_HEIGHT,
				highlightbackground=self.MONEY_GREEN,
				highlightcolor=self.MONEY_GREEN,
				highlightthickness=1,
				background=self.GREY_THEME)

			# pack the entry frames
			priceEntryFrame.pack(side=tk.LEFT)
			fillerEntryFrame.pack(side=tk.LEFT)
			strikeEntryFrame.pack(side=tk.LEFT)

			# pack propagate the entry frames
			priceEntryFrame.pack_propagate(0)
			strikeEntryFrame.pack_propagate(0)

			# create the entries
			priceEntry = tk.Entry(master=priceEntryFrame,
				width=priceEntryFrame["width"],
				background=self.GREY_THEME, 
				foreground=self.WHITE_THEME,
				font=self.entryFont,
				insertbackground=self.WHITE_THEME)
			strikeEntry = tk.Entry(master=strikeEntryFrame,
				width=strikeEntryFrame["width"],
				background=self.GREY_THEME, 
				foreground=self.WHITE_THEME,
				font=self.entryFont,
				insertbackground=self.WHITE_THEME)

			# pack the entries
			priceEntry.pack()
			strikeEntry.pack()

			# fill the entries on inception
			self._fillEntry(entryWidget=priceEntry, entryName="price", instConfigValue=self.lines[row]["inst_config"]["price"])
			self._fillEntry(entryWidget=strikeEntry, entryName="strike", instConfigValue=self.lines[row]["inst_config"]["strike"])

			# bind the entries to a click event
			priceEntry.bind("<Button-1>", self.entryWidgetFocus)
			strikeEntry.bind("<Button-1>", self.entryWidgetFocus)

			# bind the entries on focus
			priceEntry.bind("<FocusIn>", self.entryWidgetFocus)
			strikeEntry.bind("<FocusIn>", self.entryWidgetFocus)

			# bind the entries to a blur event
			priceEntry.bind("<FocusOut>", 
				lambda event, row=row, entryName="price": self.entryWidgetBlur(event, row, entryName))
			strikeEntry.bind("<FocusOut>", 
				lambda event, row=row, entryName="strike": self.entryWidgetBlur(event, row, entryName))
		elif inst == "stock":
			# we are creating one entry: price
			priceEntryFrame = tk.Frame(master=configFrame,
				width=configFrame["width"],
				height=self.ENTRY_HEIGHT,
				highlightbackground=self.MONEY_GREEN,
				highlightcolor=self.MONEY_GREEN,
				highlightthickness=1,
				background=self.GREY_THEME)

			# pack and pack_propagate the entry frame
			priceEntryFrame.pack(side=tk.LEFT)
			priceEntryFrame.pack_propagate(0)

			# create the stock entry
			priceEntry = tk.Entry(master=priceEntryFrame,
				width=priceEntryFrame["width"],
				background=self.GREY_THEME, 
				foreground=self.WHITE_THEME,
				font=self.entryFont,
				insertbackground=self.WHITE_THEME)

			# pack the entry
			priceEntry.pack()

			# fill the entry on inception
			self._fillEntry(entryWidget=priceEntry, entryName="price", instConfigValue=self.lines[row]["inst_config"]["price"])

			# bind the entries to a click event
			priceEntry.bind("<Button-1>", self.entryWidgetFocus)

			# bind the entries to a focus event
			priceEntry.bind("<FocusIn>", self.entryWidgetFocus)

			# bind the entries to a blur event
			priceEntry.bind("<FocusOut>", 
				lambda event, row=row, entryName="price": self.entryWidgetBlur(event, row, entryName))
		elif inst == "futures":
			# we are creating one entry: delivery price
			deliveryPriceEntryFrame = tk.Frame(master=configFrame,
				width=configFrame["width"],
				height=self.ENTRY_HEIGHT,
				highlightbackground=self.MONEY_GREEN,
				highlightcolor=self.MONEY_GREEN,
				highlightthickness=1,
				background=self.GREY_THEME)

			# pack and pack_propagate the entry frame
			deliveryPriceEntryFrame.pack(side=tk.LEFT)
			deliveryPriceEntryFrame.pack_propagate(0)

			# create the stock entry
			deliveryPriceEntry = tk.Entry(master=deliveryPriceEntryFrame,
				width=deliveryPriceEntryFrame["width"],
				background=self.GREY_THEME, 
				foreground=self.WHITE_THEME,
				font=self.entryFont,
				insertbackground=self.WHITE_THEME)

			# pack the entry
			deliveryPriceEntry.pack()

			# fill the entry on inception
			self._fillEntry(entryWidget=deliveryPriceEntry, entryName="delivery price", instConfigValue=self.lines[row]["inst_config"]["delivery_price"])

			# bind the entry to a click event
			deliveryPriceEntry.bind("<Button-1>", self.entryWidgetFocus)

			# bind the entry to a focus event
			deliveryPriceEntry.bind("<FocusIn>", self.entryWidgetFocus)

			# bind the entry to a blur event
			deliveryPriceEntry.bind("<FocusOut>", 
				lambda event, row=row, entryName="delivery_price": self.entryWidgetBlur(event, row, entryName))


	def entryWidgetFocus(self, event):
		""" handles a click or a focus on a entry """
		if self._isMenuOpen() or event.widget["highlightbackground"] == self.DIM_GREEN:
			return "break"
		else:
			if event.widget["foreground"] == self.PLACEHOLDER_WHITE:
				# if the entry foreground is self.PLACEHOLDER_WHITE, their is a placeholder. thus, we must clear it
				# delete all input from the widget
				event.widget.delete(0, len(event.widget.get()))

				# change the entry widget foreground to a valid color
				event.widget.configure(foreground=self.WHITE_THEME)


	def entryWidgetBlur(self, event, row, entryName):
		""" handle blur events for entry widgets """
		# store the entry input to determine it's validity
		entryInput = event.widget.get()
		instType = self.lines[row]["inst"]

		if len(entryInput.strip()) == 0:
			# the entry is empty or only has spaces, print a placeholder
			if entryName == "delivery_price":
				self._printPlaceholder(event.widget, "delivery price")
			else:
				self._printPlaceholder(event.widget, entryName)

			self.lines[row]["inst_config"][entryName] = None

			# if it is connected to a scale (it's in an active row), update it's paired scale (set it to dark mode)
			if self._selectedRow() == row:
				if instType == "option":
					if entryName == "price":
						# the entry is on a selected row and is the price entry, set it to dark mode
						self.setScaleDarkMode(self.scale1)
					else:
						self.setScaleDarkMode(self.scale2)
				elif instType == "stock" or instType == "futures":
					self.setScaleDarkMode(self.scale1)
		elif self._isNumber(entryInput):
			# the value stored in self.lines for the entry has a valid number. print it
			# determine the value as an int or a decimal with 2 decimal places
			value = self._returnIntOrFloat(entryInput)

			# clear the entry
			event.widget.delete(0, len(event.widget.get()))

			# insert the value into the entry
			event.widget.insert(0, value)

			# if the value is greater than or equal to zero, print it as white, else print it as red
			if value >= 0 and value <= 1_000_000:
				event.widget.configure(foreground=self.WHITE_THEME)

				# if this entry is paired with an active scale, update the scale
				if self._selectedRow() == row:
					# this row is selected, and thus it has an active scale
					# first, determine the instrument type
					if instType == "option":
						# determine if it's the price or strike entry
						if entryName == "price":
							# set the scale to light more and update the price scale (self.scale1)
							self.setScaleLightMode(self.scale1)
							self.updateScaleValues(self.scale1, option=True)
						else:
							# set the strike scale to light mode and update it's value (self.scale2)
							self.setScaleLightMode(self.scale2)
							self.updateScaleValues(self.scale2, option=True)
					elif instType == "stock" or instType == "futures":
						# the entry belongs to the stock or futures scale (both self.scale1)
						# set it's mode to light and update it's value
						self.setScaleLightMode(self.scale1)
						self.updateScaleValues(self.scale1)
			else:
				event.widget.configure(foreground=self.RED_MONEY)

				# if this entry is paired to an active scale, update the scale
				if self._selectedRow() == row:
					# this row is selected, thus it has an active scale. disable it for invalid input
					if instType == "option":
						if entryName == "price":
							self.setScaleDarkMode(self.scale1)
						else:
							self.setScaleDarkMode(self.scale2)
					elif instType == "stock" or instType == "futures":
						self.setScaleDarkMode(self.scale1)

			# save the new entry value into self.lines
			self.lines[row]["inst_config"][entryName] = value
		else:
			# the value blurred in the entry is invalid, print it as red, and save it in $self.lines
			# clear the entry
			event.widget.delete(0, len(event.widget.get()))

			# print the input as red to signify it as invalid
			event.widget.configure(foreground=self.RED_MONEY)

			# insert the blurred entry value into the entry
			event.widget.insert(0, entryInput)

			# save it to $self.lines
			self.lines[row]["inst_config"][entryName] = entryInput

			# if this entry is on a row that is selected, it has an active, paired scale. update it
			if self._selectedRow() == row:
				if instType == "option":
					if entryName == "price":
						self.setScaleDarkMode(self.scale1)
					else:
						self.setScaleDarkMode(self.scale2)
				elif instType == "stock" or instType == "futures":
					self.setScaleDarkMode(self.scale1)

		# update the graph on every blur
		self.updateGraph()


	def _generateRowHeight(self):
		""" 
		generate the height that each row should be so that the base of the IP 
		instrument rows sits flush with the base of the graph panel 
		"""
		# error can be ignored
		try:
			retval = int( ((self.ipWindow["height"] * self.GRAPH_WINDOW_MULTIPLIER) 
						- (self.IP_title_frame["height"] + self.IP_COLUMN_HEADER_HEIGHT))
						/ self.NUMBER_OF_ROWS)

			return retval
		except:
			pass		


	def _generateAnalysisFramesHeight(self):
		""" generate height of analysis frames """
		try:
			retval =  int((self.ipWindow["height"] - self.IP_TITLE_FRAME_HEIGHT - self.IP_COLUMN_HEADER_HEIGHT - 
						self._generateRowHeight()*self.NUMBER_OF_ROWS - 2 - self.ANALYSIS_TITLE_FRAME_HEIGHT)/2)

			return retval
		except:
			pass


	def _returnIntOrFloat(self, value):
		""" given a number, round it. if it is a whole number, truncate it and return """
		# convert from string to float
		retval = float(value)
		retval = round(retval, 2)
		if math.ceil(retval) == retval:
			# the rounded number can be converted to an int and lose no information (i.e. 10.00 === 10)
			retval = int(retval)
		return retval


	def _isNumber(self, value):
		try:
			test = float(value)
		except:
			return False
		else:
			return True


	def _fillEntry(self, entryWidget, entryName, instConfigValue):
		""" fill the entry, dependent on it's respective value in $self.lines """
		if not instConfigValue:
			# there is no value stored for this entry in $self.lines: print a placeholder
			self._printPlaceholder(entryWidget, entryName)
		elif self._isNumber(instConfigValue):
			# there is a valid number value stored in $self.lines for the entry: print it
			# clear the entry
			entryWidget.delete(0, len(entryWidget.get()))

			# depending on the number, configure the entry color
			if float(instConfigValue) >= 0:
				entryWidget.configure(foreground=self.WHITE_THEME)
			else:
				entryWidget.configure(foreground=self.RED_MONEY)

			# insert the value stored in $self.lines, it is guaranteed to be formatted (done before storage)
			entryWidget.insert(0, instConfigValue)
		elif not self._isNumber(instConfigValue):
			# there is a invalid value stored in $self.lines for this entry: print the value in red to signify invalid input
			# clear the entry
			entryWidget.delete(0, len(entryWidget.get()))

			# configure the color of the entry
			entryWidget.configure(foreground=self.RED_MONEY)

			# insert the invalid input into the entry
			entryWidget.insert(0, instConfigValue)


	def _printPlaceholder(self, entryWidget, entryName):
		""" print a placeholder to a given entry, dependent on it's name """
		# clear the widget
		entryWidget.delete(0, len(entryWidget.get()))

		# configure the entry foreground color and add the placeholder
		entryWidget.configure(foreground=self.PLACEHOLDER_WHITE)
		entryWidget.insert(0, entryName)


	def _selectedRow(self):
		""" if there is a selected row, return it's index, else return false """
		for i in range(self.NUMBER_OF_ROWS):
			rowSelector = list(self.rows[i][0].children.values())[0]
			if rowSelector["text"] == self.CLICKED:
				return i
		return -1


	def closeMenu(self, event, menuBorder, menu, menuType):
		""" close the inst menu and unset the flag """
		# destroy the menu and it's border
		menuBorder.destroy()
		menu.destroy()

		# unset it's flag, dependent on $menuType
		if menuType == "preset":
			self.presetMenu = False
		elif menuType == "inst":
			self.instMenu = False
		elif menuType == "pos":
			self.posMenu = False
		elif menuType == "help":
			self.helpMenu = False


	def _isMenuOpen(self):
		""" 
		scan $self.menu_flags: if any are true, click events should be disabled 
		"""
		if (self.presetMenu
			or self.instMenu
			or self.posMenu
			or self.helpMenu):
			return True
		else:
			return False


	def _getColumnWidths(self, column):
		""" 
		return column width, dependent on column argument 

		0 = selector column width; 	1 = instrument type column width;
		2 = position column width;	3 = configuration column width;
		4 = remove column width
		"""
		# define popular width constants
		grid_middle = int(self.ipWindow["width"] - self.SELECT_REMOVE_COL_WIDTH * 2)
		type_col_width = int(grid_middle * 0.285)
		pos_col_width = int((grid_middle - type_col_width) * 0.41)

		if column == 0 or column == 4:
			# return selector column width
			return self.SELECT_REMOVE_COL_WIDTH
		elif column == 1:
			# return type column width
			return type_col_width				# the "instrument" (type) column occupies 28% of the IP window
		elif column == 2:
			# return position column width
			return pos_col_width
		elif column == 3:
			# return config column width
			return (grid_middle - type_col_width - pos_col_width)


	def drawFigure(self):
		""" draw the matplotlib figure to the master graph frame """
		self.fig = Figure(figsize=self.FIGURE_SIZE, 
			facecolor=self.GREY_THEME)
		self.ax = self.fig.add_subplot(111)

		# config axes spine
		self.ax.spines['left'].set_position('zero')	
		self.ax.spines['left'].set_linewidth(1.5)	
		self.ax.spines['right'].set_color('none')		# remove right border
		self.ax.spines['bottom'].set_position('zero')	# moves bottom border to y=0
		self.ax.spines['bottom'].set_linewidth(1.5)		# set width of x-axis
		self.ax.spines['top'].set_color('none')			# remove top border
		self.ax.set_ylim(-50, 50)
		self.ax.set_xlim(0, 50)
		xaxis = self.ax.xaxis.get_major_ticks()
		xaxis[0].label1.set_visible(False)
		xaxis[-1].set_visible(False)
		#ax.plot([1, 2, 3, 4], [1, 8, 27, 16*4])		# i may have to set ylim and xlim dynamically?

		# config figure color
		self.ax.spines["bottom"].set_color("black")
		self.ax.spines["top"].set_color("white")
		self.ax.spines["left"].set_color("black")		
		self.ax.tick_params(axis="y", colors=self.WHITE_THEME)
		
		# set axis labels
		self.ax.set_ylabel("profit", fontsize=13, color=self.WHITE_THEME)
		self.ax.set_title(r"$S_T$", fontsize=13, color=self.WHITE_THEME)

		self.graphCanvas = FigureCanvasTkAgg(figure=self.fig, 
			master=self.masterGraphFrame)
		self.graphCanvas.draw()
		
		self.graphCanvasWidget = self.graphCanvas.get_tk_widget()
		self.graphCanvasWidget.configure(width=self.masterGraphFrame["width"],
			height=self.masterGraphFrame["height"])
		self.graphCanvasWidget.pack()
		self.graphCanvasWidget.place(relx=0.5, rely=0.5, anchor="center")


	def _resizeIP(self):
		""" called to resize all of IP """
		# resize the IP frames
		try:
			self.IP_title_frame.configure(width=self.ipWindow["width"])
		except:
			pass
		# resize the IP header frames
		try:
			self.IP_sel_header_frame.configure(width=self._getColumnWidths(0))
		except:
			pass
		try:	
			self.IP_type_header_frame.configure(width=self._getColumnWidths(1))
		except:
			pass
		try:
			self.IP_pos_header_frame.configure(width=self._getColumnWidths(2))
		except:
			pass
		try:
			self.IP_config_header_frame.configure(width=self._getColumnWidths(3))
		except:
			pass
		try:
			self.IP_reset_header_frame.configure(width=self._getColumnWidths(4))
		except:
			pass

		# resize the row frames
		rowHeight = self._generateRowHeight()
		for row in self.rows:
			try:
				row[0].configure(width=self.IP_sel_header_frame["width"],
								height=rowHeight)
			except:
				pass
			try:
				row[1].configure(width=self.IP_type_header_frame["width"],
								height=rowHeight)
			except:
				pass
			try:
				row[2].configure(width=self.IP_pos_header_frame["width"],
								height=rowHeight)
			except:
				pass
			try:
				row[3].configure(width=self.IP_config_header_frame["width"],
								height=rowHeight)
			except:
				pass
			try:	
				row[4].configure(width=self.IP_reset_header_frame["width"],
								height=rowHeight)
			except:
				pass
			configChildren = list(row[3].children.values())
			if len(configChildren) > 0:
				# we have active entries in the config frame of this row
				configFrameWidth = row[3]["width"]
				if len(configChildren) == 3:
					# resize the option's config frame's entry frames
					configChildren[0].configure(width=int(configFrameWidth * 0.485))
					configChildren[1].configure(width=int(configFrameWidth * 0.03))
					configChildren[2].configure(width=int(configFrameWidth * 0.485))

					# resize the entries
					priceEntry = list(configChildren[0].children.values())[0]
					strikeEntry = list(configChildren[2].children.values())[0]

					priceEntry.configure(width=configChildren[0]["width"])
					strikeEntry.configure(width=configChildren[2]["width"])
				elif len(configChildren) == 1:
					# resize the stock/future's config frame's entry frame
					configChildren[0].configure(width=configFrameWidth)

					# resize the stock/future entry
					entry = list(configChildren[0].children.values())[0]

					entry.configure(width=configChildren[0]["width"])

		# resize the IP divider
		try:
			self.IP_divider_frame.configure(width=self.ipWindow["width"])
		except:
			pass

		# set analysis row frame height for fast reference
		analysis_row_frame_height = self._generateAnalysisFramesHeight()
		try:
			ipWindow_width = self.ipWindow["width"]
		except:
			pass

		# resize analysis title frame
		try:
			self.analysis_title_frame.configure(width=ipWindow_width,
				height=self.ANALYSIS_TITLE_FRAME_HEIGHT)
		except:
			pass
		
		# resize the analysis panel "Overall Position" row frame
		try:
			self.analysis_overall_position_frame.configure(width=self.ipWindow["width"],
				height=analysis_row_frame_height)
		except:
			pass

		# resize the "Overall Position" row frames
		try:
			self.analysis_position_label_frame.configure(width=int(ipWindow_width * self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER),
				height=analysis_row_frame_height)
			if self.analysis_position_label_frame["width"] <= 200:
				self.analysis_position_label.configure(text="Overall\nPosition")
				self.analysis_breakeven_label.configure(text="Breakeven\nPoint")
			else:
				self.analysis_position_label.configure(text="Overall Position")
				self.analysis_breakeven_label.configure(text="Breakeven Point")
		except:
			pass
		try:
			self.analysis_position_entry_frame.configure(width=int(ipWindow_width * self.ANALYSIS_POSITION_ENTRY_FRAME_WIDTH_MULTIPLIER),
				height=analysis_row_frame_height)

			# resize entry, too
			self.analysis_position_entry.configure(width=self._generatePositionEntryWidth())
		except:
			pass
		try:
			self.analysis_position_enter_btn_frame.configure(width=int(ipWindow_width * self.ANALYSIS_POSITION_BTN_FRAME_WIDTH_MULTIPLIER),
				height=analysis_row_frame_height)
		except:
			pass
		try:
			self.analysis_position_clear_btn_frame.configure(width=(self.analysis_overall_position_frame["width"] - self.analysis_position_label_frame["width"] -
				self.analysis_position_entry_frame["width"] - self.analysis_position_enter_btn_frame["width"]),
				height=analysis_row_frame_height)
		except:
			pass

		# resize the analysis panel "Breakeven Point" row frames
		try:
			self.analysis_breakeven_point_frame.configure(width=ipWindow_width, 
				height=analysis_row_frame_height)
		except:
			pass

		# resuze the "Breakeven Point" row frames
		try:
			self.analysis_breakeven_label_frame.configure(width=int(ipWindow_width * self.ANALYSIS_ROW_LABEL_FRAME_WIDTH_MULTIPLIER),
				height=analysis_row_frame_height)
		except:
			pass
		try:
			self.analysis_breakeven_result_frame.configure(width=int(ipWindow_width * self.ANALYSIS_BREAKEVEN_RESULT_FRAME_WIDTH_MULTIPLIER),
				height=analysis_row_frame_height)
		except:
			pass


		# resize graph panel master frames
		self.masterGraphFrame.configure(width=self.graphWindow["width"],
			height=self.graphWindow["height"] * self.GRAPH_WINDOW_MULTIPLIER)
		self.masterScaleFrame.configure(width=self.graphWindow["width"],
			height=self.graphWindow["height"] - self.masterGraphFrame["height"])


	def updateGraph(self):
		""" update the graph """
		# determine min and max x & y values to dynamically determine graph limits
		max_x, max_y = 0, 0
		min_x, min_y = 0, 0

		# reset the graph so that a the updated version can be drawn
		self.graphReset()

		# $lines is where we append each instrument (line) instance (i.e. Option, Asset, etc...), 
		#	and this is derived from $self.lines
		lines = []

		# everytime we update the graph containing options, we have to place ticks  
		ticks = []
		
		# we store all option strikes in $strikes, and all spot prices and delivery prices
		# 	in $spots and $forwards
		strikes = [] 
		spots = []
		delivery_prices = []

		for line in self.lines:
			if line["inst"] is not None:
				instConfig = line["inst_config"]

				if line["inst"] == "option":
					# we've encountered a option instrument

					# if it has a price and a strike, we can graph it
					if self._isNumber(instConfig["price"]) and self._isNumber(instConfig["strike"]):
						# the line has all the values we require, graph it
						# configure the option details
						price = float(instConfig["price"])
						strike = float(instConfig["strike"])

						option_type = None
						if instConfig["option_type"] == "call":
							option_type = 1
						else:
							option_type = 2

						position = None
						if instConfig["position"] == "long":
							position = 1
						else:
							position = 2

						if price < strike:
							# create the option
							option = Option(option_type, position, price, strike, self.calculatable_position)

							# add the option to the lines list
							lines.append(option)

							x, y = option.x, option.y

						if max(x) > max_x:
							max_x = max(x)
						if max(y) > max_y:
							max_y = max(y)

						if min(x) < min_x:
							min_x = min(x)
						if min(y) < min_y:
							min_y = min(y)

						# append strike info to $strikes
						strikes.append(strike)
						ticks.append(strike)



				elif line["inst"] == "stock":
					# we are creating a stock for the graph

					# if the stock line has a valid number price, we can graph it
					if self._isNumber(instConfig["price"]):
						# configure stock values
						price = float(instConfig["price"])

						position = None
						if instConfig["position"] == "long":
							position = 1
						else:
							position = 2

						# create the instrument
						stock = Asset(price, position, self.calculatable_position)

						# add the stock to lines
						lines.append(stock)

						x, y = stock.x, stock.y

						if max(x) > max_x:
							max_x = max(x)
						if max(y) > max_y:
							max_y = max(y)

						if min(x) < min_x:
							min_x = min(x)
						if min(y) < min_y:
							min_y = min(y)

						# append the spot info to $spots
						spots.append(price)
						ticks.append(price)

				elif line["inst"] == "futures":
					# we are creating a futures for the graph
					
					# if the futures line has a valid number delivery price, we can graph it
					if self._isNumber(instConfig["delivery_price"]):
						# configure futures values
						delivery_price = float(instConfig["delivery_price"])

						position = None
						if instConfig["position"] == "long":
							position = 1
						else:
							position = 2

						# create the instrument
						futures = Asset(delivery_price, position, self.calculatable_position)

						# add the stock to lines
						lines.append(futures)

						x, y = futures.x, futures.y

						if max(x) > max_x:
							max_x = max(x)
						if max(y) > max_y:
							max_y = max(y)

						if min(x) < min_x:
							min_x = min(x)
						if min(y) < min_y:
							min_y = min(y)

						# append the forward info to $futures
						delivery_prices.append(delivery_price)
						ticks.append(delivery_price)

		if len(lines) != 0:
			# align all of the minimum and maximum x-values
			# updateInstruments() updates all lines so that they have the same x ranges
			max_x_range = updateLargestX(lines)
			min_x_range = updateSmallestX(lines, max_x_range)
			updateInstruments(lines, min_x_range, max_x_range)

			# plot all instruments in $lines
			for line in lines:
				x, y = line.x, line.y
				self.ax.plot(x, y, color=(0, 0, 0), linestyle='--', dashes=(8,5), linewidth=0.8)

			# if there is more than one line, plot a profit line (thick black), else just plot the payoff function with a dashed line
			if len(lines) > 1:
				self.profit = ProfitLine(lines, min_x=min_x_range, max_x=max_x_range, calculatable_position=self.calculatable_position)
				x, y = self.profit.x, self.profit.y
				self.ax.plot(x, y, linewidth=2.75, color=(0, 0, 0))
			elif len(lines) == 1:
				self.profit = lines[0]

			# update the graphs x-limits from the lowest of x to the 110% of the largest x
			self.ax.set_xlim(min_x_range, int(max_x * 1.1))

			# we want the graph's y-limit to encompass all important imformation.
			# 	thus, the y-limit should be set from -max_y to +max_y if abs(max_y) is larger than
			# 	abs(min_y), else the y-limit should be -min_y to +min_y
			if abs(max_y) > abs(min_y):
				self.ax.set_ylim(-max_y, max_y)
			else:
				min_y = abs(min_y)
				self.ax.set_ylim(-min_y, min_y)

			# get all $ticks duplicates
			seen = {}
			duplicates = []
			for tick in ticks:
				if tick not in seen:
					seen[tick] = 1
				else:
					if seen[tick] == 1:
						duplicates.append(tick)
					seen[tick] += 1

			# plot strike ticks
			tick_height = self.ax.get_ylim()[1] * self.TICK_SIZE_MULTIPLIER
			text_pos = tick_height * 1.4
			tick_counter = 1
			for strike in strikes:
				is_duplicate = [duplicate for duplicate in duplicates if strike == duplicate]
				if len(is_duplicate) == 0:
					# plot the strike tick
					self.ax.plot([strike, strike], [0, tick_height],
						color=(0, 0, 0), linewidth=1.75)

					# plot the annotations
					self.ax.annotate(fr"$K_{tick_counter}$", (strike, text_pos),
						ha="center", fontsize=12)

					# increment tick counter 
					tick_counter += 1
			# plot spot price ticks
			spot_counter = 0
			for spot in spots:
				is_duplicate = [duplicate for duplicate in duplicates if spot == duplicate]
				if len(is_duplicate) == 0:
					# plot the spot tick
					self.ax.plot([spot, spot], [0, tick_height],
						color=(0, 0, 0), linewidth=1.75)

					# plot the annotation
					self.ax.annotate(fr"$S_{spot_counter}$", (spot, text_pos),
						ha="center", fontsize=12)

					#increment spot counter
					spot_counter += 1
			# plot the futures ticks
			futures_counter = 1
			for delivery_price in delivery_prices:
				# plot the forwards tick
				self.ax.plot([delivery_price, delivery_price], [0, tick_height],
					color=(0, 0, 0), linewidth=1.75)

				# plot the annotation
				self.ax.annotate(fr"$F_{futures_counter}$", (delivery_price, text_pos),
					color=(0, 0, 0), fontsize=12)

				# increment the forwards counter
				futures_counter += 1

			# plot the line for the calculated position (in the analysis panel)
			if self.calculatable_position:
				# present profit (vertical) line for profit pattern
				# hint: by design, the ProfitLine instance stores the position value in $profit.calculated_position

				# plot a vertical line at the specified position
				self.ax.plot([self.calculatable_position, self.calculatable_position], [self.ax.get_ylim()[0], self.ax.get_ylim()[1]],
					color=(self.MONEY_GREEN_RGB[0], self.MONEY_GREEN_RGB[1], self.MONEY_GREEN_RGB[2]), linewidth=2)

				# plot the annotation for the vertical line
				self.ax.annotate(s=self.profit.calculated_position, xy=(self.calculatable_position * 1.01, self.ax.get_ylim()[1] * 0.88),
					fontsize=16, color=(self.MONEY_GREEN_RGB[0], self.MONEY_GREEN_RGB[1], self.MONEY_GREEN_RGB[2]), fontweight="bold")
					


			# reset figure axes spines
			self.ax.spines['left'].set_position(('data', min_x_range))
			self.graphCanvas.draw()
			self.ax.spines["left"].set_color("black")

			# enable the analysis panel's overall position calculator
			self.enableOverallPosition()
		elif len(lines) == 0:
			self.graphReset()
			self.fig.clear(keep_observers=True)
			self.drawFigure()

			# disable the analysis panel's overall position calculator
			self.disableOverallPosition()

			# set $self.profit to None
			self.profit = None


	def graphReset(self):
		""" Reset the graph """
		# first, we must clear our plot
		self.ax.clear()

		# reset graph characteristics
		self.ax.spines['left'].set_position('zero')	
		self.ax.spines['left'].set_linewidth(1.5)	
		self.ax.spines['right'].set_color('none')		# remove right border
		self.ax.spines['bottom'].set_position('zero')	# moves bottom border to y=0
		self.ax.spines['bottom'].set_linewidth(1.5)		# set width of x-axis
		self.ax.spines['top'].set_color('none')			# remove top border
		self.ax.set_ylim(-50, 50)
		self.ax.set_xlim(0, 50)
		xaxis = self.ax.xaxis.get_major_ticks()
		xaxis[0].label1.set_visible(False)
		xaxis[-1].set_visible(False)

		# set axis labels
		self.ax.set_ylabel("profit", fontsize=13, color=self.WHITE_THEME)
		self.ax.set_title(r"$S_T$", fontsize=13, color=self.WHITE_THEME)

		# config figure color
		self.ax.spines["bottom"].set_color("black")
		self.ax.spines["top"].set_color("white")
		self.ax.spines["left"].set_color("black")		
		self.ax.tick_params(axis="y", colors=self.WHITE_THEME)


	def drawGraphPanel(self):
		""" draw the graph panel frames """
		# create the graph and scale master frames
		self.masterGraphFrame = tk.Frame(master=self.graphWindow,
			width=self.graphWindow["width"],
			height=int(self.graphWindow["height"] * self.GRAPH_WINDOW_MULTIPLIER),
			background=self.GREY_THEME)
		self.masterScaleFrame = tk.Frame(master=self.graphWindow,
			width=self.graphWindow["width"],
			height=int(self.graphWindow["height"] - self.masterGraphFrame["height"]),
			background=self.GREY_THEME)

		# grid the graph window master frames
		self.masterGraphFrame.grid(row=0, column=0)
		self.masterScaleFrame.grid(row=1, column=0)


	def _resizeGraph(self):
		""" resize the graph """
		try:
			self.graphCanvasWidget.configure(width=self.masterGraphFrame["width"],
				height=self.masterGraphFrame["height"])
		except:
			# somehow this prevents an error?
			pass


	def removeScales(self):
		""" destroy all children of the master scale frame, if they exist """
		scaleMasterFrameChildren = list(self.masterScaleFrame.children.values())
		for frame in scaleMasterFrameChildren:
			frame.destroy()

		# set the self.scale1 and self.scale2 constants to None
		self.scale1 = None
		self.scale2 = None


	def generateScales(self, row):
		""" given a active row, generate it's scales """
		lines_row = self.lines[row]
		instType = lines_row["inst"]
		instConfig = lines_row["inst_config"]

		# define constants
		masterWidth = self.masterScaleFrame["width"]
		SCALE_WIDTH = int(masterWidth * self.SCALE_FRAME_WIDTH_MULTIPLIER)
		masterHeight = self.masterScaleFrame["height"]
		masterHeightHalf = int(self.masterScaleFrame["height"] / 2)

		if instType == "option" and (instConfig["option_type"] and instConfig["position"]):
			# the option has a selected position, pair scales
			# create price scale frames
			priceScaleFrame = tk.Frame(master=self.masterScaleFrame,
				width=SCALE_WIDTH,
				height=masterHeightHalf,
				background=self.GREY_THEME)
			priceLabelFrame = tk.Frame(master=self.masterScaleFrame,
				width=masterWidth - SCALE_WIDTH,
				height=masterHeightHalf,
				background=self.GREY_THEME)

			# create strike scale frames
			strikeScaleFrame = tk.Frame(master=self.masterScaleFrame,
				width=SCALE_WIDTH,
				height=masterHeightHalf,
				background=self.GREY_THEME)
			strikeLabelFrame = tk.Frame(master=self.masterScaleFrame,
				width=masterWidth - SCALE_WIDTH,
				height=masterHeightHalf,
				background=self.GREY_THEME)

			# grid the scale frames
			priceLabelFrame.grid(row=0, column=0)
			priceScaleFrame.grid(row=0, column=1)
			strikeLabelFrame.grid(row=1, column=0)
			strikeScaleFrame.grid(row=1, column=1)

			# create the price and strike labels
			priceLabel = tk.Label(master=priceLabelFrame,
				text="price",
				font=self.scaleLabelFont,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME)
			strikeLabel = tk.Label(master=strikeLabelFrame,
				text="strike",
				font=self.scaleLabelFont,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME)

			# pack and place the labels
			priceLabel.pack()
			strikeLabel.pack()
			priceLabel.place(relx=0.9, rely=0.5, anchor="e")
			strikeLabel.place(relx=0.9, rely=0.5, anchor="e")

			# create the scales
			priceScale = tk.Scale(master=priceScaleFrame,
				orient=tk.HORIZONTAL,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME,
				highlightbackground=self.GREY_THEME,
				sliderrelief=tk.FLAT,
				length=self.SCALE_LENGTH,
				font=self.scaleFont)
			strikeScale = tk.Scale(master=strikeScaleFrame,
				orient=tk.HORIZONTAL,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME,
				highlightbackground=self.GREY_THEME,
				sliderrelief=tk.FLAT,
				length=self.SCALE_LENGTH,
				font=self.scaleFont)

			# add the scales to $self.scale1 and $self.scale2
			self.scale1 = priceScale
			self.scale2 = strikeScale

			# bind the scale's movement to some function
			priceScale.configure(command= lambda value, scale=priceScale: self.moveScale(value, scale))
			strikeScale.configure(command= lambda value, scale=strikeScale: self.moveScale(value, scale))

			# on inception of the scales, determine if their respective entries have
			# valid values stored in them (accessible via self.lines)
			# if they do, set the scale to light mode and update it's setting, else
			# set it to dark mode
			# first, determine the validity of the price input, and set it's scale accordingly
			if instConfig["price"] and self._isNumber(instConfig["price"]) and float(instConfig["price"]) >= 0:
				# the price entry input for the option has valid input
				self.setScaleLightMode(priceScale)
				self.updateScaleValues(priceScale, option=True)
			else:
				self.setScaleDarkMode(priceScale)
			# then determine the validity of the strike input, and set it's scale accordingly
			if instConfig["strike"] and self._isNumber(instConfig["strike"]) and float(instConfig["strike"]) >= 0:
				self.setScaleLightMode(strikeScale)
				self.updateScaleValues(strikeScale, option=True)
			else:
				self.setScaleDarkMode(strikeScale)

			# pack and place the scales
			priceScale.pack()
			strikeScale.pack()
			priceScale.place(relx=0.075, rely=0.44, anchor="w")
			strikeScale.place(relx=0.075, rely=0.44, anchor="w")
		elif instType == "stock" and instConfig["position"]:
			# the stock has an active entry, pair it to a scale
			# create price scale frames
			priceScaleFrame = tk.Frame(master=self.masterScaleFrame,
				width=SCALE_WIDTH,
				height=masterHeight,
				background=self.GREY_THEME)
			priceLabelFrame = tk.Frame(master=self.masterScaleFrame,
				width=masterWidth - SCALE_WIDTH,
				height=masterHeight,
				background=self.GREY_THEME)

			# grid the frames
			priceLabelFrame.grid(row=0, column=0)
			priceScaleFrame.grid(row=0, column=1)

			# create the price label
			label = tk.Label(master=priceLabelFrame,
				text="price",
				font=self.scaleLabelFont,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME)

			# pack and place the label
			label.pack()
			label.place(relx=0.75, rely=0.5, anchor="center")

			# create the scale
			scale = tk.Scale(master=priceScaleFrame,
				orient=tk.HORIZONTAL,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME,
				highlightbackground=self.GREY_THEME,
				sliderrelief=tk.FLAT,
				length=self.SCALE_LENGTH,
				font=self.scaleFont)

			# add the scale to self.scale1
			self.scale1 = scale

			# bind the scale's movement to some function
			scale.configure(command= lambda value, scale=scale: self.moveScale(value, scale))

			# on inception, if the entry this scale is paired to is empty, set 
			# it to dark mode, else set it to light mode and update its values
			if instConfig["price"] and self._isNumber(instConfig["price"]) and float(instConfig["price"]) >= 0:
				# set the scale to light mode and configure it's settings
				self.setScaleLightMode(scale)
				self.updateScaleValues(scale)
			else:
				# set the scale to dark mode
				self.setScaleDarkMode(scale)

			# pack and place the scale
			scale.pack()
			scale.place(relx=0.075, rely=0.44, anchor="w")
		elif instType == "futures" and instConfig["position"]:
			# the futures has an active entry, pair it to a scale
			# create delivery price scale frames
			deliveryPriceScaleFrame = tk.Frame(master=self.masterScaleFrame,
				width=SCALE_WIDTH,
				height=masterHeight,
				background=self.GREY_THEME)
			deliveryPriceLabelFrame = tk.Frame(master=self.masterScaleFrame,
				width=masterWidth - SCALE_WIDTH,
				height=masterHeight,
				background=self.GREY_THEME)

			# grid the frames
			deliveryPriceLabelFrame.grid(row=0, column=0)
			deliveryPriceScaleFrame.grid(row=0, column=1)

			# create the delivery price label
			label = tk.Label(master=deliveryPriceLabelFrame,
				text="delivery price",
				font=self.scaleLabelFont,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME)

			# pack and place the delivery price label
			label.pack()
			label.place(relx=0.545, rely=0.5, anchor="center")

			# create the scale
			scale = tk.Scale(master=deliveryPriceScaleFrame,
				orient=tk.HORIZONTAL,
				background=self.GREY_THEME,
				foreground=self.WHITE_THEME,
				highlightbackground=self.GREY_THEME,
				sliderrelief=tk.FLAT,
				length=self.SCALE_LENGTH,
				font=self.scaleFont)

			# add the scale to self.scale1
			self.scale1 = scale

			# bind the scale's movement to some function
			scale.configure(command= lambda value, scale=scale: self.moveScale(value, scale))

			# on inception, if the entry this scale is paired to is empty, set 
			# it to dark mode, else set it to light mode and update its values
			if instConfig["delivery_price"] and self._isNumber(instConfig["delivery_price"]) and float(instConfig["delivery_price"]) >= 0:
				# set the scale to light mode and configure it's settings
				self.setScaleLightMode(scale)
				self.updateScaleValues(scale)
			else:
				# set the scale to dark mode
				self.setScaleDarkMode(scale)

			# pack and place the scale
			scale.pack()
			scale.place(relx=0.075, rely=0.44, anchor="w")


	def setScaleDarkMode(self, scale):
		""" change the scales theme to a dark mode and configure it's settings """
		# set the scales theme to a dark mode to signify it's unavailability
		scale.configure(foreground=self.DARKER_GREY,
			troughcolor=self.DARKER_GREY,
			activebackground=self.GREY_THEME)

		# set the scales label to a centred 0
		scale.configure(from_=-1, to=1, resolution=1)
		scale.set(0)

		# disable the scale
		scale.configure(state="disabled")


	def setScaleLightMode(self, scale):
		""" change the scale's theme to a light mode """
		# set the scale theme to a light mode to signify it is available
		scale.configure(foreground=self.WHITE_THEME,
			troughcolor=self.WHITE_THEME,
			activebackground=self.LIGHTER_GREY,
			state="active")


	def updateScaleValues(self, scale, option=False):
		scaleMax = None
		newScaleValue = None

		if option:
			# the scale we're updating belongs to an option entry
			if scale.master.grid_info()["row"] == 0:
				# we are updating the price scale of an option
				entryFrame = list(self.rows[self._selectedRow()][3].children.values())[0]
				entry = list(entryFrame.children.values())[0]
				entryInput = self._returnIntOrFloat(entry.get())

				scaleMax = int(entryInput * 2)
				newScaleValue = entryInput
			else:
				# we are updating the strike scale of an option
				entryFrame = list(self.rows[self._selectedRow()][3].children.values())[2]
				entry = list(entryFrame.children.values())[0]
				entryInput = self._returnIntOrFloat(entry.get())

				scaleMax = int(entryInput * 2)
				newScaleValue = entryInput
		else:
			# the scale we're updating belongs to a stock/futures entry
			# set the scale according to it's paired entry
			entryFrame = list(self.rows[self._selectedRow()][3].children.values())[0]
			entry = list(entryFrame.children.values())[0]
			entryInput = self._returnIntOrFloat(entry.get())

			scaleMax = int(entryInput * 2)
			newScaleValue = entryInput

		scale.configure(from_=0, to=scaleMax)

		if scaleMax <= 20:
			scale.configure(from_=0.05, resolution=0.05)
		else:
			scale.configure(from_=1, resolution=1)

		scale.set(newScaleValue)


	def moveScale(self, value, scale):
		""" manage a scale's movement """
		selectedRow = self._selectedRow()

		if scale["state"] == "active":
			# if the scale is set while active (valid value)
			if self.scale1 and self.scale2:
				# an option scale was moved
				if scale.master.grid_info()["row"] == 0:
					# the price scale was moved. update the value into the entry
					priceEntryFrame = list(self.rows[selectedRow][3].children.values())[0]
					priceEntry = list(priceEntryFrame.children.values())[0]

					# delete any value in there currently
					priceEntry.delete(0, len(priceEntry.get()))

					# insert the new value
					priceEntry.insert(0, value)

					# update $self.lines
					self.lines[selectedRow]["inst_config"]["price"] = value
				else:
					# the strike scale was moved
					strikeEntryFrame = list(self.rows[selectedRow][3].children.values())[2]
					strikeEntry = list(strikeEntryFrame.children.values())[0]

					# delete any value in the entry currently
					strikeEntry.delete(0, len(strikeEntry.get()))

					# insert the new value
					strikeEntry.insert(0, value)

					# update $self.lines
					self.lines[selectedRow]["inst_config"]["strike"] = value

				# update the analysis panel breakeven point
				inst_config = self.lines[selectedRow]["inst_config"]
				if (self._isNumber(inst_config["strike"]) and self._isNumber(inst_config["price"])):
					if inst_config["option_type"] == "call":
						# update the breakeven point for the call option
						breakeven = float(inst_config["strike"]) + float(inst_config["price"])
						self.analysis_breakeven_result.configure(text=breakeven)
					else:
						# update the breakeven point for the put option
						breakeven = float(inst_config["strike"]) - float(inst_config["price"])
						self.analysis_breakeven_result.configure(text=breakeven)
			else:
				# the stock or futures scale was moved
				entryFrame = list(self.rows[selectedRow][3].children.values())[0]
				entry = list(entryFrame.children.values())[0]

				# delete any value in the entry currently
				entry.delete(0, len(entry.get()))

				# insert the new value
				entry.insert(0, value)

				if self.lines[selectedRow]["inst"] == "stock":
					# a stock entry scale was moved, update it in self.lines
					self.lines[selectedRow]["inst_config"]["price"] = value
				else:
					self.lines[selectedRow]["inst_config"]["delivery_price"] = value

			# update the graph
			self.updateGraph()


	def _resizeScales(self):
		""" resize the scales """
		masterScaleFrameChildren = list(self.masterScaleFrame.children.values())

		if len(masterScaleFrameChildren) > 0:
			# there are active scales, determine if there are 2 or 1
			masterWidth = self.masterScaleFrame["width"]
			SCALE_WIDTH = int(masterWidth * self.SCALE_FRAME_WIDTH_MULTIPLIER)
			masterHeight = self.masterScaleFrame["height"]

			if len(masterScaleFrameChildren) == 4:
				# there are two option scales active
				masterHeightHalf = int(masterHeight / 2)

				for frame in masterScaleFrameChildren:
					if frame.grid_info()["column"] == 0:
						frame.configure(width=masterWidth - SCALE_WIDTH,
							height=masterHeightHalf)
					else:
						frame.configure(width=SCALE_WIDTH,
							height=masterHeightHalf)
			elif len(masterScaleFrameChildren) == 2:
				# there is one stock/futures scale active
				for frame in masterScaleFrameChildren:
					if frame.grid_info()["column"] == 0:
						frame.configure(width=masterWidth - SCALE_WIDTH,
							height=masterHeight)
					else:
						frame.configure(width=SCALE_WIDTH,
							height=masterHeight)


	def resize(self, event):
		""" manages resizing widgets (frames mostly) """
		# resize master frame
		self.masterFrame.configure(width=self.master.winfo_width(),
			height=self.master.winfo_height())

		# resize window panels first
		try:
			self.headerPanel.configure(width=self.masterFrame["width"],
				height=int(self.SCREEN_HEIGHT * self.HEADER_PANEL_MULTIPLIER))
		except:
			pass
		try:
			self.windowDividerFrame.configure(width=self.masterFrame["width"])
		except:
			pass
		try:	
			self.bodyPanel.configure(width=self.masterFrame["width"],
				height=self.masterFrame["height"] - self.headerPanel["height"] - self.windowDividerFrame["height"])
		except:
			pass

		# resize body windows
		try:
			self.ipWindow.configure(width=int(self.bodyPanel["width"] * self.IP_WIDTH_MULTIPLIER),
				height=self.bodyPanel["height"])
		except:
			pass
		try:
			self.bodyDividerFrame.configure(height=self.bodyPanel["height"])
		except:
			pass
		try:
			self.graphWindow.configure(width=self.bodyPanel["width"] - self.ipWindow["width"] - self.bodyDividerFrame["width"] ,
				height=self.bodyPanel["height"])
		except:
			pass

		# resize the IP with a helper method
		self._resizeIP()

		# resize the graph
		self._resizeGraph()

		# resize scales
		self._resizeScales()



"""
XML-STYLE NOTES FOR PROJECT STRUCTURE:

<self.master>
	<self.headerPanel>
		<instrumentiumTitle>
		<helpBtn>
	</self.headerPanel>

	<self.dividerFrame></self.dividerFrame>

	<self.bodyPanel>
		<self.ipWindow>
			<self.IP_title_frame></self.IP_title_frame>

			<self.IP_sel_header_frame></self.IP_sel_header_frame>
			<self.IP_type_header_frame></self.IP_type_header_frame>
			<self.IP_position_header_frame></self.IP_position_header_frame>
			<self.IP_config_header_frame></self.IP_config_header_frame>
			<self.IP_reset_header_frame></self.IP_reset_header_frame>

			<!-- the rows are all also children of self.ipWindow -->

			<self.IP_divider_frame/> <!-- this is used to clearly separate instrument rows from the analysis panel -->

			<self.analysis_title_frame
				<analysisPanelTitle/>
			</self.analysis_title_frame>

			<self.analysis_overall_position_frame>
				<!-- 
					this frame holds a grid of frames which house a title, entry 
					(price), and two buttons ("enter" and "clear") 
				-->
				<self.analysis_position_label_frame>
					<self.analysis_position_label/>
				</self.analysis_position_label_frame>
				<self.analysis_position_entry_frame>
					<self.analysis_position_entry/>
				</self.analysis_position_entry_frame>
				<self.analysis_position_enter_btn_frame>
					<self.analysis_position_enter_btn/>
				</self.analysis_position_enter_btn_frame>
				<self.analysis_position_clear_btn_frame>
					<self.analysis_position_clear_btn/>
				</self.analysis_position_clear_btn_frame>
			</self.analysis_overall_position_frame>

			<self.analysis_breakeven_point_frame>
				<self.analysis_breakeven_label_frame>
					<
				</self.analysis_breakeven_label_frame>

				<self.analysis_breakeven_result_frame>
					<
				</self.analysis_breakeven_result_frame>
			</self.analysis_breakeven_point_frame>
		</self.ipWindow>

		<self.bodyDividerFrame></self.bodyDividerFrame>

		<self.graphWindow>
			<self.masterGraphFrame>
				<!-- this is where we add the dynamic Matplotlib figure through the Tkinter library -->
			</self.masterGraphFrame>

			<self.masterScaleFrame>
				<!-- this is where we dynamically add scales, depending on when their rows are selected -->
			</self.masterScaleFrame>
		</self.graphWindow>
	</self.bodyPanel>
</self.master>
"""



root = tk.Tk()

# manage the size of the window on program start-up
screenWidth, screenHeight = GetSystemMetrics(0), GetSystemMetrics(1)
windowWidth = int(screenWidth * 4/5)						# start-up width 4/5 screen
windowHeight = int(screenHeight * 7/10)						# start-up height 7/10 screen
windowLeft = int(screenWidth/2 - windowWidth/2)				# center x
windowTop = int(screenHeight/2 - windowHeight/2 * 1.075)	# center y plus some more
root.geometry(f"{windowWidth}x{windowHeight}+{windowLeft}+{windowTop}")

# configure root window minsize
root.minsize(1200, 660)

# configure icon
root.iconbitmap('instrumentium.ico')

# define window title
root.title("Instrumentium")

# create Instrumentium UI instance
ui = Instrumentium(root)

# configure root window background with Instrumentium instance color
root.configure(background=ui.GREY_THEME)

# handle keypresses
def keydown(event):
	if event.char == "q" or event.char == "Q":
		root.destroy()
	elif event.keysym == "Return":
		ui.master.focus()

# bind root window to events
root.bind("<KeyPress>", keydown)
root.bind("<Configure>", ui.resize)

root.mainloop()