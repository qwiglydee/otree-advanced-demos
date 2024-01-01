from random import random


def bernoulli(p):
    return random() < p


def binomial(p, n):
    return(bernoulli(p) for _ in range(n))


def bernulchoice(p, a, b):
    return a if bernoulli(p) else b