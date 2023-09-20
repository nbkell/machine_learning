# region imports
import pandas as pd
from AlgorithmImports import * 
from sklearn.ensemble import RandomForestRegressor
import make_df 

YEARS = 2
DAYS_PER_YEAR = 252

# endregion
class RandomForestAlgo(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 1, 1)
        self.SetCash(5000)  
        self.intervals = [1, 5, 10, 21, 63]
    
        # train initial model
        self.rf_reg = None 
        self.training_syms = [] 
        self.needs_trained = True
        self.AddUniverse(self.TrainingFilter)

    def CreateModel(self): 
        # filter stocks and obtain data frame
        total_days = YEARS*DAYS_PER_YEAR
        history_df = self.History(self.training_syms, total_days, Resolution.Daily)
        train_df = make_df.make_df(history_df, self.intervals, self)

        # create random forest model based on data
        self.rf_reg = RandomForestRegressor(n_estimators=100, 
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
        train_df.dropna(inplace=True)
        target = train_df.filter(like='fwd').columns
        features = train_df.columns.difference(target).tolist()
        X = train_df.drop(target, axis=1)
        y = train_df.fwd_ret_1.to_frame()
        self.rf_reg.fit(X=X, y=y)
        self.needs_trained = False

    def OnSecuritiesChanged(self, changes):
        if self.needs_trained:
            for security in changes.AddedSecurities:
                self.training_syms.append(security.Symbol)
            self.CreateModel()

    def TrainingFilter(self, coarse): 
        dvSort = sorted(coarse, key=lambda x : x.DollarVolume, reverse=True)
        ret = [x.Symbol for x in dvSort if x.Price > 10 and x.HasFundamentalData]
        return ret[:10]
                                 
    def OnData(self, data: Slice):
        pass