import os
from html.parser import HTMLParser
import requests
import time

class TitleExtractor(HTMLParser):
    inHeading = False
    inSubHeading = False
    title = ''
    subtitle = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.inHeading = True
        if tag == 'section':
            for name, value in attrs:
                if name == 'data-field' and value == 'subtitle':
                    self.inSubHeading = True

    def handle_data(self, data):
        if self.inHeading:
            self.title = data
        if self.inSubHeading:
            self.subtitle = data

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.inHeading = False
        if tag == 'section':
            self.inSubHeading = False

    def get_title(self):
        return self.title

    def get_subtitle(self):
        return self.subtitle

class ImageDownloader(HTMLParser):
    def __init__(self, assets_folder='assets'):
        super().__init__()
        self.assets_folder = assets_folder
        self.image_urls = []
        self.modified_html = ''
        os.makedirs(self.assets_folder, exist_ok=True)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'img':
            if 'src' in attrs_dict:
                image_url = attrs_dict['src']
                print(f"Found image: {image_url}")
                self.image_urls.append(image_url)
                image_name = os.path.basename(image_url)
                local_path = os.path.join(self.assets_folder, image_name)
                if self.download_image(image_url, local_path):
                    attrs_dict['src'] = '/assets/' + image_name
        self.modified_html += f"<{tag} " + " ".join(f'{key}="{value}"' for key, value in attrs_dict.items()) + ">"

    def handle_endtag(self, tag):
        if tag == 'head':
            self.modified_html += '<link rel="stylesheet" href="/medium-export.css">'
        self.modified_html += f"</{tag}>"

    def handle_data(self, data):
        self.modified_html += data

    def download_image(self, url, path):
        if os.path.exists(path):
            print(f"Image already exists: {path}, skipping download.")
            return True
        try:
            response = requests.get(url, stream=True, timeout=10, allow_redirects=False)
            if response.status_code == 301:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    print(f"Redirecting from {url} to {redirect_url}")
                    return self.download_image(redirect_url, path)
                else:
                    print(f"301 response received but no Location header found for {url}")
                    return False
            elif response.status_code == 200:
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded successfully: {path}")
                return True
            else:
                print(f"Failed to download {url} HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"Failed to download {url} {e}")
            return False

    def get_modified_html(self):
        return self.modified_html

def cleanup(text):
    return text.split('|')[0] if '|' in text else text

# Collect blog links content
blog_content = ''
files = os.listdir('docs/posts_src')
files.sort(reverse=True)

for post in files:
    print(f"Processing file: {post}")
    with open(f'docs/posts_src/{post}', 'r') as file:
        html = file.read()
        parser = TitleExtractor()
        parser.feed(html)
        image_downloader = ImageDownloader(assets_folder='docs/assets')
        image_downloader.feed(html)
        html = image_downloader.get_modified_html()
        title = cleanup(parser.get_title())
        subtitle = cleanup(parser.get_subtitle())
        blog_content += f'''
            <a href="https://thebojda.github.io/posts/{post}" class="text-decoration-none" style="color:black;" target="_black">
                <div class="mb-4">
                    <h3>{title}</h3>
                    <p>{subtitle}</p>
                </div>
            </a>
        '''
        with open(f'docs/posts/{post}', 'w') as local_file:
            local_file.write(html)

# Load template, substitute {blog}, and write to index.html
with open('template.html', 'r') as template_file:
    template = template_file.read()

output_content = template.replace('{blog}', blog_content)

with open('docs/index.html', 'w') as output_file:
    output_file.write(output_content)

