from instagram.client import InstagramAPI
from alchemyapi import AlchemyAPI
from datetime import datetime, timedelta
import math
import json

api = InstagramAPI(client_id='64de641b01d648779939696d77ccff38', client_secret='043233db9a2c4c13a40a442c7bee0c43')
alchemyapi = AlchemyAPI()
OUTFILE = "results.json"

def fetchLatestMedia(tag_name, max_age=7):
    # tag_name - the hashtag name
    # max_age - oldest returned Media object in days
    # returns a list of Media objects
    media, next_ = api.tag_recent_media(tag_name=tag_name, count=100)
    oldest_dt = datetime.now() - timedelta(days=max_age)
    while next_:
        more_media, next_ = api.tag_recent_media(tag_name=tag_name, count=100, with_next_url=next_)
        filtered = filter(lambda media: media.created_time > oldest_dt, more_media)
        media.extend(filtered)
        if len(filtered) != len(more_media):
            break
    print "Returning", len(media), "items with tag", tag_name
    return media

def fetchMediaInfo(media):
    # fetch these info from each media:
    #   type
    #   thumbnail URL
    #   high-res URL
    #   caption text
    #   num likes
    #   user
    #   created time
    return {
        'type': media.type,
        'thumbnail': media.get_thumbnail_url(),
        'link': media.get_standard_resolution_url(),
        'caption': media.caption.text,
        'like_count': media.like_count,
        'user': media.user,
        'created_time': media.created_time
    }

def countUserPosts(user):
    # user - user object
    # returns the number of posts the user has made
    media, next_ = api.user_recent_media(user_id=user.id, count=100)
    count = len(media)
    while next_:
        more_media, next_ = api.user_recent_media(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_media)
    return count

def countUserFollowers(user):
    # user - user object
    # returns the number of followers a user has
    followers, next_ = api.user_followed_by(user_id=user.id, count=100)
    count = len(followers)
    while next_:
        more_followers, next_ = api.user_followed_by(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_followers)
    return count

def countUserFollowing(user):
    # user -  user object
    # returns the number of people the user is following
    following, next_ = api.user_follows(user_id=user.id, count=100)
    count = len(following)
    while next_:
        more_following, next_ = api.user_follows(user_id=user.id, count=100, with_next_url=next_)
        count += len(more_following)
    return count

def fetchUserInfo(user):
    # fetch these info from each user:
    #   num posts
    #   num followers
    #   num following
    return {
        'posts': countUserPosts(user),
        'followers': countUserFollowers(user),
        'following': countUserFollowing(user)
    }

def getUserInfluence(user):
    # returns user influence score based on this formula:
    # sqrt(user_posts) * (user_followers / user_following) * math.log(user_followers+1, 2)
    userInfo = fetchUserInfo(user)
    print user.username, "has", userInfo['posts'], "posts, has", userInfo['followers'], "followers, and is following", userInfo['following']
    userInfluence = (math.log(userInfo['posts'], 20)+1) * (userInfo['followers']/float(userInfo['following'])) * math.log(userInfo['followers']+1, 10)
    print "User influence is", round(userInfluence, 2)
    return userInfluence

def analyzeSentiment(media):
    # uses AlchemyAPI's sentiment analysis to parse sentiment into a raw score
    # prepend string with a period (.) if first character is a hash (#)
    sentiment = alchemyapi.sentiment('text', media['caption'])
    if sentiment['status'] != 'OK':
        raise Exception(sentiment['statusInfo'])
    if 'score' in sentiment['docSentiment']:
        print "The raw sentiment score is", sentiment['docSentiment']['score']
        return (float(sentiment['docSentiment']['score']), sentiment['docSentiment']['type'])
    else:
        print "The raw sentiment score doesn't exist: assuming 0"
        return (0.0, 'neutral')

def calculateScore(media):
    user = media['user']
    likeCount = media['like_count']
    likeInfluence = math.sqrt(likeCount+1)
    print "This post has", likeCount, "likes"
    try:
        influence = getUserInfluence(user)
    except Exception, e:
        print "Error getting info for user", media['user'].username
        influence = 0.0
        sentiment, type_ = 0.0, 'error'
    else:
        try:
            sentiment, type_ = analyzeSentiment(media)
        except Exception, e:
            print "Error getting sentiment:", e
            sentiment, type_ = 0.0, 'error'
    return {
        'score': round(influence * sentiment * likeInfluence, 1),
        'type': type_
    }

def serializeUser(user):
    return {
        'id': user.id,
        'username': user.username
    }

print "Fetching latest posts about #CapitalOne"
capitalonemedia = fetchLatestMedia("CapitalOne", 2)
print "Processing latest posts about #CapitalOne"
capitalone = map(fetchMediaInfo, capitalonemedia)

print "Calculating scores"
output = { 'posts': [] }
sentimentCounts = {
    'negative': 0,
    'neutral': 0,
    'positive': 0,
    'error': 0
}
totalScore = 0.0

for media in capitalone:
    print media['caption']
    # process sentiment details
    sentimentDetails = calculateScore(media)
    sentimentScore = sentimentDetails['score']
    sentimentType = sentimentDetails['type']
    totalScore += sentimentScore
    sentimentCounts[sentimentType] += 1
    # append to output results object
    media['sentiment_score'] = sentimentScore
    media['sentiment_type'] = sentimentType
    media['user'] = serializeUser(media['user'])
    media['created_time'] = media['created_time'].__str__()
    output['posts'].append(media)
    print "The post's sentiment is", sentimentType, "with a score", sentimentScore
    print

output['avg_score'] = round(totalScore / len(capitalone), 1)
print "Average Score:", output['avg_score']
output['sentiment_counts'] = sentimentCounts
print "Sentiment counts:", sentimentCounts
output['time'] = datetime.now().__str__()
print "Finished script at", output['time']

with open(OUTFILE, "w") as outf:
    print "Dumping output to", OUTFILE
    json.dump(output, outf)

print "Done!"
