'''
init file to register filters for pyjade
'''
import markdown
import pyjade


@pyjade.register_filter('markdown')
@pyjade.register_filter('md')
def filter_markdown(text, ast):
    return markdown.markdown(text)
