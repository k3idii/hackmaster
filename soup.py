from bs4 import BeautifulSoup


## PARSER

def html_parse(html):
  return BeautifulSoup(html, "html.parser")


def find_tag(html, tag, **attr):
  doc = BeautifulSoup(html, "html.parser")
  return doc.find_all(tag, **attr)




