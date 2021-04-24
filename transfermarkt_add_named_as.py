# coding=utf-8

import pywikibot
import re
import urllib.request
from pywikibot import Claim, pagegenerators as pg
from time import sleep
from urllib.error import HTTPError
from utils.properties import PID_TRANSFRERMARKT_PLAYER_ID, PID_NAMED_AS
from utils.request import USER_AGENT

repo = pywikibot.Site('wikidata', 'wikidata')
http_error_count = 0


def parse_transfermarkt_com(id):
    global http_error_count
    url = 'https://www.transfermarkt.com/transfermarkt/profil/spieler/%s' % id
    headers = {
        'User-Agent': USER_AGENT,
    }
    request = urllib.request.Request(url=url, headers=headers)
    try:
        html = urllib.request.urlopen(request).read().decode()
        http_error_count = 0
    except HTTPError:
        http_error_count += 1
        if http_error_count >= 3:
            print('TOO MANY HTTP ERRORS')
        return None
    match = re.search('<h1 itemprop="name">(.+?)</h1>', html)
    if match is None:
        return None
    name = re.sub('<[^<]+?>', '', match.group(1))
    return name.strip()


def process_claim(claim):
    if PID_NAMED_AS in claim.qualifiers:
        return

    id = claim.getTarget()
    name = parse_transfermarkt_com(id)

    if name is None:
        print("%s -> NOT FOUND" % id)
        return

    print("%s -> %s" % (id, name))
    qualifier = Claim(repo, PID_NAMED_AS)
    qualifier.setTarget(name)
    claim.addQualifier(qualifier)
    return


def add_named_as(item):
    data = item.get()
    if 'claims' not in data or PID_TRANSFRERMARKT_PLAYER_ID not in data['claims']:
        return
    for claim in data['claims'][PID_TRANSFRERMARKT_PLAYER_ID]:
        process_claim(claim)


def iterate_items():
    query = '''
        SELECT ?item
        {
          ?item p:%s ?statement .
          ?statement ps:%s ?value .
          ?article schema:about ?item .
          ?article schema:isPartOf <https://ru.wikipedia.org/>.
          FILTER NOT EXISTS{ ?statement pq:%s [] }
        }
    ''' % (PID_TRANSFRERMARKT_PLAYER_ID, PID_TRANSFRERMARKT_PLAYER_ID, PID_NAMED_AS)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        add_named_as(item)
        sleep(30)


iterate_items()
