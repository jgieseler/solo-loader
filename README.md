# solo-loader

Data loader for SolO/EPD EPT and HET level 2 (L2) and low latency (ll) data provided by CDF files from http://soar.esac.esa.int/soar.

## Example 1 - low latency data
Example code that loads low latency (ll) electron and proton (+alphas) fluxes
(and errors) for EPT NORTH telescope from Apr 15 2021 to Apr 16 2021 into
two Pandas dataframes (one for protons & alphas, one for electrons). In general
available are 'sun', 'asun', 'north', and 'south' viewing directions for 'ept'
and 'het' telescopes of SolO/EPD.

```python
from epd_loader import *

df_protons, df_electrons, energies = \
read_epd_cdf('ept', 'north', 'll', 20210415, 20210416, path='/home/gieseler/uni/solo/data/low_latency/epd/LL02/')

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
read_epd_cdf('het', 'sun', 'l2', 20200820, 20200821, path='/home/gieseler/uni/solo/data/l2/epd/')

# plot protons and alphas
ax = df_protons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()

# plot electrons
ax = df_electrons.plot(logy=True, subplots=True, figsize=(20,60))
plt.show()
```

## Data download within Python
Level 2 data can be downloaded from http://soar.esac.esa.int/soar using `epd_l2_download()`. Following example downloads EPT NORTH telescope data for
Aug 20 2020 to the dir `/home/gieseler/uni/solo/data/l2/epd/`. Right now rudimentary working with one download (1 file/day) per call.

```python
from epd_loader import *

epd_l2_download('ept', 'north', 20200820, '/home/gieseler/uni/solo/data/l2/epd/')
```

`epd_ll_download()` provides the same functionality for low latency data but
doesn't work reliably at the moment.
