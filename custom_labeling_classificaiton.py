import matplotlib.pyplot as plt
import glob
import json

all_images = glob.glob('*.JPG')
category={}
plt.ion()

for i,image in enumerate(all_images):
    plt.imshow(plt.imread(image))
    plt.pause(0.05)
    label = input('category: ')
    category[image] = label


with open('custom_labeling_classifiction.json', 'w') as f:
    json.dump(category, f)