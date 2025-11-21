"""
Timeseries dataset generation as a csv file.
"""
import numpy as np
from sklearn.datasets import make_regression
from dataclasses import dataclass
import pandas as pd
import argparse


@dataclass
class RegressionDataConfig:
    n_time_steps: int = 200
    n_features: int = 10
    noise: float = 10.0
    bias: float = 0.0
    random_state: int = 42

class RegressionDataGenerator:
    def __init__(self, config: RegressionDataConfig):
        self.config = config
    
    def generate_data(self, add_nonlinearity=False, add_extra_noise=False):

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

        if add_extra_noise:
            # Generate Gaussian noise
            mean = 0
            extra_noise = np.random.normal(mean,
                                           self.config.noise,
                                           size=df.shape)
            df = df + extra_noise

        # Add datetime index
        df.index = time_index
        df = df.rename_axis('DateTime')

        # Add column names
        feature_cols = [f'Feature{i+1}' for i in range(df.shape[1])]
        df.columns = feature_cols

        if add_nonlinearity:
            # Add polynomial terms
            y = y + 0.3 * np.power(X, 2).sum(axis=1)
            df['NonLinearTerm'] = y
    
        return df

def main(n_features,
         n_time_steps,
         out_filename,
         add_nonlinearity=False,
         add_extra_noise=False):
    # Generate both linear and nonlinear datasets
    config = RegressionDataConfig(n_time_steps=n_time_steps,
                                  noise=15,
                                  n_features=n_features)
    generator = RegressionDataGenerator(config)

    data = generator.generate_data(add_nonlinearity=add_nonlinearity,
                                   add_extra_noise=add_extra_noise)

    data.to_csv(out_filename, index=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-features', help="Number of features (integer).",
                    required=True,
                    type=int,
                    dest='n_feats')
    parser.add_argument('--n-steps', help="Number of time steps (integer).",
                    required=True,
                    type=int,
                    dest='n_steps')
    parser.add_argument('--output', help="Output csv file name.",
                    required=True,
                    type=str,
                    dest='out')    
    parser.add_argument('--noise', help="Add extra noise to the data.",
                    required=False,
                    action='store_true')
    args = parser.parse_args()

    main(n_features=args.n_feats,
         n_time_steps=args.n_steps,
         add_extra_noise=args.noise,
         out_filename=args.out)