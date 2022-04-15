from ast import arg
from rdflib import Graph, RDFS, RDF, URIRef, Namespace, Literal, XSD
from owlrl import DeductiveClosure, RDFS_Semantics
import random, sys
import sys
from generator import add_labels, random_pick
import os
import pandas as pd
from string import Template
import networkx as nx
import networkx.algorithms.community as nxcom

from scipy import rand

def random_pick(ist_class):
    
    if ist_class==URIRef("http://www.w3.org/2001/XMLSchema#boolean"):
        print("considering boooolean")
        return(random.choice([Literal("true", datatype=XSD.boolean),Literal("false", datatype=XSD.boolean)]))

    g=Graph()
    g.parse("./Event_ontology.ttl")
    g.parse("./got_instances.ttl")

    list_e=[]
    
    class_node=URIRef(str(ist_class))
    
    for e in g.subjects(RDF.type, class_node):
        list_e.append(e)
    
    #THis is because Mentor for example is a subclass of actor. Since there are no instance directly for mentor we look for its super class (Actor) and pick instance of it.
    while( not list_e):
        print("EMPTY LIST for", class_node)
        class_node = g.value(predicate = RDFS.subClassOf, subject=class_node, any=False)
        print("new super class ", class_node)
        for e in g.subjects(RDF.type, class_node):
            list_e.append(e)

    print("\nclass is ",class_node," list is of possible is : ",list_e)
    return(random.choice(list_e)) 

def add_labels(g,story): #This methods add to our output story graph all the labels of the instances involved in the story. They are necessary for the visualization!
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/") 
    event_inst=[] 
    for s,p,o in story.triples((None,RDF.type,sem.Event)): 
        
        event_inst.append(s)
    p
    for e in event_inst:
        for s,o,p in story.triples((e, None, None)):
            
            story+=g.triples((p,RDFS.label,None))
    print("Adding necessary labels of every intence")

main_characters = {"Jon_Snow": "Q3183235",
                   "Daenerys_Targaryen": "Q2708078",
                   "Arya_Stark": "Q3624677",
                   "Bran_Stark": "Q3643599",
                   "Cersei_Lannister": "Q3665163",
                   "Tyrion_Lannister" : "Q2076759",
                   "Margaery_Tyrell": "Q12900933",
                   "Robert_Baratheon" : "Q13634885"}

def find_communities(weighted_input):
  df = pd.read_csv(weighted_input, sep = ",")
  df['char1'] = [i[-1] for i in df['char1'].str.split("/")]
  df['char2'] = [i[-1] for i in df['char2'].str.split("/")]

  tuples_lst = [(x[1]['char1'], x[1]['char2'],x[1]['valueSum']) for x in df.iterrows()]
  G = nx.Graph()
  G.add_weighted_edges_from(tuples_lst)

  communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)

  communities_dict = {}
  for com in communities:
    for mc in main_characters.keys():
      if mc in list(com):
        com_copy = list(com)
        com_copy.remove(mc)
        communities_dict[mc] = com_copy

  return communities_dict

def comm_based_pick(ist_class, communities=None, hero=None, char_type=None, villain=None):
    category = ist_class.split("/")[-1]
    if category == "Actor":
        hero = hero.split("/")[-1]

        if char_type == "Ally":
            return URIRef('http://hero_ontology/' + random.choice(list(communities[hero])))
        elif char_type == "Villain":
            enemy_comms = {}
            for k in communities.keys():
                if(not hero in communities[k] and k != hero):
                    enemy_comms[k] = communities[k]
            return URIRef('http://hero_ontology/' + random.choice(list(enemy_comms.keys())))
        if char_type == "Villain_Ally":
            villain = villain.split("/")[-1]
            return URIRef('http://hero_ontology/' + random.choice(list(communities[villain])))

    return random_pick(ist_class)

def read_network_data():
    edges = pd.read_csv("Network_of_Thrones/edges_subset.csv")
    nodes = pd.read_csv("Network_of_Thrones/nodes_subset.csv")
    return nodes, edges

def relation_based_pick(edges, related_to_char, n):
    related_to_char = related_to_char.split("/")[-1]
    so = edges[edges.Source == related_to_char][["Target", "weight"]].rename({'Target': 'Relation'}, axis=1)
    ta = edges[edges.Target == related_to_char][["Source", "weight"]].rename({'Source': 'Relation'}, axis=1)

    relations = so.append(ta).sort_values(by="weight", ascending=False)[:n]
    related_character = random.choices(list(relations["Relation"]), weights=list(relations["weight"]))
    return URIRef('http://hero_ontology/' + related_character[0])

def instantiate_ordinary_world(g, fixed):
    ordinary_world_template = Template("""SELECT ?occupation ?house ?title WHERE {
                                      HERO:$hero HERO:occupation ?occupation.
                                      HERO:$hero HERO:family ?house .
                                      HERO:$hero HERO:title ?title}""")

    qres = g.query(ordinary_world_template.substitute({'hero': fixed["Hero"].split("/")[-1]}))
    fixed["Occupation"] = random.choice([row.occupation for row in qres])
    fixed["House"] = random.choice([row.house for row in qres])
    fixed["Title"] = random.choice([row.title for row in qres])

def main(argv, arc):
    if arc!=2 or argv[1] not in ["community","relation","random"] :
        print("Error! Please enter a (valid) charachter picking method. (community,relation,random)")
        exit()
    method=argv[1]
    print(method)
    g = Graph(base="http://test.com/ns#")
    g.parse("./Event_ontology.ttl")
    g.parse("./got_instances.ttl")

    print(len(g))
    HERO = Namespace("http://hero_ontology/")
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
    DeductiveClosure(RDFS_Semantics).expand(g)

    if method == "community":
        communities = find_communities("query-result.csv")
    elif method == "relation":
        nodes, edges = read_network_data()
        n = 3

    # getting the list of all properties that main class EVENT has. properties is a list of a basic properties
    properties = []  # list of tuples, bc we need its range too
    for s, p, o in g.triples((None, RDFS.domain, sem.Event)):
        range_p = g.value(predicate=RDFS.range, subject=s,
                          any=False)  # HOPEFULLY THERE IS NOT MROE THAN ONE RANGE FOR THOSE
        properties.append((s, range_p))

    # Getting all subclasses, which are all the specific events
    subEvents = []
    for s, p, o in g.triples((None, RDFS.subClassOf, sem.Event)):
        subEvents.append(s)

    story = Graph()  # creates the graph of the story
    story.namespace_manager.bind('HERO', URIRef('http://hero_ontology/'))
    story.namespace_manager.bind('sem', URIRef('http://semanticweb.cs.vu.nl/2009/11/sem/'))
    
    # FIXED ENTITES - THE STORY DOMAIN
    fixed = {}
    fixed["Hero"] = random_pick("http://hero_ontology/Hero")
    fixed["EnemyPower"] = random_pick("http://hero_ontology/EnemyPower")
    fixed["HeroPower"] = random_pick("http://hero_ontology/HeroPower")
    fixed["ThreatTarget"] = random_pick("http://hero_ontology/ThreatTarget")

    if method == "community":
        fixed["Villain"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"],                                         "Villain")
        fixed["HeroAlly"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"], "Ally")
        fixed["VillainAlly"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"], "Villain_Ally", fixed["Villain"])
        instantiate_ordinary_world(g, fixed)
    elif method=="relation":
        fixed["Villain"] = relation_based_pick(edges, fixed["Hero"], 10)
        fixed["HeroAlly"] = relation_based_pick(edges, fixed["Hero"], n)
        fixed["VillainAlly"] = relation_based_pick(edges, fixed["Villain"], n)
        instantiate_ordinary_world(g, fixed)

    elif method=="random":
        fixed["Villain"]=random_pick("http://hero_ontology/Villain")
        fixed["HeroAlly"]=random_pick("http://hero_ontology/HeroAlly")
        fixed["VillainAlly"]=random_pick("http://hero_ontology/VillainAlly")

    print("list of subevents is:", subEvents)
    for i in subEvents:
        print("Considering event", i)
        # NOW we are considering one subevent at a time

        # FIRST ADD THE ALREADY EXISTING INSTANCE TO THE STORY AND ITS TRIPLES(EVENT_N)
        instance_i = g.value(predicate=RDF.type, object=i, any=False)
        print("found istance of ", i, ": ", instance_i)
        story += g.triples((instance_i, None, None))

        # THAN WE INSTANCIATE AND ADD TO STORY those that are common to every event
        for (p, r) in properties:  # property and range
            print(p)
            range_str = r.split('/')[-1]
            if (range_str in fixed):
                print(range_str, "is in fixed dic?")
                story.add((instance_i, p, fixed[range_str]))
            else:
                story.add((instance_i, p, random_pick(r)))

        # THIS IS TO INSTANCIATE AND ADD TO STORY THE TRIPLES SPECIFIC OF THAT EVENT i
        for s, p, o in g.triples((None, RDFS.domain, i)):  # takiing all the specific event properties
            print("       considering", s)
            allranges = []  # THIS IS THO HANDLE MULTIPLE RANGES, SEE THRETENEDELEMENT (CALL TO ADVENTURE) EXAMPLE TO UNDERSTAND
            for s1, p1, o1 in g.triples((s, RDFS.range, None)):
                print("       range: ", o1)
                allranges.append(o1)
            rand_range = (random.choice(allranges))
            range_str = rand_range.split('/')[-1]  # pick one from the possible ranges
            if (range_str in fixed):
                print(range_str, "is in fixed dic")
                story.add((instance_i, s, fixed[range_str]))
            else:
                story.add((instance_i, s, random_pick(rand_range)))

    add_labels(g,story)
    story.serialize(f"./story_{method}.ttl")
    print(f"\n{method} based story has been generated succesfully! Check ./story_{method}.ttl ")


if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

