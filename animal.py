import csv


class Animal:
    def __init__(self, name, weight, speed, bite):
        self.name = name
        self.weight = weight
        self.speed = speed
        self.bite = bite


ANIMALS = []
with open('./animals.csv') as animals:
    animalData = csv.reader(animals, delimiter=',')
    for animal in animalData:
        ANIMALS.append(Animal(animal[0], animal[1] + " pounds", animal[2] +
                              " miles per hour", animal[3] + "pounds per square inch."))


def animal_exists(name):
    for animal in ANIMALS:
        if animal.name == name:
            return True
    return False


def get_animal(name):
    for animal in ANIMALS:
        if animal.name == name:
            return animal
