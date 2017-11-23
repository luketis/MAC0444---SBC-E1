import pickle
import os

def next_occ(element, array, reverse=False):
    if reverse:
        zipped = zip(range(len(array)-1, -1, -1), reversed(array))
    else:
        zipped = zip(range(len(array)), array)
    try:
        return next(i for i,v in zipped if v == element)
    except:
        return None

def get_par_contents(array, chars=['(', ')']):
    zipped = list(zip(range(len(array)), array))
    open_pars = [i for i,v in zipped if v == chars[0]]
    close_pars = [i for i,v in zipped if v == chars[1]]
    #print(open_pars)
    #print(close_pars)
    contents = []
    for op, cp in zip(open_pars, close_pars):
        contents += [array[op+1:cp]]
    return contents

def get_movie_name(line, last_tab):
    first_par = next_occ('(', line[last_tab:])
    if first_par is None:
        return -1
    first_par += last_tab
    par_contents = get_par_contents(line)
    #bra_contents = get_par_contents(line, chars=['{', '}'])
    #if len(bra_contents) > 0:
    #    return -1
    #if 'TV' in par_contents or 'V' in par_contents or 'TV Series' in par_contents:
    #    return -1
    if len(par_contents) > 1:
        #with open("log", "a") as log:
        #    log.write("".join(par_contents) +  "\n")
        return -1
    movie_name = line[last_tab+1:first_par - 1].replace(" ", "_")
    return (movie_name, line[first_par+1:first_par+5])

def get_starred_movies(path):
    movies = []
    with open(path, encoding='latin-1') as f:
        for line in f:
            last_tab = next_occ('\t', line, reverse=True)

            if last_tab is None:
                continue
            movie_name = get_movie_name(line, last_tab)
            if movie_name != -1:
                movies += [movie_name] 
    return movies


def get_cast(movies, paths):
    actor2movie = dict()
    movie2actor = dict()
    for path in paths:
        with open(path, encoding='latin-1') as f:
            for line in f:
                last_tab = next_occ('\t', line, reverse=True)

                if last_tab is None:
                    continue
                first_tab = next_occ('\t', line)
                if first_tab != 0:
                    actor = line[:first_tab].replace(" ", "_")
                    actor = actor.replace(",", "")
                    actor = actor.replace("-", "_") 
                movie_name = get_movie_name(line, last_tab)
                if movie_name != -1 and movie_name in movies:
                    if actor not in actor2movie:
                        actor2movie[actor] = []
                    actor2movie[actor] += [movie_name]
                    if movie_name not in movie2actor:
                        movie2actor[movie_name] = []
                    movie2actor[movie_name] += [actor]
                    
    return actor2movie, movie2actor


def set_ontology_ad(dict_of, type_data, prefix, path, rel):
    for element in dict_of:
        print("    <!-- " + prefix[1:] + element + " -->")
        print()
        print("    <owl:NamedIndividual rdf:about="+prefix+element+"\">")
        print("        <rdf:type rdf:resource="+ prefix+type_data+"\"/>")
        
        for movie in dict_of[element]:
            print("        <"+rel+" rdf:resource=" +prefix+ movie[0]+ "\"/>")
        name = element.split("_", maxsplit=2)
        if len(name) > 1:
            print("        <renata:FOAF-modifiedfamilyName>"+name[0]+"</renata:FOAF-modifiedfamilyName>")
        
        print("        <renata:FOAF-modifiedfirstName>"+name[-1]+"</renata:FOAF-modifiedfirstName>")
        print("    </owl:NamedIndividual>")
        print()


def set_ontology_m(movies_ac, movies_dir, prefix, path):
    for element in movies_ac:
        print("    <!-- " + prefix[1:] + element[0] + " -->")
        print()
        print("    <owl:NamedIndividual rdf:about="+prefix+element[0]+"\">")
        print("        <rdf:type rdf:resource="+ prefix+"Movie"+"\"/>")
        
        if element in movies_dir:
            for director in movies_dir[element]:
                print("        <director rdf:resource=" +prefix+ director+ "\"/>")
        for actor in movies_ac[element]:
            print("        <actor rdf:resource=" +prefix+ actor+ "\"/>")
        print("        <year rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+str(element[1])+"</year>")
        print("    </owl:NamedIndividual>")
        print()

if __name__ == "__main__":
    star_movie = {'wes_movies':get_starred_movies("./wes"),
              'tarantino_movies': get_starred_movies("./tarantino"),
              'uma_movies': get_starred_movies("./uma"),
              'frances_movies': get_starred_movies("./frances"),
              'bill_movies': get_starred_movies("./bill_murray"),
              'harvey_movies':  get_starred_movies("./harvey_keitel")}

    movies_list = set(sum([star_movie[key] for key in star_movie], []))
    actors_paths = ["./actors.list", "./actresses.list"]
    director_paths = ["./directors.list"]
    if not os.path.isfile("actor2movie.pickle"):    
        actor2movie, movie2actor = get_cast(movies_list, actors_paths)
        with open("actor2movie.pickle", "wb") as f:
            pickle.dump(actor2movie, f)
        with open("movie2actor.pickle", "wb") as f:
            pickle.dump(movie2actor, f)
    else:    
        with open("actor2movie.pickle", "rb") as f:
            actor2movie = pickle.load(f)
        with open("movie2actor.pickle", "rb") as f:
            movie2actor = pickle.load(f)    
    if not os.path.isfile("director2movie.pickle"): 
        director2movie, movie2director = get_cast(movies_list, director_paths)
        with open("director2movie.pickle", "wb") as f:
            pickle.dump(director2movie, f)
        with open("movie2director.pickle", "wb") as f:
            pickle.dump(movie2director, f)
    else:    
        with open("director2movie.pickle", "rb") as f:
            director2movie = pickle.load(f)
        with open("movie2director.pickle", "rb") as f:
            movie2director = pickle.load(f)
    rdf_about =  "\"http://www.semanticweb.org/luketis/ontologies/2017/10/untitled-ontology-2#"

    set_ontology_ad(actor2movie, "Actor", rdf_about, "a", "acted_in")
    set_ontology_ad(director2movie, "Director", rdf_about, "a", "directed")
    set_ontology_m(movie2actor, movie2director, rdf_about, "a")

    print("</rdf:RDF>")
    print("<!-- Generated by the OWL API (version 4.2.8.20170104-2310) https://github.com/owlcs/owlapi -->")
