import random


def bernoulli(p):
    return random.random() < p


def binomial(p, n):
    return (bernoulli(p) for _ in range(n))


def bernulchoice(p, a, b):
    return a if bernoulli(p) else b


def shuffled(lst: list):
    return random.sample(lst, k=len(lst))
