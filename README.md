# mikrob

**mikrob** is a minimal Python static site generator for markdown-based blogs. Convert markdown posts to HTML with custom templates and host on GitHub Pages.

## Demo
See a live example at [mrkramar.github.io](https://mrkramar.github.io/).

## Creating a post
Posts are stored in the `/posts` directory as markdown files. Register each post in `config.json` with a title and date:

```json
"posts": {
    "my_first_post": {
        "title": "My first post",
        "date": "23-1-2021",
        "image": "images/cover.webp",
        "preview_text": "Custom preview text"
    }
}
```

The post filename must match the config key. Posts appear on the index in the order they're defined.

**Optional fields:**
- `preview_text`: Omit to use the first paragraph automatically
- `image`: Post cover image for the preview

## Markdown format

Posts support a simplified markdown syntax:
- Headers: `# h1`, `## h2`, `### h3`
- Bold: `**text**`
- Links: `[label](url)`
- Images: `![alt](path)`

## Static pages

Custom pages (about, contact, etc.) are created in `/templates`. Available template variables:
- `{{ head }}` → Contents of `/templates/site_parts/head.html`
- `{{ navbar }}` → Contents of `/templates/site_parts/navbar.html`
- `{{ img }}` → Replaced with `images/`

Example `index.html`:
```html
<!DOCTYPE html>
<html>
  {{ head }}
  <body>
    {{ navbar }}
    {{ post_previews }}
  </body>
</html>
```

## Usage

```bash
python compile.py
```

Requires Python 3.8+ (tested with 3.12). 
No external dependencies are required.
Pillow library is an optional dependency - if it is present in your environment, you can use the feature for downscaling images to set resolution.

Output is generated in the `/compiled` directory.

## Planned features
- Lists
- Blockquotes
