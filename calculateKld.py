import numpy as np
import pandas as pd
from scipy.stats import entropy


def getKLD(filename1, filename2):
    # Read files
    file1 = open(filename1, 'r')
    text1 = file1.read().split(" ")

    file2 = open(filename2, 'r')
    text2 = file2.read().split(" ") 

    # Get probability distributions
    dist1 = {}
    for word in text1:
        dist1[word] = dist1.get(word, 0) + 1


    dist2 = {}
    for word in text2:
        dist2[word] = dist2.get(word, 0) + 1

    # Normalize
    for word in dist1:
        dist1[word] = (dist1[word] / len(dist1))

    for word in dist2:
        dist2[word] = (dist2[word] / len(dist2))

    text1_data = list(dist1.values())
    text2_data = list(dist2.values())


    # Keep the lengths consistent
    if len(text1_data) < len(text2_data):
        text2_data = text2_data[:len(text1_data)]
    else:
        text1_data = text1_data[:len(text2_data)]


    relativeKLD = entropy(text1_data, text2_data) 
    return relativeKLD

if __name__ == "__main__":
    print("KLD: ", getKLD("data/englishfromchinese/scp-cn-369.txt","data/englishfromchinese/scp-cn-1000.txt"))
    