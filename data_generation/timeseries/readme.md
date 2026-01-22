# Time Series Data Generation and Hierarchical Clustering

## Instructions

This project has a `requirements.txt` that can be used to install the dependencies.  A virtual environment is recommended.  It has been tested with Python 3.11.

Create the data, for example, here we are creating data with 20 features (for multivariate time series) and 100 time steps (the script time frequency is in days), where a noise term is used.

```
python time_series_gen.py --n-features 20 --n-steps 100 --output test.csv --noise
```

Create a spectrogram/image of the times series, here with the csv `test.csv` from above. It will create a `.png` with the same naming/prefix.

```
python sequential_data_to_image.py --input test.csv
```

Finally, perform hierarchical clustering and draw a dendrogram on the new plot.
```
python cluster_time_series_image.py --input test.png --output test_hierarchical_cluster.png
```