import json
import os
import sys
import urllib
import urllib2


def match_venue(venue, oauth_token):
    query = {
        'intent': 'match',
        'near': venue['zip_code'],
        'query': venue['name'],
        'address': venue.get('address'),
        'city': venue['city'],
        'state': venue['state'],
        'zip': venue['zip_code'],
        'phone': venue.get('phone'),
        'oauth_token': oauth_token,
        'v': '20140404',
    }
    query = dict((k, v.encode('utf-8')) for k, v in query.iteritems() if v)

    url = 'https://api.foursquare.com/v2/venues/search?' + urllib.urlencode(query)
    return json.load(urllib2.urlopen(url))


class VenueStore(object):
    def __init__(self, root):
        self.root = root

    def _yelp_url_to_path(self, yelp_url):
        return os.path.join(self.root,
                            yelp_url.split('/')[-1] + '.json')

    def get(self, yelp_url):
        if os.path.exists(self._yelp_url_to_path(yelp_url)):
            return json.load(open(self._yelp_url_to_path(yelp_url)))
        else:
            return None

    def put(self, yelp_url, venue):
        json.dump(venue,
                  open(self._yelp_url_to_path(yelp_url), 'w'))


if __name__ == '__main__':
    _, json_path, oauth_token, venues_root = sys.argv

    store = VenueStore(venues_root)

    venues = json.load(open(json_path))
    for venue in venues:
        if store.get(venue['url']) is None:
            store.put(venue['url'], match_venue(venue, oauth_token))
