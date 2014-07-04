import json
import sys


if __name__ == '__main__':
    _, json_path = sys.argv
    response = json.load(open(json_path))

    assert response['meta']['code'] == 200
    matches = response['response']['venues']
    print 'matches:', len(matches)
    for m in matches:
        print 'id:', m['id']
