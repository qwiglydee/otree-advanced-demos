import random


def bernoulli(p):
    return random.random() < p


def coin():
    return bernoulli(0.5)


def binomial(p, n):
    return (bernoulli(p) for _ in range(n))


def bernulchoice(p, a, b):
    return a if bernoulli(p) else b


def multinulchoice(probs, vals):
    [res] = random.choices(vals, probs, k=1)
    return res


def shuffled(lst: list):
    return random.sample(lst, k=len(lst))
