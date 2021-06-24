# solo-loader

Data loader for SolO/EPD EPT, HET, and STEP level 2 (l2) and low latency (ll) data provided by CDF files from <http://soar.esac.esa.int/soar>.

## Requirements

- heliopy, via [Anaconda](https://anaconda.org/conda-forge/heliopy) or [pip](https://pypi.org/project/HelioPy/)
- cdflib, via [Anaconda](https://anaconda.org/conda-forge/cdflib) or [pip](https://pypi.org/project/cdflib/)

## Usage

The standard usecase is to utilize the `epd_load` function, which returns Pandas dataframe(s) of the EPD measurements and a dictionary containing information on the energy channels.
```python
from epd_loader import *

df_1, df_2, energies = \
    epd_load(sensor, viewing, level, startdate, enddate, path, autodownload)
```

### Input

- `sensor`: `ept`, `het`, or `step` (string)
- `viewing`: `sun`, `asun`, `north`, or `south` (string); not needed for `sensor = step`
- `level`: `ll` or `l2` (string)
- `startdate`, `enddate`: YYYYMMDD, e.g., 20210415 (integer) (if no `enddate` is provided, `enddate = startdate` will be used)
- `path`: directory in which Solar Orbiter data is/should be organized; e.g. `/home/gieseler/uni/solo/data/` (string)
- `autodownload`: if `True` will try to download missing data files from SOAR (bolean)

### Return

- For `sensor` = `ept` or `het`:
    1. Pandas dataframe with proton fluxes and errors (for EPT also alpha particles) in 'particles / (s cm^2 sr MeV)'
    2. Pandas dataframe with electron fluxes and errors in 'particles / (s cm^2 sr MeV)'
    3. Dictionary with energy information for all particles:
        - String with energy channel info
        - Value of lower energy bin edge in MeV
        - Value of energy bin width in MeV

- For `sensor` = `step`:
    1. Pandas dataframe with fluxes and errors in 'particles / (s cm^2 sr MeV)'
    2. Dictionary with energy information for all particles:
        - String with energy channel info
        - Value of lower energy bin edge in MeV
        - Value of energy bin width in MeV


## Data folder structure

The `path` variable provided to the module should be the base directory where the corresponding cdf data files should be placed in subdirectories. First subfolder defines the data product `level` (`l2` or `low_latency` at the moment), the next one the `instrument` (so far only `epd`), and finally the `sensor` (`ept` or `het` for now).

For example, the folder structure could look like this: `/home/userxyz/solo/data/l2/epd/het`. In this case, you should call the loader with `path=/home/userxyz/solo/data`; i.e., the base directory for the data.

*Hint: You can use the (automatic) download function described in one of the following sections to let the subfolders be created initially automatically. (NB: It might be that you need to run the code with `sudo`/`admin` privileges in order to be able to create new folders on your system.)*

## Data download within Python

Data files can be downloaded from <http://soar.esac.esa.int/soar> directly from within python. They are saved in the folder provided by the `path` argument.

### Automatic download

While using `epd_load()` to obtain the data, one can choose to automatically download missing data files. For that, just add `autodownload=True` to the function call:

```python
from epd_loader import *

df_protons, df_electrons, energies = \
    epd_load(sensor='het', viewing='sun', level='l2', 
             startdate=20200820, enddate=20200821, \
             path='/home/userxyz/solo/data/', autodownload=True)

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

epd_l2_download(20200820, '/home/userxyz/solo/data/l2/epd/ept/', 'ept', 'north')
```

`epd_ll_download()` provides the same functionality for low latency data:

```python
from epd_loader import *

epd_ll_download(20200820, '/home/userxyz/solo/data/low_latency/epd/ept/', 'ept', 'north')
```

## Example 1 - low latency data

Example code that loads low latency (ll) electron and proton (+alphas) fluxes
(and errors) for EPT NORTH telescope from Apr 15 2021 to Apr 16 2021 into
two Pandas dataframes (one for protons & alphas, one for electrons). In general
available are 'sun', 'asun', 'north', and 'south' viewing directions for 'ept'
and 'het' telescopes of SolO/EPD.

```python
from epd_loader import *

df_protons, df_electrons, energies = \
    epd_load(sensor='ept', viewing='north', level='ll', 
             startdate=20210415, enddate=20210416, \
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
    epd_load(sensor='het', viewing='sun', level='l2', 
             startdate=20200820, enddate=20200821, \
             path='/home/userxyz/solo/data/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
```

## Example 3 - reproducing EPT data from Fig. 2 in Gómez-Herrero et al. 2021<sup>[1](#gh2021)</sup>

```python
from epd_loader import *

# set your local path here
lpath = '/home/userxyz/solo/data'

# load data
df_protons, df_electrons, energies = \
    epd_load(sensor='ept', viewing='sun', level='l2', startdate=20200708, 
             enddate=20200724, path=lpath, autodownload=True)

# change time resolution to get smoother curve (resample with mean)
resample = '60min'

fig, axs = plt.subplots(2, sharex=True)
fig.suptitle('EPT Sun')

# plot selection of channels
for channel in [0, 8, 16, 26]:
    df_electrons['Electron_Flux'][f'Electron_Flux_{channel}']\
        .resample(resample).mean().plot(ax = axs[0], logy=True,
        label=energies["Electron_Bins_Text"][channel][0])
for channel in [6, 22, 32, 48]:
    df_protons['Ion_Flux'][f'Ion_Flux_{channel}']\
        .resample(resample).mean().plot(ax = axs[1], logy=True,
        label=energies["Ion_Bins_Text"][channel][0])

axs[0].set_ylim([0.3, 4e6])
axs[1].set_ylim([0.01, 5e8])

axs[0].set_ylabel("Electron flux\n"+r"(cm$^2$ sr s MeV)$^{-1}$")
axs[1].set_ylabel("Ion flux\n"+r"(cm$^2$ sr s MeV)$^{-1}$")
axs[0].legend()
axs[1].legend()
plt.subplots_adjust(hspace=0)
plt.show()
```

**NB: This is just an approximate reproduction with different energy channels (smaller, not combined) and different time resolution!**
![Figure](../main/examples/gh2021_fig_2.png)

## Example 4 - reproducing EPT data from Fig. 2 in Wimmer-Schweingruber et al. 2021<sup>[2](#ws2021)</sup>

```python
from epd_loader import *

# set your local path here
lpath = '/home/userxyz/solo/data'

# load data
df_protons_sun, df_electrons_sun, energies = \
    epd_load(sensor='ept', viewing='sun', level='l2', 
             startdate=20201210, enddate=20201211,
             path=lpath, autodownload=True)
df_protons_asun, df_electrons_asun, energies = \
    epd_load(sensor='ept', viewing='asun', level='l2', 
             startdate=20201210, enddate=20201211,
             path=lpath, autodownload=True)
df_protons_south, df_electrons_south, energies = \
    epd_load(sensor='ept', viewing='south', level='l2', 
             startdate=20201210, enddate=20201211,
             path=lpath, autodownload=True)
df_protons_north, df_electrons_north, energies = \
    epd_load(sensor='ept', viewing='north', level='l2', 
             startdate=20201210, enddate=20201211,
             path=lpath, autodownload=True)

# plot mean intensities of two energy channels; 'channel' defines the lower one
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

**NB: This is just an approximate reproduction; e.g., the channel combination is a over-simplified approximation!**
![Figure](../main/examples/ws2021_fig_2d.png)

## References

<a name="gh2021">1</a>: Gómez-Herrero et al. 2021, First near-relativistic solar electron events observed by EPD onboard Solar Orbiter, A&A, <https://doi.org/10.1051/0004-6361/202039883>.

<a name="ws2021">2</a>: Wimmer-Schweingruber et al. 2021, The first year of energetic particle measurements in the inner heliosphere with Solar Orbiter’s Energetic Particle Detector, submitted to A&A.
