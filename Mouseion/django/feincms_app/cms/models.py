from django.db import models

# Create your models here.

from feincms.module.page.models import Page
from django.utils.translation import ugettext_lazy as _
from feincms.content.richtext.models import RichTextContent

Page.register_templates({
    'title': _('General FeinCMS Template Example'),
    'path': 'template1.html',
    'regions': (
        ('header', _('Page header.')),
        ('main', _('Main content area.')),
        ('sidebar', _('Sidebar'), 'inherited'),
        ('footer', _('Page footer.')),
    ),
})

Page.create_content_type(RichTextContent)
