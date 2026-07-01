from trytond.pool import Pool
from . import hello

def register():
    Pool.register(
        hello.HelloWorld,
        module='hello_world',
        type_='model'
    )
