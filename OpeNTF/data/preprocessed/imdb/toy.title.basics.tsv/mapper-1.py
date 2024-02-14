import pickle
Verbose = True

indexes = pickle.load(open("indexes.pkl", "rb"))
teamsVecs = pickle.load(open("teamsvecs.pkl", "rb"))

genresList = {}
for movieId in indexes["i2t"].keys(): # movieId to bundle
    print("checking movieId " + str(movieId) + " actual title: " + str(indexes["i2t"][movieId])) if Verbose else None
    genreIds = teamsVecs["skill"][movieId].rows[0]
    crewIds = teamsVecs["member"][movieId].rows[0]
    for crewId in [str(crewId) for crewId in crewIds]:
        for genreId in [str(genreId) for genreId in genreIds]:
            print(" [" + indexes["i2s"][int(genreId)] + "] for [" +indexes["i2c"][int(crewId)]+ "] as ", end="") if Verbose else None
            print(genreId + " " + crewId)
            print(" [" + indexes["i2s"][int(genreId)] + "] for [" +str(indexes["i2t"][movieId])+ "] as ", end="") if Verbose else None
            print(genreId + " " + str(movieId))
        print(" [" + str(indexes["i2t"][movieId]) +"] has crew " + indexes["i2c"][int(crewId)] + " as ", end="") if Verbose else None
        print(str(movieId) + " " + crewId)
        
        #print(str(movieId) + " has genre " + genreId)