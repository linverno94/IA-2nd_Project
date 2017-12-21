# =============================================================================
# ARTIFICIAL INTELIGENCE 1ST SEMETRE 2017-2018 TECNICO LISBOA
# CNF CONVERTER

#AUTORS:
#Leonor Inverno da Piedade 78588
#Rafael Freitas 78135
# =============================================================================

from datetime import datetime
from collections import defaultdict
import sys
import copy

#------------------------------------------------------------------------------
#GENERAL FUNCTIONS
#------------------------------------------------------------------------------

def is_negated(literal):
    if len(literal) == 1:
        return False
    else:
        return True
    
def is_literal(sentence):
    if len(sentence) == 1:
        return True
    elif len(sentence) ==2 and sentence[0] == "not":
        return True
    else:
        return False

def complement(literal):
    if is_negated(literal) == True:
                to_search = literal[1]
    else:
        to_search = ["not", literal[0]]
    
    return to_search 

#PARSER FUNCTION (to analyse the problem's information)    
    
def parser():
    try:
        #info = open(filename, "r")
        list_sentences = []
        for line in sys.stdin.readlines():
        #for line in info:
            line = line.replace("(", "[")
            line = line.replace(")", "]")
            sentence = eval(line)
            sentence = list(sentence)
            list_sentences.append(sentence)
        #info.close
        return list_sentences

    except FileNotFoundError:
        print("Error: File not found!")
        sys.exit()

      
#CONVERSION TO CNF

def convert(sentence):
    resolve_eq(sentence)
    resolve_imp(sentence)
    apply_neg(sentence)
    
    global check
    check = 0
    
    while check == 0:
        check = 1
        distributive(sentence)
        
    
    clauses = separate_clauses(sentence)
    for clause in clauses:
        remove_parens(clause) #Removes excessive parentises in clauses
    return clauses


#------------------------------------------------------------------------------
#CNF CONVERSION FUNCTIONS
#------------------------------------------------------------------------------

def resolve_eq(sentence):
    if sentence[0] == '<=>':
        new_condition1 = ['=>',sentence[1], sentence[2]]
        new_condition2 = ['=>', sentence[2], sentence[1]]
        sentence[0] = 'and'
        sentence[1] = new_condition1
        sentence[2] = new_condition2
        
    for element in sentence:
        if len(element)>=2 and type(element) != str:
            resolve_eq(element)

def resolve_imp(sentence):
    if sentence[0] == '=>':
        element1 = ["not", sentence[1]]
        element2 = sentence[2]
        sentence[0] = "or"
        sentence[1] = element1
        sentence[2] = element2
        
    for element in sentence:
        if len(element)>=2 and type(element) != str:
            resolve_imp(element)
            
            
            
def apply_neg(sentence):
    
    if sentence[0] == "not":
        to_negate = sentence[1]
        
        if to_negate[0] == "not":
            del sentence[:]
            for component in to_negate[1]:
                sentence.append(component)
        
        elif to_negate[0] == "or":
            element1 = ["not", to_negate[1]]
            element2 = ["not", to_negate[2]]
            del sentence[:]
            sentence.append("and")
            sentence.append(element1)
            sentence.append(element2)
            
        
        elif to_negate[0] == "and":
            element1 = ["not", to_negate[1]]
            element2 = ["not", to_negate[2]]
            del sentence[:]
            sentence.append("or")
            sentence.append(element1)
            sentence.append(element2)
            
    
    for element in sentence:
        if len(element)>1 and type(element) != str:
            apply_neg(element)
            
    
def distributive(sentence):
    global check
    if sentence[0] == "or":
        if sentence[1][0] == "and":
            element1 = ["or", sentence[1][1], sentence[2]]
            element2 = ["or",  sentence[1][2], sentence[2]]
            del sentence[:]
            sentence.append("and")
            sentence.append(element1)
            sentence.append(element2)
            check = 0
        elif sentence[2][0] == "and":
            element1 = ["or", sentence[1], sentence[2][1]]
            element2 = ["or", sentence[1], sentence[2][2]]
            del sentence[:]
            sentence.append("and")
            sentence.append(element1)
            sentence.append(element2)
            check = 0
    for element in sentence:
            if len(element)>=3 and type(element) != str:
                distributive(element)

def separate_clauses(sentence):
    clauses = []
    percorrer = []
    percorrer.append(sentence)
    while percorrer: #Separate by "and"
        condition = percorrer.pop()
        if condition[0] == "and":
            percorrer.append(condition[1])
            percorrer.append(condition[2])
        else:
            clauses.append(condition)
    
    eliminate_or(clauses) #Remove "or" conditions
            
    return clauses

def eliminate_or(clauses):
    for clause in clauses:
        if clause[0] == "or":
            clause.pop(0)
            
        if len(clause)>1:
            eliminate_or(clause)

#------------------------------------------------------------------------------
#SIMPLIFICATION FUNCTIONS
#------------------------------------------------------------------------------

def remove_duplicates(clause): #A single clause is inputed
    newlist = []
    for literal in clause:
        if literal not in newlist:
            newlist.append(literal)
    return newlist

def remove_parens(clause): #This function removes excessive parentises in the clauses
    temp = []              #resulted from previous operations
    
    if len(clause) == 1 and type(clause[0]) == list:
        clause[:] = clause[0]
        
    for components in clause:
        if type(components) == list and components[0] != "not": #if is not a negated literal
            temp = components[:]
            clause.remove(components)
            for element in temp:
                clause.append(element)
            remove_parens(clause)

#------------------------------------------------------------------------------
#MAIN
#------------------------------------------------------------------------------                


s = parser()

#s = parser("p4.txt")
cnf = []
for sentence in s:
    clauses = convert(sentence)
    for clause in clauses:
        clause = remove_duplicates(clause) #removes duplicates inside each clause
        cnf.append(clause)
        
#Remove excessive parentises after simplification
for clause in cnf:
    remove_parens(clause)

#print(cnf)

#Write to TXT FILE
#filepath='cnf.txt'
#with open(filepath, 'w') as file_handler:
for item in cnf:
    sys.stdout.write("%s" %item)
    sys.stdout.write("\n")
#        file_handler.write("%s \n" % item)




