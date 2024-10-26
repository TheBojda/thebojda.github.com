import os
from html.parser import HTMLParser

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

def cleanup(text):
    return text.split('|')[0] if '|' in text else text

# Collect blog links content
blog_content = ''
files = os.listdir('docs/posts')
files.sort(reverse=True)

for post in files:
    with open(f'docs/posts/{post}', 'r') as file:
        html = file.read()
    parser = TitleExtractor()
    parser.feed(html)
    title = cleanup(parser.get_title())
    subtitle = cleanup(parser.get_subtitle())
    blog_content += f'''
        <a href="https://thebojda.github.com/posts/{post}" class="text-decoration-none" style="color:black;" target="_black">
            <div class="mb-4">
                <h3>{title}</h3>
                <p>{subtitle}</p>
            </div>
        </a>
    '''

# Load template, substitute {blog}, and write to index.html
with open('template.html', 'r') as template_file:
    template = template_file.read()

output_content = template.replace('{blog}', blog_content)

with open('docs/index.html', 'w') as output_file:
    output_file.write(output_content)

