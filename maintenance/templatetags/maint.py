from datetime import datetime, timedelta
from django import template
from maintenance import api
from maintenance.api import STATUS

register = template.Library()

@register.tag
def maintenance(parser, token):
    try:
        # get the arguments passed to the template tag;
        # first argument is the tag name
        tag_name, status_label = token.split_contents()
        status = STATUS._labels.values().index(status_label.upper())
    except ValueError as e:
        raise template.TemplateSyntaxError("%r tag requires exactly 2 arguments" % token.contents.split()[0], e)
        # look for the 'endpermission' terminator tag
    nodelist = parser.parse(('endmaintenance',))
    parser.delete_first_token()
    return MaintenanceNode(nodelist, status)

class MaintenanceNode(template.Node):
    def __init__(self, nodelist, status):
        self.nodelist = nodelist
        self.status = status

    def render(self, context):
        return self.nodelist[0]
