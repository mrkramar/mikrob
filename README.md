# mikrob

**mikrob** (mikro blog) is a python application for compiling markdown-like format blog entries into static html, that can be hosted on github pages. It comes with its own html/css templates with minimalistic design.

## Demo
You can see mikrob-compiled blog on my [github pages](https://mrkramar.github.io/).

## Creating a post
Posts are stored in `/posts` in a markdown format and can be named any way. To have a post displayed, it needs to be
registered in the `config.json`. Each post must have defined: title, date, preview text and image. Following is an example of such configuration:

```
"posts": {
    "my_first_post": {
        "title": "My first post",
        "date": "23-1-2021",
        "image": "../images/ipsum.webp",
        "preview_text": "This is my first post, welcome to my blog."
    },
```

The key must be the same as the markdown file name. Posts in the index will be ordered the same way as in the config.

## Simplified markdown format

The posts use simplified markdown format. The following features are supported:
- headers: `# - h1, ## - h2, ## - h3`
- bold font: `**text**`
- hyperlinks: `[label](link)`
- images: `![label](path)`


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

## Compilation
To compile the blog run `python compile.py`. It was tested with python 3.12, but should work with other versions too.
The script doesn't require any additional dependecies.
Your static site will be in the `/compiled` folder.

## Future ideas
- add lists
- add quote blocks
