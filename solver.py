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

#Checks if the inputed literal is negated
def is_negated(literal):
    if len(literal) == 1:
        return False
    else:
        return True

#Checks if the inputed clause is a literal (unit clause)    
def is_literal(sentence):
    if len(sentence) == 1:
        return True
    elif len(sentence) ==2 and sentence[0] == "not":
        return True
    else:
        return False

#Returns the negation of a inputed literal
def complement(literal):
    if is_negated(literal) == True:
        to_search = literal[1]
    else:
        to_search = ["not", literal[0]]
    
    return to_search 

#PARSER FUNCTION (to analyse the problem's information)  

def parser():
    try:
        list_sentences = []
        for line in sys.stdin.readlines():
            sentence = eval(line)
            sentence = list(sentence)
            list_sentences.append(sentence)
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
            #Checks if the clause is compatible and if the pair hasn't been resolved before
            if to_search == percorrer[j] and  [percorrer[start_index],percorrer[j]] not in already_solved:
                return percorrer[j]
        else:
            #Checks if the clause is compatible and if the pair hasn't been resolved before
            if to_search in percorrer[j] and [percorrer[start_index],percorrer[j]] not in already_solved:
                return percorrer[j]
    
    return False

#RESOLUTION FUNCTION
        
def resolution(clause1, clause2): #works iff clause1 is smaller or equal than clause2
    if is_literal(clause1) == True:
        to_search = complement(clause1)
        if is_literal(clause2) == True and is_negated(clause2)==True:
            if clause2 == to_search:
                return True
        else:    
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

#Receives clauses via stdin
clauses = parser()


#Applies simplification rules
apply_simplifications(clauses)

if clauses: #If there are still clauses after applying the simplification rules
    #Removes excessive parentises after simplifications
    for clause in clauses:
        remove_parens(clause)

    #Clauses are sorted by putting literals first and other clauses last in increasing length order
    percorrer = sorted(clauses, key=lambda item: (is_literal(item),-len(item)), reverse = True)
    
    solution = False
    possible = True #Begin the while cycle
    i = 0 
    already_solved = [] #keeps track of pairs of clauses already solved with resolution

else: #No clauses to be analysed
    solution = False
    possible = False

while(solution == False and possible == True):
    to_analyse = percorrer[i] #Takes a new clause to be solved
    if is_literal(to_analyse) == True:
        to_search = complement(to_analyse)
        #The negation of the literal being analysed will be searched in the 
        #remaining clauses, and a compatible clause is returned only if the
        #pair of clauses hasn't been resolved before
        compatible_clause = find_compatible_clause(percorrer, i, to_search, already_solved)
    else:
        #if it is not a unit clause, every negated literal is search until
        #a compatible clause is returned
        for element in to_analyse:
            to_search = complement(element)
            compatible_clause = find_compatible_clause(percorrer, i, to_search, already_solved)
            if compatible_clause != False:
                break
    
    #If a compatible clause is found, it applys resolution
    if compatible_clause != False:
            result = resolution(to_analyse, compatible_clause)
            #Appends to the "already_solved" list the pair of clauses solved
            already_solved.append([to_analyse, compatible_clause]) 
            if result == [] or result == True:
                #A contradition is found
                solution = True
            else:
                #Applys simplifications to the resulted clause
                remove_parens(result)
                result = remove_duplicates(result)
                remove_tautologies(result, True)
                
                if result != []:
                    #The next iteration will start on the first clause on the 
                    #"percorrer" list because a new result will be appended
                    i = 0
                    #The simplified result is appended to the "percorrer" list
                    percorrer.append(result)
                    #Applies simplifications to all clauses of the "percorrer" list
                    apply_simplifications(percorrer)
                    #Sorts the "percorrer" list
                    percorrer = sorted(percorrer, key=lambda item: (is_literal(item),-len(item)), reverse = True)
    else:
        #If no compatible clause is found, a new clause should be analysed
        if(i< len(percorrer)-1):
            i +=1
        else:
            #If there is no clause left to be solved, the inference cannot be
            #proven
            possible = False


print(solution)
      