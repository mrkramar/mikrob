import os
import shutil
import re
import json

# Paths
POSTS = 'posts'
TEMPLATES = 'templates'
IMAGES = 'images'
SITE_PARTS = os.path.join(TEMPLATES, 'site_parts')
STATIC_SITES = os.path.join(TEMPLATES, 'static_sites')
COMPILED = 'compiled'
IMAGE_MAX_HEIGHT = 1000  # default max height for images in pixels; change as needed

# Optional: use Pillow for downscaling images. If not installed, images are copied unchanged.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Load templates
def load_template(path):
    with open(path) as f:
        return f.read()

TEMPLATES_DATA = {
    'post': load_template(os.path.join(TEMPLATES, 'post.html')),
    'preview': load_template(os.path.join(SITE_PARTS, 'post_preview.html')),
    'navbar': load_template(os.path.join(SITE_PARTS, 'navbar.html')),
    'head': load_template(os.path.join(SITE_PARTS, 'head.html')),
}

# Regex patterns
BOLD = re.compile(r'\*\*(.*?)\*\*')
IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
FIRST_PARA = re.compile(r'<p>\s*(.*?)\s*</p>', re.DOTALL)
CODE_BLOCK = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)


def replace_vars(template, **vars):
    """Replace template variables."""
    for key, value in vars.items():
        template = template.replace(f'{{{{ {key} }}}}', value)
    return template


def process_text(text):
    """Convert markdown syntax to HTML."""
    text = BOLD.sub(r'<b>\1</b>', text)
    text = IMAGE.sub(r'<a href="\2" target="_blank"><img src="\2" alt="\1"></a>', text)
    text = LINK.sub(r'<a href="\2" target="_blank">\1</a>', text)
    return text


def parse_list(items):
    """Convert list items to HTML."""
    html = '<ul>'
    for item in items:
        html += f'<li>{process_text(item.strip())}</li>'
    html += '</ul>'
    return html


def parse_code_blocks(text):
    """Convert markdown code blocks to HTML with syntax highlighting."""
    def replace_code(match):
        lang = match.group(1) or ''
        code = match.group(2)
        escaped_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{escaped_code}</code></pre>'
    return CODE_BLOCK.sub(replace_code, text)


def downscale_images(root_dir, max_height):
    """Recursively downscale images under root_dir to have at most max_height pixels in height.

    Uses Pillow if available; otherwise does nothing.
    """
    if not PIL_AVAILABLE:
        print('Pillow not installed; skipping image downscaling. Install with: pip install pillow')
        return

    resized_count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                with Image.open(path) as img:
                    w, h = img.size
                    if h <= max_height:
                        continue
                    new_h = max_height
                    new_w = int(w * (new_h / h))
                    resized = img.resize((new_w, new_h), Image.LANCZOS)
                    # Preserve format and quality for JPEG
                    fmt = img.format or 'JPEG'
                    if fmt.upper() == 'JPEG':
                        resized.save(path, format=fmt, quality=85)
                    else:
                        resized.save(path, format=fmt)
                    resized_count += 1
            except Exception:
                # Not an image or cannot process; skip
                continue

    if resized_count:
        print(f'Downscaled {resized_count} images to max height {max_height}px')
    else:
        print('No images required downscaling')


class Post:
    def __init__(self, id, metadata):
        with open(os.path.join(POSTS, f'{id}.md')) as f:
            lines = f.readlines()
        
        self.id = id
        self.body = self.parse_body(lines)
        self.title = metadata['title']
        self.date = metadata['date']
        self.preview_image = metadata.get('image')
        self.preview_text = metadata.get('preview_text', self.extract_first_paragraph())
    
    def preview(self, template):
        image_html = ''
        if self.preview_image:
            image_html = f'<a href="posts/{self.id}.html"><img src="{self.preview_image}" alt="{self.title}"></a>'
        
        return replace_vars(template,
            post_title=self.title,
            post_date=self.date,
            post_preview_text=f'<p>{self.preview_text}</p>',
            post_link=f'posts/{self.id}.html',
            post_preview_image=image_html)

    def html(self, template):
        return replace_vars(template,
            head=TEMPLATES_DATA['head'],
            navbar=TEMPLATES_DATA['navbar'].replace('./', '../'),
            post_title=self.title,
            post_date=self.date,
            post_body=self.body)

    def parse_body(self, lines):
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if line == '\n':
                result.append('\n</p><p>\n')
            elif line.startswith('```'):
                # Collect code block
                lang = line[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code_block = f'```{lang}\n' + ''.join(code_lines) + '```'
                result.append('</p>')
                result.append(parse_code_blocks(code_block))
                result.append('<p>')
            elif line.startswith('- '):
                # Collect consecutive list items
                list_items = []
                while i < len(lines) and lines[i].startswith('- '):
                    list_items.append(lines[i][2:])
                    i += 1
                result.append('</p>')
                result.append(parse_list(list_items))
                result.append('<p>')
                i -= 1  # Adjust because the outer loop will increment
            elif line.startswith('###'):
                result.append(f'</p><h3>{process_text(line[3:].strip())}</h3><p>')
            elif line.startswith('##'):
                result.append(f'</p><h2>{process_text(line[2:].strip())}</h2><p>')
            elif line.startswith('#'):
                result.append(f'</p><h1>{process_text(line[1:].strip())}</h1><p>')
            else:
                result.append(process_text(line))
            
            i += 1
        
        return '<p>' + ''.join(result) + '</p>'
    
    def extract_first_paragraph(self):
        match = FIRST_PARA.search(self.body)
        return match.group(1).strip() if match else ''


def write_html(filename, html):
    os.makedirs(os.path.dirname(os.path.join(COMPILED, filename)), exist_ok=True)
    with open(os.path.join(COMPILED, filename), 'w') as f:
        f.write(html)


def compile_posts_and_index(config):
    posts = [Post(id, data) for id, data in config['posts'].items()]
    
    for post in posts:
        write_html(f'posts/{post.id}.html', post.html(TEMPLATES_DATA['post']))
    
    previews = '\n'.join(post.preview(TEMPLATES_DATA['preview']) for post in posts)
    index_html = replace_vars(load_template(os.path.join(TEMPLATES, 'index.html')),
        head=TEMPLATES_DATA['head'],
        navbar=TEMPLATES_DATA['navbar'],
        post_previews=previews)
    write_html('index.html', index_html)


def compile_sites():
    for filename in os.listdir(STATIC_SITES):
        if filename.endswith('.html'):
            template = load_template(os.path.join(STATIC_SITES, filename))
            html = replace_vars(template,
                head=TEMPLATES_DATA['head'],
                navbar=TEMPLATES_DATA['navbar'],
                img='images/')
            write_html(filename, html)


def copy_static_files():
    shutil.copyfile(os.path.join(TEMPLATES, 'style.css'), os.path.join(COMPILED, 'style.css'))
    
    images_dest = os.path.join(COMPILED, 'images')
    if os.path.exists(images_dest):
        shutil.rmtree(images_dest)
    shutil.copytree(IMAGES, images_dest)
    # Downscale images in the compiled output if Pillow is available
    downscale_images(images_dest, IMAGE_MAX_HEIGHT)


def main():
    with open('config.json') as f:
        config = json.load(f)
    
    os.makedirs(os.path.join(COMPILED, 'posts'), exist_ok=True)
    compile_posts_and_index(config)
    compile_sites()
    copy_static_files()
    print('done')


if __name__ == '__main__':
    main()
