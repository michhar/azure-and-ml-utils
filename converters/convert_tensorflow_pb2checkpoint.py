"""
TensorFlow protobuf to checkpoint converter.

Based upon:
https://blog.metaflow.fr/tensorflow-how-to-freeze-a-model-and-serve-it-with-a-python-api-d4f3596b3adc
https://blog.metaflow.fr/tensorflow-saving-restoring-and-mixing-multiple-models-c4c94d5d7125
https://stackoverflow.com/questions/33759623/tensorflow-how-to-save-restore-a-model
"""

import argparse 
import tensorflow as tf

def load_graph(frozen_graph_filename):
    """We load the protobuf file from the disk and parse it to retrieve the 
    unserialized graph_def"""
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we import the graph_def into a new Graph and returns it 
    with tf.Graph().as_default() as graph:
        # The name var will prefix every op/nodes in your graph
        # Since we load everything in a new graph, this is not needed
        tf.import_graph_def(graph_def, name="prefix")
    return graph


if __name__ == '__main__':
    # Let's allow the user to pass the filename as an argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen_model_filename", default="results/frozen_model.pb", type=str, help="Frozen model file to import")
    args = parser.parse_args()

    # We use our "load_graph" function
    graph = load_graph(args.frozen_model_filename)

    # We can verify that we can access the list of operations in the graph
    for op in graph.get_operations():
        print(op.name)

    with graph.as_default():
        batch_size_placeholder = tf.placeholder(tf.int64, name='batch_size_ph')
        features_placeholder = tf.placeholder(tf.int64, [227, 227, 3], 'prefix/Placeholder')
        labels_placeholder = tf.placeholder(tf.int32, [None, 2], 'labels_data_ph')
        prediction = graph.get_tensor_by_name('prefix/model_outputs:0')

        input_sample = tf.random_uniform([227, 227, 3], minval=0, maxval=255, \
            dtype=tf.int32, seed=None, name="prefix/model_outputs")
        output_sample = tf.Variable(0, name="outputs")
        saver = tf.train.Saver()

        with tf.Session(graph=graph) as sess:
            # For tensorboard
            writer = tf.summary.FileWriter('logs', sess.graph)

            tf.global_variables_initializer().run(session=sess)
            # Saving
            inputs = {
                "batch_size_placeholder": batch_size_placeholder,
                "features_placeholder": features_placeholder,
                "labels_placeholder": labels_placeholder,
            }
            outputs = {"prediction": prediction}

            # Save a protobuf
            tf.saved_model.simple_save(
                sess, 'model_tf', inputs, outputs
            )
            
            # Save a checkpoint file, index and meta
            save_path = saver.save(sess, "./new_checkpoints/model.ckpt")

            # For tensorboard
            writer.close()