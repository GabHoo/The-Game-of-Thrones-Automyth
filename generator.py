from rdflib import Graph, RDFS, RDF, URIRef, Namespace, Literal
from owlrl import DeductiveClosure, RDFS_Semantics
import random, sys
import sys

from scipy import rand


def random_pick(ist_class):

    g=Graph()
    g.parse("./Event_ontology.ttl") 
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/") #RIGHT NOW I HAD A BUNCH OF INSTANCES IN THIS TURTLE SO I AM USING THE SAME BUT IDEALLY HERE THERE WOULD BE THE OTHERO
    list_c=[]
    for char in g.subjects(RDF.type, sem.Actor):
        list_c.append(char)
    

    x=ist_class.split('/')[-1]
    
    if x=='Actor':
        return(random.choice(list_c)) 
    elif x=='Location':
       return(random.choice(list_c))
    elif x=='Power':
       return(random.choice(list_c)) #!!!! UNTIL THERE IS LIST OF POWERS
    else:
       return(random.choice(list_c)) 

def main(argv, arc):
    
    g=Graph(base="http://test.com/ns#")
    g.parse("./Event_ontology.ttl")
    print(len(g))
    HERO = Namespace("http://hero_ontology/")
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
    DeductiveClosure(RDFS_Semantics).expand(g)

    #getting the list of all properties that main class EVENT has. properties is a list of a basic properties
    properties=[]#list of tuples, bc we need its range too
    for s,p,o in g.triples((None, RDFS.domain, sem.Event)):
        range_p=g.value(predicate = RDFS.range, subject=s, any=False) #HOPEFULLY THERE IS NOT MROE THAN ONE RANGE FOR THOSE
        properties.append((s,range_p))
    

    #Getting all subclasses, which are all the specific events
    subEvents=[]
    for s,p,o in g.triples((None, RDFS.subClassOf, sem.Event)):
        subEvents.append(s)
    
    story = Graph() #creates the graph of the story

    #i_properties=properties #list with generic Event properties + upcoming specific event properties

    hero=random_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor") #defining the hero of the story

    print("list of subevents is:", subEvents)
    for i in subEvents:
        print("Considering event",i)
        #NOW we are considering one subevent at a time

        #FIRST ADD THE ALREADY EXISTING INSTANCE TO THE STORY AND ITS TRIPLES(EVENT_N)
        instance_i = g.value(predicate = RDF.type, object=i, any=False)
        print("found istance of ", i,": ", instance_i)
        story += g.triples((instance_i, None, None))
        
        #THAN WE INSTANCIATE AND ADD TO STORY those that are common to every event
        for (p,r) in properties:
            print(p)
            if(p==URIRef("http://semanticweb.cs.vu.nl/2009/11/sem/hasActor")): #this is to make sure that the hero is always the same
                story.add((instance_i, p,hero ))
            else:
                story.add((instance_i, p,random_pick(r)))

        #THIS IS TO INSTANCIATE AND ADD TO STORY THE TRIPLES SPECIFIC OF THAT EVENT i 
        for s,p,o in g.triples((None,RDFS.domain,i)): #takiing all the specific event properties and adding them one by one to the all property list
            print("       considering",s)
            allranges=[] #THIS IS THO HANDLE MULTIPLE RANGES, SEE THRETENEDELEMENT (CALL TO ADVENTURE) EXAMPLE TO UNDERSTAND
            for s1,p1,o1 in g.triples((s,RDFS.range,None)):
                print("       range: ",o1) 
                allranges.append(o1)
            
            ist=random_pick(random.choice(allranges))   
            story.add((instance_i, s,ist ))

    story.serialize("./story.ttl")



if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

