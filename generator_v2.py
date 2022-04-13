from rdflib import Graph, RDFS, RDF, URIRef, Namespace, Literal, XSD
from owlrl import DeductiveClosure, RDFS_Semantics
import random, sys
import sys
from generator import random_pick

from scipy import rand

main_characters = {"Jon_Snow": "Q3183235",
                   "Daenerys_Targaryen": "Q2708078",
                   "Arya_Stark": "Q3624677",
                   "Bran_Stark": "Q3643599",
                   "Cersei_Lannister": "Q3665163",
                   "Tyrion_Lannister" : "Q2076759",
                   "Margaery_Tyrell": "Q12900933",
                   "Petyr_Baelish": "Q4360302",
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

def hero_pick():
  return URIRef('http://hero_ontology/'+random.choice(list(communities.keys())))

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


def main(argv, arc):
    g = Graph(base="http://test.com/ns#")
    g.parse("./Event_ontology.ttl")
    print(len(g))
    HERO = Namespace("http://hero_ontology/")
    sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
    DeductiveClosure(RDFS_Semantics).expand(g)

    communities = find_communities("query-result.csv")

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

    # FIXED ENTITES - THE STORY DOMAIN
    fixed = {}
    fixed["Hero"] = hero_pick()  # defining the hero of the story
    fixed["Villain"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"], "Villain")
    fixed["EnemyPower"] = random_pick("http://hero_ontology/EnemyPower")
    fixed["HeroPower"] = random_pick("http://hero_ontology/HeroPower")
    fixed["HeroAlly"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"], "Ally")
    fixed["VillainAlly"] = comm_based_pick("http://semanticweb.cs.vu.nl/2009/11/sem/Actor", communities, fixed["Hero"], "Villain_Ally", fixed["Villain"])
    fixed["ThreatTarget"] = random_pick("http://hero_ontology/ThreatTarget")

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
            # if(p==URIRef("http://semanticweb.cs.vu.nl/2009/11/sem/hasActor")):
            # if(r==URIRef("http://hero_ontology/Hero")): #this is to make sure that the hero is always the same
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
                print(range_str, "is in fixed dic?")
                story.add((instance_i, s, fixed[range_str]))
            else:
                story.add((instance_i, s, random_pick(rand_range)))

    story.serialize("./story.ttl")


if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

