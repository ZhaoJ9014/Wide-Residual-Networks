import numpy as np
import sklearn.metrics as metrics

import wide_residual_network as wrn
from keras.datasets import cifar10
import keras.callbacks as callbacks
import keras.utils.np_utils as kutils
from keras.preprocessing.image import ImageDataGenerator
from keras.utils.visualize_util import plot

from keras import backend as K

batch_size = 64
nb_epoch = 100
img_rows, img_cols = 32, 32

(trainX, trainY), (testX, testY) = cifar10.load_data()

trainX = trainX.astype('float32')
trainX /= 255.0
testX = testX.astype('float32')
testX /= 255.0

tempY = testY
trainY = kutils.to_categorical(trainY)
testY = kutils.to_categorical(testY)

generator = ImageDataGenerator(featurewise_center=True,
                               featurewise_std_normalization=True,
                               rotation_range=10,
                               width_shift_range=5./32,
                               height_shift_range=5./32,
                               horizontal_flip=True)

generator.fit(trainX, seed=0, augment=True)

test_generator = ImageDataGenerator(featurewise_center=True,
                                    featurewise_std_normalization=True,)

test_generator.fit(testX, seed=0, augment=True)

init_shape = (3, 32, 32) if K.image_dim_ordering() == 'th' else (32, 32, 3)

# For WRN-16-8 put N = 2, k = 8
# For WRN-28-10 put N = 4, k = 10
# For WRN-40-4 put N = 6, k = 4
model = wrn.create_wide_residual_network(init_shape, nb_classes=10, N=4, k=8, dropout=0.0)

model.summary()
#plot(model, "WRN-28-8.png", show_shapes=False)

model.compile(loss="categorical_crossentropy", optimizer="adadelta", metrics=["acc"])
print("Finished compiling")
print("Allocating GPU memory")

model.load_weights("weights/WRN-28-8 Weights.h5")
print("Model loaded.")

#model.fit_generator(generator.flow(trainX, trainY, batch_size=batch_size), samples_per_epoch=len(trainX), nb_epoch=nb_epoch,
#                    callbacks=[callbacks.ModelCheckpoint("WRN-28-8 Weights.h5", monitor="val_acc", save_best_only=True)],
#                    validation_data=test_generator.flow(testX, testY, batch_size=batch_size),
#                    nb_val_samples=testX.shape[0],)

scores = model.evaluate_generator(test_generator.flow(testX, testY, nb_epoch), testX.shape[0])
print("Accuracy = %f" % (100 * scores[1]))