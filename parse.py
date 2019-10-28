import sys, pandas as pd
import numpy as np
import pandas as pd
from scipy.stats import entropy


def getEntropy(file, splitOnChars = False):
	try:
		file1 = open(file, 'r',encoding="utf8")
	except:
		return "None"


	if splitOnChars: 
		text1 = list(file1.read()) # Need to split on characters for languages like chinese
	else: 
		text1 = file1.read().split(" ")

	# Get probability distributions
	dist1 = {}
	for word in text1:
		dist1[word] = dist1.get(word, 0) + 1

	# Normalize
	for word in dist1:
		dist1[word] = (dist1[word] / len(dist1))

	text1_data = list(dist1.values())

	return entropy(text1_data) 

def parse(file, parseChars = False):
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

	originalCol = []
	translateCol = []
	differenceCol = []
	for language in languageMap:
		if language in df["href"][1]:
			lang = languageMap[language]
			break
	for i in df.index:
		opath = "data/" + lang + "Originals" + df["href"][i] + ".txt"
		tpath = "data/" + "englishFrom" + lang + df["href"][i] + ".txt"

		# Cleaning any E notation syntax using the double() func 
		try:
			origString = double(getEntropy(opath, parseChars))
		except Exception as e: 
			origString = getEntropy(opath, parseChars)

		try:
			transString = double(getEntropy(tpath, parseChars))
		except Exception as e:
			transString = getEntropy(tpath, parseChars)

		originalCol.append(origString)
		translateCol.append(transString)
		
		# try:
		# 	differenceCol.append(float(getEntropy(opath))- float(getEntropy(tpath)))	
		# except Exception as e:
		# 	pass # Format error 
		

	assert(len(originalCol) ==  len(translateCol) == df.shape[0])
	df["Original Entropy"] = originalCol
	df["Translated Entropy"] = translateCol
	# df["Change in E"] = differenceCol
	# header = columns = ['scpId','href','englishRating','englishDate','englishAuthor','chineseRating','chineseDate','chineseAuthor','chineseAuthorKudos','Original E','Translated E']
	# df.insert(11, "Change in Entropy", differenceCol, allow_duplicates=True)
	
	outfile = "data/kld/" + lang + "-entropy.csv"
	df.to_csv(outfile, index = False)

if __name__=="__main__":
	files = ["data/chinese.csv", "data/french.csv", "data/german.csv",
	"data/italian.csv", "data/japanese.csv", "data/korean.csv",
	"data/portuguese.csv","data/russian.csv","data/spanish.csv",
	"data/thai.csv"]

	for file in files:
		if file == "data/chinese.csv" or file == "data/korean.csv" or  file == "data/thai.csv" or file == "data/japanese.csv":
			parse(file, parseChars = True)
		else: 
			parse(file)
