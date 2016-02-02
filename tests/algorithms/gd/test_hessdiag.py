from functools import partial

import numpy as np

from sklearn import datasets, cross_validation, preprocessing
from neupy import algorithms, layers, estimators

from utils import compare_networks
from data import simple_classification
from base import BaseTestCase


class HessianDiagonalTestCase(BaseTestCase):
    def test_hessdiag(self):
        dataset = datasets.load_diabetes()
        data, target = dataset.data, dataset.target

        input_scaler = preprocessing.StandardScaler()
        target_scaler = preprocessing.StandardScaler()

        x_train, x_test, y_train, y_test = cross_validation.train_test_split(
            input_scaler.fit_transform(data),
            target_scaler.fit_transform(target.reshape(-1, 1)),
            train_size=0.8
        )

        nw = algorithms.HessianDiagonal(
            connection=[
                layers.Sigmoid(10),
                layers.Sigmoid(20),
                layers.Output(1)
            ],
            step=0.1,
            shuffle_data=False,
            verbose=False,
            min_eigval=1e-2
        )
        nw.train(x_train, y_train, epochs=100)
        y_predict = nw.predict(x_test)

        error = estimators.rmsle(
            target_scaler.inverse_transform(y_test),
            target_scaler.inverse_transform(y_predict).round()
        )

        self.assertAlmostEqual(0.5027, error, places=4)

    def test_compare_bp_and_hessian(self):
        x_train, _, y_train, _ = simple_classification()
        compare_networks(
            # Test classes
            algorithms.GradientDescent,
            partial(algorithms.HessianDiagonal, min_eigval=0.01),
            # Test data
            (x_train, y_train),
            # Network configurations
            connection=[
                layers.Sigmoid(10, init_method='bounded', bounds=(-1, 1)),
                layers.Sigmoid(20, init_method='bounded', bounds=(-1, 1)),
                layers.Output(1)
            ],
            step=0.1,
            shuffle_data=True,
            verbose=False,
            # Test configurations
            epochs=50,
            show_comparison_plot=False
        )
