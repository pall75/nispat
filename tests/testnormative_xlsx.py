# -*- coding: utf-8 -*-
"""
@author: pall75
"""
import sys
sys.path.append('/Users/pedro/git/nispat_pall75/nispat')

from normative_xlsx import normative_xlsx

# Example1: perform normative modelling on data from in euaims_686.xlsx using:
# - column 1 (age) as X covariates
# - column 4 (BMI) as Y responses
# - Default values for the rest of the parameters:
#   -- Data is from Sheet1
#   -- Normative modelling is based on 'TD' cases in the 'group' column
#   -- Analysis is done on both 'Males' and 'Females' (specified in 'sex' column )
excel_file='/Users/pedro/PostDoc/Projects/EU-AIMS/EXCEL_DATA/euaims_686.xlsx';
normative_xlsx(xlsx_path=excel_file,X_columns=[1],Y_column=4)

# Example2: perform normative modelling on data from in euaims_686.xlsx using:
# - column 1 (age) as X covariates
# - column 4 (BMI) as Y responses
# - Non-default values for the rest of the parameters:
#   -- Data is from Sheet2
#   -- Normative modelling is based on 'ASD' cases in the 'group' column
#   -- Analysis is done on 'Males' only
normative_xlsx(xlsx_path=excel_file,groups_column='group',normative_group='ASD',sheet_name='Sheet2',X_columns=[1],Y_column=4,sex='Males')

