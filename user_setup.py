from countrygroups import UNFCCC, EUROPEAN_UNION, ANNEX_ONE, NON_ANNEX_ONE


# ======================
# Setup of parameters
# ======================

# Please select country groups from this list. You can input the group itself or countries within the groups using ISO 3166 alpha-3 country codes.
# For example:
    # countries = UNFCCC (includes all countries in the UNFCCC)
    # countries = ['EGY', 'GRC', 'EUU', 'COL'] (includes Egypt, Greece, European Union, and Colombia)
    # International shipping is 'SEA'
countries = UNFCCC #['EGY', 'GRC', 'EUU', 'COL']

# Select a country to highlight as a vertical bar in the distribution (function not to be included in the website?)
country_to_highlight = ''

# Select the year that you want to plot:

year_of_interest = '2019'

# In case of plotting difference from a baseline year, specify the baseline year here:

baseline_year = '2000'

# Select the data that you want to plot.
#   Options are:    1:  'Emissions (PRIMAP-histcr)' (Primap-hist country-reported data, AR4)
#                   2:  'Emissions (PRIMAP-histtp)' (Primap-hist third-party data, AR4)
#                   3:  'Energy (BP)' (uses bp data)
#                   4:  'Emissions (IPCC AR6)' (uses emissions data from AR6)
#                   5:  'Emissions (IPCC AR6)', including indirect emissions
dataset = 4

# Select the gas that you want to plot:
# Options are:
#       'GHG'
#       'CO2'
#       'CH4'
#       'N2O'
#       'F-gases'
#       'HFCs'
#       'PFCs'
#       'SF6'
#       'NF3'
gas = 'CH4'

# If plotting Primap emissions data, please select the sector that you want to plot.
# These are the available sectors:
# 'M.0.EL'      (Total excluding LULUCF)
# '1'           (Energy)
# '1.A'         (Fuel combustion)
# '1.B'         (Fugitive emissions from energy production)
# '1.B.1'       (Fugitive emissions from solid fuels)
# '1.B.2'       (Fugitive emissions from oil and gas)
# '1.B.3'       (Other emissions from energy production)
# '1.C'         (NO DATA - CO2 transport and storage)
# '2'           (IPPU)
# '2.A'         (Mineral industry)
# '2.B'         (Chemical industry)
# '2.C'         (Metals industry)
# '2.D'         (Non-energy products from fuels and solvents)
# '2.E'         (Electronics industry)
# '2.F'         (NO DATA - Emissions from the use of substitutes of ozone-depleting substances)
# '2.G'         (Other emissions from product manufacture and use)
# '2.H'         (Other emissions from IPPU)
# 'M.AG'        (Agriculture)
# '3.A'         (Livestock)
# 'M.AG.ELV'    (Agriculture excluding livestock)
# '4'           (Waste)
# '5'           (Other)
primap_sector = '2'

# If plotting energy data, please select the variable that you want to plot
# Options are:      1: Share of renewables in electricity
#                   2: Share of fossil fuels in primary energy consumed
#                   3: Energy use
energy_variable = 1

# If plotting emissions data from the IPCC dataset 4, please select the sector or subsector options.
# Subsector options are:        'Residential [Buildings]'
#                               'Electricity & heat [Energy systems]'
#                               'Oil and gas fugitive emissions [Energy systems]'
#                               'Other (energy systems) [Energy systems]'
#                               'Chemicals [Industry]'
#                               'Other (industry) [Industry]'
#                               'Waste [Industry]'
#                               'Domestic Aviation [Transport]'
#                               'Other (transport) [Transport]'
#                               'Road [Transport]'
#                               'Inland Shipping [Transport]'
#                               'Enteric Fermentation (CH4) [AFOLU]'
#                               'Managed soils and pasture (CO2, N2O) [AFOLU]'
#                               'Manure management (N2O, CH4) [AFOLU]'
#                               'Non-residential [Buildings]'
#                               'Biomass burning (CH4, N2O) [AFOLU]'
#                               'Rice cultivation (CH4) [AFOLU]'
#                               'Synthetic fertilizer application (N2O) [AFOLU]'
#                               'Non-CO2 (all buildings) [Buildings]'
#                               'Coal mining fugitive emissions [Energy systems]'
#                               'Cement [Industry]'
#                               'Metals [Industry]'
#                               'Petroleum refining [Energy systems]'
#                               'Rail [Transport]'
# Sector options are:           'AFOLU'
#                               'Buildings'
#                               'Energy systems'
#                               'Industry'
#                               'Transport'
#                               'Total (excl. LULUCF)'

# If plotting emissions data from the IPCC dataset 5, please select the sector or subsector options.
# Subsector options are:        'Residential [Buildings]'
#                               'Electricity & heat [Energy systems]'
#                               'Oil and gas fugitive emissions [Energy systems]'
#                               'Other (energy systems) [Energy systems]'
#                               'Chemicals [Industry]'
#                               'Other (industry) [Industry]'
#                               'Waste [Industry]'
#                               'Domestic Aviation [Transport]'
#                               'Other (transport) [Transport]'
#                               'Road [Transport]'
#                               'Inland Shipping [Transport]'
#                               'Enteric Fermentation (CH4) [AFOLU]'
#                               'Managed soils and pasture (CO2, N2O) [AFOLU]'
#                               'Manure management (N2O, CH4) [AFOLU]'
#                               'Non-residential [Buildings]'
#                               'Biomass burning (CH4, N2O) [AFOLU]'
#                               'Rice cultivation (CH4) [AFOLU]'
#                               'Synthetic fertilizer application (N2O) [AFOLU]'
#                               'Non-CO2 (all buildings) [Buildings]'
#                               'Coal mining fugitive emissions [Energy systems]'
#                               'Cement [Industry]'
#                               'Metals [Industry]'
#                               'Petroleum refining [Energy systems]'
#                               'Rail [Transport]'
# Sector options are:           'AFOLU'
#                               'Buildings'
#                               'Energy systems'
#                               'Industry'
#                               'Transport'
#                               'Total (excl. LULUCF)'
#                               'Buildings (indirect)'
#                               'Energy systems (indirect)'
#                               'Industry (indirect)'
#                               'Transport (indirect)'
ipcc_sector_or_subsector = 'Total (excl. LULUCF)'

# Select the data type that you want to plot:
# Options are:      'absolute'
#                   'per capita'
#                   'per USD'
# WARNING:  Per capita and per USD measures do not apply to the following variables: share of renewables in electricity and share of fossil
#           fuels in primary energy consumed.
#if dataset == 3:
data_type = 'per capita'

# Select the type of plot that you want to create:
# Options are:      1: Distribution of variable in specified year.
#                   2: Change of variable since specified year.
#                   3: 5-year average trend in the specified year.
#                   4: Year of peaking
plot_type = 3