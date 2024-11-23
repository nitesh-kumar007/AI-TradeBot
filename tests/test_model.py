import unittest
from app.model import PricePredictionModel
import numpy as np

class TestModel(unittest.TestCase):
    def test_model_training(self):
        model = PricePredictionModel()
        X_train = np.random.rand(100, 10)
        y_train = np.random.rand(100)
        model.train(X_train, y_train)
        self.assertIsNotNone(model.model)

    def test_model_prediction(self):
        model = PricePredictionModel()
        model.load_model('model.pkl')
        X_test = np.random.rand(1, 10)
        prediction = model.predict(X_test)
        self.assertIsNotNone(prediction)

if __name__ == '__main__':
    unittest.main()
