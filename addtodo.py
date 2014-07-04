import json
import sys
import urllib
import urllib2


def add_todo(venue_id, oauth_token):
    query = {
        'venueId': venue_id,
        'text': 'imported from Yelp',
        'oauth_token': oauth_token,
        'v': '20140404',
    }
    query = dict((k, v.encode('utf-8')) for k, v in query.iteritems() if v)

    url = 'https://api.foursquare.com/v2/lists/self/todos/addItem'
    data = urllib.urlencode(query)
    return json.load(urllib2.urlopen(url, data=data))


if __name__ == '__main__':
    _, venue_id, oauth_token = sys.argv
    add_todo(venue_id, oauth_token)
