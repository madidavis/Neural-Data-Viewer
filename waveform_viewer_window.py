from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from datetime import datetime
#load custom Libraries
from neural_data_class import *
from main import *

import sys

#*** CUSTOM CLASS DEFINITIONS***#
#create a pyqtgraph plot of a neural data channel
class Neural_Graph():
    def __init__(self, colour, channel):
        #TOOLBAR PROPETIES
        self.toolbar = QToolBar() #Toolbar to control features
        self.toolbar.setMovable(False)
        #Toolbar buttons and labels
        self.title = QLabel("Channel " + str(channel)) #title of Plot
        self.toolbar.addWidget(self.title)
        self.hide_button = QToolButton() #add a button to control plot visibility
        self.hide_button.setText("Hide")
        self.toolbar.addWidget(self.hide_button)
        self.is_hidden = False #flag to determinn if plot hidden
        self.hide_button.clicked.connect(self.hide_plot)
        self.mark_button = QCheckBox() #checkbbox to mark channel data as bad
        self.is_marked = False
        self.mark_button.toggled.connect(self.mark_channel)
        self.toolbar.addWidget(self.mark_button)

        #GRAPH PROPERTIES
        self.channel = channel
        self.colour = colour
        self.graph = pg.PlotWidget()
        self.pen = pg.mkPen(color=self.colour)
        self.set_up_graph()

        #CONTAINER PROPERTIES
        self.container = QVBoxLayout() #vertical box to conntain plot and tool bar
        self.container.setSpacing(0)
        self.set_up_container()

    #load initial values for graph
    def set_up_graph(self):
        #self.graph.setYrange(data.min_max_list[self.channel][0], data.min_max_list[self.channel][1])
        self.graph.plot(data.visible_xdata, data.visible_ydata[self.channel], pen=self.pen)

    #set up layout of plot and toolbar
    def set_up_container(self):
        self.container.addWidget(self.toolbar)
        self.container.addWidget(self.graph)

    #allows user to hide the plot
    def hide_plot(self):
        if self.is_hidden:
            self.graph.show()
            self.hide_button.setText("Hide")
            self.is_hidden = False
        else:
            self.graph.hide()
            self.hide_button.setText("Show")
            self.is_hidden = True

    #allows user to mark a specific data channnel as bad
    def mark_channel(self):
        if self.is_marked:
            if self.channel in data.marked_channels:
                data.marked_channels.remove(self.channel)
            self.mark_button.setChecked(False)
            self.is_marked = False
            if self.is_hidden:
                self.hide_plot() #show unmarked plot
        else:
            data.marked_channels.add(self.channel)
            self.mark_button.setChecked(True)
            self.is_marked = True
            self.hide_plot() #hide marked channel
            if not self.is_hidden:
                self.hide_plot() #show unmarked plot

#create a main window
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Define Main Window QtWidgets
        self.setWindowTitle("Real Time Data Visualiser")
        self.window_width = self.frameGeometry().width()
        self.window_height = self.frameGeometry().height()


        #TIMER PROPERTIES#
        #Set timer for real time graph plotting
        self.timer = QTimer()
        self.timer_speed = 100 #may need to have actual timer and visible plot timer
        self.timer.setInterval(self.timer_speed) #initialise timer speed
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.is_timer_reversed = False
        #Set timer for hidden values - this timer should not be paused!
        self.hidden_timer = QTimer()
        self.hidden_timer.setInterval(self.timer_speed)
        self.hidden_timer.timeout.connect(self.update_hidden_plot_data)
        self.hidden_timer.start()

        #GRAPH PROPERTIES
        #Graph Channel layouts
        self.graph_vbox = QVBoxLayout() #create vertical layout to stack channels

        #Widget for Graph Display
        #plot the number of active Neural data channels
        self.graph_colour_list = [(81, 216, 240), (245, 185, 73), (135, 242, 85),
                                    (245, 91, 73), (181, 108, 245), (250, 233, 82)]
        #create an array of neural graphs
        self.graph_list = []
        for i in range(data.num_working_channels):
            graph = Neural_Graph(self.graph_colour_list[i], i)
            self.graph_vbox.addLayout(graph.container)
            self.graph_list.append(graph)



        #set layout by placing in a container
        self.graph_container = QWidget()
        self.graph_container.setLayout(self.graph_vbox)

        self.setCentralWidget(self.graph_container)



        #PLAYBACK PROPERTIES
        #Playback Control Toolbar
        self.playback_controls = QToolBar("Plotting Playback Controls")
        self.playback_controls.setMovable(False)
        self.addToolBar(Qt.BottomToolBarArea, self.playback_controls)
        self.playback_width = self.playback_controls.frameGeometry().width()
        self.playback_height = self.playback_controls.frameGeometry().height()
        self.playback_controls.setStyleSheet("QToolBar{spacing:50px; background: white}")
        self.resizeEvent = self.resize_widgets

        #Add Buttons for Playback Control
        bskip_button = QToolButton()
        bskip_button.setText("Back Skip")
        bskip_button.clicked.connect(self.backskip_to_start)
        self.playback_controls.addWidget(bskip_button)

        rewind_button = QToolButton()
        rewind_button.setText("Rewind")
        rewind_button.clicked.connect(self.reverse_plot_data)
        self.playback_controls.addWidget(rewind_button)

        play_pause_button = QToolButton()
        play_pause_button.setText("Play/Pause")
        play_pause_button.clicked.connect(self.play_pause_plot_data)
        self.playback_controls.addWidget(play_pause_button)

        forward_button = QToolButton()
        forward_button.setText("Forward")
        forward_button.clicked.connect(self.forward_plot_data)
        self.playback_controls.addWidget(forward_button)

        fskip_button = QToolButton()
        fskip_button.setText("Forward Skip")
        fskip_button.clicked.connect(self.fskip_to_current_pos)
        self.playback_controls.addWidget(fskip_button)

        #buttons for play speed control
        self.speeds = [0.25,0.5,0.75,1,2]
        speed_control = QComboBox(self)
        speed_control.addItem("Speed") #header
        for speed in self.speeds:
            speed_control.addItem(str(speed)+"x")
        speed_control.currentIndexChanged.connect(self.change_plotting_speed)
        self.playback_controls.addWidget(speed_control)


    #Change Size of widgets when main window is resized
    def resize_widgets(self, event):
        playback_width = self.playback_controls.frameGeometry().width()

    #Update Plot values
    def update_plot_data(self):
        #if end of data is reached, loop back to original values
        if (data.curr_range[1] >= data.data_length):
            self.timer.stop()
        else:
            #update visible data range
            data.update_data_range()
        #set new data on plot
        for graph in self.graph_list:
            graph.graph.plot(data.visible_xdata, data.visible_ydata[0],
                                                pen=graph.pen,
                                                 clear=True)

    #Update hidden plot values
    def update_hidden_plot_data(self):
            #if end of data is reached, loop back to original values
            if (data.hidden_range[1] >= data.data_length):
                self.hidden_timer.stop()
            else:
                #update visible data range
                data.update_hidden_data_range()



    #Update plot values in reverse
    def reverse_update_plot_data(self):
        #if end of data is reached, loop back to original values
        if (data.curr_range[0] == 0):
            self.timer.stop()
            data.curr_range = [0,3000]
            data.visible_xdata = data.update_xrange(data.curr_range[0],data.curr_range[1])
            data.visible_ydata = data.update_yrange(data.curr_range[0],data.curr_range[1])
        else:
            #update visible data range
            data.reverse_data_range()
        #set new data on plot
        for graph in self.graph_list:
            graph.graph.plot(data.visible_xdata, data.visible_ydata[0],
                                                pen=graph.pen,
                                                clear=True)


    #Pause live stream of data when play/pause button is clicked
    def play_pause_plot_data(self):
        print(data.curr_range, data.hidden_range)
        if (self.timer.isActive()):
            #if timer is running pause
            print('pause')
            self.timer.stop()
        else:
            #if timer is paused then restart
            print('play')
            self.timer.start()

    #Reverse the plotting of data
    def reverse_plot_data(self):
        print("start rev", self.is_timer_reversed)
        print("timer = ", self.timer.isActive())
        print(data.curr_range, data.hidden_range)
        if self.timer.isActive():
            if not self.is_timer_reversed:
                self.timer.timeout.connect(self.reverse_update_plot_data)
                self.timer.timeout.connect(self.reverse_update_plot_data)
                self.is_timer_reversed = True
                print("end rev", self.is_timer_reversed)
        else:
            pass


    #Forward play the plotting of data
    def forward_plot_data(self):
        print("start forward", self.is_timer_reversed)
        print("timer = ", self.timer.isActive())
        if self.timer.isActive():
            if self.is_timer_reversed:
                self.timer.timeout.connect(self.update_plot_data)
                self.timer.timeout.connect(self.update_plot_data)
                self.is_timer_reversed = False
                print("end forward", self.is_timer_reversed)
        else:
            pass

    #Skip back to the start values when backskip button is selected
    def backskip_to_start(self):
        #reinitialise visible data values
        data.curr_range = [0,3000]
        data.visible_xdata = data.update_xrange(data.curr_range[0],data.curr_range[1])
        data.visible_ydata = data.update_yrange(data.curr_range[0],data.curr_range[1])
        #if data currently paused, re-plot
        if self.is_timer_reversed:
            #if in reverse switch back to forwards
            self.timer.timeout.connect(self.update_plot_data)
            self.timer.timeout.connect(self.update_plot_data)
            self.is_timer_reversed = False
            self.timer.start()
        if not self.timer.isActive():
            #if data currently paused, re-plot
            self.main_graph.plot(data.visible_xdata, data.visible_ydata[0], clear=True)

    #Skip to current data when forward skip button is selected
    def fskip_to_current_pos(self):
        #if data currently paused, re-plot
        data_min, data_max = data.hidden_range
        data.curr_range = [data_min, data_max]


    #Change Plotting timer speed
    def change_plotting_speed(self, index):
        if index == 0:
            speed_val = 1
        else:
            speed_val = self.speeds[index-1]
        #alter the inncrement of visible data to change speed of plotting
        data.incr = int(speed_val*3000)
        print(data.incr)





#***RUN THE WINDOW***#
#create an application
app = QApplication(sys.argv)

#create and show the main window
main = MainWindow()
main.show()

#start the event loop
print(main.window_width, main.window_height)
app.exec_()
print(main.window_width, main.window_height)
