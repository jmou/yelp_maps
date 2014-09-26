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

    url = 'https://api.foursquare.com/v2/lists/self/todos/additem'
    data = urllib.urlencode(query)
    return json.load(urllib2.urlopen(url, data=data))


if __name__ == '__main__':
    oauth_token = sys.argv[1]
    for venue_id in sys.argv[2:]:
        print 'Adding', venue_id
        add_todo(venue_id, oauth_token)
