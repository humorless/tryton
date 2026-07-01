from trytond.model import ModelSQL, ModelView, fields

class HelloWorld(ModelSQL, ModelView):
    "Hello World"
    __name__ = 'hello_world.hello'

    name = fields.Char('Name', required=True)
    message = fields.Char('Message')
