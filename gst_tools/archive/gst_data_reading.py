
# Written by Louise Jeffery
# October, 2018

# Copyright License
# Creative Commons?

# Purpose:
# read data


# =========================
# Load modules etc.

import re
import logging

import pandas as pd


# =========================
# Read or load data


#current_PRIMAPhist_filename = 'PRIMAP-hist_no_extrapolation_v1.1_06-Mar-2017.csv'
current_PRIMAPhist_filename = 'PRIMAPHIST20-data-M0EL-KGHG.csv'
current_socioeconomic_data_filename = ''
current_population_data_filename = 'UN-population-data-2017.csv'
current_NDC_coverage_data_filename = 'NDCCoverage_InfoPerSectorGasCombiAndCountry.csv'


def read_historic_emissions_data(variable, sector):

    """
    This function will read in the PRIMAP-hist dataset from the correctly formatted file.
    From that data it will extract the selected variable and unit to pass back to the
    calculation functions."
    The data should all be in CO2e, but the exact unit can be requested, e.g. tCO2e
    """

    logging.info('')
    logging.info('===========================')
    logging.info('Reading in historic data')
    logging.info('===========================')
    logging.info('')

    # locate the historic data directory
    data_folder = 'data/'
    file_to_read = (data_folder + data_files_dict['historic_data']['emissions_data'])
    logging.info('reading files from: ' + file_to_read)

    # basic read-in of data
    hist_data = pd.read_csv(file_to_read)

    # if years labelled as YNNNN, switch to NNNN
    for col in hist_data.columns:
        if col.startswith('Y'):
            hist_data = hist_data.rename(columns={col: col[1:]})

    # get specific variable
    years = [y for y in hist_data[hist_data.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
    # years_int = list(map(int, years))

    hist_data = hist_data.set_index('ISO')

    # identify the units in the source data
    units = hist_data.loc[(hist_data['entity'] == variable) &
                          (hist_data['sectorCode'] == sector),
                          ['unit']]
    cur_unit = units['unit'].unique()

    # extract the requested data
    hist_emis_data = hist_data.loc[(hist_data['entity'] == variable) &
                                   (hist_data['sectorCode'] == sector),
                                   years]

    # TODO - could improve this to preserve more metadata

    # convert units (to standard Mt CO2e)
    if cur_unit == 'GgCO2eq':
        new_unit = 'MtCO2eq'
        hist_emis_data /= 1000
    else:
        new_unit = cur_unit
        logging.warning('Conversion not defined. Emissions data units remain as ' + new_unit)

    logging.info('...')
    logging.info('emissions data reading complete')
    logging.info('===========================')
    logging.info('')

    return hist_emis_data, new_unit


def read_historic_population_data():

    logging.info('')
    logging.info('===========================')
    logging.info('Reading in population data')
    logging.info('===========================')
    logging.info('')

    # locate the historic data directory
    data_folder = 'data/'
    file_to_read = (data_folder + current_population_data_filename)
    logging.info('reading files from: ' + file_to_read)

    # basic read-in of data
    pop_data = pd.read_csv(file_to_read)

    columns_available = pop_data.columns
    logging.info('Columns in historic UN population data are: ')
    logging.info(columns_available)

    pop_years = [y for y in pop_data[pop_data.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
    pop_data = pop_data.set_index('country')
    pop_unit = pop_data['unit'].unique()
    pop_data = pop_data[pop_years]

    if pop_unit == 'ThousandPers':
        logging.info('Converting population from ThousandPers to Pers')
        pop_unit = 'Pers'
        pop_data *= 1000
    else:
        logging.info('keeping population data as ' + pop_unit)

    logging.info('...')
    logging.info('population data reading complete')
    logging.info('===========================')
    logging.info('')

    return pop_data, pop_unit


def read_NDC_coverage_data(optimistic):

    # optimistic is Boolean to determine if 'no Information' should be interpreted as included or excluded in (I)NDC

    """
    NDC coverage data was prepared by Annika Gunther based on reading of all NDCs. The original data 
    format lists all countries in the first column and has a separate column for each possible gas / sector pair. 
    Each data point is a description of if / how the gas/sector is included in the NDC, with possible entries being: 
    * Covered           - NDC covers the combination
    * NotCovered        - not covered by NDC
    * NoInformation     - NDC does not give sufficient information
    * NoNDC_NoINDC      - country does not have an (i)NDC
    * See EU            - countries' emissions covered by the EU
    * NonUNFCCC         - country is not a Party to the UNFCCC

    This data prep function does the following actions in order to prep the data for making a matrix overview
    of the sector / gas coverage of NDCs.
    * rearranges the data to make a multi-index matrix for sectors and gases
    * removes all nonUNFCCC data
    * removes all individual EU countries
    * No NDC -> Not covered
    * Creates two matrices; one where 'NoInformation' is considered included, and one where it is assumed not included.
    * In these matrices; the information is converted to a binary True / False summary for easier processing

    The processed data can then be plotted using #TODO
    """

    logging.info('')
    logging.info('===========================')
    logging.info('Reading in NDC coverage data')
    logging.info('===========================')
    logging.info('')

    # locate the historic data directory
    data_folder = 'data/'
    file_to_read = (data_folder + current_NDC_coverage_data_filename)
    logging.info('reading files from: ' + file_to_read)

    # basic read-in of data
    ndc_cov_data = pd.read_csv(file_to_read)

    # make the countries an index
    ndc_cov_data = ndc_cov_data.set_index('ISO3')

    # trasnpose tp make the countries columns and then make the gas/sector index a column
    ndc_cov_data = ndc_cov_data.T
    ndc_cov_data = ndc_cov_data.reset_index()

    # Split sector / gas header into two columns
    temp = ndc_cov_data["index"].str.split(" ", n=1, expand=True)
    ndc_cov_data["entity"] = temp[0]
    ndc_cov_data["sector"] = temp[1]
    ndc_cov_data.drop(columns=["index"], inplace=True)

    # make the entity and sector columns an index
#    ndc_cov_data = ndc_cov_data.set_index('entity', 'sector')
#    ndc_cov_data = ndc_cov_data.drop('index')

    # drop all non-UNFCCC states
    # TODO - get rid of 'not covered' and 'NonUNFCCC' columns
    cols = ndc_cov_data.columns


    if optimistic == True:
        # 1. assume 'no information' means included
        # TODO - True false matrix
        ndc_coverage = nn

    else:

        # 2. assume 'no information' means not included
        ndc_coverage = nn

    logging.info('...')
    logging.info('NDC coverage data reading complete')
    logging.info('===========================')
    logging.info('')

    return ndc_coverage

