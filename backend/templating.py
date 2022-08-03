from jinja2 import Environment, FileSystemLoader

from . import settings


def render(file_name, request, **kwargs):
    template_loader = FileSystemLoader('./html', encoding='utf-8')
    
    template_env = Environment(loader=template_loader)
    template_env.globals['ALGOD_NODE_URL'] = settings.ALGOD_NODE_URL
    template_env.globals['ALGOD_NODE_TOKEN'] = settings.ALGOD_NODE_TOKEN
    template_env.globals['ALGOD_HEADERS'] = settings.ALGOD_HEADERS
    
    template = template_env.get_template(file_name)

    context = {
        'web_wrapper': 'web_wrapper.html',
        'request': request,
    }

    return template.render(context, **kwargs)
