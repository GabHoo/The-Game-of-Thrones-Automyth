from rdflib import Graph, RDFS, RDF, URIRef, Namespace, Literal
from owlrl import DeductiveClosure, RDFS_Semantics
import random, sys


import sys


def random_pick(ist_class):

    g=Graph()
    g.parse("./Event_ontology.ttl") 
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/") #RIGHT NOW I HAD A BUNCH OF INSTANCES IN THIS TURTLE SO I AM USING THE SAME BUT IDEALLY HERE THERE WOULD BE THE OTHERNE
    list_c=[]
    for char in g.subjects(RDF.type, sem.Actor):
        list_c.append(char)
    print(list_c)

    x=ist_class.split('/')[-1]
    print(x)
    if x=='Actor':
        return(random.choice(list_c)) 
    elif x=='Location':
       return(random.choice(list_c))
    elif x=='Power':
       return(random.choice(list_c)) #!!!! UNTIL THERE IS LIST OF POWERS

def main(argv, arc):
    
    g=Graph(base="http://test.com/ns#")
    g.parse("./Event_ontology.ttl")
    print(len(g))
    HERO = Namespace("http://hero_ontology/")
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
    DeductiveClosure(RDFS_Semantics).expand(g)

    #getting the list of all properties that main class EVENT has. properties is a list of a basic properties
    properties=[]
    for s,p,o in g.triples((None, RDFS.domain, sem.Event)):
        properties.append(s)
    print(properties)

    #Getting all subclasses, which are all the specific events
    subEvents=[]
    for s,p,o in g.triples((None, RDFS.subClassOf, sem.Event)):
        subEvents.append(s)
    
    story = Graph() #creates the graph of the story

    i_properties=properties #list with generic Event properties + upcoming specific event properties


    i=subEvents[1] #GOING TO CHANGE THIS INTO: for i in subEvents:
    print("Considering event",i)

    #NOW we are considering one subevent at a time
    instance_i = g.value(predicate = RDF.type, object=HERO.MeetingTheMentor, any=False)
    story += g.triples((instance_i, None, None))
    
    for s,p,o in g.triples((None,RDFS.domain,i)): #takiing all the specific event properties and adding them one by one to the all property list
        print("considering",s)
        i_properties.append(s)
        for s1,p1,o1 in g.triples((s,RDFS.range,None)):
            print(s1,p1,o1) 
            print("o1",o1)
            ist=random_pick(o1)
            print(ist)
            story.add((instance_i, s,ist ))

    story.serialize("./story.ttl")



if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

