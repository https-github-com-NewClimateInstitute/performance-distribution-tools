import re 
import os
import logging
import chardet

import pandas as pd
import numpy as np
from shortcountrynames import to_name

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# Functions for data loading and manipulation
# ======================

def calculate_diff_since_yearX(df_abs, yearX):

    """
    Calculates in absolute and relative terms the difference between data in all years compared to the specified year.
    For example, % difference relative to 1990 in all years.
    """

    logging.debug('Calculating difference compared to ' + yearX)

    # first, check that the desired year is in the data!
    if yearX not in df_abs.columns:
        raise ValueError('The year you have selected for relative calculations ('
              + str(yearX) + ') is not available, please try again.')

    # calculate all columns relative to the chosen year, first in absolute terms, then %
    df_abs_diff = df_abs.subtract(df_abs[yearX], axis='index')
    # print(df_abs_diff)
    df_perc_diff = 100 * df_abs_diff.divide(df_abs[yearX], axis='index')
    # print(df_perc_diff)

    return df_abs_diff, df_perc_diff

def calculate_energy_use(renamed_bp):
    # Primary energy consumption
    energy_use = renamed_bp['primary_ej']
    new_df = renamed_bp.copy()

    new_df['energy_use_ej'] = energy_use

    logging.debug('Added primary energy consumption. Unit: Exajoules')
    return new_df

def calculate_ff_share(renamed_bp):
    total_consumption = renamed_bp['primary_ej']
    ff_cons = renamed_bp['coalcons_ej'] + renamed_bp['gascons_ej'] + renamed_bp['oilcons_ej']
    
    new_df = renamed_bp.copy()
    new_df['ff_cons_share_%'] = (ff_cons/total_consumption)*100

    logging.debug('Added share of fossil fuel energy consumed. Unit: %')
    return new_df

def calculate_ren_elec_share(renamed_bp):
    # Share of renewable energy in electricy
    #renewables = renamed_bp['electbyfuel_ren_power'] + renamed_bp['electbyfuel_hydro']

    #renewables = renamed_bp['ren_power_twh'] + renamed_bp['hydro_twh']
    


    #total = renamed_bp['electbyfuel_total']
    
    #total = renamed_bp['elect_twh']

    #share = (renewables/total)*100

    #share = (renamed_bp['ren_power_twh'] + renamed_bp['hydro_twh']) / renamed_bp['elect_twh'] *100

    new_df = renamed_bp.copy()
    new_df['ren_elec_share'] = (new_df['ren_power_twh'] + new_df['hydro_twh']) / new_df['elect_twh'] *100

    logging.debug('Added share of renewables in electricity generated. Unit: %')
    #new_df.to_csv('proc-data/division_test.csv', index=False)
    return new_df

def change_first_year(df, new_start_year):

    """
    Reduces a dataframe to start in a later, specified year than the original data.
    Can be useful for reducing the size of the data to be handled or for performing analysis over a reduced timeframe.
    """

    # reduce the number of years (keeps things lighter and faster)
    year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
    other_cols = list(set(df.columns) - set(year_cols))

    # check the current start year
    if not year_cols:
        raise ValueError("no years left")
        
    cur_start_year = min(year_cols)
    last_year = max(year_cols)

    if int(cur_start_year) > int(new_start_year):

        new_start_year = cur_start_year

    else:
        # set other columns as index
        if other_cols:
            df = df.set_index(other_cols)

        # identify which years to keep
        years_to_keep = np.arange(int(new_start_year), (int(last_year) + 1), 1)
        years_keep_str = list(map(str, years_to_keep))

        # remove extra years
        df = df.loc[:, years_keep_str]

        # return other columns
        if other_cols:
            df = df.reset_index()

        # TODO - modify so that the output index is the same as the input!

    # check formatting
    df = check_column_order(df)

    # tell the user what happened
    logging.debug('First year of data available is now ' + str(new_start_year))
    logging.debug('Last year of data available is ' + str(last_year))

    return df

def check_column_order(df):

    """
    For ease of processing and plotting, it's best to have the columns with metadata all together and then the
    years all in the correct order. As this is a common check / priority, this is a general function for it.
    """

    # get all column names
    df_columns = df.columns

    # get the year columns
    year_columns = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]

    # if there aren't year columns, check for other numeric columns
    if year_columns:
        # make sure the years are sorted (makes them an integer in case they aren't already)
        ordered_year_columns = sorted(year_columns, key=int)

    else:
        year_columns = [y for y in df[df.columns] if isinstance(y, (int, float))]
        ordered_year_columns = sorted(year_columns)

    # get the columns that are not years
    metadata_cols = list(set(df_columns) - set(year_columns))

    # set the new column order with metadata first in alphabetical order
    new_column_order = sorted(metadata_cols) + ordered_year_columns

    # then create a new dataframe with that order
    reordered_df = df[new_column_order]

    return reordered_df

def convert_from_Gg_to_Mt(proc_data):
    conv_df = proc_data.copy()
    org_unit = proc_data['unit'].unique()[0]

    gas_unit = re.search('Gg (.+?) / yr', org_unit).group(1)

    desired_unit = 'Mt' + gas_unit

    conversion_factor = 1/1000

    logging.debug('*******************')
    logging.debug('Converting unit from "' + org_unit + '" to "' + desired_unit + 
          '" using a conversion factor of ' + str(conversion_factor))
    logging.debug('*******************')

    conv_df['unit'] = desired_unit
    
    # Convert the data
    conv_df, other_cols = set_non_year_cols_as_index(conv_df)
    conv_df = conv_df * conversion_factor
    conv_df = conv_df.reset_index()

    return conv_df

def convert_from_t_to_Mt(proc_data):
    conv_df = proc_data.copy()
    org_unit = proc_data['unit'].unique()[0]

    #SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
    desired_unit = 'MtCO2eq'#.translate(SUB)

    conversion_factor = 1/1000000

    logging.debug('*******************')
    logging.debug('Converting unit from "' + org_unit + '" to "' + desired_unit + 
          '" using a conversion factor of ' + str(conversion_factor))
    logging.debug('*******************')

    conv_df['unit'] = desired_unit
    
    # Convert the data
    conv_df, other_cols = set_non_year_cols_as_index(conv_df)
    conv_df = conv_df * conversion_factor
    conv_df = conv_df.reset_index()

    return conv_df    

def convert_norm(normalised_dset, data, per_capita_or_per_usd):
    conv_df = normalised_dset.copy()
    org_unit = normalised_dset['unit'].unique()[0]

    if data != 1 and data != 2 and data != 3 and data != 4 and data != 5:
        raise ValueError('Error. Please provide a valid data type (either 1, 2, 3 or 4.)')
    else:
        if data == 1 or data == 2:
            gas_unit = re.search('Mt(\w+)', org_unit).group(1)

            desired_unit = 't' + gas_unit + ' ' + per_capita_or_per_usd

            conversion_factor = 1000000
            if per_capita_or_per_usd == 'per USD':
                conversion_factor = 1000000 *(10**6)
                desired_unit = 'g' + gas_unit + ' ' + per_capita_or_per_usd
        elif data == 3:
            desired_unit = 'J' + ' ' + per_capita_or_per_usd
            conversion_factor = 10**9
            if per_capita_or_per_usd == 'per USD':
                conversion_factor = 10**12
                desired_unit = 'mJ' + ' ' + per_capita_or_per_usd
        elif data == 4 or data == 5:
            desired_unit = 't' + 'CO2eq ' + per_capita_or_per_usd
            conversion_factor = 1000000

            if per_capita_or_per_usd == 'per USD':
                conversion_factor = 1000000 *(10**6)
                desired_unit = 'g' + 'CO2eq ' + per_capita_or_per_usd

        logging.debug('*******************')
        logging.debug('Converting unit from "' + org_unit + '" to "' + desired_unit + 
            '" using a conversion factor of ' + str(conversion_factor))
        logging.debug('*******************')

        conv_df['unit'] = desired_unit
        
        # Convert the data
        conv_df, other_cols = set_non_year_cols_as_index(conv_df)
        conv_df = conv_df * conversion_factor
        conv_df = conv_df.reset_index()

        return conv_df

def define_bp_proc_fname(proc_data):
    source = 'bp_stat_rev_world_energy_2022'
    variable = proc_data['variable'][0]

    proc_fname = source + '_' + variable.replace(' ', '_').lower() + '.csv'

    return proc_fname

def define_gas_name(gas, dataset):
    gas_out = ''
    if gas == 'GHG':
        if dataset == 1 or dataset == 2:
            # Primap
            gas_out = 'KYOTOGHG (AR4GWP100)'
        elif dataset == 4 or dataset == 5:
            # IPCC
            gas_out = 'GHG'
    elif gas == 'CO2':
        gas_out = 'CO2'
    elif gas == 'CH4':
        gas_out = 'CH4'
    elif gas == 'N2O':
        gas_out = 'N2O'
    elif gas == 'F-gases':
        if dataset == 1 or dataset == 2:
            gas_out = 'FGASES (AR4GWP100)'
        elif dataset == 4 or dataset == 5:
            gas_out = 'Fgas'
    elif gas == 'HFCs':
        if dataset == 1 or dataset == 2:
            gas_out = 'HFCS (AR4GWP100)'
        elif dataset == 4 or dataset == 5:
            raise ValueError('The gas selected is not available in this dataset.')
    elif gas == 'PFCs':
        if dataset == 1 or dataset == 2:
            gas_out = 'PFCS (AR4GWP100)'
        elif dataset == 4 or dataset == 5:
            raise ValueError('The gas selected is not available in this dataset.')
    elif gas == 'SF6':
        if dataset == 1 or dataset == 2:
            gas_out = 'SF6'
        elif dataset == 4 or dataset == 5:
            raise ValueError('The gas selected is not available in this dataset.')
    elif gas == 'NF3':
        if dataset == 1 or dataset == 2:
            gas_out = 'NF3'
        elif dataset == 4 or dataset == 5:
            raise ValueError('The gas selected is not available in this dataset.')
    return gas_out

def define_ipcc_proc_fname(proc_data, indirect=False):
    source = 'ipcc_ar6_wg3'    
    variable = proc_data['variable'][0]

    if indirect:
        source = source + '_with_indirect'
        
    proc_fname = source + '_' + variable.replace(' ', '_').lower() + '.csv'

    return proc_fname

def define_ipcc_variable_name(sector_or_subsector, gas, ipcc_subsectors='gst_tools/ipcc_subsectors.csv'):
    subsectors = pd.read_csv(ipcc_subsectors)
    subsectors.set_index('subsector', inplace=True)

    gas_name = gas

    if sector_or_subsector not in list(subsectors.index):
        raise ValueError('The sector or subsector selected does not exist in the database. Please check if it was entered correctly.')
    else:
        if sector_or_subsector.split(' [', 1)[0] in ['Oil and gas fugitive emissions', 'Other (energy systems)', 'Other (industry)',
                    'Other (transport)', 'Coal mining fugitive emissions', 'Non-CO2 (all buildings)']:
            
            variable_name = subsectors.loc[sector_or_subsector]['1'] + ' ' + gas_name + ' ' +  subsectors.loc[sector_or_subsector]['3'] + ' ' +  subsectors.loc[sector_or_subsector]['4'] + ' ' +  subsectors.loc[sector_or_subsector]['5']
        
        elif sector_or_subsector in ['AFOLU', 'Buildings', 'Energy systems', 'Industry', 'Transport',
                                        'AFOLU (indirect)', 'Buildings (indirect)', 
                                        'Energy systems (indirect)', 'Industry (indirect)', 'Transport (indirect)']:
            variable_name = gas_name + ' ' + subsectors.loc[sector_or_subsector]['3'] + ' ' +  subsectors.loc[sector_or_subsector]['4'] + ' ' +  subsectors.loc[sector_or_subsector]['5']
        elif sector_or_subsector == "Total (excl. LULUCF)":
            variable_name = subsectors.loc[sector_or_subsector]['1'] + ' ' + gas_name + ' ' + subsectors.loc[sector_or_subsector]['3'] + ' ' +  subsectors.loc[sector_or_subsector]['5']
        else:
            variable_name = gas_name + ' ' +  subsectors.loc[sector_or_subsector]['3'] + ' ' +  subsectors.loc[sector_or_subsector]['4'] + ' ' +  subsectors.loc[sector_or_subsector]['5']
        
        return variable_name

def define_primap_proc_fname(primap_filtered, gas_dict, sect_dict):
    
    source = primap_filtered['source'][0]
    source_scenario = source.lower().replace('hist', primap_filtered['scenario'][0].lower())
    gas = gas_dict[primap_filtered['gas'][0]]
    sector = sect_dict[primap_filtered['category'][0]]
    
    proc_fname =  source_scenario + '_' + gas + '_' + sector + '.csv'

    return proc_fname

def define_primap_variable_name(sector_code, gas, dict_gas_var, primap_sectors='gst_tools/primap_sectors.csv'):
    sector_codes = pd.read_csv(primap_sectors)
    sector_codes.set_index('code', inplace=True)

    gas_name = dict_gas_var[gas]

    if sector_code in ['M.0.EL', '1.B.3', '2.G', '2.H', '1.B.1', '1.B', '1.B.2']:
        variable_name = sector_codes.loc[sector_code]['1'] + ' ' + gas_name + ' ' + sector_codes.loc[sector_code]['3'] + ' ' + sector_codes.loc[sector_code]['4']
    elif sector_code in ['1', '5']:
        variable_name = sector_codes.loc[sector_code]['1'] + ' ' + gas_name + ' ' + sector_codes.loc[sector_code]['3']
    elif sector_code in ['2.D', '2.F', '4', '1.C', '1.A', '3.A', '2', '2.A', '2.B', '2.C', '2.E', 'M.AG', 'M.AG.ELV']:
        variable_name = gas_name + ' ' + sector_codes.loc[sector_code]['2'] + ' ' + sector_codes.loc[sector_code]['3']
    else:
        raise ValueError('The sector code in the dataset ("category" column) is wrong. Please check the dataset.')

    return variable_name

def ensure_common_countries(df1, df2):

    """
    Removes any countries from either dataframe that are not in both dataframes.
    """

    # find the same countries
    df1_countries = df1['country'].unique()
    df2_countries = df2['country'].unique()
    common_countries = list(set(df1_countries).intersection(df2_countries))

    logging.debug('Common countries are: ')
    logging.debug(common_countries)
    # TODO - spit out list of countries not found!

    # reset matrices
    df1 = df1.loc[df1['country'].isin(common_countries), :]
    df2 = df2.loc[df2['country'].isin(common_countries), :]

    return df1, df2

def ensure_common_years(df1, df2):

    """
    Removes any years from either dataframe that are not in both dataframes.
    """

    def put_other_cols_as_index(df):
        year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
        other_cols = list(set(df.columns) - set(year_cols))
        df = df.set_index(other_cols)
        return df

    df1 = put_other_cols_as_index(df1)
    df2 = put_other_cols_as_index(df2)

    # find the same years
    df1_cols = df1.columns
    df2_cols = df2.columns
    common_cols = list(set(df1_cols).intersection(df2_cols))

    # reset matrices
    df1 = df1.loc[:, sorted(common_cols, key=int)]
    df2 = df2.loc[:, sorted(common_cols, key=int)]

    # return other columns
    df1 = df1.reset_index()
    df2 = df2.reset_index()

    return df1, df2

def filter_bp(renamed_bp, energy_variable, countries, start_year):
    if energy_variable != 1 and energy_variable != 2 and energy_variable != 3:
        raise ValueError('Error. Please provide a valid energy variable (either 1, 2 or 3).')
    else:
        # Calculate the variables, add them to the dataframe, and pivot the dataframe to only include this variable along with the unit column.
        if energy_variable == 1:
            filtered = calculate_ren_elec_share(renamed_bp)
            filtered = filtered[['country','ren_elec_share', 'year']]
            filtered = filtered.pivot(index='country', columns='year', values='ren_elec_share').reset_index().rename_axis(None, axis=1)
            filtered['variable'] = ['Share of renewable power']*len(filtered)
            filtered['unit'] = ['%']*len(filtered)
        elif energy_variable == 2:
            filtered = calculate_ff_share(renamed_bp)
            filtered = filtered[['country', 'ff_cons_share_%', 'year']]
            filtered = filtered.pivot(index='country', columns='year', values='ff_cons_share_%').reset_index().rename_axis(None, axis=1)
            filtered['variable'] = ['Share of fossil primary energy consumed']*len(filtered)
            filtered['unit'] = ['%']*len(filtered)
        elif energy_variable == 3:
            filtered = calculate_energy_use(renamed_bp)
            filtered = filtered[['country','energy_use_ej', 'year']]
            filtered = filtered.pivot(index='country', columns='year', values='energy_use_ej').reset_index().rename_axis(None, axis=1)
            filtered['variable'] = ['Energy use']*len(filtered)
            filtered['unit'] = ['EJ']*len(filtered)
        
        # Filter by countries
        filtered = filtered.loc[filtered['country'].isin(countries)]
        
        if len(filtered.index) == 0:
            raise ValueError('There is no data for the countries specified. Please, select different countries.')
        else:
            # Tell the user if any of the needed countries are missing and, if yes, which ones:
            missing_countries = list(set(countries) - set(filtered['country'].unique()))
            if missing_countries:
                logging.info('Not all countries requested were available in the raw data. You are missing the following:')
                for country in missing_countries:
                    logging.info('   ' + to_name(country))
                logging.info('---------')

            # Reduce to only required years
            filtered = change_first_year(filtered, start_year)
            filtered = check_column_order(filtered)

            # Check
            logging.debug('These are the 10 first rows of the processed data:')
            logging.debug(filtered.head(10))

            return filtered

def filter_ipcc(renamed_ipcc, gas, sector_or_subsector, countries, start_year, ipcc_subsectors='gst_tools/ipcc_subsectors.csv'):
    
    filtered = renamed_ipcc[['country', 'year', 'sector', 'subsector', gas]]
    
    # Calculating sector aggregation, including total excl. LULUCF
    sector_aggr = filtered.drop(columns=['subsector']).groupby(by=['country', 'year', 'sector']).sum().reset_index()

    total = sector_aggr.groupby(by=['country', 'year']).sum().reset_index()
    
    total['sector'] = ['Total (excl. LULUCF)']*len(total)
    sector_aggr_tot = pd.concat([sector_aggr, total]).reset_index(drop=True)

    sector_aggr_tot.rename(columns={'sector': 'category'}, inplace=True)
    
    # Adding sector name tag to subsectors
    filtered['subsector'] = filtered['subsector'].astype(str) + ' [' + filtered['sector'].astype(str) + ']'
    filtered = filtered.drop(columns=['sector']).rename(columns={'subsector': 'category'})
    filtered = pd.concat([filtered, sector_aggr_tot]).reset_index(drop=True)
    
    # Filtering
    filtered = filtered.loc[(filtered['category'] == sector_or_subsector)]

    if len(filtered.index) == 0:
        raise ValueError('There is no data for the sector or subsector selected. Try again.')
    else:
        filtered = filtered.loc[filtered['country'].isin(countries)]

        if len(filtered.index) == 0:
            raise ValueError('There is no data for the countries selected. Please, select different countries.')
        
        else:
            missing_countries = list(set(countries) - set(filtered['country'].unique()))
            if missing_countries:                
                logging.info('Not all countries requested were available in the raw data. You are missing the following:')
                for country in missing_countries:
                    logging.info('   ' + to_name(country))
                logging.info('---------')


            filtered = filtered[['country', 'year', gas]]
            filtered = filtered.pivot(index='country', columns='year', values=gas).reset_index().rename_axis(None, axis=1)
                
            filtered['variable'] = [define_ipcc_variable_name(sector_or_subsector, gas, ipcc_subsectors=ipcc_subsectors)]*len(filtered)
            
            filtered['unit'] = ['tCO2eq']*len(filtered)

            # Reduce to only the required years
            filtered = change_first_year(filtered, start_year)

            filtered = check_column_order(filtered)

            # Check
            logging.debug('These are the first ten rows of the processed data:')
            logging.debug(filtered.head(10))

            return filtered

def filter_ipcc_indirect(renamed_ipcc_indirect, gas, sector_or_subsector, countries, start_year, ipcc_subsectors='gst_tools/ipcc_subsectors.csv'):
    if gas != 'GHG':
        raise ValueError('The emissions dataset does not include data for the gas selected. For this dataset, you can choose GHG only.')
    elif int(start_year) < 1990:
        raise ValueError('The emissions dataset does not include data for years prior to 1990.')
    else:
        filtered = renamed_ipcc_indirect
        
        # (1) Calculating indirect emissions for all sectors
        
        indirect_data = filtered[filtered['source']=='indirect']
        ind_sector_agg = indirect_data.drop(columns=['subsector', 'source']).groupby(by=['country', 'sector']).sum().reset_index()
        ind_sector_agg['sector'] = ind_sector_agg['sector'].astype(str) + ' (indirect)'
        
        # (2) Calculating sectoral aggregates (the sectors include direct and indirect)

        sector_aggr = filtered.drop(columns=['subsector', 'source']).groupby(by=['country', 'sector']).sum().reset_index()

        # (3) Calculating total excluding LULUCF (uses only direct emissions to avoid double counting)

        total = filtered[filtered['source']=='direct'].groupby(by=['country']).sum().reset_index()
        sector_column = ['Total (excl. LULUCF)']*len(total)
        total.insert(1, 'sector', sector_column)
        
        # Concatenating sectoral indirect emissions (1), sectoral direct and indirect aggregates (2), and total emissions (3)

        sector_aggr_tot = pd.concat([ind_sector_agg, sector_aggr, total]).reset_index(drop=True)
        sector_aggr_tot.rename(columns={'sector': 'category'}, inplace=True)
        
         # Adding sector name tag to subsectors
        filtered['subsector'] = filtered['subsector'].astype(str) + ' [' + filtered['sector'].astype(str) + ']'
        
        # Leaving only one "category" column
        filtered = filtered.drop(columns=['sector', 'source']).rename(columns={'subsector': 'category'})

        # I think this is unnecessary:
        filtered = filtered.groupby(by=['country', 'category']).sum().reset_index()
        
        filtered = pd.concat([filtered, sector_aggr_tot]).reset_index(drop=True)

        
        # Filtering by category
        
        filtered = filtered.loc[(filtered['category'] == sector_or_subsector)]
        
        if len(filtered.index) == 0:
          raise ValueError('There is no data for the sector or subsector selected. Try again.')

        else:
          # Filtering by countries
          filtered = filtered.loc[filtered['country'].isin(countries)]

          if len(filtered.index) == 0:
            raise ValueError('There is no data for the countries selected. Please, select different countries.')

          else:
            missing_countries = list(set(countries) - set(filtered['country'].unique()))
            
            if missing_countries:
              logging.info('Not all countries requested were available in the raw data. You are missing the following:')
              for country in missing_countries:
                logging.info('   ' + to_name(country))
                logging.info('---------')

            filtered['variable'] = [define_ipcc_variable_name(sector_or_subsector, gas, ipcc_subsectors=ipcc_subsectors)]*len(filtered)
            filtered['unit'] = ['tCO2eq']*len(filtered)

            # Reduce to only the required years
            filtered = change_first_year(filtered, start_year)

            filtered = check_column_order(filtered)

            # Check
            logging.debug('These are the first ten rows of the processed data:')
            logging.debug(filtered.head(10))

            return filtered

def filter_primap(renamed_data, gas, sector, scenario, countries, start_year, dict_gas, primap_sectors='gst_tools/primap_sectors.csv'):
    # Reduce the dataset to only the desired variables
    proc_primap = renamed_data.loc[(renamed_data['gas'] == gas) &
                        (renamed_data['scenario'] == scenario) &
                        (renamed_data['category'] == sector)
                        ]

    if len(proc_primap.index) == 0:
        raise ValueError('There is no data for the gas, the sector, and the data source specified. Please, provide new parameters.')

    else:
        # Reduce the countries or regions to only those desired
        proc_primap = proc_primap.loc[proc_primap['country'].isin(countries)]

        if len(proc_primap.index) == 0:
            raise ValueError('There is no data for the countries specified. Please, select different countries.')
        else:
            # Tell the user if any of the needed countries are missing and, if yes, which ones:
            missing_countries = list(set(countries) - set(proc_primap['country'].unique()))
            if missing_countries:
                logging.info('Not all countries requested were available in the raw data. You are missing the following:')
                for country in missing_countries:
                    logging.info('   ' + to_name(country))
                logging.info('---------')

            # Reduce to only the required years
            proc_primap = change_first_year(proc_primap, start_year)

            proc_primap['variable'] = define_primap_variable_name(sector, gas, dict_gas, primap_sectors=primap_sectors)

            proc_primap = check_column_order(proc_primap)

            # Check
            logging.debug('These are the first ten rows of the processed data:')
            logging.debug(proc_primap.head(10))

            return proc_primap

def load_data(folder, fname):
    file_path = os.path.join(folder, fname)
    logging.debug('Reading ' + file_path)

    #with open(file_path, 'rb') as f:
    #    enc = chardet.detect(f.readline())  # or readline if the file is large
    
    raw_data = pd.read_csv(file_path, encoding='latin1')#enc['encoding'])
    return raw_data

def normalise(proc_data, normalising_dset, per_capita_or_per_usd):
    var1, var2 = ensure_common_years(proc_data, normalising_dset)
    var1, var2 = ensure_common_countries(var1, var2)
    
    if per_capita_or_per_usd == 'per capita':
        var2['unit'] = ['pers']*len(var2)
    elif per_capita_or_per_usd == 'per USD':
        var2['unit'] = ['usd']*len(var2)
    else:
        raise ValueError('Error: Please select either "per capita" or "per USD" for normalisation')
    
    check1 = verify_data_format(var1)
    check2 = verify_data_format(var2)

    if not check1 or not check2:
        raise ValueError('One of the dataframes is not correct! Please check and try again!')
    else:
        # LOU Get metadata for later use and checking
        var1_name = var1['variable'].unique()[0]
        #var2_name = var2['variable'].unique()[0]

        var1_unit  = var1['unit'].unique()[0]
        var2_unit = var2['unit'].unique()[0]

        var1 = prep_df_for_division(var1)
        var2 = prep_df_for_division(var2)

        data_normalised = var1 / var2

        # LOU Generate new metadata
        new_variable_name = var1_name + ' ' + per_capita_or_per_usd
#with open('gst_tools/name_relative_variable.txt', 'w') as f:
 #   f.write(new_variable_name)
        data_normalised['variable'] = new_variable_name

        # LOU Automatically generate the unit 
        data_normalised['unit'] = var1_unit + '/' + var2_unit
    
        data_normalised = data_normalised.reset_index()

        # LOU Reorganise dataframe
        data_normalised = check_column_order(data_normalised)

        return data_normalised

def prep_df_for_division(df):
    
    df = df.set_index('country')
    
    year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
    other_cols = list(set(df.columns) - set(year_cols))
    
    df = df.drop(other_cols, axis='columns')
    
    return df

def prepare_for_plotting(final_dset, plot_type):
    if not verify_data_format(final_dset):
        raise ValueError('WARNING: The data is not correctly formatted! Please check before continuing!')
    # Extract the key information
    else:
        SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
        variable = final_dset['variable'].unique()[0].translate(SUB)
        unit = final_dset['unit'].unique()[0].translate(SUB)

        # Tidy up for next steps
        data_years = set_countries_as_index(final_dset)
        # Delete the following prints and to_csvs:
        #print('Set countries as index, #countries is: ' + str(len(data_years)))
        #data_years.to_csv('proc-data/countries_as_index.csv', index=False)
        data_years = data_years.dropna(axis=1, how='all')
        #print('Dropped the columns that that had all NAs, #countries is:' + str(len(data_years)))
        #data_years.to_csv('proc-data/dropped_columns.csv', index=False)
        data_years = data_years.dropna(axis=0, how='all')
        #print('Dropped rows that had all NAs. Number of countries is: ' + str(len(data_years)))
        #data_years.to_csv('proc-data/dropped_rows.csv', index=False)
        
        # End of section to be deleted

        if plot_type == 4:
            year_max = data_years.idxmax(axis=1)
            year_max = pd.to_numeric(year_max)
            year_max.name = 'peak year'

            start_year = min(list(map(int, data_years.columns)))
            end_year = max(list(map(int, data_years.columns)))

            return year_max, start_year, end_year, data_years, variable, unit

        else:
            return data_years, variable, unit

def rearrange_wb_data(input_folder, wb_dset_fname):
    dset = pd.read_csv(os.path.join(input_folder, wb_dset_fname), header=2)
    dset.rename(columns={'Country Code':'country',
                         'Indicator Name':'variable'}, inplace=True)
    return dset

def rename_bp(raw_bp):
    raw_data_renamed = raw_bp.rename(columns={
                        'ISO3166_alpha3': 'country',
                        'Year': 'year'}, inplace=False)
    raw_data_renamed = raw_data_renamed.astype({'year': str})  
    return raw_data_renamed

def rename_ipcc(raw_ipcc):
    raw_data_renamed = raw_ipcc.rename(columns={
                        'country': 'country_name',
                        'ISO': 'country',
                        'sector_title': 'sector',
                        'subsector_title': 'subsector'}, inplace=False)

    raw_data_renamed.loc[raw_data_renamed['subsector'] == 'Rail ', 'subsector'] = 'Rail'

    raw_data_renamed = raw_data_renamed.drop(raw_data_renamed[raw_data_renamed.subsector == 'International Aviation'].index)
    raw_data_renamed = raw_data_renamed.drop(raw_data_renamed[raw_data_renamed.subsector == 'International Shipping'].index)

    raw_data_renamed = raw_data_renamed.astype({'year': str})
    return raw_data_renamed

def rename_ipcc_indirect(raw_ipcc_indirect):
    raw_data_renamed = raw_ipcc_indirect.rename(columns={
        'ISO': 'country',
        'sector_title': 'sector',
        'subsector_title': 'subsector'}, inplace=False)
    
    raw_data_renamed.loc[raw_data_renamed['subsector'] == 'Rail ', 'subsector'] = 'Rail'

    raw_data_renamed = raw_data_renamed.drop(raw_data_renamed[raw_data_renamed.subsector == 'International Aviation'].index)
    raw_data_renamed = raw_data_renamed.drop(raw_data_renamed[raw_data_renamed.subsector == 'International Shipping'].index)

    return raw_data_renamed

def rename_primap(raw_primap):
    raw_data_renamed = raw_primap.rename(columns={'scenario (PRIMAP-hist)': 'scenario',
                         'area (ISO3)': 'country',
                         'category (IPCC2006_PRIMAP)': 'category',
                         'entity': 'gas'}, inplace=False)
    raw_data_renamed['country'].replace({'EU27BX': 'EUU'}, inplace=True)
    return raw_data_renamed

def set_countries_as_index(df):

        """
        Identifies all metadata (not year columns) in the dataframe and sets as index.
        This enables the user to then manipulate the data knowing it is all numeric.
        The function also returns the column headings of the metadata, in case needed.
        """

        # if years labelled as YNNNN, switch to NNNN
        for col in df.columns:
            if col.startswith('Y'):
                if len(col) == 5:
                    df = df.rename(columns={col: col[1:]})

        # get year columns
        year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]

        # get other columns
        other_cols = list(set(df.columns) - set(year_cols))

        # set country columns as index
        df = df.set_index(['country'])

        # drop other columns
        # remaining_cols = list(set(other_cols) - set(['country']))

        # make sure that the years are in the right (numeric) order
        if year_cols:
            order_year_columns = sorted(year_cols, key=int)
            df = df[order_year_columns]

        return df

def set_non_year_cols_as_index(df):

    """ 
    Identifies all metadata (not year columns) in the dataframe and sets as index. 
    This enables the user to then manipulate the data knowing it is all numeric. 
    The function also returns the column headings of the metadata, in case needed.   
    """

    # get year columns
    year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]

    # get other columns
    other_cols = sorted(list(set(df.columns) - set(year_cols)))
    
    # set other columns as index
    df = df.set_index(other_cols)
    
    # make sure that the years are in the right (numeric) order
    if year_cols:
        order_year_columns = sorted(year_cols, key=int)
        df = df[order_year_columns]
        
    return df, other_cols

def verify_data_format(df):

    """
    To work for the gst_tools, all data read in needs to contain one and only one variable and
    the unit must be both specified and the same for all variables. The set of countries must be unique.
    All of these need to be in correctly labelled columns.
    It's also fairly pointless if there are no years in the data.
    This function checks for these aspects and tells the user what's wrong if it doesn't work.
    """

    verified = True

    # First, check for the right columns
    columns_required = ['variable', 'unit', 'country']
    column_check = all(elem in df.columns for elem in columns_required)
    if column_check:
        verified = True
    else:
        logging.warning('Missing columns in dataframe! Columns missing are:')
        logging.warning(set(columns_required) - set(list(df.columns)))
        verified = False
        return verified

    # check the uniqueness of the data
    if len(df['variable'].unique()) != 1:
        logging.warning('WARNING: the "variable" is non-unique! Please check your input data!')
        verified = False
        return verified

    if len(df['unit'].unique()) != 1:
        logging.warning('WARNING: the "units" are non-unique! Please check your input data!')
        verified = False
        return verified

    # check that no countries are repeated
    if len(df['country'].unique()) != len(df['country']):
        logging.warning('WARNING: Some countries appear to be repeated! Please check your input data!')
        verified = False
        return verified

    # make sure that there are some year columns
    year_cols = [y for y in df[df.columns] if (re.match(r"[0-9]{4,7}$", str(y)) is not None)]
    if len(year_cols) == 0:
        logging.warning("WARNING: there don't appear to be any year columns! Please check your input data!")
        verified = False
        return verified

    # if all the checks are passed, return True
    return verified

def write_to_file(proc_data, proc_folder, proc_fname):
    # First ensure that years, unit, 'country', and variable are all in data. If they are can proceed to print data
    # WARNING What about other things to check?
    if 'country' not in proc_data.columns or 'unit' not in proc_data.columns:
        raise ValueError('Missing required information! Please check your input data and processing!')
    else:
        fullfname_out = os.path.join(proc_folder, proc_fname)

    # LOU Check folder exists
    if not os.path.exists(proc_folder):
        os.makedirs(proc_folder)

    # LOU Write to csv in proc data folder
    proc_data.to_csv(fullfname_out, index=False)

    # celebrate success 
    logging.debug('Processed data written to file! - ' + fullfname_out)