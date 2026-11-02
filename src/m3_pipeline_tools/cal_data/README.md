
# Calibration Files & Other Processing Metadata

### Directory Structure
```
calibration_data/
├── __init__.py
├── README.md
├── all_possible_darks.csv
├── l1b_processing_info.csv
├── m3_detector_temperature.tab
├── mission_housekeeping_data.csv
├── obs_cal_info.csv
├── possible_real_obs_not_processed_to_l1b.csv
├── l1b/      # l1b calibration files
└── l2/       # l2 calibration files
```
Target mode calibration files begin with 'm3t' while Global mode calibration files begin with 'm3g'.

### Per-Observation Processing Metadata
Each file below contains information scraped from L0 and L1B LBL files, as well as HDR files
associated with RDN IMG files in the PDS3 (JPL) version of the PDS M3 dataset. The PDS4 (USGS)
version of the PDS M3 dataset did not preserve the HDR files. Target and Global mode observations
are combined in these lists.

`l1b_processing_info.csv`: Per-observation metadata for only the final PDS version (version 3,
CH1M3_0003 in the JPL PDS) of all L1B data. The primary file used by `moonlight-pipeline` for
determining the required calibration files at runtime. Currently, we use the mission L1B label 
orientation information to match pipeline outputs to the mission L1B data

`m3_detector_temperature.tab`: A mission-produced table of detector temperatures for most
observations. Temperatures in this table do not always match the detector temperatures listed in
the PDS labels or HDR files, which also sometimes change between versions within the PDS. We do
not know:
1) When during the observation the temperature was recorded.
2) Which sensor the temperature came from.

`mission_housekeeping_data.csv`: The file from which `l1b_processing_info.csv` was derived, with
significantly more metadata for all versions of each observation available in the PDS.

`obs_cal_info.csv`: The original per-observation metadata used by this pipeline. Deprecated.

`all_possible_darks.csv`: List of all possible dark signal observations. Dark observations were not
demarcated as such in their labels. We can infer an observation is a dark based on observation
length or if it is listed in the HDR of an L1B file as a dark signal observation used in calibration
(see `l1b_processing_info.csv`). _This is not an exact science. Some 'real' observations were
short and never processed to L1B due to other factors._

`possible_real_obs_not_processed_to_l1b.csv`: List of observations that may contain ‘real’ observational
data but were not processed to L1B / L2. These were likely excluded from processing by the mission
due to high observation temperatures or other quality issues. This list may include unusually
long dark signal observations.

### Calibration File Special Notes
Calibration files from the PDS are included here for use with the processing pipelines. Listed below
are calibration files that we modified or created, or that otherwise require special explanation.

`global_ssc.csv` and `target_ssc.csv`: All the smooth shape correction factors for each observation,
separated by observation mode (see the DPSIS for an explanation of this mission-derived correction). 
These were pulled from each individual SSC file in the PDS.

`lab_flat_field_global.fits`: We linearly interpolated the filter seams of the lab flat. In 
`lab_flat_field_global_old.fits`, the PDS version of the global flat field, the horizontal filter 
seams are disruptions of the flat field pattern. However, in the target mode lab flat those same filter
seams _were_ spectrally linearly interpolated. There is no obvious processing reason for the
filter seam treatment in the laboratory flat fields to differ between target and global mode.

`m3g20081211_rdn_gain.tab` and `m3t20070912_rdn_gain.tab`: These gain files provided by the 
PDS have a value of '1' for every band. We don't implement them in the pipeline because they
are all '1'.

`m3g20081118_rdn_cal.tab`: The PDS file modified date (2010-06-29) and filename date of these 
radiance calibration factors for global mode pre-date a change to the radiance calibration 
factors of the last five bands noted in the errata.txt file of the JPL PDS:

    5.)  Level 1B calibration update December 31, 2010
 
     The M3 Level 1B radiometric calibration was updated to better account 
     for the thermal emitted energy from the laboratory calibration fixture 
     during laboratory calibration of the M3 instrument in April 2007.  This 
     update improves the radiometric calibration of the last 5 spectral 
     channels in the M3 Global data set.  This update in calibration should 
     replace version 1.0 of the M3 Level 1B data products delivered in 
     June of 2010.
