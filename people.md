---
layout: page
title: People
subtitle: Members and alumni of QuasyLab
---

## Members

<ul>
{% for person in site.data.people.members %}
  <li>
    {% if person.homepage %}<a href="{{ person.homepage }}"><strong>{{ person.name }}</strong></a>{% else %}<strong>{{ person.name }}</strong>{% endif %}{% if person.role %} &mdash; {{ person.role }}{% endif %}{% if person.dblp %} &middot; <a href="{{ person.dblp }}">publications</a>{% endif %}
  </li>
{% endfor %}
</ul>

## Past PhD students

<ul>
{% for person in site.data.people.alumni %}
  <li>
    {% if person.homepage %}<a href="{{ person.homepage }}"><strong>{{ person.name }}</strong></a>{% else %}<strong>{{ person.name }}</strong>{% endif %}{% if person.dblp %} &middot; <a href="{{ person.dblp }}">publications</a>{% endif %}
  </li>
{% endfor %}
</ul>
