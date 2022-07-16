#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/7 10:10 AM
# @Author  : houlinjie
# @Site    : 
# @File    : propogation.py
# @Software: PyCharm


import math
import random
import numpy as np
import sys


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# derivative of sigmoid
def dsigmoid(y):
    return y * (1.0 - y)

# using tanh over logistic sigmoid is recommended
def tanh(x):
    return math.tanh(x)

# derivative for tanh sigmoid
def dtanh(y):
    return 1 - y * y

class MLP_NeuralNetwork(object):
    """
    An example is provided below with the digit recognition dataset
    provided
    """
    def __init__(self, input, hidden, output, iterations, learning_rate, momentum, rate_decay):
        """
        :param input: number of input neurons
        :param hidden: number of hidden neurons
        :param output: number of output neurons
        :param iterations:
        :param learning_rate:
        :param momentum:
        :param rate_decay
        """
        # initialize parameters
        self.iterations = iterations
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.rate_decay = rate_decay

        # initialize arrays
        self.input = input + 1 # add 1 for bias node
        self.hidden = hidden
        self.output = output

        # set up array of 1s for activations
        self.ai = [1.0] * self.input
        self.ah = [1.0] * self.hidden
        self.ao = [1.0] * self.output

        # create randomized  weights
        # use scheme from efficient backprop to initialize weights
        input_range = 1.0 / self.input ** (1 / 2)
        output_range = 1.0 / self.hidden ** (1 / 2)
        self.wi = np.random.normal(loc=0, scale=input_range, size=(self.input))
        self.wo = np.random.normal(loc=0, scale=output_range, size=(self.hidden))

        # create arrays of 0 for changes
        # this is essentially an array of temporary values that gets update
        # based on how much the weights need to change in the following it
        self.ci = np.zeros((self.input, self.hidden))
        self.co = np.zeros((self.hidden, self.output))

    def feedForward(self, inputs):
        if len(inptus) != self.input - 1;
            raise ValueError('Wrong number of inputs you silly goose!')

        # input activations
        for i in range(self.input - 1):
            self.ai[i] = inputs[i]

        # hidden activations
        for j in range(self.hidden):
            sum = 0.0
            for i in range(self.input):
                sum += self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # output activations
        for k in range(self.output):
            sum = 0.0
            for j in range(self.hidden):
                sum += self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)
        return self.ao[:]

    def backPropagate(self, targets):
