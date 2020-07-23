#***SETUP***#
#Import Custom Libraries
from rhd_conversion import *
from neural_data_class import*


#***LOAD RAW DATA***#
#convert file to numpy array
file_name = "Data/8_GLUTAMATE_30kHz Sampling Freq_191221_183536.rhd"
raw_data_array = rhd_to_numpy(file_name)

#***NEURAL DATA CLASS***#
data = Neural_Data(file_name, raw_data_array, 30000)
data.init_channels()
print(data.min_max_list)
