#!/usr/bin/env python
"""Sutom cheating program"""

import sys
import os
from argparse import ArgumentParser

import requests
from bs4 import BeautifulSoup

LOCAL_CACHE_PATH = "~/.cache/sutom"
WEBSITE = "www.listesdemots.net"


def get_url_path(letter, pos):
  """Determines the URL path for a given letter and letter position"""
  return f"https://{WEBSITE}/{pos[0]}/{letter}/1/"


def get_url_file(letter, pos, length, page):
  """Determines the URL filename for a given letter, letter position, word
     length, and page"""
  return f"mots{length}lettres{pos}{letter}" \
         f"{'page' if page > 1 else ''}"     \
         f"{page if page > 1 else ''}.htm"


def get_url(letter, pos, length, page):
  """Determines the complete URL for a given letter, letter position, word
     length, and page"""
  return "".join([get_url_path(letter, pos),
                  get_url_file(letter, pos, length, page)])


def get_words(_l, _le, _p, page=1, last_page=None):
  """Recursively get the words from listesdemots.net and returns them"""
  http_response = requests.get(get_url(_l, _p, _le, page), timeout=30)
  html = BeautifulSoup(http_response.content, "html.parser")

  if last_page is None:
    # get last page
    last_page = html.select("html > body > table > tr > td.a_tp a.pg")[-1]
    try:
      last_page = int(last_page.get_text())
    except ValueError as _e:
      last_page = last_page['href']
      if not last_page:
        raise LookupError("Could not determine the last page on {WEBSITE}") \
              from _e

  words = html.select("html > body > table > tr > td.a_tp span.mt")[0] \
    .get_text().split()

  if isinstance(last_page, int):
    if get_url(_l, _p, _le, page) == get_url(_l, _p, _le, last_page):
      return words
  elif isinstance(last_page, str):
    if get_url_file(_l, _p, _le, page) == last_page:
      return words

  return words + get_words(_l, _le, _p, page + 1, last_page)


def write_words_to_cache(letter, length, file):
  """Write the words from get_words() to the cache file <file>"""
  pos = "debutant"  # Can be "finissant", see other options on listesdemots.net
  words = get_words(letter, length, pos)

  with open(file, 'a', encoding="utf8") as _f:
    _f.write("\n".join(words))


def calculate_score(word):
  """Calculate a word's 'score'"""
  letter_freqs = {'E': 0.163856062405439,
                  'A': 0.0846411160456124,
                  'I': 0.0753511519523731,
                  'S': 0.0738510221210065,
                  'N': 0.0724731336213265,
                  'R': 0.0688070190485508,
                  'T': 0.0671492647178708,
                  'O': 0.0574415479653822,
                  'L': 0.0562942473528375,
                  'U': 0.0513995722509306,
                  'D': 0.0416672451681509,
                  'C': 0.0367139095980486,
                  'M': 0.0297085830189299,
                  'P': 0.0282205841160575,
                  'G': 0.0139438727847322,
                  'B': 0.0129092304880543,
                  'V': 0.0126391481643633,
                  'H': 0.0126304411054067,
                  'F': 0.0126252259398858,
                  'Q': 0.00732785294144035,
                  'Y': 0.00519362820003302,
                  'X': 0.00428310684275233,
                  'J': 0.00390966041579792,
                  'K': 0.00327892731840535,
                  'W': 0.00197321217460795,
                  'Z': 0.00171123424200444}
  value = 0
  seen_letters = {}
  for letter in word:
    if letter not in seen_letters:
      seen_letters[letter] = 0
    seen_letters[letter] += 1

    letter_val = letter_freqs[letter.upper()]
    # We decrease the value with repeated letters
    value += letter_val / seen_letters[letter]
  return value


def matches_pattern(word, pattern):
  """Returns a bool representing if a word matches the pattern"""
  for index, pattern_letter in enumerate(pattern):
    if pattern_letter != '.' and word[index] != pattern_letter:
      return False
  return True


def matches_misplaced(word, misplaced):
  """Return a bool representing if a word matches one of the misplaced
     patterns"""
  if misplaced:
    for misplaced_pattern in misplaced:
      for index, misplaced_letter in enumerate(misplaced_pattern):
        if misplaced_letter != '.' \
           and word[index].upper() == misplaced_letter.upper():
          return True
  return False


def matches_absent(word, absent_letters):
  """Returns a bool representing if a word matches any absent letters"""
  if absent_letters:
    for letter in word:
      if letter.upper() in absent_letters.upper():
        return True
  return False


def main():
  """main procedure"""
  parser = ArgumentParser()
  parser.add_argument('pattern', metavar="SEARCH PATTERN with dots")
  parser.add_argument("-n", "--not-present", dest="absent", action="store",
                      help="LETTERS that aren't present in the pattern (cannot"
                      " be repeated)", metavar="LETTERS")
  parser.add_argument("-m", "--misplaced", dest="misplaced", action="append",
                      help="pattern with dots and misplaced letters "
                      "(can be repeated. DO NOT PUT MATCHES IN IT!)",
                      metavar="PATTERN")
  args = parser.parse_args()
  pattern = sys.argv[1].upper()
  filename = f"{pattern[0]}_{len(pattern)}.wrds"
  cachedir = os.path.expanduser(LOCAL_CACHE_PATH)
  cachefile = os.path.join(cachedir, filename)
  if not os.path.isdir(cachedir):
    os.makedirs(cachedir)
  if not os.path.isfile(cachefile):
    write_words_to_cache(pattern[0].lower(), len(pattern), cachefile)

  score = {}
  with open(cachefile, 'r', encoding="utf8") as _f:
    for word in _f.readlines():
      if matches_pattern(word, pattern) \
         and not matches_misplaced(word, args.misplaced) \
         and not matches_absent(word, args.absent):
        word = word.strip()
        score[word] = calculate_score(word)

  maxval = 0
  maxword = None
  for word, value in score.items():
    if value > maxval:
      maxval = value
      maxword = word

  print(f"{maxword} ({maxval})")


if __name__ == "__main__":
  main()
