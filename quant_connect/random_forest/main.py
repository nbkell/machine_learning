# imports
# To dos:
# - OnData is incorrect (need to figure out how update portfolio at the beginning of each day)
# - Need to figure out save models so that backtest does not retrain every time it runs 
import pandas as pd
from datetime import time
from AlgorithmImports import * 
from sklearn.ensemble import RandomForestRegressor
import make_df 

# algorithm parameters
TRAIN_YEARS = 2
DAYS_PER_YEAR = 252
LOOK_BACK_DAYS = 70
UNIVERSE_SIZE = 100
N_POSITIONS = 25
MIN_POSITIONS = 15
START_CASH = 100000

class RandomForestAlgo(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2020, 2, 1)
        self.SetCash(100000) 
        self.update_time = time(10, 30)
        self.intervals = [1, 5, 10, 21, 63]
    
        # train initial model
        self.rf_reg = None 
        self.training_syms = [] 
        self.needs_trained = True
        self.AddUniverse(self.TrainingFilter)

    def CreateModel(self): 
        # filter stocks and obtain data frame
        total_days = TRAIN_YEARS*timedelta(365)
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
        ''' Used to train model at the outset of the algorithm'''
        if self.needs_trained:
            for security in changes.AddedSecurities:
                self.training_syms.append(security.Symbol)
            self.CreateModel()

    def TrainingFilter(self, coarse): 
        dvSort = sorted(coarse, key=lambda x : x.DollarVolume, reverse=True)
        ret = [x.Symbol for x in dvSort if x.Price > 10 and x.HasFundamentalData]
        return ret[:UNIVERSE_SIZE]
                                 
    def OnData(self, data: Slice):
        if self.Time.time() != self.update_time or self.needs_trained:
            return
        # use model to predict 1 day returns for each security in the universe
        history_df = self.History(self.training_syms, LOOK_BACK_DAYS, Resolution.Daily) 
        current_df = make_df.make_df(history_df, self.intervals, self).groupby('symbol').last()
        target = current_df.filter(like='fwd').columns
        features = current_df.columns.difference(target).tolist()
        current_df = current_df.drop(target, axis=1)
        returns_map = {}
        for index, row in current_df.iterrows():
            symbol = index[0].split()[0]
            row_df = row.to_frame().transpose() 
            cur_returns = self.rf_reg.predict(row_df) 
            returns_map[symbol] = cur_returns

        sorted_returns = [(sym, returns_map[sym]) for sym in returns_map]
        sorted_returns.sort(key=lambda tup: tup[1])

        # determine short and long positions based on predictions
        m = len(sorted_returns)
        longs = set()
        for i in range(m-1, m-N_POSITIONS, -1):
            sym, ret = sorted_returns[i]
            if ret > 0:
                longs.add(sym)
            else:
                break
        shorts = set() 
        for i in range(N_POSITIONS): 
            sym, ret = sorted_returns[i]
            if ret < 0:
                 shorts.add(sym) 
            else:
                break
        slen, llen = len(shorts), len(longs) 
        if slen < MIN_POSITIONS or llen < MIN_POSITIONS: 
            longs = shorts = set()
        
        # determine holdings percentages for each symbol
        ltot = slen + llen
        self.Debug(str(shorts))
        self.Debug(str(longs))
        for symbol in self.training_syms: 
            if symbol in longs:
                self.SetHoldings(symbol, 1/ltot)
            elif symbol in shorts:
                self.SetHoldings(symbol, -1/ltot)
            else:
               self.SetHoldings(symbol, 0)
