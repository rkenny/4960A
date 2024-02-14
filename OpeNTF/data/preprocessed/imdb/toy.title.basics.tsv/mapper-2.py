import pickle # for loading pickles
import random # to sort bundle-user into train/test

Verbose = False
testSetSize = 0.40 # % of bundle/user pairs that go into the test set
indexes = pickle.load(open("indexes.pkl", "rb"))
teamsVecs = pickle.load(open("teamsvecs.pkl", "rb"))

userItemFilename = "mappedFiles/user_item.txt"
bundleItemFilename = "mappedFiles/bundle_item.txt"
userBundleTrainFilename = "mappedFiles/user_bundle_train.txt"
userBundleTestFilename = "mappedFiles/user_bundle_test.txt"

userItemFile = open(userItemFilename, "w")
bundleItemFile = open(bundleItemFilename, "w")
userBundleTrainFile = open(userBundleTrainFilename, "w")
userBundleTestFile = open(userBundleTestFilename, "w")

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
            # print(userId[1] + " " + itemId[1])
            userItemFile.write(userId[1] + "\t" + itemId[1] + "\n")
            print(" [" + indexes["i2s"][userId[0]] + "] for [" +str(indexes["i2t"][bundleId[0]])+ "] as ", end="") if Verbose else None
            # print(userId[1] + " " + bundleId[1]) # this is the train/test set
            if random.random() < testSetSize:
                userBundleTestFile.write(userId[1] + "\t" + bundleId[1] + "\n")
            else:
                userBundleTrainFile.write(userId[1] + "\t" + bundleId[1] + "\n")
        print(" [" + str(indexes["i2t"][bundleId[0]]) +"] has crew " + indexes["i2c"][bundleId[0]] + " as ", end="") if Verbose else None
        # print(bundleId[1] + " " + itemId[1])
        bundleItemFile.write(bundleId[1] + "\t" + itemId[1] + "\n")
  
print("User Count: "+ str(len(userCount.keys())))
print("Item Count: " + str(len(itemCount.keys())))
print("Bundle Count: " + str(len(bundleCount.keys())))
