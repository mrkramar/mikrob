import os
import shutil

posts_path = 'posts'
templates_path = 'templates'
images_path = 'images'
site_parts_path = templates_path + '/' + 'site_parts'
compiled_path = 'compiled'

def initial_setup():
    os.makedirs(compiled_path, exist_ok=True)
    os.makedirs(compiled_path + '/posts', exist_ok=True)

def write_html(filename, html):
    with open(compiled_path + '/' + filename, 'w+') as f:
        f.write(html)


class Post:
    def __init__(self, posts_path, id):
        with open(posts_path + '/' + id, 'r') as post_content:
            post_content = post_content.readlines()
            self.id = id.strip('.txt')
            self.date = post_content[0].strip('\n')
            self.title = post_content[1].strip('\n')
            paragrahs = post_content[3:]
            body = ''
            for p in paragrahs:
                if p == '\n':
                    p = '\n<br><br>\n'
                body += p
            self.body = body
    
    def preview(self, template):
        return template \
            .replace('{{ post_title }}', self.title) \
            .replace('{{ post_date }}', self.date) \
            .replace('{{ post_preview_text }}', self.body) \
            .replace('{{ post_link }}', 'posts/' + self.id + '.html')

    def html(self, template):
        return template \
            .replace('{{ head }}', head) \
            .replace('{{ navbar }}', navbar) \
            .replace('{{ post_title }}', self.title) \
            .replace('{{ post_date }}', self.date) \
            .replace('{{ post_body }}', self.body)

    def compile(self):
        write_html('posts/' + self.id + '.html', self.html(post_site_template))


def compile_posts_and_index():
    posts = []
    for post_id in os.listdir(posts_path):
        post = Post(posts_path, post_id)
        posts.append(post)
        post.compile()

    with open(site_parts_path + '/post_preview.html', 'r') as template:
        template = template.read()
        post_previews = [post.preview(template) for post in posts]
        post_previews = '\n'.join(post_previews)

    with open(templates_path + '/index.html') as template:
        html = template \
            .read() \
            .replace('{{ head }}', head) \
            .replace('{{ navbar }}', navbar) \
            .replace('{{ post_previews }}', post_previews)
        write_html('index.html', html)

def compile_static():
    for site in ['about.html', 'contact.html']:
        with open(templates_path + '/' + site) as template:
            html = template \
                .read() \
                .replace('{{ head }}', head) \
                .replace('{{ navbar }}', navbar) \
                .replace('{{ img }}', 'images/')
            write_html(site, html)

def copy_images():
    if os.path.exists(compiled_path + '/images'):
        shutil.rmtree(compiled_path + '/images')
    shutil.copytree(images_path, compiled_path + '/images')

def copy_css():
    shutil.copyfile(templates_path + '/style.css', compiled_path + '/style.css')

def compile_all():
    compile_posts_and_index()
    compile_static()
    copy_css()
    copy_images()

post_site_template = open(templates_path + '/post.html').read()
navbar = open(site_parts_path + '/navbar.html').read()
head = open(site_parts_path + '/head.html').read()

initial_setup()
compile_all()
print('done')
