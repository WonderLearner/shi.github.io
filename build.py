#!/usr/bin/env python3
"""Build the academic website with Python 3. No third-party packages required."""
from pathlib import Path
from html import escape
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
SITE = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
PAPERS = json.loads((ROOT / 'content/publications.json').read_text(encoding='utf-8'))
NAV = [('index.html', 'About'), ('research.html', 'Research'), ('publications.html', 'Publications'),
       ('team.html', 'Team'), ('teaching.html', 'Teaching'), ('join.html', 'Join us')]

def e(value):
    return escape(str(value), quote=True)

def link(url, label, cls=''):
    return f'<a href="{e(url)}"' + (f' class="{e(cls)}"' if cls else '') + f'>{e(label)}</a>'

def image(path, alt, cls='', eager=False):
    return f'<img src="{e(path)}" alt="{e(alt)}" class="{e(cls)}" loading="{"eager" if eager else "lazy"}" decoding="async">'

def page(filename, title, body, description=''):
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == filename else '') + f'>{label}</a>' for url, label in NAV)
    doc_title = f'{title} | Shengling Shi · TU Delft' if filename != 'index.html' else 'Shengling Shi | Learning & Control · TU Delft'
    description = description or SITE['intro']
    person = {'@context':'https://schema.org','@type':'Person','name':SITE['name'],
              'jobTitle':SITE['role'],'email':SITE['email'],
              'affiliation':{'@type':'CollegeOrUniversity','name':'Delft University of Technology'},
              'sameAs':[SITE['scholar'],SITE['profile']]}
    person_json = json.dumps(person, ensure_ascii=False).replace('<', '\\u003c')
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(doc_title)}</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#172e44"><meta property="og:title" content="{e(doc_title)}">
<meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script>
<script type="application/ld+json">{person_json}</script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="index.html" aria-label="Shi Group home"><span class="brand-mark" aria-hidden="true">S.</span><span class="brand-name">Shi Group<span>TU Delft</span></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation">Menu</button>
<nav class="nav-links" id="site-navigation" aria-label="Main navigation">{nav}</nav>
</div></header>
<main class="wrap" id="main">{body}</main>
<footer class="site-footer"><div class="wrap">
<div class="footer-top"><div><p class="footer-name">Shengling Shi</p><p class="footer-address">Delft Center for Systems and Control<br>Faculty of Mechanical Engineering · TU Delft<br>{link('mailto:'+SITE['email'],SITE['email'])}</p></div>
<div class="footer-links">{link(SITE['scholar'],'Google Scholar')}{link(SITE['profile'],'TU Delft profile')}{link(SITE['department_url'],'DCSC')}</div></div>
<div class="footer-bottom"><span>© 2026 Shengling Shi</span><span>{link('https://www.youtube.com/@DCSCTUDelft','DCSC seminars')} &nbsp;·&nbsp; {link('https://disc.tudelft.nl/','DISC')}</span></div>
</div></footer></body></html>'''
    (OUT / filename).write_text(html, encoding='utf-8')

def header(title, lead='', eyebrow='Shi Group · TU Delft'):
    return f'<div class="page-header"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1>' + (f'<p class="lead">{e(lead)}</p>' if lead else '') + '</div>'

def heading(title, url='', label=''):
    return f'<div class="section-heading"><h2>{e(title)}</h2>' + (link(url,label) if url else '') + '</div>'

def paper(p, tag=False):
    authors = re.sub(r'(?<!\w)S\. Shi\*?', lambda m: '<strong>'+m.group(0)+'</strong>', e(p['authors']))
    title = link(p['links'][0]['url'],p['title']) if p['links'] else e(p['title'])
    links = ''.join(link(x['url'], 'arXiv' if x['label']=='ArXiv' else x['label']) for x in p['links'])
    return f'<li class="paper">' + (f'<span class="tag">{e(p["year"])} · {e(p["topic"])}</span>' if tag else '') + f'<h3>{title}</h3><p class="authors">{authors}</p><p class="citation">{e(p["citation"])}</p><div class="paper-links">{links}</div></li>'

def paper_list(papers, tag=False):
    return '<ul class="paper-list">'+''.join(paper(p,tag) for p in papers)+'</ul>'

def news(items):
    return '<ul class="news-list">'+''.join(f'<li class="news-item"><time>{e(n["date"])}</time><p>{e(n["text"])} ' + (link(n['url'],n['link_label']) if n.get('url') else '') + '</p></li>' for n in items)+'</ul>'

def video(v):
    title=e(v['title']);poster=e(v['poster'])
    if v['type']=='mp4':
        tracks=''.join(f'<track kind="captions" src="{e(t["src"])}" srclang="{e(t["language"])}" label="{e(t["label"])}">' for t in v.get('captions',[]))
        content=f'<video controls autoplay muted loop playsinline preload="metadata" poster="{poster}" aria-label="{title}"><source src="{e(v["src"])}" type="video/mp4">{tracks}Your browser does not support this video. {link(v["src"],"Download video")}</video>'
        fallback = ''
    else:
        if v['type']=='youtube':
            embed='https://www.youtube-nocookie.com/embed/'+v['id']+'?autoplay=1'
            external='https://www.youtube.com/watch?v='+v['id']
        elif v['type']=='drive':
            embed='https://drive.google.com/file/d/'+v['id']+'/preview'
            external='https://drive.google.com/file/d/'+v['id']+'/view'
        else:raise ValueError('Unknown video type: '+v['type'])
        content=f'<button class="video-launch" type="button" data-embed="{e(embed)}" data-title="{title}" aria-label="Play {title}">{image(v["poster"], "") }<span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3v18l15-9z"/></svg></span></button>'
        fallback=link(external,'Open video','external-video')
    return f'<figure class="video-card"><div class="video-frame">{content}</div><figcaption><h3>{title}</h3><p>{e(v["description"])}</p>{fallback}</figcaption></figure>'

def home():
    body=f'''<section class="hero" aria-labelledby="intro-title"><div class="hero-copy">
<p class="eyebrow">Delft Center for Systems and Control</p><h1 id="intro-title">Shengling Shi</h1>
<p class="role">Assistant Professor · TU Delft</p>
<p class="intro">{e(SITE['intro'])}</p><p class="intro">{e(SITE['research_intro'])}</p>
<div class="text-links">{link('mailto:'+SITE['email'],'Email')}{link(SITE['scholar'],'Google Scholar')}{link(SITE['profile'],'TU Delft profile')}</div></div>
<figure class="portrait">{image(SITE['portrait'],'Shengling Shi','',True)}<figcaption>Learning, dynamics, and control<br>Delft, the Netherlands</figcaption></figure></section>'''
    cards=''.join(f'<article class="research-card"><a class="image-link" href="research.html#{r["id"]}" aria-label="{e(r["title"])}">{image(r["image"],r["alt"])}</a><p class="number">0{i+1}</p><h3>{link("research.html#"+r["id"],r["title"])}</h3><p>{e(r["short"])}</p></article>' for i,r in enumerate(SITE['research']))
    body+='<section class="section" aria-label="Research">'+heading('Research','research.html','Explore our work')+'<div class="research-grid">'+cards+'</div></section>'
    body+='<section class="section" aria-label="News">'+heading('News')+news(SITE['news'][:4])+'<details class="archive"><summary>Earlier news</summary>'+news(SITE['news'][4:])+'</details></section>'
    body+='<section class="section" aria-label="Selected publications">'+heading('Selected publications','publications.html','All publications')+paper_list(PAPERS[:3],True)+'</section>'
    body+='<section class="section" aria-label="Biography">'+heading('Background')+f'<p>{e(SITE["bio"])}</p><p>{e(SITE["service"])}</p></section>'
    page('index.html','About',body)

def research():
    body=header('Research','Learning and control methods grounded in theory, with applications to human movement and robotics.')
    body+='<nav class="anchor-nav" aria-label="Research areas">'+''.join(link('#'+r['id'],r['title']) for r in SITE['research'])+'</nav>'
    for i,r in enumerate(SITE['research']):
        related=[p for prefix in r['papers'] for p in PAPERS if p['title'].startswith(prefix)]
        refs='<div class="related"><h3>Related publications</h3><ul>'+''.join('<li>'+link(p['links'][0]['url'],p['title'])+'</li>' for p in related)+'</ul></div>' if related else ''
        body+=f'<section class="research-detail" id="{r["id"]}"><div class="research-main"><div><p class="eyebrow">Research area 0{i+1}</p><h2>{e(r["title"])}</h2><p>{e(r["description"])}</p>{refs}</div><figure class="research-figure">{image(r["image"],r["alt"])}<figcaption>{e(r["caption"])}</figcaption></figure></div>'
        if r['id']=='bio-inspired':body+='<div class="video-grid">'+''.join(video(v) for v in SITE['videos'][:2])+'</div>'
        if i == 1:
            body += '<div class="featured-video">'
            body += video({
                "title": "Constrained Generative Model for Human Motion Generation",
                "description": "Qijun Feng · MSc thesis, 2026",
                "type": "mp4",
                "src": "https://folklorer5.github.io/constraint-guided-human-motion-page/assets/videos/teaser.mp4",
                "poster": "https://folklorer5.github.io/constraint-guided-human-motion-page/assets/images/teaser.jpg"
            })
            body += '<p>' + link(
                "https://folklorer5.github.io/constraint-guided-human-motion-page/",
                "Project page"
            ) + '</p>'
            body += '</div>'
        body+='</section>'
    page('research.html','Research',body)

def publications():
    body=header('Publications','Journal articles, conference papers, and preprints in learning-based control and system identification.')
    body+='<div class="pub-layout"><nav class="pub-sidebar" aria-label="Publication sections"><span class="eyebrow">Browse</span>'
    for id,label in [('journals','Journal articles'),('conferences','Conference papers'),('preprints','Preprints'),('software','Software')]:body+=link('#'+id,label)
    body+=link(SITE['scholar'],'Google Scholar')+'</nav><div>'
    for kind,id,title in [('Journal Papers','journals','Journal articles'),('Conference Proceedings','conferences','Conference papers'),('Submitted Papers','preprints','Preprints')]:
        ps=sorted([p for p in PAPERS if p['kind']==kind],key=lambda p:p['year'],reverse=True)
        body+=f'<section class="pub-group" id="{id}"><h2>{title}</h2>'+paper_list(ps,True)+'</section>'
    body+='<section class="pub-group" id="software"><h2>Software</h2><div class="software"><h3>SYSDYNET</h3><p>A MATLAB app and toolbox for dynamic network identification, developed with collaborators.</p><p>P. M. J. Van den Hof, S. Shi, et al. “SYSDYNET – A MATLAB App and Toolbox for Dynamic Network Identification.” IFAC Symposium on System Identification, 2024.</p><div class="paper-links">'+link('https://www.sysdynet.net/','Toolbox website')+link('https://www.sciencedirect.com/science/article/pii/S2405896324013715?via%3Dihub','Paper')+'</div></div></section></div></div>'
    page('publications.html','Publications',body)

def team():
    body=header('Our team','Researchers and students working across learning, dynamics, and control.')
    body+=f'<section class="group-photo" aria-label="Faculty">{image(SITE["portrait"],"Shengling Shi")}<div><p class="eyebrow">Faculty</p><h2>Shengling Shi</h2><p class="role">Assistant Professor</p><p>{e(SITE["bio"])}</p><div class="text-links">{link("mailto:"+SITE["email"],"Email")}{link(SITE["scholar"],"Google Scholar")}</div></div></section>'
    for role,title in [('PhD student','PhD researchers'),('MSc student',"Master’s students")]:
        body+='<section class="section">'+heading(title)+'<div class="people-grid">'
        for m in SITE['members']:
            if m['role']!=role:continue
            body+=f'<article class="person"><h3>{e(m["name"])}</h3><p class="person-role">{e(m["role"])} · TU Delft</p>'
            if m['topic']:body+=f'<p class="topic">{e(m["topic"])}</p>'
            body+=f'<p class="education">{e(m["education"])}</p>'
            if m['coadvisors']:body+=f'<p class="coadvisors">{e(m["coadvisors"])}</p>'
            body+='</article>'
        body+='</div></section>'
    body += '<section class="section">' + heading("Bachelor’s students") + '</section>'
    body+='<section class="section">'+heading('Alumni')+'<div class="alumni-list">'
    for a in SITE['alumni']:
        body+=f'<article class="alumnus"><h3>{e(a["name"])}</h3><p class="metadata">{e(a["degree"])} · {e(a["year"])}</p><p class="thesis">'+(link(a['url'],a['title']) if a['url'] else e(a['title']))+'</p>'
        if a['coadvisors']:body+=f'<p class="coadvisors">{e(a["coadvisors"])}</p>'
        if a['next']:body+=f'<p class="next">Next position: {e(a["next"])}</p>'
        body+='</article>'
    body+='</div></section>'
    page('team.html','Team',body)

def teaching():
    body=header('Teaching','Courses in signals, dynamical systems, and control.')
    for c in SITE['teaching']:
        body+=f'<article class="course"><time>{e(c["year"])}</time><div><h2>{e(c["title"])}</h2><p class="metadata">{e(c["level"])} course · {e(c["institution"])}</p><p>{e(c["description"])}</p></div></article>'
    body+='<section class="contact-panel"><h2>Thesis and research projects</h2><p>Interested in a bachelor’s or master’s research project? '+link('join.html','Learn about working with the group')+'.</p></section>'
    page('teaching.html','Teaching',body)

def join():
    o=SITE['opportunities']
    body=header('Join us','Thesis projects, research visits, and fellowship opportunities.')
    for title,txt in [('PhD & postdoc',o['phd_postdoc']),('Visiting researchers',o['visitors']),('Student projects',o['students'])]:
        body+=f'<section class="opportunity"><h2>{e(title)}</h2><div><p>{e(txt)}</p>'
        if title=='Visiting researchers':body+='<p>'+link('https://marie-sklodowska-curie-actions.ec.europa.eu/actions/postdoctoral-fellowships','MSCA Postdoctoral Fellowships')+'</p>'
        body+='</div></section>'
    body+='<section class="contact-panel"><h2>Get in touch</h2><p>'+link('mailto:'+SITE['email'],SITE['email'])+'</p><p>Delft Center for Systems and Control<br>Faculty of Mechanical Engineering<br>Delft University of Technology, the Netherlands</p></section>'
    page('join.html','Join us',body)

def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
    (OUT/'.nojekyll').touch()
    home(); research(); publications(); team(); teaching(); join()
    page('404.html','Page not found',header('Page not found','The page may have moved.')+'<p>'+link('index.html','Return to the homepage')+'</p>')
    print(f'Built 7 pages and {len(PAPERS)} publication entries in {OUT}')

if __name__=='__main__':build()
