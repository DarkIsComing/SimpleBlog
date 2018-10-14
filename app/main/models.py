from .. import db
from ..useraccounts.models import User
import markdown2 as Markdown, bleach
import datetime, hashlib, urllib

post_status = ((0,
                'post'), (1, 'draft'))


def get_clean_html_content(html_content):
    allow_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'p', 'hr', 'img',
                        'table', 'thead', 'tbody', 'tr', 'th', 'td',
                        'sup', 'sub']
    allow_attrs = {'*': ['class'],
                'a': ['href', 'rel', 'name'],
                'img': ['alt', 'src', 'title'], }
    html_content = bleach.linkify(bleach.clean(html_content, tags=allow_tags, attributes=allow_attrs, strip=True))
    return html_content


class Post(db.Document):
    title = db.StringField(max_length=255, required=True, default='New blog')
    abstract = db.StringField()
    content = db.StringField(required=True)
    content_html = db.StringField(required=True)
    author = db.ReferenceField(User)
    tags = db.ListField(db.StringField(max_length=64))
    category = db.StringField(max_length=64)
    status = db.IntField(required=True, choices=post_status, default=0)
    create_time = db.DateTimeField()
    modify_time = db.DateTimeField()

    '''rewrite save method.'''
    def save(self, allow_set_time=False, *args, **kwargs):
        if not allow_set_time:
            time = datetime.datetime.utcnow()
            if not self.create_time:
                self.create_time = time
            self.modify_time = time

        self.content_html = Markdown.markdown(self.content, extras=['code-friendly', 'fenced-code-blocks', 'tables'])
        self.content_html = get_clean_html_content(self.content_html)

        return super(Post, self).save(*args, **kwargs)


class Comment(db.Document):
    post_id = db.StringField(required=True)
    post_title = db.StringField()
    author = db.StringField(required=True)
    email = db.EmailField(max_length=255)
    body = db.StringField()
    body_html = db.StringField()
    create_time = db.DateTimeField()
    disabled = db.BooleanField(default=True)
    replay_to = db.ReferenceField('self')
    gavatar_id = db.StringField(default='00000000000')

    def save(self, *args, **kwargs):
        if self.body:
            body_html = Markdown.markdown(self.body, extras=['code-friendly', 'fenced-code-blocks', 'tables'])
            self.body_html = get_clean_html_content(body_html)

        if self.email:
            self.gavatar_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

        if not self.create_time:
            self.create_time=datetime.datetime.utcnow()

    def get_gavatar_url(self, img_size=0, default_image_url=None):
        gavatar_url = '//s.gravatar.com/avatar/' + self.gavatar_id
        params = {}
        if img_size:
            params['s'] = str(img_size)
        if default_image_url:
            params['d'] = default_image_url

        if params:
            gavatar_url = '{0}?{1}'.format(gavatar_url, urllib.urlencode(params))

        return gavatar_url

    def __unicode__(self):
        return self.body[:64]

    meta = {
        'ordering': ['-create_time']
    }
