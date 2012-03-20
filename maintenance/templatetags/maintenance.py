from django.template import Library
from django.utils.translation import gettext as _

library = Library()

@library.simple_tag
def maintenance():
    return