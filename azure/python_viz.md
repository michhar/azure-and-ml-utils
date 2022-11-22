# Python Visuals

Also, these Python visuals may be used with Power BI


The following is a seasonal plot example aggregating across weeks for two datasets.  It is powerful in that you could pick up weekly patterns.  This could be changed to hourly or monthly if you have multiple years of data.
```
# Paste or type your script code here:

import pandas as pd
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns


def seasonal_plot(df1, df2, isp_name):
    """Seasonal plot of a variable"""

    palette = sns.color_palette("Set1", df1['Week'].nunique())

    # Boxplots
    fig2, ax2 = plt.subplots(nrows=1, ncols=2)

        # Figure size
    fig2.set_figwidth(12)
    fig2.set_figheight(6)
    
    # Weekly trend
    sns.boxplot(x=df1['Date'], y=df1['E2ELatency_ms_1'], ax=ax2[0])
    ax2[0].set_title("Dataset 1 {}-wise Box Plot - {}".format('Week', isp_name))
    ax2[0].set_xlabel('Week', fontsize=16)
    ax2[0].set_ylabel(df1.columns[0], fontsize=16)
    ax2[0].set_ylim(0, 1500)
    ax2[0].tick_params(axis='x', rotation=90)
    
    # Weekly trend
    sns.boxplot(x=df2['Date'], y=df2['E2ELatency_ms_2'], ax=ax2[1])
    ax2[1].set_title("Dataset 2 {}-wise Box Plot - {}".format('Week', isp_name))
    ax2[1].set_xlabel('Week', fontsize=16)
    ax2[1].set_ylabel(df2.columns[0], fontsize=16)
    ax2[1].set_ylim(0, 1500)
    ax2[1].tick_params(axis='x', rotation=90)

    fig2.tight_layout()
    plt.show()

# Get data
data_1 = pd.DataFrame(np.int32(dataset['E2ELatency_1']), index=pd.to_datetime(dataset['PreciseTimeStamp'],
                                                            utc=True,
                                                            format='%Y-%m-%d %H:%M:%S'))
data_1.columns = ['E2ELatency_ms_1']

# Get data
data_2 = pd.DataFrame(np.int32(dataset['E2ELatency_2']), index=pd.to_datetime(dataset['PreciseTimeStamp'],
                                                            utc=True,
                                                            format='%Y-%m-%d %H:%M:%S'))
data_2.columns = ['E2ELatency_ms_2']

# Prepare the dataset - get weeks
data_1['Week'] = [w for w in data_1.index.week]
data_2['Week'] = [w for w in data_2.index.week]

data_1['Year'] = [w for w in data_1.index.year]
data_2['Year'] = [w for w in data_2.index.year]

data_1 = data_1.sort_values(['Week'], ascending=[True])
data_2 = data_2.sort_values(['Week'], ascending=[True])

# Fix dates (convert week number to the monday of that week as a date)
data_1['Date'] = pd.to_datetime([time.asctime(time.strptime('{} {} 1'.format(data_1['Year'][i], data_1['Week'][i]), '%Y %W %w')) for i in range(data_1.shape[0])])
data_1['Date'] = [str(d)[:10] for d in data_bb['Date']]
data_2['Date'] = data_1['Date']

seasonal_plot(data_1, data_2, isp_name='ISP_Name')


```
