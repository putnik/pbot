# coding=utf-8

import pywikibot
import re

from pywikibot import pagegenerators
from time import sleep


CATEGORY_EN = 'Flags by year of introduction'
CATEGORY_RU = 'Флаги по годам'

PATTERN_EN = 'Category:Flags introduced in %s'
PATTERN_RU = 'Категория:Флаги %s года'
PATTERN_YEAR = '([0-9]+)'

site_en = pywikibot.Site('en', 'wikipedia')
site_ru = pywikibot.Site('ru', 'wikipedia')
repo = pywikibot.Site('wikidata', 'wikidata')


def merge(target_item, redirect_item):
    print('MERGE: %s <- %s' % (target_item.getID(), redirect_item.getID()))
    redirect_item.mergeInto(target_item, ignore_conflicts='description')

    if redirect_item.isRedirectPage():
        return

    descriptions = redirect_item.get(force=True)['descriptions']
    new_descriptions = {}
    for code in descriptions:
        new_descriptions[code] = ''
    redirect_item.editDescriptions(new_descriptions, summary='Clearing item to prepare for redirect')
    redirect_item.set_redirect_target(target_item, force=True)


def iterate_items():
    search_pattern_ru = PATTERN_RU % PATTERN_YEAR
    cat_ru = pywikibot.Category(site_ru, CATEGORY_RU)
    subcats_ru = cat_ru.subcategories()
    subcats_generator = pagegenerators.PreloadingGenerator(subcats_ru, 500)
    for subcat_ru in subcats_generator:
        matches = re.fullmatch(search_pattern_ru, subcat_ru.title())
        year = matches[1]
        title_en = PATTERN_EN % year
        subcat_en = pywikibot.Category(site_en, title_en)
        try:
            item_en = subcat_en.data_item()
        except pywikibot.exceptions.NoPage:
            print('NO PAGE: %s' % title_en)
            continue
        item_ru = subcat_ru.data_item()

        id_en = item_en.getID()
        id_ru = item_ru.getID()
        if id_en == id_ru:
            print('SKIP: %s = %s' % (id_en, id_ru))
        elif id_en < id_ru:
            merge(item_en, item_ru)
            sleep(5)
        else:
            merge(item_ru, item_en)
            sleep(5)


iterate_items()
