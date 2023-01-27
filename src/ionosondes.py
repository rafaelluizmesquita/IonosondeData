try:
    import pandas as pd
except:
    raise Exception("Missing the pandas libraries")
try:
    import numpy as np
except:
    raise Exception("Missing the numpy libraries")
try:
    import requests
except:
    raise Exception("Missing the requests libraries")
try:
    import glob
except:
    raise Exception("Missing the glob libraries")
try:
    import datetime
except:
    raise Exception("Missing the datetime libraries")
try:
    import os
except:
    raise Exception("Missing the os libraries")
try:
    import sys
except:
    raise Exception("Missing the sys libraries")
try:
    import time
except:
    raise Exception("Missing the time libraries")

def getroot():
    return os.getcwd()
def getnames():
    avnaming = getroot()+'/data/infoData/00_availabilityAndNaming'
    names = ["ID",'Station',"LAT","LON",'sta',"end"]

    dtypes = {"ID":str,'Station':str,"LAT":np.float64,"LON":np.float64,'sta':str,"end":str}  
    naming = pd.read_csv(avnaming, sep='\t', skiprows=1, names=names,dtype = dtypes)

    return np.array(naming.ID)
def readfilessite():
    site = 'https://lgdc.uml.edu/common/DIDBStationList'
    r = requests.get(site, allow_redirects=True)
    open(getroot()+'/data/UpdatedStationList.txt', 'wb').write(r.content)


def getURLlist():
    siteinfofile = glob.glob(getroot()+'/data/infoData/00_a*')[0]

    sitinfo = pd.read_csv(siteinfofile, sep = '\t')
    url = []
    for i in range(sitinfo.shape[0]):
        date = sitinfo['EARLIEST DATA'].iloc[i]
        datesplit = date.split(' ')
        mnam = datesplit[0]
        mon = datetime.datetime.strptime(mnam, '%b').month
        day = int(datesplit[1])
        yea = int(datesplit[3])

        EDATE = ('&charName=hmF2&DMUF=1000&fromDate={:}%2F{:02d}%2F{:02d}+00%3A00%3A00'.format(yea,mon,day))
        date = sitinfo['LATEST DATA'].iloc[i]
        datesplit = date.split(' ')
        mnam = datesplit[0]
        mon = datetime.datetime.strptime(mnam, '%b').month
        day = int(datesplit[1])
        yea = int(datesplit[3])

        LDATE = ('&toDate={:}%2F{:02d}%2F{:02d}+00%3A00%3A00'.format(datetime.datetime.now().year,\
                                                               datetime.datetime.now().month,\
                                                               datetime.datetime.now().day))

        back = EDATE + LDATE
        fron = 'https://lgdc.uml.edu/common/DIDBGetValues?ursiCode='
        back0='&charName=hmF2&DMUF=3000&fromDate=2022%2F01%2F01+00%3A00%3A00&toDate=2022%2F02%2F14+00%3A01%3A00'
        url.append(fron+sitinfo.URSI.iloc[i]+back)
    return url
def downloadALLfiles():
    URL = getURLlist()

    for url in URL:
        r = requests.get(url, allow_redirects=True)
        code = url.split('ursiCode=')[-1].split('&')[0]
        try:
            open(getroot()+'/data/ALL/'+code+'.txt', 'wb').write(r.content)
            print('Downloaded Site - ' + code)
        except:
            isExist = os.path.exists(getroot()+'/data/ALL/')
            if not isExist:
                # Create a new directory because it does not exist
                os.makedirs(getroot()+'/data/ALL/')
                open(getroot() + '/data/ALL/' + code + '.txt', 'wb').write(r.content)
                print('Downloaded Site - ' + code)
def downloadfiles(code):
    #2022-01-01T00:00:00.000Z - 2022-02-14T00:01:00.000Z
    fron = 'https://lgdc.uml.edu/common/DIDBGetValues?ursiCode='
    back='&charName=hmF2&DMUF=1000&fromDate=2022%2F01%2F01+00%3A00%3A00&toDate=2022%2F02%2F14+00%3A01%3A00'
    url = fron+code+back
    r = requests.get(url, allow_redirects=True)
    open(getroot()+'/data/'+code+'.txt', 'wb').write(r.content)

#     names = getnames()
#     for n in names:
#         downloadfiles(n)

def makeheader(sitename,codename):
    return '!.. MesquitaOutput V0\n!.. %s - %s - 39.7140.1MANUAL    EDITED    Analog\n \
1.0         ! UTORLT: 1.0/0.0 = UT/LT in column 1\n \
1.0         ! HMORWN: 1.0/0.0 = hmF2/wind in column 2\n \
2           ! NCOLS:  # of columns to be used by FLIP\n \
1 1 0 0 0 0 ! COLUMNS: Columns to be used by FLIP 0/1\n \
550.0       ! ALT_TE: alt. of topside Te \n'%(sitename,codename)
def readIODF(ISfile):
    dtypes = {"Time":str,'CS':np.float64,"hmF2":np.float64,"QD":str}
    names = ['Time', 'CS', 'hmF2', 'QD']
    io_df = pd.read_csv(ISfile, sep=r"\s+", skiprows=20, names=names,dtype = dtypes)
    io_df['DOY'] = pd.to_datetime(io_df.Time).dt.dayofyear
    io_df['dts'] = pd.to_datetime(io_df.Time)
    return io_df

def getSiteInfo(ISfile):
    file = open(ISfile, 'r')
    content = file.readlines()
    splits = content[4].split(', URSI-Code ')[-1].split(' ')
    splits[-1] = splits[-1][:-1]
    codename = splits[0]
    sitename = ' '.join(splits[1:])

    llsplit = content[4].split(', URSI-Code ')[0].split('GEO ')[-1].split(' ')

    latn = llsplit[0]
    lonn = llsplit[1]
    auxoutfile = 'LAT=%s_LON=%s_DOY_YYYY.DAT'%(latn,lonn)
    file.close()

    return [sitename,codename,latn,lonn,auxoutfile]

def addTimeDecToFinalDF(io_df, doy_start,doy_end):
    uniday = io_df.DOY.unique()


    outdf = io_df.loc[(io_df.DOY > doy_start)&(io_df.DOY < doy_end)]

    HMF2 = np.array(outdf.hmF2)

    timedec = []
    for dd in outdf['dts']:
        timedec.append('%2.2f'%((dd.timetuple().tm_yday-doy_start-1)*24. \
                                + dd.hour+dd.minute/60.+dd.minute/3600.))


    outdf['timedec'] = timedec

    outdf = outdf.drop(columns=['Time','CS','QD'], axis=1)
    if (np.size(outdf) > 0):
        return outdf
    else:
        return 'No such DOY'
# io_df = readIODF(ISfiles[2])
# doy_start,doy_end  = 30,40
# print(addTimeDecToFinalDF(io_df, doy_start,doy_end))
# asdasdsad
def saveFiles(ISfile, prints = False, perday = False,doy_start = 30,doy_end = 40):
    sitename,codename,latn,lonn,auxoutfile = getSiteInfo(ISfile)

    header = makeheader(sitename,codename)
    directory = getroot()+'/data/ionosonde/'+codename+'/'
    if not os.path.exists(directory):
        os.mkdir(directory)

    io_df = readIODF(ISfile)
    if perday:
        for i in range(1,367):
            outdf = addTimeDecToFinalDF(io_df,i,i+1)

            try:
                outdf = outdf.rename(columns={"timedec": "UT", "hmF2": "HMF2"})
                outname = auxoutfile.replace('YYYY','%s'%outdf.dts.iloc[0].year).replace('DOY',\
                                                                                 '%003d'%outdf.DOY.iloc[0])
                outnamefull = directory+outname

                if os.path.exists(outnamefull):
                    os.remove(outnamefull)
                with open(outnamefull, 'a') as file:
                    file.write(header)
                    outdf.to_csv(file,\
                             sep = '\t', columns=['UT','HMF2'], header = True, index=False)
                file.close()

                with open(outnamefull) as ofile:
                    fmt = ' %3.2f %3.2f'
                    np.savetxt(ofile, outdf['UT','HMF2'].values, fmt=fmt)

                if prints:
                    print('File saved - '+outname)
            except:
                if prints:
                    print("Not exist, the file for this day does!"+' - DOY:'+str(i))
    else:
        outdf = addTimeDecToFinalDF(io_df,doy_start,doy_end)

        try:
            outdf = outdf.rename(columns={"timedec": "UT", "hmF2": "HMF2"})
#             print('%003d'%outdf.DOY.iloc[0])
            outname = auxoutfile.replace('YYYY','%s'%outdf.dts.iloc[0].year).replace('DOY',\
                                                                                 '%003d'%outdf.DOY.iloc[0])
            outnamefull = directory+outname
            if os.path.exists(outnamefull):
                os.remove(outnamefull)
            with open(outnamefull, 'a') as file:
                file.write(header)
                outdf.to_csv(file,\
                         sep = '\t', columns=['UT','HMF2'], header = True, index=False)
            file.close()

            with open(outnamefull) as ofile:
                fmt = ' %3.2f %3.2f'
                np.savetxt(ofile, outdf['UT','HMF2'].values, fmt=fmt)

            if prints:
                print('File saved - '+outname)
        except:
            if prints:
                pass
            print("Not exist, the file for this day does!"+' - DOY:'+str(i))

# ISfiles = (np.sort(glob.glob(getroot()+'/data/raw/*.txt')))
# if False:
#     for ISfile in ISfiles:
#         saveFiles(ISfile, prints = False, perday = False,doy_start = 31,doy_end = 39)
#     #     print('Done with file = '+ISfile)
#     print(getURLlist())
# remove_empty = False
# if remove_empty:
#     root = getroot()+'/data/ionosonde/'
#     folders = list(os.walk(root))[1:]
#     for folder in folders:
#         if not folder[2]:
#             os.rmdir(folder[0])
#             print('removed folder - '+folder[0])
