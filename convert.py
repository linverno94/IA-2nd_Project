#SECOND MINI PROJECT
#CONVERT FILE

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
        to_search = ["not", literal]
    
    return to_search 

#PARSER FUNCTION (to analyse the problem's information)    
    
def parser(filename):
    try:
        info = open(filename, "r")
        list_sentences = []
        for line in info:
            line = line.replace("(", "[")
            line = line.replace(")", "]")
            sentence = eval(line)
            sentence = list(sentence)
            list_sentences.append(sentence)
        info.close
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
#CONVERSION FUNCTIONS
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
#SIMPLIFICATION FUNCTIONS
#------------------------------------------------------------------------------

def remove_duplicates(clause): #A single clause is inputed
    newlist = []
    for literal in clause:
        if literal not in newlist:
            newlist.append(literal)
    return newlist

def remove_tautologies(clauses):
    global changes
    for clause in clauses:
        percorrer = []
        percorrer = clause.copy()
        if is_literal(clause) == False: #Tautologies are not present in unity clauses
            for literal in percorrer: 
                to_search = complement(literal)
                
                if to_search in clause:
                        changes = 1
                        clause.remove(literal)
                        clause.remove(to_search)
        
        if not clause:
            clauses.remove(clause) #Remove empty lists in clauses

def remove_redundancies(clauses):
    percorrer = clauses.copy()
    while percorrer:
        clause = percorrer.pop()
        if is_literal(clause) == True and is_negated(clause) == True:
            check = 0
            to_search = complement(clause)
            for component in clauses:
                    if to_search in component or to_search == component:
                        check = 1
                    
            if check == 0:
                clauses.remove(clause)
            
        else:
            for literal in clause:
                check = 0
                to_search = complement(literal)
                for component in clauses:
                    if to_search in component or to_search == component:
                        check = 1
                    
                if check == 0:
                    clauses.remove(clause)
                    break        
       
def check_subsets(clauses): #Verifies if there is any clause that is subset of another
    global changes          #If so, the largest clause is removed
    percorrer = []         
    percorrer = clauses.copy()
    while percorrer:
        subset = percorrer.pop()
        temp = clauses.copy()
        temp.remove(subset)
        for clause in temp:
            is_subset = True
            
            if is_literal(subset) == True:
                if subset not in clause and subset != clause:
                        is_subset = False
                        
            else:
                for element in subset:
                    if element not in clause:
                        is_subset = False
                        break
                
            if is_subset == True:
                changes = 1
                clauses.remove(clause)
                if clause in percorrer:
                    percorrer.remove(clause)
                

#------------------------------------------------------------------------------
#MAIN
#------------------------------------------------------------------------------                

s = parser("p1.txt")
cnf = []
for sentence in s:
    clauses = convert(sentence)
    for clause in clauses:
        clause = remove_duplicates(clause) #removes duplicates inside each clause
        cnf.append(clause)

#SIMPLIFICATION RULES
global changes #Flag that lets the program know if there are no simplifications left to be done
changes = 1
while changes ==1:
    changes=0
    remove_tautologies(cnf) #When a component and its complement exist in the same clause
    check_subsets(cnf) #NAO GOSTO DISTO, PERGUNTAR SE ISTO E VERDADE. Ao menos remove os duplicados...
    remove_redundancies(cnf) #Cheks if every component has its complement

#Remove excessive parentises after simplification
for clause in cnf:
    remove_parens(clause)


#Write to TXT FILE
filepath='cnf.txt'
with open(filepath, 'w') as file_handler:
    for item in cnf:
        file_handler.write("%s \n" % item)