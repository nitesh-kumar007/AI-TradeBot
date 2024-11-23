import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import joblib

class PricePredictionModel:
    def __init__(self, param_grid=None):
        self.param_grid = param_grid or {
            'n_estimators': [100, 200],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
        }
        self.model = XGBRegressor()

    def train(self, X_train, y_train):
        tscv = TimeSeriesSplit(n_splits=5)
        grid_search = GridSearchCV(self.model, self.param_grid, cv=tscv, scoring='neg_mean_squared_error')
        grid_search.fit(X_train, y_train)
        self.model = grid_search.best_estimator_

    def predict(self, X_test):
        return self.model.predict(X_test)

    def evaluate(self, y_true, y_pred):
        return mean_squared_error(y_true, y_pred)

    def save_model(self, model_path='model.pkl'):
        joblib.dump(self.model, model_path)

    def load_model(self, model_path='model.pkl'):
        self.model = joblib.load(model_path)
