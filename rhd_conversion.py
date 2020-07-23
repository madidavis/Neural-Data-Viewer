import os, sys
#import intan module
sys.path.insert(0, '/Intan/')
print(os.getcwd())
from load_intan_rhd_format import read_data

#Read .rhd file and returns numpy array of amplitude data
#Adapted from Esther's Concentrate RAW code
def rhd_to_numpy(file_name):
  rhd_dic = read_data(file_name) #read rhd file
  rhd_array = rhd_dic["amplifier_data"] #extract relevant data and put in np array
  print(rhd_array, rhd_array.shape)

  return rhd_array
