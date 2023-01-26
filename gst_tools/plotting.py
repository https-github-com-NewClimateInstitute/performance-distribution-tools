import re 
import os
import logging

import pandas as pd
import numpy as np

from shortcountrynames import to_name

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from math import log10, floor

# ======================
# Functions for plotting
# ======================

def add_selected_country(axs, xmin, xmax, selected_country, country_value, unit, uba_colours, stats_font_size=9):
    if (country_value > xmin) & (country_value < xmax):
        # Indicate it on the plot
        axs.axvline(x=country_value, ymax=0.9, linewidth=1.5, color=uba_colours['uba_dark_purple'])

        # Annotate with country name
        ymin, ymax = axs.get_ylim()
        ypos = 0.65 * ymax
        axs.annotate((to_name(selected_country) + ' ' + "\n{:.2g}".format(country_value)) + ' ' + unit,
                    xy=(country_value, ypos), xycoords='data',
                    fontsize=stats_font_size, color=uba_colours['uba_dark_purple'],
                    bbox=dict(facecolor='white', edgecolor=uba_colours['uba_dark_purple'], alpha=0.75)
                    )
    else:
        axs.annotate((to_name(selected_country) + ' ' + "\n{:.2g}".format(country_value)) + ' ' + unit,
                    xy=(.75, .65), xycoords=axs.transAxes,
                    fontsize=stats_font_size, color=uba_colours['uba_dark_purple'],
                    bbox=dict(facecolor='white', edgecolor=uba_colours['uba_dark_purple'], alpha=0.75)
                    )

def annotate_plot(axs, xlabel, title, unit, sourcename, maximum, minimum, mean, median, npts, remove_outliers, noutliers, label_font_size=12, title_font_size=14, stats_font_size=10, sig_dig=2):
    axs.annotate(("Data source:\n " + sourcename + "\n" +
                  "\nMaximum = "   + str(sig_figs(maximum, sig_dig)) +                    # {:.2f}".format(maximum) +
                  "\nMinimum = "   + str(sig_figs(minimum, sig_dig)) +                    # {:.2f}".format(minimum) +
                  "\nMean = "      + str(sig_figs(mean, sig_dig))    +                    # {:.2f}".format(mean) +
                  "\nMedian = "    + str(sig_figs(median, sig_dig))  +                    # {:.2f}".format(median) +
                  "\nCountries = " + str(npts)                                            # {:.0f}".format(npts)
                  ),
                 # Previously set position (upper right corner): xy=(1.05, 0.6)
                 xy=(1.05, 0.2), xycoords=axs.transAxes,
                 fontsize=stats_font_size, color='black',
                 bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75))

    # If some countries were removed, indicate it on the plot
    if remove_outliers:
        if noutliers == 1:
            sing_or_plur = ' outlier'
        else:
            sing_or_plur = ' outliers'
        axs.annotate(('  ' + str(noutliers) + sing_or_plur + ' not shown'),
                     # Previously set position, just below the stats box: xy=(1.05, 0.53)
                     xy=(1.02, 0.10), xycoords=axs.transAxes,
                     fontsize=stats_font_size-2, color='black')

    # Label axes and add title
    axs.set_xlabel((xlabel + ' \n(' + unit + ')'), fontsize=label_font_size)
    axs.set_ylabel('Number of countries', fontsize=label_font_size)
    axs.tick_params(axis='both', which='major', labelsize=label_font_size-1)
    axs.set_title((title + "\n"), fontweight='bold', fontsize=title_font_size)

def calculate_trends(df, num_years_trend=5):

    """
    Calculates the annual percentage change and also the rolling average over the specified number of years.
    """

    # disp average used for trend
    logging.debug('Averaging trend over ' + str(num_years_trend) + ' years.')

    # calculate annual % changes
    df_perc_change = df.pct_change(axis='columns') * 100
    new_unit = '%'

    # average over a window
    df_rolling_average = df_perc_change.rolling(window=num_years_trend, axis='columns').mean()

    return df_perc_change, df_rolling_average, new_unit

def define_plot_name(type, variable, year_of_interest, baseline_year, output_folder, file_type='png'):
    if type != 1 and type != 2 and type != 3 and type != 4:
        raise ValueError('Error. Please provide a valid plot type (either 1, 2, 3 or 4.)')
    else:
        if type == 1:
            type_text = 'Distribution in ' + str(year_of_interest)
        elif type == 2:
            type_text = 'Change since ' + str(baseline_year)
        elif type == 3:
            type_text = 'Average annual change'
        elif type == 4:
            type_text = 'Year of peaking'

        DESUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
        fname = output_folder + (type_text.lower() + ' ' + variable.lower()).translate(DESUB).replace(' ', '_') + '.' + file_type

        return type_text, fname

def eliminate_outliers(series, ktuk=3):
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

    logging.debug('-----------')
    logging.debug('Identifying and removing outliers')
    
    q75, q25 = np.nanpercentile(series, [75, 25])
    iqr = q75 - q25
    tukey_min = q25 - ktuk * iqr
    tukey_max = q75 + ktuk * iqr
    # for testing:
    # logging.debug('tukey_min is ' + str(tukey_min))
    # logging.debug('tukey_max is ' + str(tukey_max))

    # Tell the user what the outliers are:
    lower_outliers = series[series < tukey_min]
    logging.debug('lower outliers are:')
    logging.debug(lower_outliers)
    upper_outliers = series[series > tukey_max]
    logging.debug('upper outliers are: ')
    logging.debug(upper_outliers)
    logging.debug('---')

    noutliers = len(lower_outliers) + len(upper_outliers)

    # actually remove the outliers
    series = series[(series > tukey_min) & (series < tukey_max)]

    return series, noutliers

def get_plot_stats(series):
    # get some basic info about the data to use for setting styles, calculating bin sizes, and annotating plot
    #print(series)
    maximum = max(series) #OLD int(max(series))
    minimum = min(series) #OLD int(min(series))
    mean = np.mean(series)
    median = np.median(series)
    npts = len(series)
    full_range = maximum-minimum#np.ceil(maximum - minimum)

    # Use data metrics to determine which approach to use for bins.
    if (minimum < 0) & (maximum > 0):

        # If both positive and negative, bins should be symmetric around 0!
        # What's the range of data?
        

        # Freedman–Diaconis rule
        # (need to recalculate IQR)
        q75, q25 = np.nanpercentile(series, [75, 25])

        iqr = q75 - q25
        bin_width = 2 * (iqr) / (npts ** (1 / 3))
        #OLDif (int(2 * (iqr) / (npts ** (1 / 3)))) != 0:
        #OLD    bin_width = int(2 * (iqr) / (npts ** (1 / 3)))
        #OLDelse:
        #OLD    bin_width = 1

        # or the simple 'excel' rule:
        # bin_width = int(full_range / np.ceil(npts**(0.5)))

        # for nbins, need to take into account asymmetric distribution around 0
        nbins = int(np.ceil(2 * max([abs(minimum), abs(maximum)])) / bin_width)
        if not (nbins / 2).is_integer():
            nbins = nbins + 1

        # determine bin edges
        #OLD bins_calc = range(int((0 - (1 + nbins / 2) * bin_width)), int((0 + (1 + nbins / 2) * bin_width)), bin_width)
        bins_calc = np.arange((0 - (1 + nbins / 2) * bin_width), (0 + (1 + nbins / 2) * bin_width), bin_width)
        logging.debug('bins set to ' + str(bins_calc))

    else:
        #if maximum < 25:

            #bin_width = 1

            # or the simple 'excel' rule:
            #OLDbin_width = int(full_range / np.ceil(npts**(0.5)))
        bin_width = full_range / np.ceil(npts**(0.5))

            # for nbins, need to take into account asymmetric distribution around 0
        nbins = maximum #np.ceil(maximum)#np.ceil(abs(maximum))
        logging.debug('nbins is: ' + str(nbins))
        logging.debug('bin_width is: ')
        logging.debug(bin_width)
        logging.debug('Maximum is:')
        logging.debug(maximum)
            # determine bin edges
        if minimum < 0 and maximum <= 0:        
            bins_calc = np.arange(minimum, 0, bin_width)#np.ceil(nbins), bin_width)
        else:
            bins_calc = np.arange(0, nbins, bin_width)
            #bins_calc = np.arange(0, int(1 + nbins), bin_width)
        logging.debug('bins set to ' + str(bins_calc))
        logging.debug('bins_calc:')
        logging.debug(bins_calc)

        #else:
            # use inbuilt Freedman-Diaconis
            # ? TODO - modify to ensure integers? or replicate above?
         #   bins_calc = 'fd'
    return maximum, minimum, mean, median, npts, bins_calc

def get_uba_colours():

    # UBA dict from Annika Guenther
    uba_colours = {}
    uba_colours['uba_bright_green'] = [xx / 255 for xx in (94, 173, 53)]
    uba_colours['uba_dark_green'] = [xx / 255 for xx in (0, 118, 38)]
    uba_colours['uba_bright_blue'] = [xx / 255 for xx in (0, 155, 213)]
    uba_colours['uba_dark_blue'] = [xx / 255 for xx in (0, 95, 133)]
    uba_colours['uba_bright_orange'] = [xx / 255 for xx in (250, 187, 0)]
    uba_colours['uba_dark_orange'] = [xx / 255 for xx in (215, 132, 0)]
    uba_colours['uba_bright_pink'] = [xx / 255 for xx in (206, 31, 94)]
    uba_colours['uba_dark_pink'] = [xx / 255 for xx in (131, 5, 60)]
    uba_colours['uba_bright_purple'] = [xx / 255 for xx in (157, 87, 154)]
    uba_colours['uba_dark_purple'] = [xx / 255 for xx in (98, 47, 99)]
    uba_colours['uba_bright_grey'] = [xx / 255 for xx in (240, 241, 241)]
    uba_colours['uba_dark_grey'] = [xx / 255 for xx in (75, 75, 55)]

    return uba_colours

def make_histogram(df, year, unit, plot_type=0, xlabel='', variable_title='', 
                sourcename='unspecified', save_plot=True, filepath='',
                remove_outliers=True, ktuk=3,
                plot_name='', selected_country='DEU',
                dpi=600, font='Arial', label_font_size=12, title_font_size=14, stats_font_size=10,
                x_below_countries = 0.31,
                x_below_arrow = 0.15,
                x_above_countries = 0.54,
                x_above_arrow = 0.85
                ):

    """
    This is based on the make_simple_histogram function but caters to data that
    contains both positive and negative values. For the GST, it's important to be
    able to see whether or not trends etc. are positive or negative and a symmetric
    binning approach is needed.

    To calculate the bin sizes, we use a couple of conditional rules based on the data
    available, including the max and min of the data and the number of data points.
    For most plots we are expecting around 200 countries, but could also be a few regions.

    TODO - edit selected country option to deal with ISO codes or names.
    """

    # announce the plot..
    logging.debug('---------')
    logging.debug('Making plot for: ' + str(plot_name))
    logging.debug('---------')
    
    #if plot_type == 1 or plot_type == 2:
    series = df[str(year)]
    #else:
    #    series = df.iloc[:,-1]

    # Check the data - needs to not be, for example, all zeros
    if len(series.unique()) == 1:
        raise ValueError('All values in the series are the same! Exiting plotting routine for ' + str(plot_name))                

    # get the value here in case it's excluded as an outlier
    if selected_country != '':
        # get value of that country
        country_value = series[selected_country]
        print(country_value)
    # set a style
    # attempting to modify to UBA grid style but didn't work.
    #sns.set_style('darkgrid', {'xtick.color': '.95', 'grid.color': '.5'})
    sns.set(style='darkgrid')
    sns.set_palette(set_uba_palette())
    uba_colours = get_uba_colours()
    sns.set(font=font)
    
    if remove_outliers:
        series, noutliers = eliminate_outliers(series, ktuk=ktuk)
    else:
        noutliers = 0

    # STATS
    # get some basic info about the data to use for setting styles, calculating bin sizes, and annotating plot
    maximum, minimum, mean, median, npts, bins_calc = get_plot_stats(series)

    # --------------
    # MAKE THE PLOT

    # set up the figure
    fig, axs = plot(series, bins_calc, uba_colours['uba_dark_green'])
    fig.patch.set_facecolor('white')
    xmin, xmax = axs.get_xlim()

    if minimum < 0:
        make_symmetric_around_zero(axs, series, xmin, xmax, stats_font_size=stats_font_size,
                x_below_countries = x_below_countries,
                x_below_arrow = x_below_arrow,
                x_above_countries = x_above_countries,
                x_above_arrow = x_above_arrow)

    # If a country is selected for highlighting, then indicate it on the plot!
    if selected_country:
        add_selected_country(axs, xmin, xmax, selected_country, country_value, unit, uba_colours, stats_font_size=stats_font_size)

    # Annotate the plot with stats
    title = variable_title + ' in ' + str(year)

    annotate_plot(axs, xlabel, title, unit, sourcename, maximum, minimum, mean, median, npts, remove_outliers, noutliers, label_font_size=label_font_size, title_font_size=title_font_size, stats_font_size=stats_font_size)

    # save to file
    
    if save_plot:
        if selected_country:
            filepath = filepath.replace('/', '/' + to_name(selected_country) + '_')

        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close()

    return plt

def make_histogram_peaking(series, var, start_year, end_year, save_plot=False, filepath = '', dpi=450, font='Calibri', label_font_size=12, title_font_size=14, stats_font_size=10):

    """
    This function is specifically written to plot the peaking year of a variable for a range
    of countries.
    """

    uba_palette = set_uba_palette()
    sns.set_palette(uba_palette)
    sns.set(style="darkgrid", context="paper")

    # Check the data - needs to not be, for example, all zeros
    if len(series.unique()) == 1:
        raise ValueError('All values in the series are the same! Exiting plotting routine for ' + str(var))

    # set a style
    sns.set(style="darkgrid")

    # STATS
    # get some basic info about the data to use for setting styles, calculating bin sizes, and annotating plot

    maximum, minimum, mean, median, npts, bins_calc = get_plot_stats(series)

    # determine bin edges - annual!
    bin_width = 1
    bins_calc = range((start_year - 1), (end_year + 2), bin_width)

    # --------------
    # MAKE THE PLOT

    # set up the figure
    fig, axs = plt.subplots()
    fig.patch.set_facecolor('white')
    uba_colours = get_uba_colours()

    # make histogram
    N, bins, patches = axs.hist(series, bins=bins_calc,
                                edgecolor='white', linewidth=1)

    for i in range(0, len(patches)):
        patches[i].set_facecolor(uba_colours['uba_dark_purple'])
    patches[-1].set_facecolor(uba_colours['uba_bright_orange'])
    patches[-1].set_alpha(0.5)

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

    # number of countries in the last bin
    nlast = N[-1]

    # Annotate the plot with stats
    axs.annotate(("{:.0f} countries, ".format(npts) +
                  "\nof which {:.0f} have ".format(nlast) +
                  "\nnot yet reached a maximum (yellow)"),
                 xy=(0.03, 0.82), xycoords=axs.transAxes,
                 fontsize=stats_font_size, color='black',
                 bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75))

    # label axes and add title
    axs.set_xlabel('Year', fontsize=label_font_size)
    axs.set_ylabel('Number of countries', fontsize=label_font_size)
    axs.set_title(('Year when ' +  var[0].lower() + var[1:]+ ' peaked'), fontweight='bold', fontsize=title_font_size)

    # save to file
    if save_plot:
        #fname = ('basic_histogram-peaking-since-' + str(start_year) + '-' + var + '.png')
        #if not os.path.exists(filepath):
        #    os.makedirs(filepath)
        #filename = os.path.join(filepath, fname)
        plt.savefig(filepath, format='png', dpi=dpi, bbox_inches='tight')
        plt.close()

    return plt

def make_symmetric_around_zero(axs, series, xmin, xmax, stats_font_size=12,
                x_below_countries = 0.31,
                x_below_arrow = 0.15,
                x_above_countries = 0.54,
                x_above_arrow = 0.85
            ):
    # reset xmin or xmax
    if np.absolute(xmax) > np.absolute(xmin):
        plt.xlim(-xmax, xmax)
    else:
        plt.xlim(xmin, -xmin)

    # and add a line at 0
    axs.axvline(linewidth=1, color='k')

    # and annotate with the number of countries either side of the line
    # ARROWS!

    nbelow = len(series[series < 0])
    nabove = len(series[series > 0])

    if nbelow == 1:
        sing_or_plur_below = ' country'
    else:
        sing_or_plur_below = ' countries'

    if nabove == 1:
        sing_or_plur_above = ' country'
    else:
        sing_or_plur_above = ' countries'



    axs.annotate(str(nbelow) + sing_or_plur_below,
                # Previously set position of the text on the left: xy=(0.31, 1.0)
                xytext=(x_below_countries, 1.0), xycoords=axs.transAxes,
                fontsize=stats_font_size, color='black',
                # Previously set position of the arrow on the left: xy=(0.15, 1.01)
                xy=(x_below_arrow, 1.01),
                arrowprops=dict(arrowstyle="-|>", color='black'),
                bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75)
                )
    axs.annotate(str(nabove) + sing_or_plur_above,
                # Previously set position of the text on the right: xy=(0.54, 1.0)
                xytext=(x_above_countries, 1.0), xycoords=axs.transAxes,
                fontsize=stats_font_size, color='black',
                # Previously set position of the arrow on the right: xy=(0.85, 1.01)
                xy=(x_above_arrow, 1.01),
                arrowprops=dict(arrowstyle="-|>", color='black'),
                bbox=dict(facecolor='white', edgecolor='grey', alpha=0.75)
                )   

def plot(series, bins_calc, colour):
    fig, axs = plt.subplots()

    # make histogram
    sns.distplot(series,
                 kde=False,
                 bins=bins_calc,
                 hist_kws=dict(alpha=0.75),
                 color=colour)

    return fig, axs

def sig_figs(x, precision):
    """
    Rounds a number to number of significant figures
    Parameters:
    - x (float) - the number to be rounded (float)
    - precision (integer) - the number of significant figures
    Returns:
    - float
    """
    # Credits to: Matt Gosden, https://mattgosden.medium.com/rounding-to-significant-figures-in-python-2415661b94c3

    if x == 0:
        return 0
    else:
        x = float(x)
        precision = int(precision)

        return round(x, -int(floor(log10(abs(x)))) + (precision - 1))

def set_uba_palette():
    uba_palette = [
                [xx / 255 for xx in (0, 118, 38)],
                [xx / 255 for xx in (18, 93, 134)],
                [xx / 255 for xx in (98, 47, 99)],
                [xx / 255 for xx in (215, 132, 0)],
                [xx / 255 for xx in (131, 5, 60)],
                [xx / 255 for xx in (97, 185, 49)],
                [xx / 255 for xx in (0, 155, 213)],
                [xx / 255 for xx in (157, 87, 154)],
                [xx / 255 for xx in (250, 187, 0)],
                [xx / 255 for xx in (206, 31, 94)],
                [xx / 255 for xx in (240, 241, 241)],
                [xx / 255 for xx in (75, 75, 55)]
                  ]
    return uba_palette

