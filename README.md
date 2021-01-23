# mikrob

**mikrob** is a simple python application for compiling custom format blog entries into static html, that can be hosted on github pages. It comes with its own html templates with minimalistic design.

## Demo
You can see mikrob-compiled blog on my [github pages](https://mrkramar.github.io/).

## Writing posts
Posts are stored in `/posts`. They currently use very simple format, which consist only of date, title and paragraphs. In future, I will try to emulate simplified markdown format, so the posts can have their own subtitles, citations, etc.

```
<post date>
<post title>

<text paragraph1>
<text paragraph1>
<text paragraph1>

<text paragraph2>
<text paragraph2>
...
```

## Static pages
Static pages can be created in `/templates`. There are some predefined tags that can be used:
 - `{{ head }}` - is replaced with header defined in `/templates/site_parts/head.html`
 - `{{ navbar }}` - is replaced with navigation bar defined in `/templates/site_parts/navbar.html`

### Index
`index.html` template can be as simple as:
```html
<!DOCTYPE html>
<html lang="en">

{{ head }}

<body>

  {{ navbar }}

  {{ post_previews }}

</body>
</html>
```
with the use of tags described above.

## Compilation
Compilation is simple as running `python compile.py`.
Your static site will be in `/compiled` folder.
