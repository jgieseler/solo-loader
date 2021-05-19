# solo-loader

Data loader for SolO/EPD EPT and HET level 2 (l2) and low latency (ll) data provided by CDF files from <http://soar.esac.esa.int/soar>.

## Requirements

- heliopy, via [Anaconda](https://anaconda.org/conda-forge/heliopy) or [pip](https://pypi.org/project/HelioPy/)
- cdflib, via [Anaconda](https://anaconda.org/conda-forge/cdflib) or [pip](https://pypi.org/project/cdflib/)

## Data folder structure

The `path` variable provided to the module should be the base directory where the corresponding cdf data files should be placed in subdirectories. First subfolder defines the data product `level` (`l2` or `low_latency` at the moment), the next one the `instrument` (so far only `epd`), and finally the `sensor` (`ept` or `het` for now).

For example, the folder structure could look like this: `/home/userxyz/solo/data/l2/epd/het`. In this case, you should call the loader with `path=/home/userxyz/solo/data`; i.e., the base directory for the data.

*Hint: You can use the (automatic) download function described in one of the following sections to let the subfolders be created initially automatically. (NB: It might be that you need to run the code with `sudo`/`admin` privileges in order to be able to create new folders on your system.)*

## Example 1 - low latency data

Example code that loads low latency (ll) electron and proton (+alphas) fluxes
(and errors) for EPT NORTH telescope from Apr 15 2021 to Apr 16 2021 into
two Pandas dataframes (one for protons & alphas, one for electrons). In general
available are 'sun', 'asun', 'north', and 'south' viewing directions for 'ept'
and 'het' telescopes of SolO/EPD.

```python
from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('ept', 'north', 'll', 20210415, 20210416, \
    path='/home/userxyz/solo/data/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
```

## Example 2 - level 2 data

Example code that loads level 2 (l2) electron and proton (+alphas) fluxes
(and errors) for HET SUN telescope from Aug 20 2020 to Aug 20 2020 into
two Pandas dataframes (one for protons & alphas, one for electrons).

```python
from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('het', 'sun', 'l2', 20200820, 20200821, \
    path='/home/userxyz/solo/data/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
```

## Example 3 - plotting electron data from Fig. 2 in Gómez-Herrero et al. 2021<sup>[1](#gh2021)</sup>

```python
from epd_loader import *

# load data
df_protons, df_electrons, energies = \
    read_epd_cdf('ept', 'sun', 'l2', 20200708,20200725,
                 path='/home/gieseler/uni/solo/data',
                 autodownload=True)

# change time resolution to get smoother curve (resample with mean)
resample = '60min'

# plot selection of channels
for channel in [0, 8, 16, 26]:
    ax =  df_electrons['Electron_Flux'][f'Electron_Flux_{channel}']\
            .resample(resample).mean().plot(logy=True,
            label=energies["Electron_Bins_Text"][channel][0])

ax.set_ylabel("Electron flux\n"+r"(cm$^2$ sr s MeV)$^{-1}$")
plt.title('EPT Sun')
plt.legend()
plt.show()
```

## Example 4 - reproducing electron data from Fig. 2 in Wimmer-Schweingruber et al. 2021<sup>[2](#ws2021)</sup>

```python
from epd_loader import *

lpath = '/home/gieseler/uni/solo/data'
df_protons_sun, df_electrons_sun, energies = \
    read_epd_cdf('ept', 'sun', 'l2', 20201210, 20201211,
                 path=lpath, autodownload=True)
df_protons_asun, df_electrons_asun, energies = \
    read_epd_cdf('ept', 'asun', 'l2', 20201210, 20201211,
                 path=lpath, autodownload=True)
df_protons_south, df_electrons_south, energies = \
    read_epd_cdf('ept', 'south', 'l2', 20201210, 20201211,
                 path=lpath, autodownload=True)
df_protons_north, df_electrons_north, energies = \
    read_epd_cdf('ept', 'north', 'l2', 20201210, 20201211,
                 path=lpath, autodownload=True)

# get mean intensities of two energy channels; 'channel' defines the lower one
channel = 6
ax = pd.concat([df_electrons_sun['Electron_Flux'][f'Electron_Flux_{channel}'],
                df_electrons_sun['Electron_Flux'][f'Electron_Flux_{channel+1}']],
                axis=1).mean(axis=1).plot(logy=True, label='sun', color='#d62728')
ax = pd.concat([df_electrons_asun['Electron_Flux'][f'Electron_Flux_{channel}'],
                df_electrons_asun['Electron_Flux'][f'Electron_Flux_{channel+1}']],
                axis=1).mean(axis=1).plot(logy=True, label='asun', color='#ff7f0e')
ax = pd.concat([df_electrons_north['Electron_Flux'][f'Electron_Flux_{channel}'],
                df_electrons_north['Electron_Flux'][f'Electron_Flux_{channel+1}']],
                axis=1).mean(axis=1).plot(logy=True, label='north', color='#1f77b4')
ax = pd.concat([df_electrons_south['Electron_Flux'][f'Electron_Flux_{channel}'],
                df_electrons_south['Electron_Flux'][f'Electron_Flux_{channel+1}']],
                axis=1).mean(axis=1).plot(logy=True, label='south', color='#2ca02c')

plt.xlim([datetime.datetime(2020, 12, 10, 23, 0), 
          datetime.datetime(2020, 12, 11, 12, 0)])

ax.set_ylabel("Electron flux\n"+r"(cm$^2$ sr s MeV)$^{-1}$")
plt.title('EPT electrons ('+str(energies['Electron_Bins_Low_Energy'][channel])
          + '-' + str(energies['Electron_Bins_Low_Energy'][channel+2])+' MeV)')
plt.legend()
plt.show()
```

![Figure](../main/examples/ws2021_fig_2d.png)

## Data download within Python

Data files can be downloaded from <http://soar.esac.esa.int/soar> directly from within python. They are saved in the folder provided by the `path` argument.

### Automatic download

While using `read_epd_cdf()` to obtain the data, one can choose to automatically download missing data files. For that, just add `autodownload=True` to the call of `read_epd_cdf()`:

```python
from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('het', 'sun', 'l2', 20200820, 20200821, \
    path='/home/userxyz/solo/data/', \
    autodownload=True)

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
```

Note: The code will always download the *latest version* of the file available at SOAR. So in case a file `V01.cdf` is already locally present, `V02.cdf` will be downloaded nonetheless.

### Manual download

Level 2 data *can* be manually downloaded using `epd_l2_download()`. But because this is usually only done internally, the `path` variable is defined a bit different here; it needs to be the *full* path to where the cdf files should be stored (instead of the *base* directory). Following example downloads EPT NORTH telescope data for Aug 20 2020 to the dir `/home/userxyz/solo/data/`. Right now rudimentary working with one download (1 file/day) per call.

```python
from epd_loader import *

epd_l2_download('ept', 'north', 20200820, '/home/userxyz/solo/data/l2/epd/ept/')
```

`epd_ll_download()` provides the same functionality for low latency data:

```python
from epd_loader import *

epd_ll_download('ept', 'north', 20200820, '/home/userxyz/solo/data/low_latency/epd/ept/')
```

## References

<a name="gh2021">1</a>: Gómez-Herrero et al. 2021, First near-relativistic solar electron events observed by EPD onboard Solar Orbiter, A&A, <https://doi.org/10.1051/0004-6361/202039883>.

<a name="ws2021">2</a>: Wimmer-Schweingruber et al. 2021, The first year of energetic particle measurements in the inner heliosphere with Solar Orbiter’s Energetic Particle Detector, submitted to A&A.
