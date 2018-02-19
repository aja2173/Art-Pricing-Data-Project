def predict(csv_file):
    import pandas as pd
    import csv
    import numpy as np
    import matplotlib.pyplot as plt
    import sklearn
    from sklearn.preprocessing import Imputer
    
    #Training Data
    data_file_path = 'data.csv'
    data= pd.read_csv(data_file_path, encoding = 'latin-1',)
    data = data.dropna(axis = 0, subset = ['hammer_price'])

    #Get the categorical data, fill in with most frequent
    col_transform = ['artist_name','artist_nationality','category','currency','location']
    cat_data = data[['artist_name','artist_nationality','category','currency','location']]
    cat_data = pd.get_dummies(cat_data, columns = col_transform)
    cat_data = cat_data.apply(lambda x:x.fillna(x.value_counts().index[0]))

    num_cols = ['artist_birth_year','estimate_high','artist_death_year','estimate_low','hammer_price','measurement_depth_cm', 'measurement_height_cm', 'measurement_width_cm']
    num_data = data[num_cols]
    num_data = num_data.apply(lambda x:x.fillna(x.mean()))

    #For reading in test data

    def add_missing_col(df, cols):
        miss_cols = set(cols) - set(df.columns)
        for c in miss_cols:
            df[c] = 0

    def make_cols(df, cols):  

        add_missing_col(df, cols)
        assert( set( cols ) - set( df.columns ) == set())

        df = df[cols]

        return df

    cat_np = cat_data.as_matrix()
    num_np = num_data.drop(columns = 'hammer_price').as_matrix()

    X = np.concatenate((cat_np,num_np),axis = 1)
    Y = num_data['hammer_price'].as_matrix()

    features = list(cat_data) + list(num_data.drop(columns = 'hammer_price'))
    
    #Testing Data
    test_data = pd.read_csv(csv_file, encoding = 'latin-1')

    cat_test_data = test_data[['artist_name','artist_nationality','category','currency','location']]
    cat_test_data = pd.get_dummies(cat_test_data, columns = col_transform)

    num_test_data = test_data[num_cols]
    
    #Testdata - Might be some unseen data in the categorical data, make sure all columns in test data are same as train
    cat_test_data = make_cols(cat_test_data,cat_data.columns)

    cat_test_np = cat_test_data.as_matrix()
    num_test_np = num_test_data.drop(columns = 'hammer_price').as_matrix()
    
    #Fill in any NA values, based on cat(most_frequent) or num data(mean)
    imp_cat = Imputer(missing_values = 'NaN', strategy = 'most_frequent', axis = 0)
    imp_cat.fit(cat_np)
    cat_test_np = imp_cat.transform(cat_test_np)
    
    imp_num = Imputer(missing_values = 'NaN', strategy = 'mean', axis = 0)
    imp_num.fit(num_np)
    num_test_np = imp_num.transform(num_test_np)
    
    testX = np.concatenate((cat_test_np,num_test_np),axis = 1)
    testY = num_test_data['hammer_price'].as_matrix()
    
    #Now test data is in correct format
    
    #Train the models on X and Y(from the original data)
    
    #Sold or not

    Y_sold = (Y > 0).astype(int)

    from sklearn.tree import DecisionTreeClassifier

    maxdepth = 200

    soldornot = DecisionTreeClassifier(max_depth = maxdepth, random_state = 0)
    soldornot.fit(X, Y_sold)
    
    #Price regressor
    #Get only the examples that sold

    sold_index = np.nonzero(Y_sold)[0]
    X_price = X[sold_index,:]
    Y_price = Y[sold_index]

    #Train a regressor on the examples that sold
    from sklearn.tree import DecisionTreeRegressor
    maxdepth = 500

    price_tree = DecisionTreeRegressor(max_depth = maxdepth, random_state = 1)
    price_tree.fit(X_price, Y_price)

    #Now we have the models, we can just put testX into the models
    #For the test set
    sold_out = soldornot.predict(testX)
    n_examples = len(sold_out)

    for i in range(n_examples):
        if sold_out[i] == 0:
            sold_out[i] = -1
        else:
            example = testX[None, i, :]
            price_out = price_tree.predict(example)
            sold_out[i] = price_out

    from sklearn.metrics import mean_squared_error
    from math import sqrt

    def get_rmse(y_predicted, y_true):
        rmse = sqrt(mean_squared_error(y_predicted, y_true))
        return rmse
    
    #Using the testY, return rmse
    rmse = get_rmse(sold_out,testY)
    
    return rmse