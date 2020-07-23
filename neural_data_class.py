#SET UP
#Load all libraries
import numpy as np
import pandas as pd
import random
from itertools import count

#global variable to store id numbers
id_list = []


#class to store all neural data obtained from .rhd file
class Neural_Data(object):
  def __init__(self, file_name, data_array, sampling_rate):
    global id_list

    self.file_name = file_name #name of rhd file
    self.data_array = data_array #array of channels of neural data
    self.sampling_rate = sampling_rate
    self.length = 60 #length of time of recording
    self.id = self.get_data_id() #unique id for each data set
    self.data_length = data_array.shape[1]
    self.num_active_channels = data_array.shape[0]
    self.num_working_channels = 6
    self.channel_list = [] #list of objects for active channels

    #attributes for data plotting
    self.time_val = np.linspace(0,self.length, self.sampling_rate*self.length)#array of times data points are recorded
    self.curr_range = [0,3000] #index for range of displayed data
    self.visible_xdata = self.update_xrange(self.curr_range[0],self.curr_range[1]) #x axis data visible on plot
    self.visible_ydata = self.update_yrange(self.curr_range[0],self.curr_range[1])#y axis data visible on plot
    self.incr = 3000 #speed/amount of data updated per unit time
    self.min_max_list = self.find_channel_min_max()
    #variables to keep track of real time plottinng when plots are pause/rewound
    self.hidden_range = [0,3000]
    self.hidden_xdata = self.update_hidden_xrange(self.hidden_range[0],self.hidden_range[1])
    self.hidden_ydata = self.update_hidden_yrange(self.hidden_range[0],self.hidden_range[1])
    self.hidden_incr = 3000

    #list of marked/bad channels
    self.marked_channels = set()



  #generates a unique id for each set of neural data
  def get_data_id(self):
    if len(id_list) == 0: id = 0
    else: id = id_list[len(id_list) - 1] + 1
    id_list.append(id)
    return id

  #creates channnel objects for each active channel
  def init_channels(self):
    channel_list = []
    for i in range(self.num_active_channels):
      channel = Neural_Data_Channel(self.file_name, self.data_array,
                                     self.sampling_rate, self.id, i,
                                     self.data_array[i])
      channel_list.append(channel)
    self.channel_list = channel_list
    return channel_list


  #find min and max data values for each channel
  def find_channel_min_max(self):
      min_max_list = np.zeros((32, 2))
      for channel in range(self.num_active_channels):
          min_max_list[channel][0] = np.min(self.data_array[channel])
          min_max_list[channel][1] = np.max(self.data_array[channel])
      return min_max_list

  #update current x data range
  def update_xrange(self, min, max):
    #x data = time
    self.visible_xdata = self.time_val[min:max]
    return self.visible_xdata;

  #update hidden x data range
  def update_hidden_xrange(self, min, max):
    self.hidden_xdata = self.time_val[min:max]
    return self.hidden_xdata;

  #update current y data range
  def update_yrange(self, min, max):
    #y data = amplifier values across channels
    self.visible_ydata = self.data_array[:,min:max]
    return self.visible_ydata;

  #update hidden y data range
  def update_hidden_yrange(self, min, max):
      self.hidden_ydata = self.data_array[:,min:max]
      return self.hidden_ydata;

  #update hidden data range
  def update_hidden_data_range(self):
      #change range of values
      self.hidden_range[0] += self.hidden_incr
      self.hidden_range[1] += self.hidden_incr

      self.update_hidden_yrange(self.hidden_range[0], self.hidden_range[1])
      self.update_hidden_xrange(self.hidden_range[0], self.hidden_range[1])
      return 0;

  #updata data range
  def update_data_range(self):
    #change range of values
    self.curr_range[0] += self.incr
    self.curr_range[1] += self.incr

    self.update_yrange(self.curr_range[0], self.curr_range[1])
    self.update_xrange(self.curr_range[0], self.curr_range[1])
    return 0;

  #update values in reverse when in rewind mode
  def reverse_data_range(self):
      #change range of values
      self.curr_range[0] -= self.incr
      self.curr_range[1] -= self.incr

      self.update_yrange(self.curr_range[0], self.curr_range[1])
      self.update_xrange(self.curr_range[0], self.curr_range[1])


#Subclass for specific channels of neural data
class Neural_Data_Channel(Neural_Data):
  def __init__(self, file_name, data_array, sampling_rate,
               data_id, channel_id, channel_array):
    super().__init__(file_name, data_array, sampling_rate)
    self.id = data_id
    self.channnel_id = channel_id
    self.channel_data_array = channel_array
