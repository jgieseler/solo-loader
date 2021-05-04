import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import urllib.request

from spacepy import pycdf


###############################################################################
# """
# Example code that loads electron and proton fluxes (and errors) for 'ept'
# 'north' telescope from Apr 15 2021 to Apr 16 2021 into a Pandas dataframe.
# In general available are 'sun', 'asun', 'north', and 'south' viewing
# directions for 'ept' and 'het' telescopes of SolO/EPD.
# """
#
# from epd_ll_loader import *
#
# df, prot_bins_text, ele_bins_text = \
#   read_epd_low_latency_cdf('ept', 'north', 20210415, 20210416,
#   path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
#
# ax = df.plot(logy=True, subplots=True, figsize=(20,60))
#
# plt.show
#
###############################################################################


def get_epd_filelist(dataset, viewing, startdate, enddate, path=None):
    """
    INPUT:
        dataset: 'ept_low_latency' or 'het_low_latency'
        viewing: 'sun', 'asun', 'north', 'south'
        startdate, enddate: YYYYMMDD
        path: full directory to cdf files; e.g.:
              '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'
    RETURNS:
        List of files matching selection criteria.
    """

    # lazy approach to avoid providing 'path' on my computer (Jan)
    if path is None:
        path = '/home/gieseler/uni/solo/data/low_latency/epd/LL02/'

    filelist_sun = []
    filelist_asun = []
    filelist_north = []
    filelist_south = []
    for i in range(startdate, enddate+1):
        filelist_sun = filelist_sun + \
            glob.glob(path+'solo_LL02_epd-'+dataset+'-sun-rates_'+str(i) +
                      'T??????-????????T??????_V???.cdf')
        filelist_asun = filelist_asun + \
            glob.glob(path+'solo_LL02_epd-'+dataset+'-asun-rates_'+str(i) +
                      'T??????-????????T??????_V???.cdf')
        filelist_north = filelist_north + \
            glob.glob(path+'solo_LL02_epd-'+dataset+'-north-rates_'+str(i) +
                      'T??????-????????T??????_V???.cdf')
        filelist_south = filelist_south + \
            glob.glob(path+'solo_LL02_epd-'+dataset+'-south-rates_'+str(i) +
                      'T??????-????????T??????_V???.cdf')

    if viewing == 'sun':
        return filelist_sun
    if viewing == 'asun':
        return filelist_asun
    if viewing == 'north':
        return filelist_north
    if viewing == 'south':
        return filelist_south


def read_epd_low_latency_cdf(dataset, viewing, startdate, enddate, path=None):
    """
    INPUT:
        dataset: 'ept' or 'het' (string)
        viewing: 'sun', 'asun', 'north', or 'south' (string)
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
        df, energies = \
            read_epd_low_latency_cdf('ept', 'north', 20210415, 20210416, \
            path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')
    """
    filelist = get_epd_filelist(dataset.lower(), viewing.lower(),
                                startdate, enddate, path=path)

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
                        '/home/gieseler/uni/solo/data/low_latency/epd/LL02')
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

    """
    Problem: Low latency files have random start time (e.g. T000101) that needs
             to be explicitly given for downloading the file. One workaround
             would be to get list of available files first (provided as .json),
             and from that extract the file name. Example get URL would be:
             http://soar.esac.esa.int/soar-sl-tap/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY=SELECT+*+FROM+v_ll_data_item+WHERE+(instrument='EPD')+AND+((begin_time>'2021-04-15+00:00:00')+AND+(end_time<'2021-04-16+01:0:00'))
    """
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
