from __future__ import print_function
from __future__ import division


import os
import sys
import ntpath
import pandas as pd
import numpy as np
from normative import estimate
sys.path.append('/Users/pedro/git/nispat_pall75/nispat')
import fileio

def get_outliers(data, method='median', m=3):
    outliers=np.full(data.shape, False, dtype=bool)
    notnan = ~np.isnan(data)
    not999 = data != 999 
    valid_data = np.where(notnan & not999) [0]
    data=data[valid_data]
    if method=='mean':
        bbb = abs(data - np.mean(data)) >= m * np.std(data)
        if sum(bbb) > 0:
          outliers[valid_data[bbb]]=True
        return outliers
    elif method=='median':
        k=1.4826
        #return abs(data - np.median(data)) >= m*k*np.median(abs(data-np.median(data)))
        bbb = abs(data - np.median(data)) >= m*k*np.median(abs(data-np.median(data)))
        if sum(bbb) > 0:
          outliers[valid_data[bbb]]=True
        return outliers
    else:
        return

def normative_xlsx(xlsx_path,
                   X_columns,
                   Y_columns,
                   groups_column='group',
                   normative_group='TD',
                   asd_group='ASD',
                   sheet_name='Sheet1',
                   sex='Males_and_Females'):
    
    """ calls normative.estimate function after reading data from xlsx file

    This function reads an xlsx file to setup the parameters to call
    normative.estimate that will:
    
        1) estimate a normative model (with crossvalidation) of responses (Y)
    from covariates (X) using the normative cases specified in the xlsx
    
        2) use the normative model to make response predictions for the test
    cases specified in the xlsx
    

    Basic usage::

        normative_xlsx(xlsx_path, X_columns, Y_column, [extra_arguments])

    where the parameters are defined below.

    :param xlsx_path: xlsx file containing all  data cases
    :param X_columns: array of column numbers for the covariates (start at 0)
    :param Y_column: column name for the predicted variable (response)
    :param groups_column: column name containing the subgroup labels
    :param normative_group: label for the normative group in groups_column
    :param sheet_name: xlsx sheet name containing the data cases
    :param sex: normative model only on 'Males', 'Females' or both

    A new directory is created with name based on the xlsx file, the response,
    and the covariate columns.

    :new output dir: <xlsx_name>_<Y_column>_<X_columns>

    All outputs from normative.estimate are written to disk in the new
    directory.
    
    :outputs: * yhat - predictive mean
              * ys2 - predictive variance
              * Hyp - hyperparameters
              * Z - deviance scores
              * Rho - Pearson correlation between true and predicted responses
              * pRho - parametric p-value for this correlation
              * rmse - root mean squared error between true/predicted responses
              * smse - standardised mean squared error

    The outputsuffix '_cv10' is used for the outputs corresponding the
    crossvalidation estimation of the normative model. The outputsuffix '_test'
    is used for the outputs corresponding the predictions for the test cases.
    
    """
    
    # Read normative and non-normative cases from xlsx file 
    df = pd.read_excel(open(xlsx_path,'rb'), sheet_name=sheet_name);
    column_names = list(df.columns.values)
    groups = df[groups_column].values    
    normatives = groups == normative_group
    asds = groups == asd_group
    non_normatives = groups != normative_group

    # Select cases for chosen sex
    if 'sex' in column_names:
        males = (df['sex']==1).values #Males
        females = (df['sex']==-1).values #Females
        males_and_females=males|females
        if sex==1: #Males
            chosen_sex=males
            sexstr = '_Males'
        elif sex==-1: #Females
            chosen_sex=females
            sexstr = '_Females'
        else:
            chosen_sex=males_and_females
            sexstr = ''
    else:
        chosen_sex=np.full(groups.shape, True, dtype=bool)
        sexstr = ''
    
    # Get the column names corresponding to the covariates X
    X_columns_names = [ column_names[i] for i in X_columns]
    wdir = os.path.realpath(os.path.curdir)
    z_df = df[['subject_id', 'age', 'group', 'sex']].copy()
    
    # Compute normative modelling for each response variable Y using all covariates X
    for Y_column in Y_columns:
        Y_column_name = column_names[Y_column]        
        # Create the dirname for the normative model based on the xlsx and X,Y column names
        covstr =''
        for i in range(0,len(X_columns_names)):
          covstr= covstr + '_' + X_columns_names[i]
        xlsx_name=os.path.splitext(ntpath.basename(xlsx_path))[0];    
        #nm_name = xlsx_name + '_' + Y_column_name + covstr + sexstr
        nm_name = xlsx_name + covstr + sexstr
        nm_dir  = os.path.join(wdir, nm_name)
        if not os.path.exists(nm_dir):
            os.makedirs(nm_dir)    
        os.chdir(nm_dir)
    
        # Get the values for the covariates X 
        X = df.iloc[:,X_columns].values
        #X_isnan=np.isnan(X)    
        #x_isnan = X_isnan.any(axis=1)
        #X_outliers = np.full(X.shape, False, dtype=bool)
        #for j in range(0,X.shape[1]):
        #    X_outliers[:, j]=get_outliers(X[:,j],'median',5)
        #x_outliers = X_outliers.any(axis=1)
    
        # Get the values for the response variable Y
        Y = df.iloc[:,Y_column].values
        y_isnan=np.isnan(Y) 
        y_outliers=get_outliers(Y,'median',5)
        
        #ok_indexes= ~x_isnan & ~x_outliers & ~y_isnan & ~y_outliers & chosen_sex    
        #ok_indexes= ~y_isnan & ~y_outliers & chosen_sex    
        #ok_indexes= ~y_isnan & chosen_sex    
        
        # Set normative cases (normatives) and test cases
        normative_cases = normatives & ~y_isnan & ~y_outliers & chosen_sex 
        #test_cases = non_normatives & ok_indexes
        test_cases = asds & ~y_isnan & chosen_sex
        
        # Covariates X for normative cases
        X_c = X[ normative_cases ]
    #    X_c = X_c.reshape(len(X_c),1)
        covfile= 'covariates.txt'    
        covfile = os.path.join(nm_dir, covfile)
        np.savetxt(covfile,X_c)
    
        # Covariates X for test cases
        X_p = X[ test_cases ]
    #    X_p = X_p.reshape(len(X_p),1)
        testcov = 'testcovariates.txt'
        testcov = os.path.join(nm_dir, testcov)
        np.savetxt(testcov,X_p)
    
        # Response Y for normative and test cases
        Y_c = Y[ normative_cases ]
        Y_c = Y_c.reshape(len(Y_c),1)
        respfile = 'responses.txt'
        respfile = os.path.join(nm_dir, respfile)
        np.savetxt(respfile,Y_c)    
        
        # Response Y for test cases
        Y_p = Y[ test_cases ]
        Y_p = Y_p.reshape(len(Y_p),1)
        testresp = 'testresponses.txt'
        testresp = os.path.join(nm_dir, testresp)
        np.savetxt(testresp,Y_p)
    
        # Add new column for Z scores
        z_column_name = Y_column_name + '_Z'
        z_df[ z_column_name ]= ''
    
        # GP regression and crossvalidation on normative data
        cvfolds = 10
        cvoutputsuffix = '_cv' + str(cvfolds)
        estimate(respfile, covfile, cvfolds=cvfolds, outputsuffix=cvoutputsuffix)
        zcvfile = 'Z' + cvoutputsuffix + '.txt'
        Zcv = fileio.load(zcvfile)    
        #df_new[ z_column_name ][normative_cases ]= Zcv
        z_df.loc[normative_cases,z_column_name] = Zcv
    
        # GP regression of normative data followed by prediction on test data
        testoutputsuffix = '_test'
        estimate(respfile, covfile, testresp=testresp, testcov=testcov, outputsuffix=testoutputsuffix)
        ztestfile = 'Z' + testoutputsuffix + '.txt'
        Ztest = fileio.load(ztestfile)
        #df_new[ z_column_name ][test_cases ]= Ztest
        z_df.loc[test_cases,z_column_name] = Ztest


    # Save Z-scores to new xlsx file
    z_df.to_excel(xlsx_name + '_Z.xlsx')

