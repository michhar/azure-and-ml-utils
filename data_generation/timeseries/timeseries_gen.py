"""
Timeseries dataset generation as a csv file.
"""
import numpy as np
from sklearn.datasets import make_regression
from dataclasses import dataclass
import pandas as pd

@dataclass
class RegressionDataConfig:
    n_time_steps: int = 200
    n_features: int = 50
    noise: float = 10.0
    bias: float = 0.0
    random_state: int = 42

class RegressionDataGenerator:
    def __init__(self, config: RegressionDataConfig):
        self.config = config
    
    def generate_data(self, add_nonlinearity=False):

        time_index = pd.date_range(start='2018-01-01',
                            periods=self.config.n_time_steps,
                            freq='D')
                
        X, y = make_regression(
            n_samples=self.config.n_time_steps,
            n_features=self.config.n_features,
            noise=self.config.noise,
            bias=self.config.bias,
            random_state=self.config.random_state
        )

        # Make all numerical vals pos, int, and range 0-255
        df = pd.DataFrame(np.int32(np.abs(X) * 255))
        df = np.clip(df, 0, 255)

        # Add datetime index
        df.index = time_index
        df = df.rename_axis('DateTime')

        # Add column names
        feature_cols = [f'Feature{i+1}' for i in range(self.config.n_features)]
        df.columns = feature_cols

        if add_nonlinearity:
            # Add polynomial terms
            y = y + 0.3 * np.power(X, 2).sum(axis=1)
            df['NonLinearTerm'] = y
    
        return df

# Generate both linear and nonlinear datasets
config = RegressionDataConfig(n_time_steps=200, noise=15, n_features=10)
generator = RegressionDataGenerator(config)

linear_data = generator.generate_data()
nonlinear_data = generator.generate_data(add_nonlinearity=False)

nonlinear_data.to_csv('synthetic_timeseries.csv', index=True)