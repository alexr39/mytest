#import librarys 
import json
import difflib
from difflib import get_close_matches


# now i need to load json data from file to python dict
data = json.load(open("dictionary.json"))


#simple function for retriving definition
def retrive_definition(word):
	#remove upper letters from input
	word = word.lower()
	
	#1st elif
	#2nd elif

	if word in data:
		return data[word]
	elif word.title() in data:
		return data[word.title()]
	elif word.upper() in data:
		return data[word.upper()]
	elif len(get_close_matches(word, data.keys())) > 0:
		action = input("Did you mean %s instead? [y or n]" %get_close_matches(word, data.keys())[0])
		if action == "y":
			return data[get_close_matches(word,data.keys())[0]]
		elif action == "n":
			return("The word doesn't exist, yet.")
		else:
			return("We don't understand your entry. Apologes.")
	else:
		return("This word doesn't exist, please double check it.")


#input word from keyboard by user
word_user = input("Enter a word: ")



#Retive definition usinf function

output = (retrive_definition(word_user))
if type(output) == list:
	for item in output:
		print("-", item)
else:
	print("-", output)