# coding=utf-8

import pywikibot
import re
import urllib.request
from pywikibot import Claim, pagegenerators as pg
from time import sleep
from urllib.error import HTTPError
from utils.properties import PID_WARHEROES_ID, PID_NAMED_AS
from utils.request import USER_AGENT

repo = pywikibot.Site('wikidata', 'wikidata')


def parse_warheroes_ru(id):
    html = None
    tries = 0
    while html is None:
        try:
            url = 'http://www.warheroes.ru/hero/hero.asp?Hero_id=%s' % id
            headers = {
                'User-Agent': USER_AGENT,
            }
            request = urllib.request.Request(url=url, headers=headers)
            html = urllib.request.urlopen(request).read().decode()
        except HTTPError:
            if tries > 3:
                return None
            tries += 1
            sleep(2 ** tries)
    match = re.search('<meta property="og:title" content="([^"]+?)" />', html)
    if match is None:
        return None
    return match.group(1)


def process_claim(claim):
    if PID_NAMED_AS in claim.qualifiers:
        return

    id = claim.getTarget()
    name = parse_warheroes_ru(id)

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
    if 'claims' not in data or PID_WARHEROES_ID not in data['claims']:
        return
    for claim in data['claims'][PID_WARHEROES_ID]:
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
    ''' % (PID_WARHEROES_ID, PID_WARHEROES_ID, PID_NAMED_AS)
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        add_named_as(item)
        # sleep(5)


iterate_items()
