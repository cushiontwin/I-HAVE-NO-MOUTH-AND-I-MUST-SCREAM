import multiprocessing
import pygame_stuff
import bomb


if __name__ == "__main__":
    # A pipe lets the processes communicate both ways
    connA, connB = multiprocessing.Pipe()

    pB = multiprocessing.Process(target=bomb.run, args=(connB,))
    pA = multiprocessing.Process(target=pygame_stuff.run, args=(connA,))

    pB.start()
    pA.start()

    pB.join()
    pA.join()
