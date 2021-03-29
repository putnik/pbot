# coding=utf-8

import pywikibot
import re
from pywikibot import pagegenerators as pg

PID_BIRTH_PLACE = 'P19'
PID_DEATH_PLACE = 'P20'
PID_ADM_UNIT = 'P131'
PID_COUNTRY = 'P17'
PID_FILE = 'adm_entity_%s'
REMOVE_SUMMARY = u'Remove administrative entity qualifiers that can be obtained from the target item'

site = pywikibot.Site('ru', 'wikipedia')
repo = pywikibot.Site('wikidata', 'wikidata')
processed = {}


def mark_processed(qid, pid):
    processed[pid].append(qid)
    with open(PID_FILE % pid, 'a') as file:
        file.write('%s\n' % qid)


def is_processed(qid, pid):
    if pid not in processed:
        try:
            with open(PID_FILE % pid) as file:
                processed[pid] = [row.strip() for row in file]
        except FileNotFoundError:
            processed[pid] = []
    return qid in processed[pid]


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
    claim.removeQualifiers(qualifiers, summary=REMOVE_SUMMARY)
    return


def check_adm_entity(item, place_pid):
    if is_processed(item.getID(), place_pid):
        return
    data = item.get()
    if 'claims' not in data or place_pid not in data['claims'] or len(data['claims'][place_pid]) != 1:
        return
    for claim in data['claims'][place_pid]:
        current_html = load_preview('{{wikidata|%s|from=%s}}' % (place_pid, item.getID()))
        new_html = load_preview('{{wikidata/песочница|%s|from=%s}}' % (place_pid, item.getID()))
        if current_html == new_html:
            print('%s: REMOVE' % item.getID())
            remove_qualifiers(claim)
        else:
            print('%s: SKIP' % item.getID())
        mark_processed(item.getID(), place_pid)


def iterate_items(pid):
    print(pid)
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
        try:
            check_adm_entity(item, pid)
        except:
            print('%s: OOPS!!!' % item.getID())


iterate_items(PID_BIRTH_PLACE)
iterate_items(PID_DEATH_PLACE)
