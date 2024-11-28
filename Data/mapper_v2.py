#!/usr/bin/python3

import pickle # for loading pickles
import random # to sort bundle-user into train/test
import cmn 

testSetSize = 0.2
baseFolder = '/mnt/4960/Data/'
datasetName = 'imdb'
datasetFolder = baseFolder + datasetName +'/'
dataTranche = datasetFolder + 'title.basics.tsv' + '/'
inputFolder = dataTranche
outputFolder = inputFolder+'output/'

userItemFilename = outputFolder+'user_item.txt'
bundleItemFilename = outputFolder+'bundle_item.txt'
userBundleTrainFilename = outputFolder+'user_bundle_train.txt'
userBundleTestFilename = outputFolder+'user_bundle_test.txt'
dataSizeFilename = outputFolder+datasetName+'_data_size.txt'

userItemFile = open(userItemFilename, "w")
bundleItemFile = open(bundleItemFilename, "w")
userBundleTrainFile = open(userBundleTrainFilename, "w")
userBundleTestFile = open(userBundleTestFilename, "w")
dataSizeFile = open(dataSizeFilename, "w")

indexes = pickle.load(open(inputFolder + 'indexes.pkl', 'rb'))
teamsVecs = pickle.load(open(inputFolder + 'teamsvecs.pkl', 'rb'))
teams = pickle.load(open(inputFolder + 'teams.pkl', 'rb'))

userCount = {}
itemCount = {}
bundleCount = {}

for bundleId in [(bundleId, str(bundleId)) for bundleId in indexes["i2t"].keys()] : # movieId to bundle
    bundleCount[bundleId[0]] = True
    # print("checking bundleId " + bundleId[1] + " actual title: " + str(indexes["i2t"][bundleId[0]]))
    userIds = teamsVecs["skill"][bundleId[0]].rows[0] # genre as user for imdb
    for userId in [(userId, str(userId)) for userId in userIds]:
        if random.random() < testSetSize:
            # print(userId[1] + " " + bundleId[1] + " (user_bundle test)")
            userBundleTestFile.write(userId[1] + "\t" + bundleId[1] + "\n")
        else:
            # print(userId[1] + " " + bundleId[1] + " (user_bundle train)")
            userBundleTrainFile.write(userId[1] + "\t" + bundleId[1] + "\n")
        userBundleTestFile.flush()
        userBundleTrainFile.flush()
    itemIds = teamsVecs["member"][bundleId[0]].rows[0] # crew as item for imdb
    for itemId in [(itemId, str(itemId)) for itemId in itemIds]:
        itemCount[itemId[0]] = True
        for userId in [(userId, str(userId)) for userId in userIds]:
            userCount[userId[0]] = True
            # print(userId[1] + " " + itemId[1] + "(user_item)")
            userItemFile.write(userId[1] + "\t" + itemId[1] + "\n")
            userItemFile.flush()
        # print(bundleId[1] + " " + itemId[1] + "(bundle item)")
        bundleItemFile.write(bundleId[1] + "\t" + itemId[1] + "\n")
    bundleItemFile.flush()

dataSizeFile.write(str(len(userCount.keys()))+"\t"+str(len(bundleCount.keys()))+"\t"+str(len(itemCount.keys())))
dataSizeFile.flush()
dataSizeFile.close()

userBundleTestFile.close()
userBundleTrainFile.close()
userItemFile.close()
bundleItemFile.close()
