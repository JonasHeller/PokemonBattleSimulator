from SPARQLWrapper import SPARQLWrapper, JSON

def noUrl(string):
    # remove http://example.org/pokemon from string
    return string[31:]

def queryStats(attPoke, defPoke):
    # query database for pokemon stats
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pok")
    sparql.setQuery("""
    PREFIX pok: <http://www.example.org/pokemon/>
    select * where { 
        {pok:"""+attPoke+""" pok:stats ?s .}

          UNION
        {pok:"""+defPoke+"""  pok:stats ?s}
    }
    """)
    sparql.setReturnFormat(JSON)
    
    
    
    # read results and get relevant entries
    results = sparql.query().convert()
    results = results['results']['bindings']
    return noUrl(results[0]['s']['value']), noUrl(results[1]['s']['value'])

def queryType(attPoke, defPoke, effect):
    """ 
    Takes an attacking Pokémon, a defending Pokémon and an effectiveness as arguments. Returns a dictionary with as keys 
    the attacking Pokémon's types that are of the given effectiveness, and as values the respective types of the defending
    Pokémon
    """
    # query database for pokemon type effectiveness
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pok")
    sparql.setQuery("""
       PREFIX pok: <http://www.example.org/pokemon/>

    select distinct ?pokemon ?attype ?deftype 
    where {
        ?pokemon pok:hasType ?attype. {

            select ?attype ?deftype
    where {

        ?attype pok:"""+effect+""" ?deftype. {

    select ?deftype
    where {
    pok:"""+defPoke+""" pok:hasType ?deftype.
    }       
        }  
    }
        }
    }
    """)
    sparql.setReturnFormat(JSON)
    
    
    
    # read results and get relevant entries
    results = sparql.query().convert()['results']['bindings']
    
    # get attDict
    attDict = [[noUrl(result['pokemon']['value']), noUrl(result['attype']['value']), noUrl(result['deftype']['value'])] 
               for result in results if noUrl(result['pokemon']['value']) == attPoke]
    
    attDict2 = {}
    
    for att in attDict:
        if att[1] in list(attDict2.keys()):
            attDict2[att[1]].append(att[2])
        else:
            attDict2[att[1]] = [att[2]]
    
    return attDict2

def flatten(poke, eff):
    return {q for y in [poke[eff][x] for x in poke[eff]] for q in y}

def simulate(attPoke, defPoke):
    """
    Returns the result of the battle
    """

    # query database for strengths/weaknesses
    attEff = {'Strong': queryType(attPoke, defPoke, 'StrongTo'), 'Weak': queryType(attPoke, defPoke, 'WeakTo'), 'Stats': queryStats(attPoke, defPoke)[0]}
    print(attEff)
    defEff = {'Strong': queryType(defPoke, attPoke, 'StrongTo'), 'Weak': queryType(defPoke, attPoke, 'WeakTo'), 'Stats': queryStats(defPoke, attPoke)[0]}
    print(defEff)
    # return unique strengths/weaknesses
    asl = len(flatten(attEff, 'Strong'))
    dsl = len(flatten(defEff, 'Strong'))
    print(asl)
    print(dsl)
    # cancel out two types
    for x in attEff['Strong'].keys():
        if x in attEff['Weak'].keys():
            asl -= 1
    for x in defEff['Strong'].keys():
        if x in defEff['Weak'].keys():
            dsl -= 1

    print(asl)
    print(dsl)

    # decide result by type advantage,
    if asl < dsl and asl != -1 and dsl != -1:
        return defPoke, 'Strong', defEff['Strong'] 
    elif asl > dsl and asl != -1 and dsl != -1:
        return attPoke, 'Strong', attEff['Strong']
    
    # type disadvantage
    else:
        awl = len(flatten(attEff, 'Weak'))
        dwl = len(flatten(defEff, 'Weak'))
        if awl > dwl:
            return defPoke, 'Weak', attEff['Weak']
        elif awl < dwl:
            return attPoke, 'Weak', defEff['Weak']
        # or total stats
        else:
            if attEff['Stats'] < defEff['Stats']:
                return defPoke,'Stats'
            elif attEff['Stats'] > defEff['Stats']:
                return attPoke,'Stats'
            else:
                return 'draw'

def queryImage(poke):
    # query database for pokemon image
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pok")
    sparql.setQuery("""
    PREFIX pok: <http://www.example.org/pokemon/>
    PREFIX bibo: <http://purl.org/ontology/bibo/>
    select ?i where { 
        pok:"""+poke+""" bibo:Image ?i .
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings'][0]['i']['value']
    return results

def queryAudio(poke):
    # query database for pokemon sound
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pok")
    sparql.setQuery("""
    PREFIX pok: <http://www.example.org/pokemon/>
    PREFIX bibo: <http://purl.org/ontology/bibo/>
    select ?i where { 
        pok:"""+poke+""" bibo:AudioDocument ?i .
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings'][0]['i']['value']
    return results

def results(attPoke, defPoke):
    """
    Returns a text containing the results and an explanation. If there is a winner, also returns a URL with 
    a picture of the winning Pokémon.    
    """
    
    # normalize results
    result = simulate(attPoke, defPoke)
    inference = result[0] + ' won, because '
    print(result)
    # check reason for results
    if len(result) == 3:
        subTypes = list(result[2].keys())
        objTypes = [''.join(result[2][x]) if len(result[2][x]) == 1 
                    else ''.join(result[2][x][0]) +' and ' + ''.join(result[2][x][1]) for x in subTypes]
 
        # set results for win by advantage
        if result[1] == 'Strong':
            predicate = ' is very effective against '
            if len(subTypes) == 1:
                inference += subTypes[0] + predicate + objTypes[0] + '.'
            else:
                inference += subTypes[0] + predicate + objTypes[0] + ' and because ' + subTypes[1] + predicate + objTypes[1] + '.'
        # set results for win by disadvantage
        else:
            predicate = ' is not very effective against '
            if len(subTypes) == 1:
                inference += subTypes[0] + predicate + objTypes[0] + '.'
            else:
                inference += subTypes[0] + predicate + objTypes[0] + ' and because ' + subTypes[1] + predicate + objTypes[1] + '.'
    
    # set results for win by stat difference
    elif result[1]  == 'Stats':
        inference += result[0] + ' has higher base stats.'
    
    # print results for draw
    else:
        return "Its a draw, because these Pokémon are evenly matched.", queryImage(attPoke), queryAudio(attPoke), queryImage(defPoke), queryAudio(defPoke), attPoke, defPoke
    return inference, queryImage(result[0]), queryAudio(result[0]), result[0]

def get_abs():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX db: <http://dbpedia.org/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
          dbr:Pokémon dbo:abstract ?obj .
        } 
        LIMIT 1

    """)
    sparql.setReturnFormat(JSON)

    # read results and get relevant entries
    return "'"+sparql.query().convert()['results']['bindings'][0]['obj']['value']+"' - DBpedia, October 2019"


def get_games():
    #query dbpedia for 10 games 
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX db: <http://dbpedia.org/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
          ?subj dbo:series dbr:Pokémon_\(video_game_series\).
        } 
          LIMIT 10


    """)
    sparql.setReturnFormat(JSON)

    # read results and get relevant entries
    results = sparql.query().convert()['results']['bindings']
    return [x['subj']['value'] for x in results]

def get_thumbnail():
    # Get the pokemon logo 
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX db: <http://dbpedia.org/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
          dbr:Pokémon dbo:thumbnail ?obj .
        } 
        LIMIT 1

    """)
    sparql.setReturnFormat(JSON)

    # read results and get relevant entries
    return sparql.query().convert()['results']['bindings'][0]['obj']['value']

def get_names():
    # Get all pokemon names
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pok")
    sparql.setQuery("""
    PREFIX pok: <http://www.example.org/pokemon/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    select ?pok where { 
        ?pok foaf:name ?o .
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings']
    resultlist = []
    for pokemon in results:
        resultlist.append(pokemon['pok']['value'].split('/')[-1])
    return resultlist
