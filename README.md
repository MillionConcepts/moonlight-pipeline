# Moonlight Pipeline 

## Overview
The Moonlight project aims to re-implement the data processing pipelines for the Moon 
Mineralogy Mapper (M3), an imaging spectrometer that flew aboard Chandrayaan-1.

The L0 (raw DN) to L1B (radiance) and L1B to L2 (reflectance) pipelines are under active
development. Processing steps are heavily informed by mission-produced documentation, such
as the [DPSIS](mission_docs/DPSIS_big.pdf). 

We have also developed a new L1B flagging pipeline to ease analysis of M3 L1B and L2 
products. This pipeline outputs an L1B-shaped flag bitmask for a single observation by 
combining mission-defined flag maps with new data quality flags.

Future work includes new spectral parameter and mineralogy maps. 

## Installation
The Moonlight Pipeline is not currently distributed via any package manager. The easiest 
way to install it is simply to clone this repository. We recommend installing 
its requirements by feeding the provided [environment.yml](environment.yml) file to 
`conda`. 

## Basic Usage
A series of Jupyter Notebook tutorials for this repository live in [tutorials](./tutorials/). 
1. [Basic Processing](./tutorials/tutorial1_basic_processing.ipynb)
   * Overview of FITS file usage with M3 data.
2. [Basic Bitmask Flagging](./tutorials/tutorial2_flagging.ipynb)
   * Overview of using the flag bitmasks produced by both the L1B flagging pipeline and the 
    (in development) L0 to L1B pipeline.
3. [Comprehensive Flagging](./tutorials/tutorial3_comprehensive_flagging.ipynb)
   * Comprehensive explanation of flag meanings in the flag bitmasks, as well as how to 
     run the L1B flagging pipeline on pre-existing PDS L1B products.
4. [Removing Smooth Shape Correction](./tutorials/tutorial4_removing_ssc.ipynb)
   * How to remove the mission-derived smooth shape correction from observational data.
5. [Running Pipelines](./tutorials/tutorial5_running_pipelines.ipynb)
   * Overview of running the L0 to L1B processing pipelines.  

More comprehensive documentation for Moonlight Pipeline is forthcoming with the 
release of L1B and L2 processing pipelines.

## Storage & Required Files
The Moonlight Pipeline repository is designed to work with the PDS4 release of M3 data,
where most observational and calibration data were delivered as FITS files. All files 
required to run the pipelines are available at the PDS. 

Some information from the PDS has been compiled for ease of use and is stored in the cal folder: 
[cal_data folder](./src/m3_pipeline_tools/cal_data/). See the [cal_data README](./src/m3_pipeline_tools/cal_data/README.md) for more information.

Required files for flagging are discussed in [Comprehensive Flagging](./tutorials/tutorial3_comprehensive_flagging.ipynb).
Required files for L0 to L1B processing are discussed in [Running Pipelines](./tutorials/tutorial5_running_pipelines.ipynb).

M3 observational data can be large. L1B (radiance) and L2 (reflectance) output files are roughly 
double the size of the L0 observational data. Larger L1B and L2 products can be 3+ GB.
Necessary calibration files (BDE maps and flat fields) for each observation are small 
(<700 KB). Dark signal observations are ~15 MB for Global Mode and ~160 MB for Target.

## Dependencies
Moonlight Pipeline requires Python>=3.15.

It also depends on the following Python libraries:
* numpy
* scipy
* spiceypy
* astropy
* pandas
* pyarrow

The following dependencies are optional, but required to run the tutorial notebooks:
* matplotlib
* notebook

## OS
Moonlight Pipeline was developed and tested on an Ubuntu-based Linux distribution.

## Feedback and Contributions
We would love to receive bug reports. We are also happy to clarify points of 
confusion or consider feature requests. Please file GitHub Issues. We 
also invite contributions; if you are interested in adding work to Moonlight Pipeline, 
please email the repository maintainers and let us know what you might be 
interested in fixing, tweaking, or implementing.

## Acknowledgements
This project has been supported by NASA PDART Grant 80NSSC26K0230.
