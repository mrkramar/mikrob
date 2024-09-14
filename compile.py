import os
import shutil
import re
import json


posts_path = 'posts'
templates_path = 'templates'
images_path = 'images'
site_parts_path = templates_path + '/' + 'site_parts'
compiled_path = 'compiled'

post_site_template = open(templates_path + '/post.html').read()
post_preview_template = open(site_parts_path + '/post_preview.html').read()
navbar = open(site_parts_path + '/navbar.html').read()
head = open(site_parts_path + '/head.html').read()


class Post:
    def __init__(self, id, metadata):
        with open(posts_path + f'/{id}.md', 'r') as post_content:
            lines = post_content.readlines()

        self.id = id
        self.body = self.parse_body(lines)
        self.title = metadata['title']
        self.date = metadata['date']
        self.preview_image = metadata['image']
        self.preview_text = metadata['preview_text']
    
    def preview(self, template):    
        return template \
            .replace('{{ post_title }}', self.title) \
            .replace('{{ post_date }}', self.date) \
            .replace('{{ post_preview_text }}', f'<p>{self.preview_text}</p>') \
            .replace('{{ post_link }}', 'posts/' + self.id + '.html') \
            .replace('{{ post_preview_image }}', 
                     f'<a href="posts/{self.id}.html" target="_blank"><img src="{self.preview_image}" alt="{self.title}"></a>')


    def html(self, template):
        return template \
            .replace('{{ head }}', head) \
            .replace('{{ navbar }}', navbar.replace('./', '../')) \
            .replace('{{ post_title }}', self.title) \
            .replace('{{ post_date }}', self.date) \
            .replace('{{ post_body }}', self.body)

    def parse_body(self, lines):
        result = []

        def process_text(text):
            # Convert bold text
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Convert images 
            text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<a href="\2" target="_blank"><img src="\2" alt="\1"></a>', text)
            # Convert links
            text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
            return text

        for line in lines:
            if line == '\n':
                result.append('\n</p><br><p>\n')
            if line.startswith('###'):
                result.append(f'</p><h3>{process_text(line[3:].strip())}</h3><p>')
            elif line.startswith('##'):
                result.append(f'</p><h2>{process_text(line[2:].strip())}</h2><p>')
            elif line.startswith('#'):
                result.append(f'</p><h1>{process_text(line[1:].strip())}</h1><p>')
            else:
                result.append(process_text(line))

        return ''.join(result)


def compile_posts_and_index(config):
    posts = []
    for post_key, post_config in config['posts'].items():
        post = Post(post_key, post_config)
        posts.append(post)
        write_html(f'posts/{post.id}.html', post.html(post_site_template))

    post_previews = '\n'.join([post.preview(post_preview_template) for post in posts])

    with open(templates_path + '/index.html') as template:
        html = template \
            .read() \
            .replace('{{ head }}', head) \
            .replace('{{ navbar }}', navbar) \
            .replace('{{ post_previews }}', post_previews)
        write_html('index.html', html)


def compile_sites():
    for site in ['about.html', 'contact.html']:
        with open(templates_path + '/' + site) as template:
            html = template \
                .read() \
                .replace('{{ head }}', head) \
                .replace('{{ navbar }}', navbar) \
                .replace('{{ img }}', 'images/')
            write_html(site, html)


def copy_static_files():
    # css
    shutil.copyfile(templates_path + '/style.css', compiled_path + '/style.css')

    # images
    if os.path.exists(compiled_path + '/images'):
        shutil.rmtree(compiled_path + '/images')
    shutil.copytree(images_path, compiled_path + '/images')


def write_html(filename, html):
    with open(compiled_path + '/' + filename, 'w+') as f:
        f.write(html)


def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    # prepare dirs
    os.makedirs(compiled_path, exist_ok=True)
    os.makedirs(compiled_path + '/posts', exist_ok=True)

    compile_posts_and_index(config)
    compile_sites()
    copy_static_files()


main()
print('done')
