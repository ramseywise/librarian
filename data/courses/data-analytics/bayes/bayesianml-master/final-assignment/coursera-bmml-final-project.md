---
imported_hash: c6efcf93e01a469f
title: 'Final project: Finding the suspect'
summary: In this project we will try to implement an app for crating facial composite that will be able to construct desired faces without explicitly providing databases of templates.
order: 2
kind: notebook
section: BayesianML master / Final assignment
source: learn-ai-engineering/data-analytics/Bayes/BayesianML-master/final_assignment/Coursera BMML, Final project.ipynb
---

# Final project: Finding the suspect

<a href="https://en.wikipedia.org/wiki/Facial_composite.">Facial composits</a> are widely used in forensics to generate images of suspects. Since victim or witness usually isn't good at drawing, computer-aided generation is applied to reconstruct the face attacker. One of the most commonly used techniques are evolutionary systems that compose the final face from many predefined parts.

In this project we will try to implement an app for crating facial composite that will be able to construct desired faces without explicitly providing databases of templates. We will apply Variational Autoencoders and Gaussian processes for this task.

Final project is developed in a way that you can apply learned techniques to real project yourself. We will include main guidelines and hints, but great part of the project will need your creativity and experience from previous assignments.

### Installation

We will need ```tensorflow```, ```keras```, ```GPy```, ```GPyOpt```, ```h5py``` libraries for this assignment.

```python
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import clear_output
import tensorflow as tf
import GPy
import GPyOpt
import keras
from keras.layers import Input, Dense, Lambda, InputLayer, concatenate, Activation, Flatten, Reshape
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D, Deconv2D
from keras.losses import MSE
from keras.models import Model, Sequential
from keras import backend as K
from keras import metrics
from keras.datasets import mnist
from keras.utils import np_utils
from tensorflow.python.framework import ops
from tensorflow.python.framework import dtypes
import utils
import os
%matplotlib inline
```

### Grading
As some of the final project tasks can be graded only visually, final assignment is graded using peer-review procedure. You will be asked to upload your Jupyter notebook on the web and attach link to it in the submission form. Detailed submission instructions and grading criterions are written in the end of this notebook.

## Model description
We will first train variational autoencoder on face images to compress them to low dimension. One important feature of VAE is that constructed latent space is in some sence continous. That means, that we can safely move along the space and any point along our path will be reconstructed into a valid face.

Using this continuous latent space we can use bayesian optimization to maximise some similarity function between person's face in victim/witness's memory and a face reconstructed from current point of latent space. Bayesian optimization is an appropriate choice here, since people start to forget detales about the attacker after they were shown many similar photos. Because of this, we want to reconstruct the photo with the smallest possible number of trials.

## Generating faces

For this task you will need to use some database of face images. There are multiple datasets available on the web that you can use: for example, <a href="http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html">CelebA</a> or <a href="http://vis-www.cs.umass.edu/lfw/">Labeled Faces in the Wild</a>. We used Alligned & Cropped version of CelebA that you can find <a href="https://www.dropbox.com/sh/8oqt9vytwxb3s4r/AADSNUu0bseoCKuxuI5ZeTl1a/Img?dl=0&preview=img_align_celeba.zip">here</a> to pretrain VAE model for you. See optional part of final project if you whish to train VAE on your own.

<b>Task 1:</b> Train VAE on faces dataset and draw some samples from it. (You can use code from previous assignmnets. You may also want to use convolutional encoders and decoders as well as tuning hyperparameters)

```python
sess = tf.InteractiveSession()
K.set_session(sess)
```

```python
latent_size = 8
```

```python
vae, encoder, decoder = utils.create_vae(batch_size=128, latent=latent_size)
sess.run(tf.global_variables_initializer())
vae.load_weights('CelebA_VAE_small_8.h5')
```

```python
K.set_learning_phase(False)
```

```python
latent_placeholder = tf.placeholder(tf.float32, (1, latent_size))
decode = decoder(latent_placeholder)
```

#### GRADED 1 (3 points): Draw 25 samples from trained VAE model
As first part of assignment, you need to become familiar with trained model. For all tasks you will only need a decoder to reconstruct samples froma a latent space.

To decode latent variable, you need to run ```decode``` operation defined above with random samples from standard normal distribution.

```python
### TODO: Draw 25 samples from VAE here
plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i+1)
    # Sample z for N(0,I)
    z_latent = np.random.normal(size=(1,latent_size))
    # Run the decoder tensor
    image = sess.run(decode,feed_dict = {latent_placeholder:z_latent})
    # Get rid of the extra dimension (since batch_size is 1)
    image = image[0,:,:,:]
    plt.imshow(np.clip(image, 0, 1))
    plt.axis('off')
```

## Search procedure

Now that we have a way to reconstruct images, we need to set up an optimization procedure to find a person that will be the most similar to the one we are thinking about. To do so, we need to set up some scoring utility. Imagine that you want to generate an image of Brad Pitt. You start with a small number of random samples, say 5, and rank them according their similarity to your vision of Brad Pitt: 1 for the worst, 5 for the best. You then rate image by image using GPyOpt that works in a latent space of VAE. For the new image you need to somehow assign a real number that will show how good this image is. The simple idea is to ask a user to compare a new image with previous images (along with their scores). User then enters score to a current image.

The proposed scoring has a lot of drawbacks, and you may feel free to come up with new ones: e.g. showing user 9 different images and asking a user which image looks the "best".

Note that the goal of this task is for you to implement a new algorithm by yourself. You may try different techniques for your task and select one that works the best.

<b>Task 2:</b> Implement person search using Bayesian optimization. (You can use code from the assignment on Gaussian Processes)

Note: try varying ```acquisition_type``` and ```acquisition_par``` parameters.

```python
class FacialComposit:
    def __init__(self, decoder, latent_size,n_iter=10,n_start=10,select_top=5):
        self.latent_size = latent_size
        self.latent_placeholder = tf.placeholder(tf.float32, (1, latent_size))
        self.decode = decoder(self.latent_placeholder)
        self.samples = None
        self.images = None
        self.rating = None
        self.n_iter = n_iter
        self.n_start = n_start
        self.select_top = select_top

    def _get_image(self, latent):
        img = sess.run(self.decode,
                       feed_dict={self.latent_placeholder: latent[None, :]})[0]
        img = np.clip(img, 0, 1)
        return img

    @staticmethod
    def _show_images(images, titles):
        assert len(images) == len(titles)
        clear_output()
        plt.figure(figsize=(3*len(images), 3))
        n = len(titles)
        for i in range(n):
            plt.subplot(1, n, i+1)
            plt.imshow(images[i])
            plt.title(str(titles[i]))
            plt.axis('off')
        plt.show()

    @staticmethod
    def _draw_border(image, w=2):
        bordred_image = image.copy()
        bordred_image[:, :w] = [1, 0, 0]
        bordred_image[:, -w:] = [1, 0, 0]
        bordred_image[:w, :] = [1, 0, 0]
        bordred_image[-w:, :] = [1, 0, 0]
        return bordred_image

    def query_initial(self, n_start=5, select_top=None):
        '''
        Creates initial points for Bayesian optimization
        Generate *n_start* random images and asks user to rank them.
        Gives maximum score to the best image and minimum to the worst.
        :param n_start: number of images to rank initialy.
        :param select_top: number of images to keep
        '''
        self.samples = np.random.normal(size=(n_start,self.latent_size)) ### YOUR CODE HERE (size: select_top x latent_size)
        self.images = np.asarray([self._get_image(self.samples[idx]) for idx in range(n_start)]) ### YOUR CODE HERE (size: select_top x 64 x 64 x 3)
        self.rating = []

        selected_idx = []
        self._show_images(self.images,range(n_start))
        num_questions = 0

        while(num_questions < select_top):
            idx = int(input("Enter Image ID"))
            # Each image must be assigned a rating only once.
            if idx in selected_idx:
                print("A rating has already been entered for this image, try another image")
                #TODO : Ask user if they want to overwrite their previous score
                continue

            r = int(input("Enter rating between 1-5:"))
            selected_idx.append(idx)
            self.rating.append(r)
            num_questions += 1

        # Trim the lists based on user responses
        self.images = self.images[selected_idx]
        self.samples = self.samples[selected_idx]
        self.rating = np.asarray(self.rating)

        # Check that tensor sizes are correct
        np.testing.assert_equal(self.rating.shape, [select_top])
        np.testing.assert_equal(self.images.shape, [select_top, 64, 64, 3])
        np.testing.assert_equal(self.samples.shape, [select_top, self.latent_size])

    def evaluate(self, candidate):
        '''
        Queries candidate vs known image set.
        Adds candidate into images pool.
        :param candidate: latent vector of size 1xlatent_size
        '''
        initial_size = len(self.images)
        image = self._get_image(candidate[0])

        current_best_index = self.get_best()

        self._show_images([image,self.images[current_best_index]],["Current Image","Current Best Image"])

        candidate_rating = int(input("Enter rating for the current image : "))### YOUR CODE HERE

        # Update lists
        self.rating = np.append(self.rating,np.asarray([candidate_rating]),axis=0)
        self.images = np.append(self.images,[image],axis=0)
        self.samples = np.append(self.samples,np.asarray([candidate[0]]),axis=0)


        assert len(self.images) == initial_size + 1
        assert len(self.rating) == initial_size + 1
        assert len(self.samples) == initial_size + 1
        return candidate_rating

    def optimize(self, w=4, acquisition_type='MPI', acquisition_par=0.3):
        if self.samples is None:
            self.query_initial(n_start=self.n_start,select_top=self.select_top)

        bounds = [{'name': 'z_{0:03d}'.format(i),
                   'type': 'continuous',
                   'domain': (-w, w)}
                  for i in range(self.latent_size)]
        optimizer = GPyOpt.methods.BayesianOptimization(f=self.evaluate, domain=bounds,
                                                        acquisition_type = acquisition_type,
                                                        acquisition_par = acquisition_par,
                                                        exact_eval=False, # Since we are not sure
                                                        model_type='GP',
                                                        X=self.samples,
                                                        Y=self.rating[:, None],
                                                        maximize=True)

        optimizer.run_optimization(max_iter=self.n_iter, eps=-1)
        # Show all images used to reach the final one
        print('Images sampled in the search')
        self._show_images(self.images,range(len(self.images)))

    def get_best(self):
        # In case of tied scores, return the last image in the search
        index_list = np.where(self.rating == np.amax(self.rating))[0]
        index_best = index_list[-1]
        return index_best

    def draw_best(self, title=''):
        index_best = self.get_best()
        image = self.images[index_best]
        plt.imshow(image)
        plt.title(title)
        plt.axis('off')
        plt.show()
```

#### GRADED 2 (3 points):
Describe your approach below: How do you assign score to a new image? How do you select reference images to help user assign a new score? What are the limitations of your approach?

#### My Approach:

The basic idea is very simple, the app starts off with asking the user to rank randomly generated images based on the presence (or lack thereof) of some pre-defined characteristic. Taking these initial images and their ratings, the Bayesian Optimization method takes over by sampling points across the latent space and showing the user images that are likelier to have the desired feature. To help the user provide an accurate rating, the 'evaluate' functions shows the current best (most highly rated, recent image) to the user along with the current image that the user needs to rate.

The key characteristic of this approach is the how the points from the latent space are sampled. This is controlled by the acquisition type. A popular acquisition type that is supported by the GPyOpt library is 'Expected Improvement' (EI). The acquisition parameter controls the exploration (sample from regions with high uncertainty) and exploitation (sample from region with high certainty of a good score) trade-off. Higher values of this parameter lead to a more 'explorative' sampling. The recommended value is 0.01.

#### Drawback:

This approach is not consistent i.e. multiple runs would lead different "final" images. This however is unavoidable due to the subjective nature of the metric and the randomness in the initial choices provided.

## Testing your algorithm

In the these sections we will apply implemented app to search of different people. Each task will ask you to generate images that will have some property like "dark hair" or "moustache". You will need to run your search algorithm and provide best found image.

#### Task 3.1: Finding person with darkest hair (3 points)

```python
composit = FacialComposit(decoder, 8)
composit.optimize(acquisition_type='EI',acquisition_par=0.01)
```

```python
composit.draw_best('Darkest hair')
```

#### Task 3.2. Finding person with the widest smile (3 points)

```python
composit = FacialComposit(decoder, 8)
composit.optimize(acquisition_type='EI',acquisition_par=0.01)
```

```python
composit.draw_best('Widest smile')
```

#### Task 3.3. Finding Daniil Polykovskiy or Alexander Novikov — lecturers of this course (3 points)

Note: this task highly depends on a quality of VAE and search algorithm. You may need to restart your search algorithm a few times and start with larget initial set.

```python
composit = FacialComposit(decoder, 8,n_start=20,select_top=10)
composit.optimize(acquisition_type='EI',acquisition_par=0.01)
```

```python
composit.draw_best('Lecturer')
```

#### <small>Don't forget to post resulting image of lecturers on the forum ;)</small>

#### Task 3.4. Finding specific person (optional, but very cool)

Now that you have a good sence of what your algorithm can do, here is an optional assignment for you. Think of a famous person and take look at his/her picture for a minute. Then use your app to create an image of the person you thought of. You can post it in the forum <a href="https://www.coursera.org/learn/bayesian-methods-in-machine-learning/discussions/forums/SE06u3rLEeeh0gq4yYKIVA">Final project: guess who!</a>

```python
### Your code here
```

### Submission
You should submit an HTML version of your work. To convert your notebook to HTML, press file $\rightarrow$ download as $\rightarrow$  HTML (.html). Make sure that resulting html file can be opened when copied to a separate folder (that all of the images are present). You should attach only your html file to the peer review console.

### Grading criterions

#### Task 1 (3 points) [samples from VAE]
* 0 points: No results were provided here or provided images were not generated by VAE
* 1 point: Provided images poorly resemble faces
* 2 points: Provided images look like faces, maybe with some artifacts, but all look the same
* 3 points: Provided images look like faces, maybe with some artifacts, and look different

#### Task 2 (3 points) [training procedure]
* 0 points: No result was provided
* 1 point: Some algorithm was proposed, but it does not use Bayesian optimization
* 2 points: Algorithm was proposed, but there were no details on some important aspects: how to assign a score to a new image / how to you select a new image / what are the limitations of the approach
* 3 points: Algorithm was proposed, all questions in the task were answered

#### Tasks 3.1-3.3 (3 points each) [search for person]
* 0 points: Nothing was provided
* 1 point: Resulting image was provided, but some of the required images (evolution & nearest image) are not provided
* 2 points: All images are provided, but resulting image does not have requested property
* 3 points: All images are provided, resulting image has required features (long hair / wide smile / looks like lecturer)

## Passing grade is 60% (9 points)
