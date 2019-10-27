import sys, pandas as pd
import numpy as np
import pandas as pd
from scipy.stats import entropy


def getKLD(filename1, filename2):
	# Read files

	try:
		file1 = open(filename1, 'r',encoding="utf8")
		file2 = open(filename2, 'r', encoding="utf8")
	except:
		return "None"
		
	text1 = file1.read().split(" ")
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


def parse(file):
	df = pd.read_csv(file)
	languageMap = {"cn":"chinese",
					"jp":"japanese",
					"fr":"french",
					"de":"german",
					"it":"italian",
					"ko":"korean",
					"pt":"portuguese",
					"ru":"russian",
					"es":"spanish",
					"th":"thai"}

	newCol = []
	for language in languageMap:
		if language in df["href"][1]:
			lang = languageMap[language]
			break
	for i in df.index:
		opath = "data/" + lang + "Originals" + df["href"][i] + ".txt"
		tpath = "data/" + "englishFrom" + lang + df["href"][i] + ".txt"
		result = getKLD(opath, tpath)
		newCol.append(result)
	assert(len(newCol) ==  df.shape[0])
	df["kld"] = newCol
	
	outfile = "data/kld/" + lang + "-kld.csv"
	df.to_csv(outfile, index = False)

if __name__=="__main__":
	files = ["data/chinese.csv", "data/french.csv", "data/german.csv",
	"data/italian.csv", "data/japanese.csv", "data/korean.csv",
	"data/portuguese.csv","data/russian.csv","data/spanish.csv",
	"data/thai.csv"]

	for file in files:
		parse(file)
