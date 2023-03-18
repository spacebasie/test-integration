# -*- coding: utf-8 -*-
import time
import serial

def jenson_button(serial_p, filen):

    SCREEN_DISPLAY=False
    SAVE_TO_FILE=False
    ARRAY_ONLY = True
    my_arr = []

    if serial_p == None:
        SERIAL_PORT='/dev/cu.usbserial-01BE2758' # serial port terminal
    else:
        SERIAL_PORT = serial_p
    # SERIAL_PORT='COM5'
    if filen == None:
        file_name= 'BBB_output.csv'
    else:
        file_name = filen
    fid = open(file_name,'ab')

    scale = serial.Serial(SERIAL_PORT,timeout=20,baudrate=9600)

    while True:
        str_scale=scale.readline()
        # time_now=time.strftime("%Y-%m-%d %H:%M:%S ")
        if SCREEN_DISPLAY: 
            # print(str.encode( time_now ) + str_scale)
            print(str_scale)
        time.sleep(0.01)  # in seconds
        if SAVE_TO_FILE: 
            # fid.write(str.encode(time_now)+str_scale)
            fid.write(str_scale)
        if ARRAY_ONLY:
            # Make this dataframe so it's easier to append with everythhing
            # for a in str_scale:
            #     if a != str:
            #         my_arr.append(a)
            my_arr.apend(str_scale)

    return my_arr
    scale.close()
    fid.close()