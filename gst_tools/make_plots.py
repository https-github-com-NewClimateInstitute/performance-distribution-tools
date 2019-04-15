# Project and Title

# Author(s): Louise Jeffery
# Contact: louise.jeffery@pik-potsdam.de; mlouise@posteo.de 
# Date: **MONTH, YYYY**

# Copyright License:
# 

# Purpose:
# 

# =====================================================

import re, sys, os

import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from shortcountrynames import to_name

# ======================


# def make_simple_histogram(df, variable, unit):
#
#     # set a style
#     sns.set(style="darkgrid")  #, rc={"axes.facecolor": (0, 0, 0, 0)})
#
#     fig, axs = plt.subplots()
#
#     # Make default histogram
#     sns.distplot(df, kde=False)
#                  #rug=True)
#                  #rug_kws={"color": "rebeccapurple", "alpha": 0.5, "linewidth": 0.5, "height": 0.1})
#
#     # set xlim - otherwise too squished to read...
#     # plt.xlim(left=0)
#
#     # save to file
#     outputdir = 'output/plots/'
#     plt.savefig((outputdir + 'basic_histogram_' + label + '.pdf'),
#                 format='pdf')
#     plt.close()


# main plotting function used throughout - flexibility given so that it can cope with a range of different input!

def make_histogram(df, var, unit_, remove_outliers=False, save_plot=False, kTuk=3, selected_country=''):

    """
    This is based on the make_simple_histogram function but caters to data that
    contains both positive and negative values. For the GST, it's important to be
    able to see whether or not trends etc. are positive or negative and a symmetric
    binning approach is needed.

    To calculate the bin sizes, we use a couple of conditional rules based on the data
    available, including the max and min of the data and the number of data points.
    For most plots we are expecting around 200 countries, but could also be a few regions.

    TODO - the 'outlier' calculation is helpful to see some data better BUT need to be careful.
    Proposed solution is to make BOTH plots so that it's clear to the user when data has been
    removed.

    TODO - 'df' is actually a series -> better name?

    TODO - edit selected country option to deal with ISO codes or names.
    """

    # Check the data - needs to not be, for example, all zeros
    if len(df.unique()) == 1:
        print('---------')
        print('All values in the series are the same! Exiting plotting routine for ' + str(var))
        print('---------')
        return

    # get the value here in case it's excluded as an outlier
    if selected_country:
        # get value of that country
        country_value = df[selected_country]

    # set a style
    sns.set(style="darkgrid")

    if remove_outliers:
        # Outliers - in some cases, the date contains extreme outliers. These make for an unreadable
        # plot and in most cases arise from exceptional circumstances. These outliers are therefore removed
        # from the plots and the removal signalled to the user.
        # Example: Equatorial Guinea's emissions rose dramatically in the mid-90s due to the discovery of
        # oil. So much so, that the current emissions relative to 1990 are over 6000% higher. Including these
        # emissions in the plots would render a useless graph so we remove this country from the overview.

        # Use Tukey's fences and the interquartile range to set the bounds of the data
        # https://en.wikipedia.org/wiki/Outlier
        # For reference: kTUk default is set to 3 (above)
        # k = 1.5 -> outlier; k = 3 -> far out
        # TODO - get full and proper reference for this!!!

        print('-----------')
        print('Identifying and removing outliers')

        # calculate limits
        q75, q25 = np.percentile(df, [75, 25])
        iqr = q75 - q25
        tukey_min = q25 - kTuk * iqr
        tukey_max = q75 + kTuk * iqr
        # for testing:
        # print('tukey_min is ' + str(tukey_min))
        # print('tukey_max is ' + str(tukey_max))

        # Tell the user what the outliers are:
        lower_outliers = df[df < tukey_min]
        print('lower outliers are:')
        print(lower_outliers)
        upper_outliers = df[df > tukey_max]
        print('upper outliers are: ')
        print(upper_outliers)
        print('---')

        noutliers = len(lower_outliers) + len(upper_outliers)

        # actually remove the outliers
        df = df[(df > tukey_min) & (df < tukey_max)]

    # STATS
    # get some basic info about the data to use for setting styles, calculating bin sizes, and annotating plot
    maximum = max(df)
    minimum = min(df)
    mean = np.mean(df)
    median = np.median(df)
    npts = len(df)

    # Use data metrics to determine which approach to use for bins.
    if (minimum < 0) & (maximum > 0):

        # If both positive and negative, bins should be symmetric around 0!
        # What's the range of data?
        full_range = np.ceil(maximum - minimum)

        # Freedman–Diaconis rule
        # (need to recalculate IQR)
        q75, q25 = np.percentile(df, [75, 25])
        iqr = q75 - q25
        bin_width = int(2 * (iqr) / (npts ** (1 / 3)))

        # or the simple 'excel' rule:
        # bin_width = int(full_range / np.ceil(npts**(0.5)))

        # for nbins, need to take into account asymmetric distribution around 0
        nbins = int(np.ceil(2 * max([abs(minimum), abs(maximum)])) / bin_width)
        if not (nbins / 2).is_integer():
            nbins = nbins + 1

        # determine bin edges
        bins_calc = range(int((0 - (1 + nbins / 2) * bin_width)), int((0 + (1 + nbins / 2) * bin_width)), bin_width)
        print('bins set to ' + str(bins_calc))

    else:
        # use inbuilt Freedman-Diaconis
        # ? TODO - modify to ensure integers? or replicate above?
        bins_calc = 'fd'

    # --------------
    # MAKE THE PLOT

    # set up the figure
    fig, axs = plt.subplots()

    # make histogram
    sns.distplot(df,
                 kde=False,
                 bins=bins_calc,
                 color='mediumseagreen',
                 rug=False,
                 rug_kws={"color": "rebeccapurple", "alpha": 0.7, "linewidth": 0.4, "height": 0.03})

    # get xlims
    xmin, xmax = axs.get_xlim()

    # Dynamically set x axis range to make symmetric abut 0
    if minimum < 0:

        # reset xmin or xmax
        if np.absolute(xmax) > np.absolute(xmin):
            plt.xlim(-xmax, xmax)
        else:
            plt.xlim(xmin, -xmin)

        # and add a line at 0
        axs.axvline(linewidth=1, color='k')

        # and annotate with the number of countries either side of the line
        nbelow = len(df[df < 0])
        nabove = len(df[df > 0])

        axs.annotate(str(nbelow),
                     xytext=(0.42, 0.95), xycoords=axs.transAxes,
                     fontsize=9, color='black',
                     xy=(0.3, 0.96),
                     arrowprops=dict(arrowstyle="-|>", color='black'),
                     bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75)
                     )
        axs.annotate(str(nabove),
                     xytext=(0.55, 0.95), xycoords=axs.transAxes,
                     fontsize=9, color='black',
                     xy=(0.7, 0.96),
                     arrowprops=dict(arrowstyle="-|>", color='black'),
                     bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75)
                     )

    # If a country is selected for highlighting, then indicate it on the plot!
    if selected_country:

        # get value of that country
        # country_value = df[selected_country]

        if (country_value > xmin) & (country_value < xmax):
            # indicate it on the plot
            axs.axvline(x=country_value, ymax=0.9, linewidth=1.5, color='rebeccapurple')

            # annotate with country name
            ymin, ymax = axs.get_ylim()
            ypos = 0.65 * ymax
            axs.annotate((to_name(selected_country) + ' ' + "\n{:.2g}".format(country_value)) + unit_,
                         xy=(country_value, ypos), xycoords='data',
                         fontsize=9, color='rebeccapurple',
                         bbox=dict(facecolor='white', edgecolor='rebeccapurple', alpha=0.75)
                         )

        else:
            axs.annotate((to_name(selected_country) + ' ' + "\n{:.2g}".format(country_value)) + unit_,
                         xy=(.75, .65), xycoords=axs.transAxes,
                         fontsize=9, color='rebeccapurple',
                         bbox=dict(facecolor='white', edgecolor='rebeccapurple', alpha=0.75)
                         )

    # Annotate the plot with stats
    axs.annotate((" max = {:.2f}".format(maximum) +
                  "\n min = {:.2f}".format(minimum) +
                  "\n mean = {:.2f}".format(mean) +
                  "\n median = {:.2f}".format(median) +
                  "\n n = {:.0f}".format(npts)
                  ),
                 xy=(.75, 0.75), xycoords=axs.transAxes,
                 fontsize=9, color='black',
                 bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75))

    # if some countries were removed, indicate on the plot
    if remove_outliers:
        axs.annotate((str(noutliers) + ' outliers not shown.'),
                     xy=(0.75, 1.01), xycoords=axs.transAxes,
                     fontsize=8, color='black')

    # label axes and add title
    axs.set_xlabel((var + ' (' + unit_ + ')'), fontsize=10)
    axs.set_ylabel('Number of countries', fontsize=10)
    axs.set_title((var + ' in ' + df.name), fontweight='bold')

    # save to file
    if save_plot:
        filepath = os.path.join('output', 'plots')
        if selected_country:
            fname = ('basic_histogram-' + var + '-' + to_name(selected_country) + '.pdf')
        else:
            fname = ('basic_histogram-' + var + '.pdf')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = os.path.join(filepath, fname)
        plt.savefig(filename, format='pdf', bbox_inches='tight')
        plt.close()

    # show the plot
    plt.show()


def make_histogram_peaking(df, var, unit_, start_year, end_year, save_plot=False):
    """
    This is based on the make_simple_histogram function but caters to data that
    contains both positive and negative values. For the GST, it's important to be
    able to see whether or not trends etc. are positive or negative and a symmetric
    binning approach is needed.

    To calculate the bin sizes, we use a couple of conditional rules based on the data
    available, including the max and min of the data and the number of data points.
    For most plots we are expecting around 200 countries, but could also be a few regions.

    TODO - 'df' is actually a series -> better name?
    """

    # Check the data - needs to not be, for example, all zeros
    if len(df.unique()) == 1:
        print('---------')
        print('All values in the series are the same! Exiting plotting routine for ' + str(var))
        print('---------')
        return

    # set a style
    sns.set(style="darkgrid")

    # STATS
    # get some basic info about the data to use for setting styles, calculating bin sizes, and annotating plot
    maximum = int(max(df))
    minimum = int(min(df))
    mean = np.mean(df)
    median = np.median(df)
    npts = len(df)

    # determine bin edges - annual!
    bin_width = 1
    bins_calc = range((start_year - 1), (end_year + 2), bin_width)

    # --------------
    # MAKE THE PLOT

    # set up the figure
    fig, axs = plt.subplots()

    # make histogram
    sns.distplot(df, kde=False,
                 bins=bins_calc,
                 rug=False,  # with bins fixed at annual, the rugs aren't additional
                 color='mediumseagreen',
                 rug_kws={"color": "rebeccapurple", "alpha": 0.7, "linewidth": 0.4, "height": 0.03})

    # Dynamically set x axis range to make symmetric abut 0
    if minimum < 0:
        # get and reset xmin or xmax
        xmin, xmax = axs.get_xlim()
        if np.absolute(xmax) > np.absolute(xmin):
            plt.xlim(-xmax, xmax)
        else:
            plt.xlim(xmin, -xmin)

        # and add a line at 0
        axs.axvline(linewidth=1, color='k')

    # Annotate the plot with stats
    axs.annotate((" max = {:.0f}".format(maximum) +
                  "\n min = {:.0f}".format(minimum) +
                  "\n mean = {:.2f}".format(mean) +
                  "\n median = {:.0f}".format(median)),
                 xy=(1.03, 0.75), xycoords=axs.transAxes,
                 fontsize=9, color='black',
                 bbox=dict(facecolor='white', alpha=0.75))

    # label axes and add title
    axs.set_xlabel('Year')
    axs.set_ylabel('Number of countries')
    axs.set_title(('Peaking year of ' + var + ' since ' + str(start_year)), fontweight='bold')

    # save to file
    if save_plot:
        filepath = os.path.join('output', 'plots')
        fname = ('basic_histogram-' + var + '-peaking-since' + str(start_year) + '.pdf')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = os.path.join(filepath, fname)
        plt.savefig(filename, format='pdf')
        plt.close()

    # show the plot
    plt.show()


def plot_facet_grid_countries(df, variable, value, main_title='', plot_name='', save_plot=False):
    # First, get some idea of the data so that it's easier to make clean plots
    ranges = df.max(axis=1) - df.min(axis=1)
    check = (ranges.max() - ranges.min()) / ranges.min()
    if abs(check) < 8:
        yshare = True
    else:
        yshare = False

    # set up the df for plotting
    year_cols = df.columns
    dftomelt = df.reset_index()
    dftomelt['country'] = dftomelt['country'].apply(to_name)
    dfmelt = pd.melt(dftomelt, id_vars=['country'],
                     value_vars=year_cols, var_name=variable, value_name=value)

    # set up the grid
    grid = sns.FacetGrid(dfmelt, col='country', palette="tab20c", sharey=yshare,
                         col_wrap=4, aspect=1)

    # make the actual plots
    grid.map(sns.lineplot, variable, value, color="rebeccapurple")

    # Give subplots nice titles
    grid.set_titles(col_template='{col_name}')

    # tidy up a bit
    for ax in grid.axes.flat:
        ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(4, prune="both"))
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(4, prune="both"))
        ax.axhline(0, color='k')
    if yshare:
        grid.fig.subplots_adjust(hspace=.15, wspace=.1, top=.95)
    else:
        grid.fig.subplots_adjust(hspace=.15, wspace=.25, top=.95)

    # give the whole plot a title
    grid.fig.suptitle(main_title, fontweight='bold', fontsize=15)

    if save_plot:
        filepath = os.path.join('output', 'plots')
        # grid.map(horiz_zero_line)
        fname = ('facetgrid-' + plot_name + '-' + value + '.pdf')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = os.path.join(filepath, fname)
        plt.savefig(filename, format='pdf')
        plt.close()
