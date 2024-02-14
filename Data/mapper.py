#!/usr/bin/python3

import pickle # for loading pickles
import random # to sort bundle-user into train/test
import sys
import argparse

args = argparse.ArgumentParser(description='OpeNTF Data Reformatter')
required = args.add_argument_group('Required arguments')
required.add_argument('-i', '--input', help='Directory containing input data', required=True, type=str)
required.add_argument('-o', '--output', help='Destination directory', required=True, type=str)
required.add_argument('-n', '--name', help='Data set name', required=True, type=str)

required.add_argument('-t', help='Percentage of pairs to go into the test set. Must be between 0.0 and 1.0', required=True, type=float)
required.add_argument('-c', '--count', help='Max number of items to consider', required=True, type=int)
optional = args.add_argument_group('Optional arguments')
optional.add_argument('-v', help='Verbose output', action="store_true")
parameters = args.parse_args()

quitAfterX = parameters.count #100000
indexesPickle = parameters.input + '/indexes.pkl'
teamsVecsPickle = parameters.input + '/teamsvecs.pkl'

Verbose = parameters.v
testSetSize = parameters.t # % of bundle/user pairs that go into the test set

userItemFilename = parameters.output + "/user_item.txt"
bundleItemFilename = parameters.output + "/bundle_item.txt"
userBundleTrainFilename = parameters.output + "/user_bundle_train.txt"
userBundleTestFilename = parameters.output + "/user_bundle_test.txt"
dataSizeFilename = parameters.output + '/'+parameters.name+'_data_size.txt'

indexes = pickle.load(open(indexesPickle, "rb"))
teamsVecs = pickle.load(open(teamsVecsPickle, "rb"))

userItemFile = open(userItemFilename, "w")
bundleItemFile = open(bundleItemFilename, "w")
userBundleTrainFile = open(userBundleTrainFilename, "w")
userBundleTestFile = open(userBundleTestFilename, "w")
dataSizeFile = open(dataSizeFilename, "w")

userCount = {}
itemCount = {}
bundleCount = {}


for bundleId in [(bundleId, str(bundleId)) for bundleId in indexes["i2t"].keys()] : # movieId to bundle
    bundleCount[bundleId[0]] = True
    print("checking bundleId " + bundleId[1] + " actual title: " + str(indexes["i2t"][bundleId[0]])) if Verbose else None
    userIds = teamsVecs["skill"][bundleId[0]].rows[0] # genre as user for imdb
    itemIds = teamsVecs["member"][bundleId[0]].rows[0] # crew as item for imdb
    for itemId in [(itemId, str(itemId)) for itemId in itemIds]:
        itemCount[itemId[0]] = True
        for userId in [(userId, str(userId)) for userId in userIds]:
            userCount[userId[0]] = True
            print(" [" + indexes["i2s"][userId[0]] + "] for [" +indexes["i2c"][itemId[0]]+ "] as ", end="") if Verbose else None
            userItemFile.write(userId[1] + "\t" + itemId[1] + "\n")
            print(" [" + indexes["i2s"][userId[0]] + "] for [" +str(indexes["i2t"][bundleId[0]])+ "] as ", end="") if Verbose else None
            if random.random() < testSetSize:
                userBundleTestFile.write(userId[1] + "\t" + bundleId[1] + "\n")
            else:
                userBundleTrainFile.write(userId[1] + "\t" + bundleId[1] + "\n")
        print(" [" + str(indexes["i2t"][bundleId[0]]) +"] has crew " + indexes["i2c"][bundleId[0]] + " as ", end="") if Verbose else None
        bundleItemFile.write(bundleId[1] + "\t" + itemId[1] + "\n")
    quitAfterX = quitAfterX - 1
    if quitAfterX == 0:
        break

dataSizeFile.write(str(len(userCount.keys()))+"\t"+str(len(bundleCount.keys()))+"\t"+str(len(itemCount.keys())))
