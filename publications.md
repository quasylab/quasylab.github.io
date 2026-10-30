---
layout: page
title: Publications
subtitle: Papers by QuasyLab members
---

{% assign pubs = site.data.publications %}
{% assign years = pubs | group_by: "year" %}

<style>
  .pub-years { margin-bottom: 1.5rem; line-height: 2; }
  .pub-years a { margin-right: .6rem; }
  .pub-filter { margin-bottom: 1.5rem; }
  .pub-filter button { margin: 0 .3rem .4rem 0; }
  .pub-list { padding-left: 0; list-style: none; }
  .pub-list li { margin-bottom: 1rem; }
  .pub-title { font-weight: 600; }
  .pub-venue { font-style: italic; }
  .pub-label { font-size: .75rem; vertical-align: middle; }
  .pub-links a { font-size: .85rem; margin-right: .5rem; }
  .pub-member { font-weight: 600; }
</style>

This list is generated from [our BibTeX file]({{ '/quasylab.bib' | relative_url }}) ({{ pubs.size }} entries).
Names of group members are in **bold**. Each member's full list is also on DBLP: see the [People]({{ '/people' | relative_url }}) page.

<div class="pub-years">
{% for y in years %}<a href="#y{{ y.name }}">{{ y.name }}</a>{% endfor %}
</div>

<div class="pub-filter" role="group" aria-label="Filter by type">
  <button type="button" class="btn btn-sm btn-primary" data-filter="all">All</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-filter="article">Journal</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-filter="inproceedings">Conference</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-filter="incollection">Chapter</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-filter="proceedings">Editorship</button>
</div>

{% for y in years %}
<section class="pub-year" id="y{{ y.name }}">
<h2>{{ y.name }}</h2>
<ul class="pub-list">
{% for p in y.items %}
  <li data-type="{{ p.type }}">
    <span class="badge badge-secondary pub-label">{{ p.label }}</span>
    <span class="pub-title">{{ p.title | escape }}.</span><br>
    {% for a in p.authors %}{% if a.member %}<span class="pub-member">{{ a.name | escape }}</span>{% else %}{{ a.name | escape }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}{% if p.editors %} (eds.){% endif %}.<br>
    {% if p.venue != "" %}<span class="pub-venue">{{ p.venue | escape }}</span>, {% endif %}{{ p.year }}.
    <span class="pub-links">
      {% if p.doi %}<a href="https://doi.org/{{ p.doi }}">DOI</a>{% elsif p.url %}<a href="{{ p.url }}">Link</a>{% endif %}
      {% if p.dblp %}<a href="{{ p.dblp }}.bib">BibTeX</a>{% endif %}
    </span>
  </li>
{% endfor %}
</ul>
</section>
{% endfor %}

<script>
  document.querySelectorAll('.pub-filter button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = btn.dataset.filter;
      document.querySelectorAll('.pub-filter button').forEach(function (b) {
        b.classList.toggle('btn-primary', b === btn);
        b.classList.toggle('btn-outline-primary', b !== btn);
      });
      document.querySelectorAll('.pub-list li').forEach(function (li) {
        li.style.display = (f === 'all' || li.dataset.type === f) ? '' : 'none';
      });
      document.querySelectorAll('.pub-year').forEach(function (sec) {
        var visible = sec.querySelector('.pub-list li:not([style*="none"])');
        sec.style.display = visible ? '' : 'none';
      });
    });
  });
</script>
