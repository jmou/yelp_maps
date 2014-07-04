.PHONY: add-all

gen/yelp_bookmarks.json: scrape.py
	rm -f $@ && scrapy runspider scrape.py -o $@

gen/venues: foursquare.py gen/yelp_bookmarks.json
	mkdir -p $@ && python $^ $$FOURSQUARE_ACCESS_TOKEN $@ && touch $@

gen/4sq_venues.txt: summarize.py gen/venues
	for i in gen/venues/*; do echo $$i; python $< $$i; done | grep ^id: | cut -d\  -f2 > $@

add-all: addtodo.py gen/4sq_venues.txt
	xargs python $< $$FOURSQUARE_ACCESS_TOKEN < $(word 2,$^)
