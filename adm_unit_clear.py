# coding=utf-8

import pywikibot
import re
from pywikibot import pagegenerators as pg

site = pywikibot.Site('ru', 'wikipedia')
repo = pywikibot.Site('wikidata', 'wikidata')

PID_BIRTH_PLACE = 'P19'
PID_DEATH_PLACE = 'P20'
PID_ADM_UNIT = 'P131'
PID_COUNTRY = 'P17'


def load_preview(code):
    html = site.expand_text(code)
    return re.sub('<[^<]+?>', '', html)


def remove_qualifiers(claim):
    qualifiers = []
    if PID_ADM_UNIT in claim.qualifiers:
        for qualifier in claim.qualifiers[PID_ADM_UNIT]:
            qualifiers.append(qualifier)
    if PID_COUNTRY in claim.qualifiers:
        for qualifier in claim.qualifiers[PID_COUNTRY]:
            qualifiers.append(qualifier)
    claim.removeQualifiers(qualifiers)
    return


def check_adm_unit(item, place_pid):
    data = item.get()
    if 'claims' not in data or place_pid not in data['claims'] or len(data['claims'][place_pid]) != 1:
        return
    for claim in data['claims'][place_pid]:
        current_html = load_preview('{{wikidata|%s|from=%s}}' % (place_pid, item.getID()))
        new_html = load_preview('{{wikidata/песочница|%s|from=%s}}' % (place_pid, item.getID()))
        if current_html == new_html:
            remove_qualifiers(claim)


def iterate_items(pid):
    query = '''
        SELECT DISTINCT ?item
        WHERE {
          ?item ^schema:about/schema:isPartOf <https://ru.wikipedia.org/>;
                 p:%s ?place .
          { ?place pq:P17 ?country }
          UNION
          { ?place pq:P131 ?unit }
        }
    ''' % pid
    generator = pg.WikidataSPARQLPageGenerator(query, site=repo)
    for item in generator:
        check_adm_unit(item, pid)


iterate_items(PID_BIRTH_PLACE)
iterate_items(PID_DEATH_PLACE)
