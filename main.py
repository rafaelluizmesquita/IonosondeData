
import sys
import os

homedirectory = os.getcwd()+'/src'
if homedirectory not in sys.path:
    sys.path.append(homedirectory)

import ionosondes

#Choose operation:

downloadFulldatabase = True
downloadSpecificDays = [False,0,365]# Program will run if if True from downloadSpecificDays[0] to
                                    # downloadSpecificDays[1]

if downloadFulldatabase:
    ionosondes.downloadALLfiles()

if downloadSpecificDays[0]:
    pass



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
