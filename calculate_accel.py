#%%
from os import chdir
chdir(r'D:\Users\Geovanni\Sync\UMKC\3rd 1st Semester\CS5590 Special Topics IoT\IoTProject\code')
# import pandas as pd

#%%
def create_data():
    import ESPSerial
    f = open('accdata','w')
    i=0
    runf=1000
    try:
        if writeESPSerial.check_serial_open():
            while i < runf:
                data = writeESPSerial.read_from_esp(.2)
                if type(data) == type(None):
                    continue
                if len(data)>0:
                    f.write(data+'\n')
                    i+=1

                    if i%(runf/10)==0:
                        print(i)
        else:
            print("Connection could not be opened")
    except KeyboardInterrupt:
        writeESPSerial.close_connect()
    finally:
        if writeESPSerial.check_serial_open():
            writeESPSerial.close_connect()
        f.close()

#%%
if 0:
    create_data()

# df_accgyro = pd.read_table('./accdata', header=None, sep=' ')

# %%
# df_accgyro.head()

# %%
