#####################################################
# Labeling for image classification
# Run example:
# python custom_labeling_classificaiton.py --suffix JPG
#####################################################

import matplotlib.pyplot as plt
import glob
import json
import argparse

def arg_parse():
    """
    Parse arguments
    """

    parser = argparse.ArgumentParser(description='Labeling script for image classification')


    parser.add_argument("--suffix", dest='suffix', help="image file ending", type=str)

    return parser.parse_args()

args = arg_parse()

all_images = glob.glob('*.' + args.suffix)
category={}
plt.ion()

for i,image in enumerate(all_images):
    plt.imshow(plt.imread(image))
    plt.pause(0.05)
    label = input('category: ')
    category[image] = label


with open('custom_labeling_classifiction.json', 'w') as f:
    json.dump(category, f)