from countrygroups import UNFCCC, EUROPEAN_UNION, ANNEX_ONE, NON_ANNEX_ONE


# ======================
# Setup of parameters
# ======================

# Please select country groups from this list. You can input the group itself or countries within the groups using ISO 3166 alpha-3 country codes.
# For example:
    # countries = UNFCCC (includes all countries in the UNFCCC)
    # countries = ['EGY', 'GRC', 'EUU', 'COL'] (includes Egypt, Greece, European Union, and Colombia)
    # International shipping is 'SEA'
countries = UNFCCC

# Select the year that you want to plot:

year_of_interest = '2015'

# In case of plotting difference from a baseline year, specify the baseline year here:

baseline_year = '1990'

# Select the data that you want to plot.
#   Options are:    1:  'Emissions (Primap-histcr)' (Primap-hist country-reported data)
#                   2:  'Emissions (Primap-histtp)' (Primap-hist third-party data)
#                   3:  'Energy (bp)' (uses bp data)
#                   4:  'Emissions (IPCC AR6)' (uses emissions data from AR6)

dataset = 4

# If plotting Primap emissions data, please select the type of gas that you want to plot.
# These are the options:
#   'CH4'
#   'CO2'
#   'N2O'
#   'HFCS (SARGWP100)' (as estimated in AR2)
#   'HFCS (AR4GWP100)' (as estimated in AR4)
#   'PFCS (SARGWP100)' (as estimated in AR2)
#   'PFCS (AR4GWP100)' (as estimated in AR4)
#   'SF6'
#   'NF3'
#   'FGASES (SARGWP100)' (as estimated in AR2)
#   'FGASES (AR4GWP100)' (as estimated in AR4)
#   'KYOTOGHG (SARGWP100)' (as estimated in AR2)
#   'KYOTOGHG (AR4GWP100)' (as estimated in AR4)
   
primap_gas = 'KYOTOGHG (AR4GWP100)'

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

# If plotting emissions data from IPCC, please select the gas.
# Options are:      'CO2'
#                   'CH4'
#                   'N2O'
#                   'Fgas'
#                   'GHG'
ipcc_gas = 'GHG'

# If plotting emissions data from the IPCC, please select the sector.
# Options are:      'Residential'
#                   'Electricity & heat'
#                   'Oil and gas fugitive emissions'
#                   'Other (energy systems)'
#                   'Chemicals'
#                   'Other (industry)'
#                   'Waste'
#                   'Domestic Aviation'
#                   'Other (transport)'
#                   'Road'
#                   'Inland Shipping'
#                   'Enteric Fermentation (CH4)'
#                   'Managed soils and pasture (CO2, N2O)'
#                   'Manure management (N2O, CH4)'
#                   'Non-residential'
#                   'Biomass burning (CH4, N2O)'
#                   'Rice cultivation (CH4)'
#                   'Synthetic fertilizer application (N2O)'
#                   'Non-CO2 (all buildings)'
#                   'Coal mining fugitive emissions'
#                   'Cement'
#                   'Metals'
#                   'Petroleum refining'
#                   'International Aviation'
#                   'Rail'
#                   'International Shipping'
ipcc_subsector = 'Rail'

# Select the data type that you want to plot:
# Options are:      'absolute'
#                   'per capita'
#                   'per USD'
# WARNING:  Per capita and per USD measures do not apply to the following variables: share of renewables in electricity and share of fossil
#           fuels in primary energy consumed.
data_type = 'per capita'

# Select the type of plot that you want to create:
# Options are:      1: Distribution of variable in specified year.
#                   2: Change of variable since specified year.
#                   3: 5-year average trend in the specified year.
#                   4: Year of peaking

plot_type = 2