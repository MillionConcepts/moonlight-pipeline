""" Functions for flagging bad columns in L0 or L1B data."""

import numpy as np
from typing import Literal


def neighbor_diff(
        image: np.ndarray,
        axis: int = 1,
        side: Literal["left", "right"] = "left"
):
    """
    Subtract neighboring columns for col-col offsets (good for flat evaluation
    and flagging).
    """
    shift = 1 if side == "left" else -1
    neighbor = np.roll(image, shift, axis=axis)
    diff = image - neighbor
    # np.roll wraps around. we don't want that. zero it out instead.
    edge = 0 if side == "left" else -1
    np.moveaxis(diff, axis, 0)[edge] = 0
    return diff


def flag_by_std(diff_image: np.ndarray, std_multiplier: float):
    """
    Flag all pixels in band col difference image based on median + sigma
    threshold.
    """
    std = abs(np.std(diff_image))
    median = abs(np.median(diff_image))
    flagged_pixels = abs(diff_image) > (median + std * std_multiplier)
    return flagged_pixels.astype(int)


def flag_side(
        obs_band: np.ndarray,
        std_multiplier: float,
        side: Literal["left", "right"]
):
    """ Call neighbor diff and run flagging. """
    oneway = neighbor_diff(obs_band, side=side)
    return flag_by_std(oneway, std_multiplier)


def combo_side_flags(obs_band: np.ndarray, std_multiplier: float):
    """
    Get flags for left col subtraction and right col subtraction, then combine.
    """
    # left side
    flagged_left = flag_side(obs_band, std_multiplier, "left")
    # right side
    flagged_right = flag_side(obs_band, std_multiplier, "right")
    return flagged_left + flagged_right


def flag_whole_cols(
        obs_band: np.ndarray,
        std_multiplier: float,
        flag_col_ratio: float,
        band: int,
):
    """
    Returns indices of columns for a single band that are 'bad' for a specified
    minimum percentage of the column (60-70% is a good setting I think). 'Bad'
    means offset from the left and right columns by more than the median plus a
    specified std_multiplier.

    (>60% of pixels) offset by more than median diffs + .5 std of image diffs
    """
    combo_flags = combo_side_flags(obs_band, std_multiplier)
    counts_per_col = combo_flags.sum(axis=0)
    image_len = obs_band.shape[0]
    # flag_ratios is percent of col that is flagged, edge cols only have
    # one neighbor which is why we divide by n_sides
    n_sides = np.full(obs_band.shape[1], 2)
    n_sides[[0, -1]] = 1
    flag_ratios = (counts_per_col / n_sides) / image_len
    # this warning gets really annoying. maybe dump at the end as a list
    #  of all cols that had the warning + their percentiles?
    # if np.percentile(flag_ratios, 96) > flag_col_ratio:
    #     print(
    #         f"The cutoff flag ratio given for col flagging,
    #         {flag_col_ratio}, "
    #         f"is lower than the 96th percentile pixels flagged per column, "
    #         f"{np.percentile(flag_ratios, 96)} for band {band}.")
    cutoff = max(flag_col_ratio, np.percentile(flag_ratios, 96))
    return np.where(flag_ratios > cutoff)[0], flag_ratios


def compare_group_to_neighbors(
        obs_band: np.ndarray,
        group: np.ndarray,
        std_multiplier: float,
        group_test_cols: int = 3,
):
    """
    Use columns neighboring the flagged column groups (groups are flagged
    columns within a certain number of pixels of each other) as a kind of
    'normal' threshold. A secondary check to the first flagging pass.

    Meant to resolve the following situations that arise using column diffs:
        1) sometimes a normal column neighboring a bad column is flagged as
            'bad' when it is in fact fine vs two neighboring bad cols,
            especially in target mode
        2) a column in between two 'bad' columns that is offset from its larger
            neighborhood vs a column in between two 'bad' columns that is
            actually normal
    """
    n_cols = obs_band.shape[1]

    # get selection of valid neighboring columns with neighborhood size from
    # group_test_cols
    left_neighbors = np.arange(group[0] - min(group_test_cols,
                               group[0]),
                               group[0]
                               )
    right_neighbors = np.arange(group[-1] + 1,
                                group[-1] + 1 + min(group_test_cols,
                                n_cols - 1 - group[-1])
                                )
    neighbors = np.concatenate([left_neighbors, right_neighbors])

    if neighbors.size < 2:
        # edge case
        return None, None

    neighbor_med = np.median(obs_band[:, neighbors], axis=1, keepdims=True)
    neighbor_offset = obs_band[:, neighbors] - neighbor_med
    threshold = (abs(np.median(neighbor_offset)) +
                 np.std(neighbor_offset) * std_multiplier)
    # get fraction of bad col values and neighbor "normal" values above
    # threshold
    secondary_ratios = (abs(obs_band[:, group] - neighbor_med)
                        > threshold).mean(axis=0)
    normal_ratio = (abs(neighbor_offset) > threshold).mean()

    return secondary_ratios, normal_ratio


def build_bad_col_map(
        obs_image: np.ndarray,
        std_multiplier: float = .5,
        flag_col_ratio: float = .6,
        group_col_gap: int = 0,
        group_test_cols: int = 3,
):
    """
    Build col x band flag map where flagged pixels are 'bad' across most lines
    of observation. Uses difference with neighboring cols of observation.

    Most bad columns in M3 data global mode are 1 pixel wide. In Target mode,
    they are frequently 2 pixels wide. Using column diffs for flagging means
    there are a few edge cases we need to check for below:
        1) sometimes a normal column neighboring a bad column is flagged as
            'bad' when it is in fact fine vs two neighboring bad cols,
            especially in target mode
        2) a column in between two 'bad' columns that is offset from its larger
            neighborhood vs a column in between two 'bad' columns that is
            actually normal

    Currently, we do not propagate the flagged ratio or specific flagged pixels
    in each col, but we could in the future.

    Args:
        obs_image: Obs image data, could be rdn or DN.
        std_multiplier: Multiplier with std for threshold at which to flag.
        flag_col_ratio: What ratio of pixels in a col should be flagged before
            the col is flagged.
        group_col_gap: How many cols apart to treat flagged columns as the same
            'group'. We use this to test for columns that are actually bad and
            not just the neighbor of a bad column.
        group_test_cols: How many columns to either side of a merged group of
            flagged columns to use for testing which cols in the group are
            actually bad and not just the neighbor of a bad column.
    """
    _, bands, cols = obs_image.shape
    flag_map = np.zeros((bands, cols), dtype=int)
    for band in range(bands):
        indices, ratios = flag_whole_cols(
            obs_image[:, band, :],
            std_multiplier,
            flag_col_ratio,
            band
        )
        # if nothing is flagged for this band, skip the rest of the loop
        if indices.size == 0:
            continue

        obs_band = obs_image[:, band, :]

        # divide the indices into groups of columns based on proximity to each
        # other, those within group_col_gap pixels of each other are grouped.
        groups = np.split(
            indices, np.where(np.diff(indices) > group_col_gap + 1)[0] + 1
        )
        for group in groups:
            # set all flagged cols to 1
            flag_map[band, group] = 1

            # get range of cols for each group, special case at detector edge
            group_start = 0 if group[0] <= group_col_gap else group[0]
            group_stop = cols if group[-1] >= cols - 1 - group_col_gap else (
                    group[-1] + 1)
            group_range = np.arange(group_start, group_stop)

            # get ratio of flagged lines in each col of the group using a wider
            # neighborhood of nearby columns (group_test_cols is how many
            # neighboring cols)
            secondary_ratios, normal_ratio = compare_group_to_neighbors(
                obs_band=obs_band,
                group=group_range,
                std_multiplier=std_multiplier,
                group_test_cols=group_test_cols
            )

            # set the 'actually bad' columns in the flag_map as 2 using
            # secondary_ratios. flag 2 is set at the bitmask level (we
            # currently ignore 1 flags in flag_map for the bitmask).
            if secondary_ratios is None:
                # edge case, use col in a group with the highest ratio flagged
                real_bad_cols = group[[np.nanargmax(ratios[group])]]
            else:
                # use the ratio of 'flagged' pixels within the neighboring
                # 'normal' cols as a threshold
                is_bad = secondary_ratios > (normal_ratio + 1) / 2
                real_bad_cols = group_range[is_bad]
                # there are infrequently more than 2 flashing 'bad' pixels
                # next to each other, drop the lowest secondary_ratio of
                # group >= 3 in length
                if len(real_bad_cols) >= 3:
                    bad_ratios = secondary_ratios[is_bad]
                    real_bad_cols = np.delete(real_bad_cols,
                                              np.argmin(bad_ratios))
            flag_map[band, real_bad_cols] = 2
    return flag_map