#####
# loadbills.py
#
# Purpose: Testing ElasticSearch API using govtrack.us API
#
# Requires: ElasticSearch running at localhost:9200
#
# Author: Simon Prickett
#####

import json
import requests
import sys

#####
# Fetch the bills from the API
#####
def fetchBills(howMany):
	print 'Attempting to fetch ' + str(howMany) + ' bills...'
	url = 'https://www.govtrack.us/api/v2/bill?congress=112&order_by=-current_status_date&limit=' + str(howMany)
	res = requests.get(url)
	return res.json()

#####
# Push the bills into ElasticSearch
#####
def storeBills(bills):
	for bill in bills['objects']:
		print '***Storing: ' + str(bill['id']) + ' - ' + bill['title_without_number']
		url = 'http://localhost:9200/congress/bills/' + str(bill['id'])
		res = requests.put(url, data = json.dumps(bill))
#####
# Run an example aggregation query
#####
def aggregateBills(queryName, queryField):
	url = 'http://localhost:9200/congress/bills/_search'
	res = requests.get(url, data = '{ "aggs": { "' + queryName + '": { "terms": { "field": "' + queryField + '" } } } }')
	results = res.json()
	for result in results['aggregations'][queryName]['buckets']:
		print result['key'] + ': ' + str(result['doc_count'])

#####
# Display usage message
#####
def usage():
	print 'Usage: ' + sys.argv[0] + ' store|query'

#####
# Entry point
#####
if (len(sys.argv) == 2):
	if (sys.argv[1] == 'store'):
		print 'Fetching bills from API and adding to ElasticSearch...'
		storeBills(fetchBills(1000))
	else:
		if (sys.argv[1] == 'query'):
			print 'Running example queries...'
			print '---------------------'
			print 'Bills by state of sponsor:'
			aggregateBills('all_states', 'sponsor_role.state')
			print '---------------------'
			print 'Bills by gender of sponsor:'
			aggregateBills('all_genders', 'sponsor.gender')
			print '---------------------'
			print 'Bills by party of sponsor:'
			aggregateBills('all_parties', 'sponsor_role.party')
			print '---------------------'
		else:
			usage()
else:
	usage()