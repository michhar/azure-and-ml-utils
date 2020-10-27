"""
Converts Pascal VOC format (VOTT generated) to YOLO format.  
For use with Darknet program on Linux machine.  The annotations
for this script originated from using the VOTT labeling tool.

Warning:  this script deletes the "data" folder to recreate it.
Also, line 34 must be updated for this script to work with user
annotations.

Notes:
- User must change class list on line 34
- Recommended to use Python 3 to run this script
- The "data" folder is created in the directory that this script is
run in, but operates on any Pascal VOC (VoTT exported) base folder.
- For Darknet, copy the "data" folder to the proper location (e.g. 
'<path to darknet repo>/build/darknet/x64/') before training.

Usage example:
python pascalvoc_to_YOLO.py --annot-folder objects_output

Files created:
- image files are copied over from Pascal VOC folder
- <image id>.txt files - annotations normalized 0-1
- obj.names - class names
- obj.data - class number and file paths
- train.txt - training image set
- valid.txt - validation image set
"""
import xml.etree.ElementTree as ET
import os
import glob
import argparse
import shutil
import random


# User defined!  Change to your needs and order matters:
classes = ['helmet', 'no_helmet']

# Constant
obj_data_contents = """
train  = build/darknet/x64/data/train.txt
valid  = build/darknet/x64/data/valid.txt
names = build/darknet/x64/data/obj.names
backup = backup/"""

def convert_annotation(image_id, annot_folder, image_ext):
    in_file = open('{}/Annotations/{}.xml'.format(annot_folder, image_id))
    tree=ET.parse(in_file)
    root = tree.getroot()

    # Get image width and height by walking tree (there's only one size entry)
    for size in root.iter('size'):
        image_width = int(size.find('width').text)
        image_height = int(size.find('height').text)
    
    # Get bounding boxes
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        class_name = obj.find('name').text
        # Check if the class name is in the user specified classes or 
        # it's difficult (skip if so)
        if class_name not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(class_name)
        xmlbox = obj.find('bndbox')
        b = (int(float(xmlbox.find('xmin').text)), int(float(xmlbox.find('ymin').text)),
            int(float(xmlbox.find('xmax').text)), int(float(xmlbox.find('ymax').text)))
        # Calcute YOLO bounding boxes
        # b is xmin,ymin,xmax,ymax
        xmin, ymin, xmax, ymax = b
        # Normalize 0-1
        xmin, xmax = xmin / image_width, xmax / image_width
        ymin, ymax = ymin / image_height, ymax / image_height
        # YOLO format
        box_height = ymax - ymin
        box_width = xmax - xmin
        x_center = xmin + 0.5*box_width
        y_center = ymin + 0.5*box_height # subtract 1 because measuring from top
        yolo_box = [x_center, y_center, box_width, box_height]

        with open('data/img/%s.txt'%(image_id), 'a') as out:
            # Write out annotation
            print('writing output to {}'.format('data/obj/%s.txt'%(image_id)))
            out.write(str(cls_id) + " " + ",".join([str(a) for a in yolo_box]) + '\n')
            # Copy image
            shutil.copy('{}/JPEGImages/{}.{}'.format(annot_folder, image_id, image_ext),
                'data/img/{}.{}'.format(image_id, image_ext))

if __name__ == '__main__':
    # For command line options
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    # There should be one "asset.json" for each image with annotations
    parser.add_argument(
        '--annot-folder', type=str, dest='annot_folder', default='output',
        help='Annotations folder from VoTT 2.0 Pascal VOC format export.  \
            Warning:  this script will delete any existing annotations in \
                the "data" folder!'
    )

    args = parser.parse_args()

    # how data for YOLO programs usually look
    # Make output dir
    out_dir = os.path.join('data', 'img') 
    try:
        if os.path.exists('data'):
            shutil.rmtree('data')
        os.makedirs(out_dir, exist_ok=True)
        print("Directory '%s' created successfully" % out_dir) 
    except OSError as error: 
        print("Directory '%s' can not be created" % out_dir)

    images = glob.glob(os.path.join(args.annot_folder, 'JPEGImages', '*.*'))
    for img_id in images:
        img_id_base = os.path.basename(img_id)
        split_name = img_id_base.split('.')
        img_id = '.'.join(split_name[:-1])
        print('Image ID: ', img_id)
        # Image id is name w/o extension, annotation input folder and 
        # image file extension
        convert_annotation(img_id, args.annot_folder, split_name[-1])

        # Create train.txt and valid.txt (randomly assign images to these lists)
        r = random.choice(range(10))
        dir_for_darknet = 'build/darknet/x64/data/img/'
        if r < 1: # 10% of images will be in validation set
            with open('data/valid.txt', 'a') as valid_list:
                valid_list.write(dir_for_darknet + img_id_base + '\n')
        else:
            with open('data/train.txt', 'a') as train_list:
                train_list.write(dir_for_darknet + img_id_base + '\n')

        with open('data/obj.names', 'w') as names_file:
            for c in classes:
                names_file.write(c + '\n')

        with open('data/obj.data', 'w') as paths_file:
            paths_file.write('classes = {}'.format(len(classes)))
            paths_file.write(obj_data_contents)



    
