import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import urllib.request

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


def get_epd_filelist(dataset, viewing, level, startdate, enddate, path=None):
    """
    INPUT:
        dataset: 'ept' or 'het'
        viewing: 'sun', 'asun', 'north', 'south'
        level: 'll', 'l2'
        startdate, enddate: YYYYMMDD
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'
    RETURNS:
        List of files matching selection criteria.
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
            glob.glob(path+'solo_'+l_str+'_epd-'+dataset+'-sun-rates_' +
                      str(i) + t_str + '_V*.cdf')
        filelist_asun = filelist_asun + \
            glob.glob(path+'solo_'+l_str+'_epd-'+dataset+'-asun-rates_' +
                      str(i) + t_str + '_V???.cdf')
        filelist_north = filelist_north + \
            glob.glob(path+'solo_'+l_str+'_epd-'+dataset+'-north-rates_' +
                      str(i) + t_str + '_V*.cdf')
        filelist_south = filelist_south + \
            glob.glob(path+'solo_'+l_str+'_epd-'+dataset+'-south-rates_' +
                      str(i) + t_str + '_V???.cdf')

    if viewing == 'sun':
        return filelist_sun
    if viewing == 'asun':
        return filelist_asun
    if viewing == 'north':
        return filelist_north
    if viewing == 'south':
        return filelist_south


def read_epd_cdf(dataset, viewing, level, startdate, enddate, path=None):
    """
    INPUT:
        dataset: 'ept' or 'het' (string)
        viewing: 'sun', 'asun', 'north', or 'south' (string)
        level: 'll', 'l2'
        startdate, enddate: YYYYMMDD, e.g., 20210415 (integer)
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/' (string)
    RETURNS:
        1. Pandas dataframe with proton and electron fluxes and errors (for
            EPT also Alpha particles) in 'particles / (s cm^2 sr MeV)'
        2. Dictionary with energy information for all particles:
            - String with energy channel info
            - Value of lower energy bin edge in MeV
            - Value of energy bin width in MeV
    EXAMPLE:
        df_p, df_e, energies = read_epd_cdf('ept', 'north', level='ll',
20210415, 20210416, path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
        df_p, df_e, energies = read_epd_cdf('ept', 'north', level='l2',
20200820, 20200821, path='/home/gieseler/uni/solo/data/l2/epd/')
    """
    filelist = get_epd_filelist(dataset.lower(), viewing.lower(),
                                level.lower(), startdate, enddate, path=path)

    cdf_epd = pycdf.concatCDF([pycdf.CDF(f) for f in filelist])

    if dataset.lower() == 'ept':
        if level.lower() == 'll':
            protons = 'Prot'
            electrons = 'Ele'
        if level.lower() == 'l2':
            protons = 'Ion'
            electrons = 'Electron'
    if dataset.lower() == 'het':
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

    if dataset.lower() == 'ept':
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
        if dataset.lower() == 'ept':
            df_epd_e = pd.DataFrame(cdf_epd['QUALITY_FLAG_1'][...],
                                    index=cdf_epd['EPOCH_1'][...],
                                    columns=['QUALITY_FLAG_1'])
        if dataset.lower() == 'het':
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

    if dataset.lower() == 'ept':
        energies_dict["Alpha_Bins_Text"] = cdf_epd['Alpha_Bins_Text'][...]
        energies_dict["Alpha_Bins_Low_Energy"] = \
            cdf_epd['Alpha_Bins_Low_Energy'][...]
        energies_dict["Alpha_Bins_Width"] = cdf_epd['Alpha_Bins_Width'][...]

    '''
    Careful if adding more species - they might have different EPOCH
    dependencies and cannot easily be put in the same dataframe!
    '''

    return df_epd_p, df_epd_e, energies_dict


# old:
def read_epd_ll_cdf(dataset, viewing, level, startdate, enddate, path=None):
    """
    INPUT:
        dataset: 'ept' or 'het' (string)
        viewing: 'sun', 'asun', 'north', or 'south' (string)
        level: 'll', 'l2'
        startdate, enddate: YYYYMMDD, e.g., 20210415 (integer)
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/' (string)
    RETURNS:
        1. Pandas dataframe with proton and electron fluxes and errors (for
            EPT also Alpha particles) in 'particles / (s cm^2 sr MeV)'
        2. Dictionary with energy information for all particles:
            - String with energy channel info
            - Value of lower energy bin edge in MeV
            - Value of energy bin width in MeV
    EXAMPLE:
        df, energies = read_epd_cdf('ept', 'north', level='ll', 20210415,
20210416, path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
        df, energies = read_epd_cdf('ept', 'north', level='l2', 20200820,
20200821, path='/home/gieseler/uni/solo/data/l2/epd/')
    """
    filelist = get_epd_filelist(dataset.lower(), viewing.lower(),
                                level.lower(), startdate, enddate, path=path)

    print(filelist)
    cdf_epd = pycdf.concatCDF([pycdf.CDF(f) for f in filelist])

    if dataset.lower() == 'ept':
        protons = 'Prot'
    if dataset.lower() == 'het':
        protons = 'H'

    # df_epd = pd.DataFrame(cdf_epd[protons+'_Flux'][...][:,0], \
    #               index=cdf_epd['EPOCH'][...], columns = [protons+'_Flux_0'])
    df_epd = pd.DataFrame(cdf_epd['QUALITY_FLAG'][...],
                          index=cdf_epd['EPOCH'][...],
                          columns=['QUALITY_FLAG'])

    for i in range(cdf_epd[protons+'_Flux'][...].shape[1]):
        # p intensities:
        df_epd[protons+f'_Flux_{i}'] = cdf_epd[protons+'_Flux'][...][:, i]
        # p errors:
        df_epd[protons+f'_Flux_Sigma_{i}'] = \
            cdf_epd[protons+'_Flux_Sigma'][...][:, i]

    if dataset.lower() == 'ept':
        for i in range(cdf_epd['Alpha_Flux'][...].shape[1]):
            # p intensities:
            df_epd[f'Alpha_Flux_{i}'] = cdf_epd['Alpha_Flux'][...][:, i]
            # p errors:
            df_epd[f'Alpha_Flux_Sigma_{i}'] = \
                cdf_epd['Alpha_Flux_Sigma'][...][:, i]

    for i in range(cdf_epd['Ele_Flux'][...].shape[1]):
        # e intensities:
        df_epd[f'Ele_Flux_{i}'] = cdf_epd['Ele_Flux'][...][:, i]
        # p errors:
        df_epd[f'Ele_Flux_Sigma_{i}'] = cdf_epd['Ele_Flux_Sigma'][...][:, i]

    energies_dict = {
        protons+"_Bins_Text": cdf_epd[protons+'_Bins_Text'][...],
        protons+"_Bins_Low_Energy": cdf_epd[protons+'_Bins_Low_Energy'][...],
        protons+"_Bins_Width": cdf_epd[protons+'_Bins_Width'][...],
        "Ele_Bins_Text": cdf_epd['Ele_Bins_Text'][...],
        "Ele_Bins_Low_Energy": cdf_epd['Ele_Bins_Low_Energy'][...],
        "Ele_Bins_Width": cdf_epd['Ele_Bins_Width'][...]
        }

    if dataset.lower() == 'ept':
        energies_dict["Alpha_Bins_Text"] = cdf_epd['Alpha_Bins_Text'][...]
        energies_dict["Alpha_Bins_Low_Energy"] = \
            cdf_epd['Alpha_Bins_Low_Energy'][...]
        energies_dict["Alpha_Bins_Width"] = cdf_epd['Alpha_Bins_Width'][...]

    '''
    Careful if adding more species - they might have different EPOCH
    dependencies and cannot easily be put in the same dataframe!
    '''

    return df_epd, energies_dict


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


def epd_ll_download(dataset, viewing, date, path=''):
    """
    Download EPD low latency data from http://soar.esac.esa.int/soar
    One file/day per call.

    Example:
        epd_ll_download('ept', 'north', 20210415,
                        '/home/gieseler/uni/solo/data/low_latency/epd/LL02/')

    Problem: Low latency files have random start time (e.g. T000101) that needs
             to be explicitly given for downloading the file. One workaround
             would be to get list of available files first (provided as .json),
             and from that extract the file name. Example get URL would be:
             http://soar.esac.esa.int/soar-sl-tap/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY=SELECT+*+FROM+v_ll_data_item+WHERE+(instrument='EPD')+AND+((begin_time>'2021-04-15+00:00:00')+AND+(end_time<'2021-04-16+01:0:00'))
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

    # Problem: see header of function for details
    url = 'http://soar.esac.esa.int/soar-sl-tap/data?' + \
          'retrieval_type=LAST_PRODUCT&data_item_id=solo_LL02_epd-' + \
          dataset.lower()+'-'+viewing.lower()+'-rates_'+str(date) + \
          'T000101-'+str(date+1)+'T000100&product_type=LOW_LATENCY'

    # Get filename from url
    file_name = get_filename_url(
        urllib.request.urlopen(url).headers['Content-Disposition'])

    if tqdm_available:
        download_url(url, path+file_name)
    else:
        urllib.request.urlretrieve(url, path+file_name)

    return path+file_name


def epd_l2_download(dataset, viewing, date, path=''):
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
          dataset.lower()+'-'+viewing.lower()+'-rates_'+str(date) + \
          '&product_type=SCIENCE'

    # Get filename from url
    file_name = get_filename_url(
        urllib.request.urlopen(url).headers['Content-Disposition'])

    if tqdm_available:
        download_url(url, path+file_name)
    else:
        urllib.request.urlretrieve(url, path+file_name)

    return path+file_name
