import tensorflow as tf
from tensorflow.keras.layers.experimental import preprocessing

import numpy as np
import os
import time

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

def buildModel(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
        tf.keras.layers.GRU(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dense(vocab_size)
    ])
    return model

def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def generateText(model, start_string, char2idx, idx2char):
    num_generate = 100

    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    text_generated = []

    temperature = 1.0

    model.reset_states()

    for i in range(num_generate):
        predictions = model(input_eval)

        predictions = tf.squeeze(predictions, 0)

        predictions = predictions / temperature
        
        predicted_id = tf.random.categorical(predictions, num_samples = 1)[-1, 0].numpy()

        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(idx2char[predicted_id])

    return (start_string + ''.join(text_generated))


def textRNN(tweets):
    text = tweets
    vocab = sorted(set(text))
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)
    text_as_int = np.array([char2idx[c] for c in text])
    seq_length = 200
    examples_per_epoch = len(text)//(seq_length + 1)
    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
    sequences = char_dataset.batch(seq_length+1, drop_remainder=True)
    dataset = sequences.map(split_input_target)
    BATCH_SIZE = 64
    BUFFER_SIZE = 10000
    dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
    vocab_size = len(vocab)
    embedding_dim = 256
    rnn_units = 4096
    model = buildModel(vocab_size = vocab_size, embedding_dim = embedding_dim, rnn_units = rnn_units, batch_size = BATCH_SIZE)

    print(dataset.take(1))

    """for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)

    sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples = 1)
    sampled_indices = tf.squeeze(sampled_indices, axis = -1).numpy()

    example_batch_loss = loss(target_example_batch, example_batch_predictions)"""
    
    model.compile(optimizer='adam', loss=loss)

    checkpoint_dir = './training_checkpoints'

    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath = checkpoint_prefix,
        save_weights_only = True
    )

    EPOCHS = 10

    history = model.fit(dataset, epochs = EPOCHS, callbacks = [checkpoint_callback])

    tf.train.latest_checkpoint(checkpoint_dir)

    model = buildModel(vocab_size, embedding_dim, rnn_units, batch_size = 1)

    model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

    model.build(tf.Tensorshape([1, None]))

    textgen = generateText(model, "A", char2idx, idx2char)

    print(textgen)

textRNN('The climate crisis is here. We need a #GreenNewDeal. More than 20 years ago, Sergei Krikalev arrived at the @Space_Station with his crewmates to begin an unbroken streak of h… The filibuster is a Jim Crow relic that must be abolished. Imagine a world without Halloween. Or The Thing. Or Escape from New York. Or The Fog. Or Christine. Or Big Trouble in Litt… why doesn’t GINGER have an official vinyl release. that’s fucked up #WandaVision is #CertifiedFresh at 97 on the #Tomatometer, with 113 reviews. ')