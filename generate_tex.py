#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import xml.sax
import datetime

date = datetime.datetime.now().strftime("%Y-%m-%d")

from mako.template import Template
cvTemplate = Template(filename='cv.template')

type_to_section = {'journal': 'Journal Articles', 
                   'intConf': 'Conference Papers', 
                   'natConf': 'National Conference Papers', 
                   'workshop': 'Workshop Papers', 
                   'bookChapter' : 'Book Chapters', 
                   'phdThesis': 'Ph.D. Thesis'}

type_order = ['Journal Articles', 
              'Conference Papers',
              'National Conference Papers',
              'Workshop Papers',
              'Book Chapters',
              'Ph.D. Thesis'
              ]


class bibliographieHandler(xml.sax.ContentHandler):
    """ Un parser XML sax pour le fichier de bibliographie. """

    def __init__(self):
        self.tree = []
        self.buffer = ''
        self.current_id = ''
        self.articles = {}
        self.auteurs = []

    def startElement(self, name, attrs):
        self.tree.append((name, attrs))

        if name == "article":
            self.current_id = attrs['id']
            self.articles[self.current_id] = {}
            self.articles[self.current_id]["type"] = attrs['type']
            self.articles[self.current_id]["article_id"] = self.current_id

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        tag, attrs = self.tree.pop()

        if tag == 'article':
            if self.articles[self.current_id].has_key("abbr"):
                self.articles[self.current_id]["desc"] += ' ('+self.articles[self.current_id]['abbr']+')'
            self.articles[self.current_id]["desc"] += ', ' + str(self.articles[self.current_id]['annee'])
            if self.articles[self.current_id].has_key("longueur"):
                self.articles[self.current_id]["desc"] += ', '+self.articles[self.current_id]['longueur']

        elif tag == "auteur":
            self.auteurs.append(self.buffer.strip())

        elif tag == "auteurs":
            self.articles[self.current_id]["auteurs"] = self.auteurs
            self.auteurs = []

        elif tag == "annee":
            self.articles[self.current_id]["annee"] = int(self.buffer.strip())

        else:
            self.articles[self.current_id][tag] = self.buffer.strip()



        self.buffer = ''

input_file = "bibliographie.xml"
cv_file = "cv_florian_boudin.tex"

try:
    biblio = bibliographieHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(biblio)
    parser.parse(input_file)

    # Sort articles by year
    categories = {}
    years = []
    for article_id in biblio.articles:
        annee = biblio.articles[article_id]["annee"]
        if not categories.has_key(annee):
            categories[annee] = []
            years.append(annee)
        categories[annee].append(biblio.articles[article_id])
    years.sort(reverse=True)

    # Sort articles by types
    categories = {}
    articles_of_year = {}
    for article_id in biblio.articles:
        article_type = type_to_section[biblio.articles[article_id]["type"]]
        annee = biblio.articles[article_id]["annee"]
        if not categories.has_key(article_type):
            categories[article_type] = []
        categories[article_type].append(biblio.articles[article_id])
        if not articles_of_year.has_key(annee):
            articles_of_year[annee] = []
        articles_of_year[annee].append(article_id)

    # Tri des articles du type par date
    # Pour tous les types
    for article_type in categories:
        sorted_list = []
        # Pour chaque annee décroissante
        for annee in years:
            # Pour chaque article du type
            for article in categories[article_type]:
                article_id = article["article_id"]
                if article_id in articles_of_year[annee]:
                    sorted_list.append(article)

        # Remplacer les articles triés
        categories[article_type] = sorted_list

    i = 1
    for category in type_order:
        for article in categories[category]:
            article['counter'] = i
            i+=1

    handle = codecs.open(cv_file, 'w', 'utf-8')
    handle.write(cvTemplate.render(tri=type_order, articles=categories, date=date))
    handle.close()


except xml.sax.SAXException as e:
    print input_file, e.getMessage()