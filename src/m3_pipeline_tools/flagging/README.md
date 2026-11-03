# Flag Bitmask Description

_We recommend also viewing the tutorial notebooks on flagging in /tutorials. All the text
below is copied from the Comprehensive Flagging tutorial._

| Flag          | Value | Binary     | Bit position | Meaning                                           |
|---------------|-------|------------|--------------|---------------------------------------------------|
| NO_FLAG       | 0     | `00000000` |              | No flag set                                       |
| L2_DEPRECATED | 1     | `00000001` | bit 0        | Band flagged by the mission in L2 as deprecated   |
| NAN           | 2     | `00000010` | bit 1        | Pixel set to NaN for being negative at L0 level   |
| BDE           | 4     | `00000100` | bit 2        | Column spectrally interpolated because of the BDE |
| BAD_COL       | 8     | `00001000` | bit 3        | Column offset from its neighbors                  |
| NO_FLICKER    | 16    | `00010000` | bit 4        | Bad-group column, no flicker on this line         |
| FLICKER_BUMP  | 32    | `00100000` | bit 5        | Flickers brighter than neighbors                  |
| FLICKER_DROP  | 64    | `01000000` | bit 6        | Flickers darker than neighbors                    |

### Flag 1: L2 Deprecated

Between L1B (radiance) and L2 (reflectance), the mission deprecated a selection of bands. These bands were processed to
L1B but all of their values were set to -999 in L2. All pixels in these deprecated bands are flagged with `flag 1`.

* For target mode these bands were: [0, 1, 2, 3, 4, 5, 6, 7, 255].

* For global mode these bands were: [0, 1]

_This means, for global mode, a deprecated band in target mode is averaged into band 85 and not flagged._

### Flag 2: Negative L0 Values / NAN

L0 raw observational data (DN) was stored as a 12 bit unsigned integer on the spacecraft but saved as a 16-bit signed
integer in the PDS.
This means the maximum value observed in L0 data is 4095. Such high values are typically only observed in target mode,
which was not as downsampled as global mode, where the largest values are around 3000.

There appears to have been a rollover effect, where, when values surpassed 4095, they became 0 in target mode and 0, -1,
or -2 in global mode. The dark signal background of normal observational data not experiencing this rollover effect is
typically at least 300 DN. Therefore we set 0 and negative values in the L0 observational data as NAN in the pipeline
and flag it with `flag 2`.

This rollover effect was covered for the dark signal observations with the flag 1.5 in the mission-produced BDE maps.

### Flag 4: Bad Detector Elements (BDE)

The original mission files have flag backplanes they call bad detector element maps (BDE) that are generated from dark
signal observations. These files have the same orientation and number of bands & samples as the L0 data, but not the L1B
data. They are provided in the USGS PDS as files ending in '_bde.fits'. These BDE maps are in detector POV, where the
x-axis is samples (cross-track) and y-axis bands / channels.

__As part of calibration, flagged pixels in the BDE maps were linearly spectrally interpolated. This means values at the
interpolated pixels are not true observational data.__

The mission-derived BDE maps have the same number of bands and samples / columns as the L0 data. To flag L1B data as
spectrally interpolated by the mission, we use the orientation information from the label files to reverse the lines
and/or samples, if indicated.
We also trim the bands and samples to match the L1B data.

`Flag 4` is applied for all lines of a pixel flagged in the BDE map. This means every `flag 4` pixel in a band was
interpolated across with the closest unflagged bands, and is not a real measurement.

### Flag 8: Bad Column Flag

For a variety of reasons, "bad" columns of data persist in L1B products. The causes are numerous:

* Poor flat field, especially when the flat field was derived from another observation.
* Dark signal observation not temporally close
* Dark signal observation and the 'real' observation differ significantly in temperature.
* A flashing, bright, or very dark pixel is not flagged in the BDE map. Either because it is just below the threshold
  for flagging or
  because it didn't flash during the relatively short dark signal observation used to make the BDE map.

`Flag 8` is for identifying the most egregious columns in each band of an observation. Columns that are flagged with
this flag are flagged for _all lines_ of the observation because the column is shown to have a persistent offset from
its neighboring columns for most of the observation. In the L0 to L1B pipeline, this flag is only set after flat
fielding.

### Flags 16, 32, 64: Flicker Flags

The previous two flags, for the BDE maps, `flag 4`, and for bad columns, `flag 8`, are applied to all lines of a column.
What we refer to as the 'flicker flags' are for an electronic background effect that varies across the lines of an
observation.

We observed two groups of columns / samples in the detector that 'flickered' darker or brighter than the rest of the
background periodically during an observation. These groups are evenly spaced and always the same columns. They also
appear to flash at the same time and magnitude across all bands.

There are three flags in the flicker flag group:

* `Flag 16`: Columns known to flicker but with no apparent offset at a given line.
* `Flag 32`: Columns known to flicker that are brighter than their neighboring columns for a given line.
* `Flag 64`: Columns known to flicker that are darker than from their neighboring columns for a given line.

__Why set a flag for known flickering columns when there is no flickering detected?__

We set `Flag 16` (shown in the upper right image above) because flicker detection is not infallible. Especially in warm
observations or sections of an observation with a wide variety of terrain across-track, flickering groups may be missed.

Additionally, at the L1B level, flickering groups have already been modified by other pipeline steps, like flat
fielding. Flat fielding
the flickering columns isn't really the correct calibration behaviour because flicker is 1) additive to the background
signal and 2) temporally variable. 