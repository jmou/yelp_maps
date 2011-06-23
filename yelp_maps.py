#!/usr/bin/python2.6

# TODO use the my maps api to automate the import as well

import errno
import json
import sys
import urllib
import xml.dom.minidom

class KmlPlacemarks(object):
  def __init__(self):
    self.xml = xml.dom.minidom.Document()
    kml = self.xml.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    self.doc = self.xml.createElement('Document')
    self.xml.appendChild(kml).appendChild(self.doc)
    # name and description can be set for Document
    self._add_style('default', 'blue-dot.png')
    self._add_style('restaurants', 'restaurant.png')
    self._add_style('food', 'restaurant.png')
    self._add_style('nightlife', 'bar.png')
    self._add_style('arts', 'arts.png')

  def _add_style(self, name, imagefile):
    imagedir = 'http://maps.google.com/mapfiles/ms/micons/'
    style = self.xml.createElement('Style')
    style.setAttribute('id', name)
    (style.appendChild(self.xml.createElement('IconStyle'))
        .appendChild(self.xml.createElement('Icon'))
        .appendChild(self.xml.createElement('href'))
        .appendChild(self.xml.createTextNode(imagedir + imagefile)))
    self.doc.appendChild(style)

  @staticmethod
  def _format_address(listing, delim=', '):
    address2 = '%(city)s, %(state)s %(zip)s' % listing
    return delim.join([listing['address1'], address2])

  @staticmethod
  def _format_description(listing):
    digest = '%(rating).1f from %(review_count)d reviews' % listing
    address = KmlPlacemarks._format_address(listing, '<br>')
    phone = listing.get('phone', None)
    link = '<a href="http://www.yelp.com/biz/%s">Yelp</a>' % listing['id']
    comments = listing.get('comments', None)
    description = [digest, address, phone, link, comments]
    return '<br>'.join([x for x in description if x])

  def add(self, listing, style):
    if not listing['longitude'] or not listing['latitude']:
      return

    placemark = self.xml.createElement('Placemark')

    (placemark.appendChild(self.xml.createElement('name'))
        .appendChild(self.xml.createTextNode(listing['name'])))

    formatted = self._format_description(listing)
    (placemark.appendChild(self.xml.createElement('description'))
        .appendChild(self.xml.createTextNode(formatted)))

    (placemark.appendChild(self.xml.createElement('styleUrl'))
        .appendChild(self.xml.createTextNode('#' + style)))

    encodedCoordinates = '%(longitude)f,%(latitude)f' % listing
    (placemark.appendChild(self.xml.createElement('Point'))
        .appendChild(self.xml.createElement('coordinates'))
        .appendChild(self.xml.createTextNode(encodedCoordinates)))

    self.doc.appendChild(placemark)

  def __str__(self):
    # We don't use toprettyxml because Google won't parse <styleUrl> when it
    # has whitespace inside.
    return self.xml.toxml('utf-8')

class Overrides(object):
  def __init__(self, config):
    env = {}
    try:
      execfile(config, {}, env)
    except IOError, e:
      if e.errno != errno.ENOENT:
        raise
    self.overrides = env['overrides']

  def merge(self, listing):
    listing.update(self.overrides.get(listing['id'], {}))


def ExtractBizList(url):
  BIZ_LIST_SENTINEL = 'Yelp.biz_list = '
  biz_list = None
  for line in urllib.urlopen(url):
    line = line.strip()
    if line.startswith(BIZ_LIST_SENTINEL):
      assert line.endswith(';')
      biz_list = line[len(BIZ_LIST_SENTINEL):-1]
      break
  assert biz_list
  return json.loads(biz_list)


if __name__ == '__main__':
  KNOWN_USERS = {
    'default': '0cwT5wyOf5_qcxy94pf1rg',
    'kevin': 'ju2vJnFaoyEjzoEaktrFnw',
  }
  # It's possible to get multiple placemarks if a listing is in multiple
  # categories. Oh well. Also, this category list is fragile to additions.
  CATEGORIES = [ 'restaurants', 'food', 'nightlife', 'arts' ]
  if len(sys.argv) < 2:
    user = 'default'
  else:
    user = sys.argv[1]
  if user not in KNOWN_USERS:
    userid = user
  else:
    userid = KNOWN_USERS[user]
  URL_BASE = 'http://www.yelp.com/user_details_bookmarks?userid=' + userid
  overrides = Overrides('overrides.cfg.py')
  kml = KmlPlacemarks()
  for category in CATEGORIES:
    for listing in ExtractBizList('%s&category=%s' % (URL_BASE, category)):
      overrides.merge(listing)
      if listing.get('category_restrict', category) == category:
        kml.add(listing, category)
  print kml