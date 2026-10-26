---
layout: page
title: Publications
subtitle: Find our papers on DBLP
---

Each member's DBLP page has their full, up-to-date publication list.

## Members

<ul>
{% for person in site.data.people.members %}{% if person.dblp %}
  <li><a href="{{ person.dblp }}">{{ person.name }}</a></li>
{% endif %}{% endfor %}
</ul>

## Past PhD students

<ul>
{% for person in site.data.people.alumni %}{% if person.dblp %}
  <li><a href="{{ person.dblp }}">{{ person.name }}</a></li>
{% endif %}{% endfor %}
</ul>
