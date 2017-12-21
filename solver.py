# =============================================================================
# ARTIFICIAL INTELIGENCE 1ST SEMETRE 2017-2018 TECNICO LISBOA
# RESOLUTION SOLVER

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
            sentence = eval(line)
            sentence = list(sentence)
            list_sentences.append(sentence)
        #info.close
        return list_sentences

    except FileNotFoundError:
        print("Error: File not found!")
        sys.exit()

#------------------------------------------------------------------------------
#Solver Functions
#------------------------------------------------------------------------------

#This functions finds a candidate clause to apply resolution with the clause being analysed
def find_compatible_clause(percorrer, start_index, to_search, already_solved):
    
    for j in range(start_index, len(percorrer)):
        if is_literal(percorrer[j]) == True and is_negated(percorrer[j]) == True:
            if to_search == percorrer[j] and  [percorrer[start_index],percorrer[j]] not in already_solved:
                return percorrer[j]
        else:
            if to_search in percorrer[j] and [percorrer[start_index],percorrer[j]] not in already_solved:
                return percorrer[j]
    
    return False

#RESOLUTION FUNCTION
        
def resolution(clause1, clause2): #best if clause1 is smaller then clause2
    if is_literal(clause1) == True:
        to_search = complement(clause1)
        for element in clause2:
            if element == to_search:
                temp2 = clause2.copy()
                temp2.remove(to_search)
                return temp2
    else:
        for element in clause1:
            to_search = complement(element)
            for literal2 in clause2:
                if literal2 == to_search:
                    temp1 = clause1.copy()
                    temp2 = clause2.copy()
                    temp1.remove(element)
                    temp2.remove(to_search)
                    for literal in temp2:
                        temp1.append(literal)
                    return temp1

#------------------------------------------------------------------------------
#SIMPLIFICATION FUNCTIONS
#------------------------------------------------------------------------------
  
def remove_duplicates(clause): #A single clause is inputed
    newlist = []
    for literal in clause:
        if literal not in newlist:
            newlist.append(literal)
    return newlist

def remove_tautologies(clause, one_clause):
    
    if one_clause == True: #Algorithm used when a single clause is inputed
        if is_literal(clause) == False: #Tautologies are not present in literals
            for literal in clause: 
                to_search = complement(literal)
                
                if to_search in clause:
                        del clause[:]
                    
    else: #Algorithm used when a list of clauses is inputed
        global changes
        cl = clauses.copy()
        while cl:
            clause = cl.pop()
            if is_literal(clause) == False:
                for literal in clause: 
                    to_search = complement(literal)
                    
                    if to_search in clause:
                            changes = 1
                            clauses.remove(clause)
                            break

def remove_redundancies(clauses): #Cheks if every literal has it's complement
    global changes                #in any clause
    percorrer = clauses.copy()
    
    if len(clauses)==1: #if there is only one clause, no contradition is going 
        del clauses[:]  #to be found
    
    else:
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
                        changes = 1
                        break 

       
def check_subsets(clauses): #Verifies if there is any clause that is subset of another
    global changes          #If so, the largest clause is removed
    cl = []         
    cl = clauses.copy()
    while cl:
        subset = cl.pop()
        temp = clauses.copy()
        temp.remove(subset)
        for clause in temp:
            is_subset = True
            
            if is_literal(subset) == True and is_negated(subset) == True:
                if is_literal(clause):
                    if subset != clause:
                        is_subset = False
                else:    
                    if subset not in clause:
                        is_subset = False
            else:
                for element in subset: #valid for clauses with one then 1 literal or single positive literals
                    if is_literal(clause) == True and is_negated(clause)== True:
                        if element != clause:
                            is_subset = False
                            break
                    else:
                        if element not in clause:
                            is_subset = False
                            break
                    
            if is_subset == True:
                changes = 1
                clauses.remove(clause)
                if clause in cl:
                    cl.remove(clause)

#Steps to resolve initial simplifications                    
def apply_simplifications(clauses):
    global changes #Flag that lets the program know if there are no simplifications left to be done
    changes = 1
    while changes ==1:
        changes=0
        remove_tautologies(clauses, False) #When a component and its complement exist in the same clause
        remove_redundancies(clauses) #Cheks if every component has its complement
        check_subsets(clauses)      #Cheks if a clause is implied by another
#------------------------------------------------------------------------------
#Other Functions                    
#------------------------------------------------------------------------------

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

#clauses = parser("cnf.txt")

clauses = parser()

#APPLY SIMPLIFICATION RULES
apply_simplifications(clauses)

if clauses:
    #Removes excessive parentises after simplifications
    for clause in clauses:
        remove_parens(clause)

    #Clauses are sorted by putting literals first and other clauses last
    percorrer = sorted(clauses, key=lambda item: is_literal(item), reverse= True)
    
    solution = False
    possible = True #Begin the while cycle
    i = 0 
    already_solved = [] #keeps track of pairs of clauses already solved by resolution

else:
    solution = False
    possible = False

while(solution == False and possible == True):
    #input()
    to_analyse = percorrer[i]
    #print("Analysing %s" %to_analyse)
    #First it searches a compatible for resolution
    if is_literal(to_analyse) == True:
        to_search = complement(to_analyse)
        #print(to_search)
        compatible_clause = find_compatible_clause(percorrer, i, to_search, already_solved)
    else:
        for element in to_analyse:
            to_search = complement(element)
            #print(to_search)
            compatible_clause = find_compatible_clause(percorrer, i, to_search, already_solved)
            if compatible_clause != False:
                break
    
    #print("Found Compatible clause: %s" %compatible_clause)
    #If a compatible clause is found, it applys resolution
    if compatible_clause != False:
            result = resolution(to_analyse, compatible_clause)
            already_solved.append([to_analyse, compatible_clause]) 
            #print("Result %s" %result)
            if result == []:
                #print("FOUND CONTRADITION!")
                solution = True
            else:
                i = 0
                remove_parens(result)
                result = remove_duplicates(result)
                remove_tautologies(result, True)
                
                if result != []:
                    #print("Simplified result %s" %result)
                    percorrer.append(result)
                    #print("New percorrer %s" %percorrer)
                    apply_simplifications(percorrer)
                    #print("simplified %s" %percorrer)
                    percorrer = sorted(percorrer, key=lambda item: is_literal(item), reverse= True)
                    #print("Sorted %s" %percorrer)
    else:
        if(i< len(percorrer)-1):
            i +=1
        else:
            possible = False


print(solution)
    
      