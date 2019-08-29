# -*- coding: utf-8 -*-
"""
@author: João Ferreira
"""
import nltk.data
import os
from nltk.corpus import floresta
import nltk
import xmltodict

class Token:
	def __init__(self, line = 0,pos = 0,token = '',	lemma = '',	entity = '',contractions =[],clitics = [], ptoken='', tag=''):
		self.line = line
		self.pos = pos
		self.token = token
		self.ptoken = ptoken
		self.lemma = lemma
		self.entity = entity
		self.contractions = contractions
		self.clitics = clitics
		self.tag = tag

class Contractions:
	def __init__(self, contractions_path):
		with open(contractions_path) as fd:
			self.doc = xmltodict.parse(fd.read())
			self.result = (self.doc["contractions"]["replacement"])
	def replace_contrations(self, tokens):
		encontrou = 0
		#Check if tokens contain contractions
		#If so, change them to the most extended form

		newTokens = []
		for tok in tokens:
			encontrou = 0
			for elem in self.result:
				if(tok.token==elem['@target']):
					encontrou=1
					subs = elem['#text'].split(" ")
					tok.ptoken = "" #como tem contractions vamos criar dois tokens novos com a mesma posição e colocar o ptoken a vazio para n ser mais processado
					for part in subs:
						#criamos os novos tokens
						tok2 = Token(tok.line, tok.pos, tok.token, '', '', [], [], part,'')
						# adicionamos as contractions para ficarmos com a relação
						tok.contractions.append(part)
						newTokens.append(tok2)
			#if word in not contration add it as it was
			if(encontrou==0):
				tok.ptoken = tok.token
				tok.contractions= []
		tokens.extend(newTokens)	
		return tokens
		
class Cilitics:
	def __init__(self, clitics_path):
		with open(clitics_path) as fd:
			self.doc = xmltodict.parse(fd.read())
			self.result = (self.doc["clitics"]["replacement"])
	def replace_clitics(self, tokens):
		newTokens=[]
		for token in tokens:
			if(len(tokens)>0):
				encontrou = 0
				token2 = token.ptoken
				for elem2 in self.result:
					if(token.ptoken==elem2['@target']):
						encontrou=1
						subs = elem2['#text'].split(" ")
						token.ptoken = ''
						for part in subs:
							tok2 = Token(token.line, token.pos, token.token, '', '', [], [], part,'')
							token.clitics.append(part)
							newTokens.append(tok2)
				if(encontrou==0):
					withslash = token.ptoken.split("-")
					if(len(withslash)>1):
						nova_palavra = ""
						for parte in withslash:
							if(parte!=withslash[0]):
								nova_palavra +="-" + parte
						encontrou = 0
						token2 = token.ptoken
						for elem2 in self.result:
							if(nova_palavra==elem2['@target']):
								encontrou=1
								subs = elem2['#text'].split(" ")
								token.ptoken = ''
								for part in subs:
									tok2 = Token(token.line, token.pos, token.token, '', '', [], [], part,'')
									token.clitics.append(part)
									newTokens.append(tok2)
						#if word in not contration add it as it was
						if(encontrou==1):
							token.ptoken= withslash[0]+"-"
							token.clitics = []
				if(encontrou==0):
					token.clitics = []
		tokens.extend(newTokens)	
		return tokens

def load_token_configurations(config_file):
	contractions_path = ""
	clitics_path = ""
	with open(config_file) as g:
		for line in g:
			if(line[0]!="#"):
				if(line.split("=")[0]=="contractions"):
					contractions_path = line.split("=")[1].strip('\n')
				elif(line.split("=")[0]=="clitics"):
					clitics_path = line.split("=")[1].strip('\n')
	return contractions_path,clitics_path

def get_input_from_file(fileinput):
	text = []
	with open(fileinput,'r') as f:
		for line in f:
			text .append(line)
	return text

def nltk_tokenize(text):
	result = []
	for line in text:
		tok=(nltk.word_tokenize(line))
		for elem in tok:
			result.append(elem)
		result.append("\n")
	return result
def nlpyport_sent_tokenizer(text):
	sentences = []
	sent_tokenizer=nltk.data.load('tokenizers/punkt/portuguese.pickle')
	sentences = sent_tokenizer.tokenize(text)
	if(len(sentences)==0):
		sentences.append(text)
	return sentences
def nlpyport_tokenizer(text,TokPort_config_file, file=False, sentenceTokenizer=True):
	#define the tagset being used
	floresta.tagged_words(tagset = "pt-bosque")
	contractions_path = ""
	clitics_path = ""
	tokens=[]
	tokens_after_contractions = []
	tokens_after_clitics = []
	psentences = []
	
	#get the directory of the resources
	contractions_path,clitics_path = load_token_configurations(TokPort_config_file)
	contractions = Contractions(contractions_path)
	cilitics = Cilitics(clitics_path)
	
	if(file!= False):
		text = get_input_from_file(text)
	#Do thea actual tokenization
	tokensList = []
	if(sentenceTokenizer):
		sentences = nlpyport_sent_tokenizer(text)
		for i,sentence in enumerate(sentences):
			tokens = []
			tokens = nltk.word_tokenize(sentence)
			for t, token in enumerate(tokens):
				cToken = Token(i, t, token)
				tokensList.append(cToken)
			psentences.append({"tokens":tokens,"ftokens":[]}) 
			
	else:
		tokens = nltk_tokenize(text)
		for t, token in enumerate(tokens):
				cToken = Token(0, t, token)
				tokensList.append(cToken)
		psentences.append({"tokens":tokens,"ftokens":[]})
		
	tokensList = contractions.replace_contrations(tokensList)
	#print("line pos original token lema entity contractions clitics tag")
	#for token in tokensList:
	#	print ("%s | %s | %s | %s | %s |  %s | %s | %s | %s" % (token.line, token.pos, token.token, token.ptoken, token.lemma, token.entity, token.contractions, token.clitics, token.tag))

	#Check if tokens contain clitics
	#If so, change them to the most extended form
	
	tokens_after_clitics = cilitics.replace_clitics([tokens for tokens in tokensList if tokens.ptoken!=''])

	return tokens_after_clitics
'''
if __name__ == '__main__':
	print(nlpyport_tokenizer("EntradaCadeiaTotal.txt"))
'''
