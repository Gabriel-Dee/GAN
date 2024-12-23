# -*- coding: utf-8 -*-
"""GAN - Synthetic data Generator.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1N4S5Jqq00FPhHNYVpH0QiVxd1KWitWcQ

# Using Generative AI with Python to Generate Synthetic Data

**Abstract**
This paper explores advanced techniques in generative artificial intelligence (AI), focusing on Generative Adversarial Networks (GANs) and Variational Autoencoders (VAEs), to generate synthetic time-series data. Specifically, we tailor these techniques to a fictional use case in the retail space and compare the generated data with traditional methods to demonstrate the advantages of using generative AI over traditional methods such as ARIMA and rule-based models. The study provides a comprehensive overview of these advanced models, their theoretical foundations, implementation details using Python, and practical applications.

**Introduction**
bold textGenerative AI models aim to create new data samples that resemble a given dataset. These models have revolutionized fields such as image synthesis, natural language processing, and data augmentation. While basic generative models provide a foundation, advanced techniques like GANs and VAEs offer enhanced capabilities and performance. This paper delves into these advanced models, presenting their architectures, implementation strategies, and applications.

**Background**
Generative Adversarial Networks (GANs) — Introduced by Goodfellow et al. (2014), GANs consist of two neural networks, a generator and a discriminator, that engage in a zero-sum game. The generator creates fake data samples, while the discriminator attempts to distinguish between real and fake samples. The training process iteratively refines both models, leading to the generation of highly realistic data.

Variational Autoencoders (VAEs) — Proposed by Kingma and Welling (2013), VAEs are probabilistic generative models that encode input data into a latent space and decode it back to the original space. This encoding-decoding process allows VAEs to generate new data samples by sampling from the latent space, making them suitable for applications requiring data interpolation and generation.

**Implementation Example:**
Generating Time-Series Data for a Retail Store.
In this section, we will implement GANs and VAEs to generate synthetic time-series data for a fictional retail use case: generating daily sales data for a chain of retail stores. We will compare the results with traditional data generation methods.

**Use Case Description**
bold textA retail chain wants to generate synthetic daily sales data for their stores to test and validate their predictive models. This data includes the daily sales figures over a month (30 days) for multiple stores. The goal is to create realistic sales data that can be used to improve inventory management, optimize pricing strategies, and forecast future sales trends.

**System Requirements**

Python 3.7+
TensorFlow 2.0+
NumPy
Matplotlib
statsmodels
A system with at least 8GB RAM and a CPU or GPU for faster computation.

## **Generative Adversarial Networks (GANs)**

The GAN architecture comprises two
main components:
- Generator: Produces fake time-series data from random noise.
- Discriminator: Classifies time-series data as real or fake.
"""

!pip show tensorflow

import tensorflow as tf
print(tf.__version__)

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

# Generator model for time-series data
def build_generator():
    inputs = layers.Input(shape=(30, 1))
    x = layers.LSTM(100, return_sequences=True)(inputs)
    x = layers.LSTM(50)(x)
    x = layers.Dense(30, activation='linear')(x)
    outputs = layers.Reshape((30, 1))(x)
    model = tf.keras.Model(inputs, outputs)
    return model

# Discriminator model for time-series data
def build_discriminator():
    inputs = layers.Input(shape=(30, 1))
    x = layers.LSTM(50, return_sequences=True)(inputs)
    x = layers.LSTM(50)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = tf.keras.Model(inputs, outputs)
    return model

# Compile the models
generator = build_generator()
discriminator = build_discriminator()
discriminator.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Combine the models
discriminator.trainable = False
gan_input = layers.Input(shape=(30, 1))
gan_output = discriminator(generator(gan_input))
gan = tf.keras.Model(gan_input, gan_output)
gan.compile(optimizer='adam', loss='binary_crossentropy')

"""## Training Procedure:"""

# Generate synthetic retail sales data
def generate_real_data(n_samples):
    # Generate 'n_samples' of time-series data with 30 time steps each
    X = np.linspace(0, 100, n_samples * 30).reshape(n_samples, 30, 1)
    y = np.sin(X) + np.random.normal(scale=0.5, size=X.shape)
    return y

# Training loop
def train_gan(generator, discriminator, gan, epochs=1000, batch_size=32):
    for epoch in range(epochs):
        # Generate real and fake data
        real_data = generate_real_data(batch_size)
        noise = np.random.normal(0, 1, (batch_size, 30, 1))
        fake_data = generator.predict(noise)

        # Train discriminator
        d_loss_real = discriminator.train_on_batch(real_data, np.ones((batch_size, 1)))
        d_loss_fake = discriminator.train_on_batch(fake_data, np.zeros((batch_size, 1)))
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # Train generator
        noise = np.random.normal(0, 1, (batch_size, 30, 1))
        valid_y = np.array([1] * batch_size)
        g_loss = gan.train_on_batch(noise, valid_y)

        # Print the progress
        if epoch % 100 == 0:
            print(f"{epoch} [D loss: {d_loss[0]}, acc.: {100*d_loss[1]}%] [G loss: {g_loss}]")

# Train the GAN
train_gan(generator, discriminator, gan)

"""## **Variational Autoencoders (VAEs)**

Architecture:

The VAE architecture includes:

- Encoder: Maps input time-series data to a latent space.
- Decoder: Reconstructs time-series data from the latent space.
"""

from tensorflow.keras import backend as K

# Encoder model for time-series data
def build_encoder(input_shape, latent_dim):
    inputs = tf.keras.Input(shape=input_shape)
    x = layers.LSTM(50, return_sequences=True)(inputs)
    x = layers.LSTM(50)(x)
    z_mean = layers.Dense(latent_dim)(x)
    z_log_var = layers.Dense(latent_dim)(x)
    return tf.keras.Model(inputs, [z_mean, z_log_var])

# Sampling layer
def sampling(args):
    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

# Decoder model for time-series data
def build_decoder(latent_dim, output_shape):
    inputs = tf.keras.Input(shape=(latent_dim,))
    x = layers.Dense(50)(inputs)
    x = layers.RepeatVector(output_shape[0])(x)
    x = layers.LSTM(50, return_sequences=True)(x)
    x = layers.TimeDistributed(layers.Dense(output_shape[1]))(x)
    return tf.keras.Model(inputs, x)

# Define VAE model
input_shape = (30, 1)
latent_dim = 10

encoder = build_encoder(input_shape, latent_dim)
decoder = build_decoder(latent_dim, input_shape)

inputs = tf.keras.Input(shape=input_shape)
z_mean, z_log_var = encoder(inputs)
z = layers.Lambda(sampling)([z_mean, z_log_var])
outputs = decoder(z)

vae = tf.keras.Model(inputs, outputs)

# Define VAE loss
reconstruction_loss = tf.keras.losses.mean_squared_error(K.flatten(inputs), K.flatten(outputs))
reconstruction_loss *= input_shape[0] * input_shape[1]
kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
kl_loss = -0.5 * K.sum(kl_loss, axis=-1)
vae_loss = K.mean(reconstruction_loss + kl_loss)

vae.add_loss(vae_loss)
vae.compile(optimizer='adam')

"""## Training Procedure:"""

# Train the VAE
vae.fit(generate_real_data(1000), epochs=50, batch_size=32)

"""**Comparing with Traditional Methods**
Traditional methods for generating synthetic time-series data include:

- Statistical Models: Autoregressive Integrated Moving Average (ARIMA), Exponential Smoothing.
- Rule-Based Systems: Generating data based on predefined rules and patterns.

To compare, we will evaluate the quality and diversity of the synthetic data generated by GANs, VAEs, and traditional methods.

**Quality Assessment**
- Visual Inspection: Plot synthetic data samples to visually assess realism.
- Statistical Measures: Compare statistical properties (mean, variance, autocorrelation) of synthetic and real data.

**Diversity Assessment**
- Coverage: Measure how well the synthetic data covers the range of the real data.
- Novelty: Evaluate the introduction of new, plausible patterns not present in the training data.

## ARIMA
"""

import pandas as pd
import statsmodels.api as sm

# Generate synthetic retail sales data for ARIMA
real_data_arima = generate_real_data(100).flatten()

# Fit ARIMA model
arima_model = sm.tsa.ARIMA(real_data_arima, order=(5, 1, 0))
arima_fit = arima_model.fit()

# Generate predictions
arima_pred = arima_fit.predict(start=0, end=len(real_data_arima)-1, typ='levels')

# Reshape predictions to match the shape of other data
arima_pred = arima_pred.values.reshape(100, 30, 1)

"""## Rule-Based System"""

# Generate synthetic retail sales data using rule-based system
def generate_rule_based_data(n_samples):
    # Generate 'n_samples' of time-series data with 30 time steps each
    X = np.linspace(0, 100, n_samples * 30).reshape(n_samples, 30, 1)
    y = np.sin(X) * (1 + 0.1 * np.random.randn(*X.shape))
    return y

# Generate rule-based data
rule_based_data = generate_rule_based_data(100)

"""## Advantages of Using Generative AI
Generative AI offers several advantages over traditional methods:

- Realism: GANs and VAEs can produce highly realistic data that closely mimics real-world patterns.
- Flexibility: Generative models can learn complex dependencies and generate diverse data samples.
- Scalability: Once trained, these models can generate large volumes of synthetic data quickly.

## Future and Ethical Considerations
Generative AI continues to evolve, with trends such as improved architectures, cross-modal generation, and increased emphasis on ethical considerations. As generative models become more powerful, addressing ethical issues like data privacy and misuse is crucial.
"""