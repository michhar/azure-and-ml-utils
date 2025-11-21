"""
Convert sequential data in a csv file to a RGB image with same
basename, but '.png' instead.
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse


def main(csvfile):
    with open(csvfile, 'r') as f:
        sequencesdata = pd.read_csv(csvfile, index_col=0)
        sequencesdata = sequencesdata.T
        
    imgfile = '.'.join(os.path.basename(csvfile).split('.')[:-1]) + '.png'

    plt.imsave(imgfile, sequencesdata)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="Input csv.",
                        required=True,
                        type=str)
    args = parser.parse_args()

    main(args.input)

    
