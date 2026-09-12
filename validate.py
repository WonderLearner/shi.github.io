#!/usr/bin/env python3
"""Check generated pages, fragments, metadata, and local media before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT=Path(__file__).resolve().parent/'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.references=[];self.errors=[];self.h1s=0;self.main=0;self.title=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.errors.append('Duplicate ID: '+a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.h1s+=1
        if tag=='main':self.main+=1
        if tag=='title':self.title+=1
        if tag=='img' and 'alt' not in a:self.errors.append('Image missing alt text')
        if tag=='iframe' and not a.get('title'):self.errors.append('Iframe missing title')
        for attr in ['href','src','poster']:
            if a.get(attr):self.references.append(a[attr])

def validate():
    pages={};errors=[]
    for file in ROOT.glob('*.html'):
        p=Page();p.feed(file.read_text(encoding='utf-8'));pages[file.resolve()]=p
        errors += [file.name+': '+x for x in p.errors]
        if (p.h1s,p.main,p.title)!=(1,1,1):errors.append(file.name+': expected one h1, main, and title')
    if len(pages)!=7:errors.append('Expected seven HTML pages')
    for file,p in pages.items():
        for ref in p.references:
            url=urlsplit(ref)
            if url.scheme or url.netloc:continue
            dest=(file.parent/unquote(url.path)).resolve() if url.path else file
            if not dest.is_relative_to(ROOT.resolve()):errors.append(file.name+': reference escapes output: '+ref)
            elif not dest.is_file():errors.append(file.name+': missing local file: '+ref)
            elif url.fragment and dest in pages and unquote(url.fragment) not in pages[dest].ids:
                errors.append(file.name+': missing anchor: '+ref)
    if errors:
        print('\n'.join(errors));sys.exit(1)
    print(f'Validated {len(pages)} pages: local links, anchors, media, document structure, and image labels.')
if __name__=='__main__':validate()
