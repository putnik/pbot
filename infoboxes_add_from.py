# coding=utf-8

import pywikibot
from contextlib import suppress
from pywikibot import pagegenerators as pg
from pywikibot.exceptions import LockedPageError
from mwparserfromhell import parse

site = pywikibot.Site('ru', 'wikipedia')

FROM_TEMPLATES = (
    'If-wikidata',
    'Wikidata',
    'Wikidata-coords',
    'Категория по дате',
)


def get_paddings(name):
    right_padding = len(name) - 1
    left_padding = len(name) - len(name.lstrip()) + len('from')
    return left_padding, right_padding


def add_from(infobox_page):
    wikicode = parse(infobox_page.text)
    has_infobox = False
    for template in wikicode.filter_templates():
        template_name = template.name.strip()
        template_name = template_name[0].upper() + template_name[1:]

        if any(param.name.strip() == 'from' for param in template.params):
            continue

        if template_name == 'Карточка':
            has_infobox = True
            left_padding = 0
            right_padding = 0
            index = 0
            for i, param in enumerate(template.params):
                if param.name.strip() == 'автозаголовки':
                    left_padding, right_padding = get_paddings(param.name)
                    index = i
                    break
                elif param.name.strip() == 'имя':
                    left_padding, right_padding = get_paddings(param.name)
                    index = i
                elif right_padding == 0:
                    left_padding, right_padding = get_paddings(param.name)
            padded_from = 'from'.rjust(left_padding).ljust(right_padding)
            from_code = "%s = {{{from|}}}\n" % padded_from
            if index and template.params[index].value.endswith("\n\n"):
                new_value = template.params[index].value.rstrip("\n") + "\n"
                template.params[index].value = new_value
                from_code += "\n"
            template.params.insert(index + 1, from_code)

        elif template_name in FROM_TEMPLATES \
                or template_name.startswith("Wikidata/") \
                or template_name.startswith("Карточка/"):
            template.params.append("from={{{from|}}}")

    if not has_infobox:
        return

    infobox_page.text = wikicode
    summary = u"автоматическое добавление параметра from в вызовы шаблонов" + \
              u" {{Карточка}}, {{wikidata}} и их подшаблонов"
    with suppress(LockedPageError):
        infobox_page.save(summary, force=True)


def iterate_items():
    infobox_category = pywikibot.Category(site, 'Шаблоны-карточки по алфавиту')
    generator = pg.CategorizedPageGenerator(infobox_category, namespaces=10)
    for infobox_page in generator:
        print(infobox_page.title())
        add_from(infobox_page)


iterate_items()
