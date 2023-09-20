#region imports
from AlgorithmImports import *
from sklearn.ensemble import RandomForestRegressor 
#endregion

def train_rf(df, n_splits, train_periods, test_periods, lookahead):
    ''' Trains a random forest model '''
    # train model
    rf_reg = RandomForestRegressor(n_estimators=100, 
                                max_depth=None, 
                                min_samples_split=2, 
                                min_samples_leaf=5, 
                                min_weight_fraction_leaf=0.0, 
                                max_features='auto', 
                                max_leaf_nodes=None, 
                                min_impurity_decrease=0.0, 
                                bootstrap=True, 
                                oob_score=False, 
                                n_jobs=-1, 
                                random_state=None, 
                                verbose=0, 
                                warm_start=False)   
    df.dropna(inplace=True)
    target = sorted(df.filter(like='fwd').columns)
    features = df.columns.difference(target).tolist()

    X = df.drop(target, axis=1)
    y = df.fwd_ret_1.to_frame()

    rf_reg.fit(X=X, y=y)
    return rf_reg 
    





