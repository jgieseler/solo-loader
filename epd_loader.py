import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import urllib.request

from pathlib import Path
from spacepy import pycdf


###############################################################################
"""
Example code that loads low latency (ll) electron and proton (+alphas) fluxes
(and errors) for 'ept' 'north' telescope from Apr 15 2021 to Apr 16 2021 into
two Pandas dataframes (one for protons & alphas, one for electrons). In general
available are 'sun', 'asun', 'north', and 'south' viewing directions for 'ept'
and 'het' telescopes of SolO/EPD.

from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('ept', 'north', 'll', 20210415, 20210416,
path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
"""

"""
Example code that loads level 2 (l2) electron and proton (+alphas) fluxes
(and errors) for 'het' 'sun' telescope from Aug 20 2020 to Aug 20 2020 into
two Pandas dataframes (one for protons & alphas, one for electrons).

from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('het', 'sun', 'l2', 20200820, 20200821,
path='/home/gieseler/uni/solo/data/l2/epd/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

"""

"""
Level 2 data can be downloaded from http://soar.esac.esa.int/soar/ using
epd_l2_download(). Following example downloads 'ept' 'north' telescope data for
Aug 20 2020 (downloads 1 file/day per call).

epd_l2_download('ept', 'north', 20200820,
    '/home/gieseler/uni/solo/data/l2/epd/')

epd_ll_download() provides the same functionality for low latency data but
doesn't work reliably.
"""
###############################################################################


def cdf_info(cdf):
    ccdf = pycdf.CDFCopy(cdf)    # dict containing attributes copied from CDF
    for i in ccdf.keys():
        print('\"'+i+'\"')
        print(cdf[i].attrs)
        print('')
    return


def get_epd_filelist(sensor, level, startdate, enddate, path=None,
                     filenames_only=False):
    """
    INPUT:
        sensor: 'ept' or 'het'
        level: 'll', 'l2'
        startdate, enddate: YYYYMMDD
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'
        filenames_only: if True only give the filenames, not the full path
    RETURNS:
        Dictionary with four entries for 'sun', 'asun', 'north', 'south';
        each containing a list of files matching selection criteria.
    """

    if level == 'll':
        l_str = 'LL02'
        t_str = 'T??????-????????T??????'
        # lazy approach to avoid providing 'path' on my computer (Jan)
        if path is None:
            path = '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'
    if level == 'l2':
        l_str = 'L2'
        t_str = ''
        # lazy approach to avoid providing 'path' on my computer (Jan)
        if path is None:
            path = '/home/gieseler/uni/solo/data/l2/epd/'

    filelist_sun = []
    filelist_asun = []
    filelist_north = []
    filelist_south = []
    for i in range(startdate, enddate+1):
        filelist_sun = filelist_sun + \
            glob.glob(path+'solo_'+l_str+'_epd-'+sensor+'-sun-rates_' +
                      str(i) + t_str + '_V*.cdf')
        filelist_asun = filelist_asun + \
            glob.glob(path+'solo_'+l_str+'_epd-'+sensor+'-asun-rates_' +
                      str(i) + t_str + '_V???.cdf')
        filelist_north = filelist_north + \
            glob.glob(path+'solo_'+l_str+'_epd-'+sensor+'-north-rates_' +
                      str(i) + t_str + '_V*.cdf')
        filelist_south = filelist_south + \
            glob.glob(path+'solo_'+l_str+'_epd-'+sensor+'-south-rates_' +
                      str(i) + t_str + '_V???.cdf')

    if filenames_only:
        filelist_sun = [os.path.basename(x) for x in filelist_sun]
        filelist_asun = [os.path.basename(x) for x in filelist_asun]
        filelist_north = [os.path.basename(x) for x in filelist_north]
        filelist_south = [os.path.basename(x) for x in filelist_south]

    filelist = {
        'sun': filelist_sun,
        'asun': filelist_asun,
        'north': filelist_north,
        'south': filelist_south
        }
    return filelist

def read_epd_cdf(sensor, viewing, level, startdate, enddate, path=None, \
                 autodownload=False):
    """
    INPUT:
        sensor: 'ept' or 'het' (string)
        viewing: 'sun', 'asun', 'north', or 'south' (string)
        level: 'll', 'l2'
        startdate, enddate: YYYYMMDD, e.g., 20210415 (integer)
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/' (string)
        autodownload: if True will try to download missing data files from SOAR
    RETURNS:
        1. Pandas dataframe with proton fluxes and errors (for EPT also Alpha
           particles) in 'particles / (s cm^2 sr MeV)'
        2. Pandas dataframe with electron fluxes and errors in
           'particles / (s cm^2 sr MeV)'
        3. Dictionary with energy information for all particles:
            - String with energy channel info
            - Value of lower energy bin edge in MeV
            - Value of energy bin width in MeV
    EXAMPLE:
        df_p, df_e, energies = read_epd_cdf('ept', 'north', 'll',
20210415, 20210416, path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
        df_p, df_e, energies = read_epd_cdf('ept', 'north', 'l2',
20200820, 20200821, path='/home/gieseler/uni/solo/data/l2/epd/')
    """
    # filelist = get_epd_filelist(sensor.lower(), viewing.lower(),
    #                             level.lower(), startdate, enddate, path=path)
    filelist = get_epd_filelist(sensor.lower(), level.lower(), startdate,
                                enddate, path=path)[viewing.lower()]

    print('a')                  

    cdf_epd = pycdf.concatCDF([pycdf.CDF(f) for f in filelist])

    if sensor.lower() == 'ept':
        if level.lower() == 'll':
            protons = 'Prot'
            electrons = 'Ele'
        if level.lower() == 'l2':
            protons = 'Ion'
            electrons = 'Electron'
    if sensor.lower() == 'het':
        if level.lower() == 'll':
            protons = 'H'
            electrons = 'Ele'
        if level.lower() == 'l2':
            protons = 'H'  # EPOCH
            electrons = 'Electron'  # EPOCH_4, QUALITY_FLAG_4

    # df_epd = pd.DataFrame(cdf_epd[protons+'_Flux'][...][:,0], \
    #               index=cdf_epd['EPOCH'][...], columns = [protons+'_Flux_0'])
    df_epd_p = pd.DataFrame(cdf_epd['QUALITY_FLAG'][...],
                            index=cdf_epd['EPOCH'][...],
                            columns=['QUALITY_FLAG'])

    for i in range(cdf_epd[protons+'_Flux'][...].shape[1]):
        # p intensities:
        df_epd_p[protons+f'_Flux_{i}'] = cdf_epd[protons+'_Flux'][...][:, i]
        # p errors:
        if level.lower() == 'll':
            df_epd_p[protons+f'_Flux_Sigma_{i}'] = \
                cdf_epd[protons+'_Flux_Sigma'][...][:, i]
        if level.lower() == 'l2':
            df_epd_p[protons+f'_Uncertainty_{i}'] = \
                cdf_epd[protons+'_Uncertainty'][...][:, i]

    if sensor.lower() == 'ept':
        for i in range(cdf_epd['Alpha_Flux'][...].shape[1]):
            # alpha intensities:
            df_epd_p[f'Alpha_Flux_{i}'] = cdf_epd['Alpha_Flux'][...][:, i]
            # alpha errors:
            if level.lower() == 'll':
                df_epd_p[f'Alpha_Flux_Sigma_{i}'] = \
                    cdf_epd['Alpha_Flux_Sigma'][...][:, i]
            if level.lower() == 'l2':
                df_epd_p[f'Alpha_Uncertainty_{i}'] = \
                    cdf_epd['Alpha_Uncertainty'][...][:, i]

    if level.lower() == 'll':
        df_epd_e = pd.DataFrame(cdf_epd['QUALITY_FLAG'][...],
                                index=cdf_epd['EPOCH'][...],
                                columns=['QUALITY_FLAG'])
    if level.lower() == 'l2':
        if sensor.lower() == 'ept':
            df_epd_e = pd.DataFrame(cdf_epd['QUALITY_FLAG_1'][...],
                                    index=cdf_epd['EPOCH_1'][...],
                                    columns=['QUALITY_FLAG_1'])
        if sensor.lower() == 'het':
            df_epd_e = pd.DataFrame(cdf_epd['QUALITY_FLAG_4'][...],
                                    index=cdf_epd['EPOCH_4'][...],
                                    columns=['QUALITY_FLAG_4'])

    for i in range(cdf_epd[electrons+'_Flux'][...].shape[1]):
        # e intensities:
        df_epd_e[electrons+f'_Flux_{i}'] = \
            cdf_epd[electrons+'_Flux'][...][:, i]
        # e errors:
        if level.lower() == 'll':
            df_epd_e[f'Ele_Flux_Sigma_{i}'] = \
                cdf_epd['Ele_Flux_Sigma'][...][:, i]
        if level.lower() == 'l2':
            df_epd_e[f'Electron_Uncertainty_{i}'] = \
                cdf_epd['Electron_Uncertainty'][...][:, i]

    energies_dict = {
        protons+"_Bins_Text": cdf_epd[protons+'_Bins_Text'][...],
        protons+"_Bins_Low_Energy": cdf_epd[protons+'_Bins_Low_Energy'][...],
        protons+"_Bins_Width": cdf_epd[protons+'_Bins_Width'][...],
        electrons+"_Bins_Text": cdf_epd[electrons+'_Bins_Text'][...],
        electrons+"_Bins_Low_Energy":
            cdf_epd[electrons+'_Bins_Low_Energy'][...],
        electrons+"_Bins_Width": cdf_epd[electrons+'_Bins_Width'][...]
        }

    if sensor.lower() == 'ept':
        energies_dict["Alpha_Bins_Text"] = cdf_epd['Alpha_Bins_Text'][...]
        energies_dict["Alpha_Bins_Low_Energy"] = \
            cdf_epd['Alpha_Bins_Low_Energy'][...]
        energies_dict["Alpha_Bins_Width"] = cdf_epd['Alpha_Bins_Width'][...]

    '''
    Careful if adding more species - they might have different EPOCH
    dependencies and cannot easily be put in the same dataframe!
    '''

    return df_epd_p, df_epd_e, energies_dict


def get_filename_url(cd):
    """
    Get download filename for a url from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0][1:-1]


def epd_ll_download(sensor, viewing, date, path=''):
    """
    Download EPD low latency data from http://soar.esac.esa.int/soar
    One file/day per call.

    Example:
        epd_ll_download('ept', 'north', 20210415,
                        '/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
    """

    try:
        from tqdm import tqdm

        class DownloadProgressBar(tqdm):
            def update_to(self, b=1, bsize=1, tsize=None):
                if tsize is not None:
                    self.total = tsize
                self.update(b * bsize - self.n)

        def download_url(url, output_path):
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1,
                                     desc=output_path.split('/')[-1]) as t:
                urllib.request.urlretrieve(url, filename=output_path,
                                           reporthook=t.update_to)

        tqdm_available = True
    except ModuleNotFoundError:
        print("Module tqdm not installed, won't show progress bar.")
        tqdm_available = False

    # get list of available data files, obtain corresponding start & end time
    fl = get_available_soar_files(date, date, sensor, 'll') 
    try:
        stime = fl[0][-32:-25]
        etime = fl[0][-16:-9]

        url = 'http://soar.esac.esa.int/soar-sl-tap/data?' + \
            'retrieval_type=LAST_PRODUCT&data_item_id=solo_LL02_epd-' + \
            sensor.lower()+'-'+viewing.lower()+'-rates_'+str(date) + \
            stime+'-'+str(date+1)+etime+'&product_type=LOW_LATENCY'

        print(url)

        # Get filename from url
        file_name = get_filename_url(
            urllib.request.urlopen(url).headers['Content-Disposition'])

        if tqdm_available:
            download_url(url, path+file_name)
        else:
            urllib.request.urlretrieve(url, path+file_name)

        return path+file_name
    except:
        print('No data found at SOAR!')
        
        return


def epd_l2_download(sensor, viewing, date, path=''):
    """
    Download EPD level 2 data from http://soar.esac.esa.int/soar
    One file/day per call.

    Example:
        epd_l2_download('ept', 'north', 20200820,
            '/home/gieseler/uni/solo/data/l2/epd/')
    """

    try:
        from tqdm import tqdm

        class DownloadProgressBar(tqdm):
            def update_to(self, b=1, bsize=1, tsize=None):
                if tsize is not None:
                    self.total = tsize
                self.update(b * bsize - self.n)

        def download_url(url, output_path):
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1,
                                     desc=output_path.split('/')[-1]) as t:
                urllib.request.urlretrieve(url, filename=output_path,
                                           reporthook=t.update_to)

        tqdm_available = True
    except ModuleNotFoundError:
        print("Module tqdm not installed, won't show progress bar.")
        tqdm_available = False

    url = 'http://soar.esac.esa.int/soar-sl-tap/data?' + \
          'retrieval_type=LAST_PRODUCT&data_item_id=solo_L2_epd-' + \
          sensor.lower()+'-'+viewing.lower()+'-rates_'+str(date) + \
          '&product_type=SCIENCE'

    # Get filename from url
    file_name = get_filename_url(
        urllib.request.urlopen(url).headers['Content-Disposition'])

    if tqdm_available:
        download_url(url, path+file_name)
    else:
        urllib.request.urlretrieve(url, path+file_name)

    return path+file_name


def get_available_soar_files(startdate, enddate, sensor, level='l2'):
    from astropy.io.votable import parse_single_table

    # add 1 day to enddate to better work with SOAR's API
    # enddate = (pd.to_datetime(str(enddate))+pd.to_timedelta('1d')).strftime('%Y%m%d')  

    sy = str(startdate)[0:4]
    sm = str(startdate)[4:6]
    sd = str(startdate)[6:8]

    ey = str(enddate)[0:4]
    em = str(enddate)[4:6]
    ed = str(enddate)[6:8]

    if level.lower() == 'l2':
        p_level = 'L2'  # "processing_level"
    #     data_type = 'v_sc_data_item'   
    if level.lower() == 'll':
        p_level = 'LL02'  # "processing_level"
    #     data_type = 'v_ll_data_item'
    data_type = 'v_public_files'

    # url = "http://soar.esac.esa.int/soar-sl-tap/tap/sync?REQUEST=doQuery&" + \
    #        "LANG=ADQL&retrieval_type=LAST_PRODUCT&FORMAT=votable_plain&QUERY=SELECT+*+FROM+"+data_type + \
    #        "+WHERE+(instrument='EPD')+AND+((begin_time%3E%3D'"+sy+"-"+sm + \
    #        "-"+sd+"+00:00:00')+AND+(end_time%3C%3D'"+ey+"-"+em+"-"+ed + \
    #        "+01:00:00'))"
    url = "http://soar.esac.esa.int/soar-sl-tap/tap/sync?REQUEST=doQuery&" + \
           "LANG=ADQL&retrieval_type=LAST_PRODUCT&FORMAT=votable_plain&QUERY=SELECT+*+FROM+"+data_type + \
           "+WHERE+(instrument='EPD')+AND+((begin_time%3E%3D'"+sy+"-"+sm + \
           "-"+sd+"+00:00:00')+AND+(begin_time%3C%3D'"+ey+"-"+em+"-"+ed + \
           "+01:00:00'))"

    filelist = urllib.request.urlretrieve(url)

    # open VO table, convert to astropy table, convert to pandas dataframe
    df = parse_single_table(filelist[0]).to_table().to_pandas()

    # convert bytestrings to unicode, from stackoverflow.com/a/67051068/2336056
    for col, dtype in df.dtypes.items():
        if dtype == np.object:  # Only process object columns.
            # decode, or return original value if decode return Nan
            df[col] = df[col].str.decode('utf-8').fillna(df[col]) 

    # remove duplicates with older version number
    df = df.sort_values('file_name')
    df.drop_duplicates(subset=['item_id'], keep='last', inplace=True)

    # only use data level wanted; i.e., 'LL' or 'L2'
    df = df[df['processing_level'] == p_level] 

    # list filenames for given telescope (e.g., 'HET')
    # filelist = df['filename'][df['sensor'] == sensor.upper()].sort_values()
    filelist = [s for s in df['file_name'].values if sensor.lower() in s]
      
    # list filenames for 'rates' type (i.e., remove 'hcad')
    filelist = [s for s in filelist if "rates" in s]
    
    # filelist.sort()

    return filelist
    

"""
input_path = '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'
sensor = 'ept'
viewing = 'north'


# fl = get_epd_filelist('ept', 'll', 20210415, 20210422,filenames_only=True)    
# fl['asun']+fl['north']+fl['south']+fl['sun']  

fls = get_available_soar_files(20210415, 20210418, sensor, 'll') 


for i in fls:
    my_file = Path(input_path)/i
    if not my_file.is_file():
        print(i+' - MISSING => DOWNLOADING...')
        tdate = int(i.split('_')[3].split('T')[0])
        tview = i.split('-')[2]
        _ = epd_ll_download(sensor, tview, tdate, path=input_path)
        # _ = [epd_ll_download(sensor, view, tdate, path=input_path) for view in ['asun', 'north', 'south', 'sun']]
"""
