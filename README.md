HTML Generator
==============

A python package to generate HTML from a template which is defined through a tree of render-elements.

Getting started
---------------

Installing:

    pip install htmlgenerator

A simple example:

```python
import htmlgenerator as hg

my_page = hg.HTML(hg.HEAD(), hg.BODY(hg.H1("It works!")))

print(hg.render(my_page, {}))
```

This will print the following HTML-document:

```hmtl
<!DOCTYPE html><html ><head ><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /></head><body ><h1 >It works!</h1></body></html>
```

Note that the provided implementation of the HTML tag and the HEAD tag come with sensible defaults for DOCTYPE and META tags.

HTML elements
-------------

The package ```htmlgenerator``` defines all standard HTML tags with uppercase classnames, e.g. BODY, DIV, SECTION, etc.
The __init__ method of HTML elements will treat all passed arguments as child elements and keyword arguments as attributes on the HTML element. Leading underscores of attribute names will be removed (to allow *class* and *for* attributes to be specified) and underscores will be replaced by dashes because python does not allow identifiers to have a dash and HTML attributes normally do not use underscores.

Example:

```python
from htmlgenerator import render, DIV, OL, LI

print(
    render(
        DIV(
            "My list is:",
            OL(
                LI("not very long"),
                LI("having a good time"),
                LI("rendered with htmlgenerator"),
                LI("ending with this item"),
            ),
        ),
        {},
    )
)
print(
    render(
        DIV(
            "Hello world!",
            _class="success-message",
            style="font-size: 2rem",
            data_status="ok",
        ),
        {},
    )
)
```

Output:

```hmtl
<div class="success-message" style="font-size: 2rem" data-status="ok">Hello world!</div>
<div>My list is:<ol><li>not very long</li><li>having a good time</li><li>rendered with htmlgenerator</li><li>ending with this item</li></ol></div>
```


Rendering
---------

The method ```htmlgenerator.render``` should be used to render an element tree. All nodes in the tree should inherit from ```htmlgenerator.BaseElement```. Leaves in the tree can be arbitrary python objects. The render function expects the root element of the tree and a context dictionary as arguments.
The output is generated by rendering the tree recursively. If an object in the tree is an instance of ```BaseElement``` its render method will be called with the context as single argument and it must return a generator which yields objects of type ```str```. Otherwise the object will be converted to a string and escaped for use in HTML. In order to prevent a string from beeing escaped ```htmlgenerator.mark_safe``` or ```django.utils.html.mark_safe``` from the django package can be used.

Example python object:

```python
import datetime
from htmlgenerator import render, DIV

print(render(DIV("Hello, here is some date: ", datetime.date.today()), {}))
print(
    render(
        DIV(
            "Hello, here is some data: ",
            {"fingers": [1, 2, 3, 4, 5], "stuff": {"set": {1, 2, 3, 3, 3, 3, 3}}},
        ),
        {},
    )
)
```

Output:

```hmtl
<div>Hello, here is some date: 2020-11-20</div>
<div>Hello, here is some data: {&#x27;fingers&#x27;: [1, 2, 3, 4, 5], &#x27;stuff&#x27;: {&#x27;set&#x27;: {1, 2, 3}}}</div>
```


Example render object:

```python
from htmlgenerator import render, DIV


class DoStuff:
    # be aware that all yielded strings will not be seperated by spaces but concatenated directly
    def render(self, context):
        yield "eat "
        yield "sleep "
        yield "program"


print(render(DIV("I like to ", DoStuff()), {}))
```

Output:

```hmtl
<div>I like to eat sleep program</div>
```

Example escaping:

```python
from htmlgenerator import mark_safe, render, DIV

print(
    render(
        DIV(
            "Hello, here is some HTML: ",
            '<div style="font-size: 2rem">Hello world!</div>',
        ),
        {},
    )
)
print(
    render(
        DIV(
            "Hello, here is NOT some HTML: ",
            mark_safe('<div style="font-size: 2rem">Hello world!</div>'),
        ),
        {},
    )
)
```

Output: 

```hmtl
<div>Hello, here is some HTML: &lt;div style=&quot;font-size: 2rem&quot;&gt;Hello world!&lt;/div&gt;</div>
<div>Hello, here is NOT some HTML: <div style="font-size: 2rem">Hello world!</div></div>
```


Lazy values
-----------

In order to allow rendering values which are not yet known at construction time but only at render time lazy values can be used.
By default htmlgenerator comes with the following lazy values:

- ```htmlgenerator.ContextFunction```: Calls a function with the values containing element and the context as argument and renders the returned value (shortcut ```htmlgenerator.F```)
- ```htmlgenerator.ContextValue```: Renders a variable from the context, can use . to access nested attributes or dictionary keys (shortcut ```htmlgenerator.C```)
- ```htmlgenerator.ElementAttribute```: Renders an attribute of an element, mainly used for bound values (see below), can use . to access nested attributes (shortcut ```htmlgenerator.ATTR```)

A lazy value will be resolved just before it is rendered. Custom implementations of lazy values can be added by inheriting from ```htmlgenerator.Lazy```.

Example:

```python
from htmlgenerator import render, DIV, C, F, ATTR

print(
    render(
        DIV("Hello, ", C("person.name")),
        {"person": {"name": "Alice", "occupation": "Writer"}},
    )
)
print(render(DIV("Crazy calculation: 4 + 2 = ", F(lambda element, context: 4 + 2)), {}))
print(render(DIV("This text is wrapped inside a ", ATTR("tag"), " element"), {}))
```

Output:

```hmtl
<div>Hello, Alice</div>
<div>Crazy calculation: 4 + 2 = 6</div>
<div>This text is wrapped inside a div element</div>
```

Virtual elements
----------------

In order to allow the building of a dynamic page virtual elements need to be used. The following virtual elements exist:


- ```htmlgenerator.BaseElement```: The base for all elements, can also be used to group elements without generating output by itself
- ```htmlgenerator.If```: Lazy evaluates the first argument at render time and returns the first child on true and the second child on false
- ```htmlgenerator.Iterator```: Takes an iterator which can be a lazy value and renders the child element for each iteration

Example:

```python
from htmlgenerator import render, SPAN, BaseElement, If, C, Iterator

print(
    render(BaseElement("Just", SPAN("some"), "elements", SPAN("without"), "parent"), {})
)
print(render(If(C("cold"), "It is cold", "It is not cold"), {"cold": True}))
print(render(If(C("cold"), "It is cold", "It is not cold"), {"cold": False}))
print(render(Iterator(range(7), SPAN("I love loops ")), {}))
```

Output:

```hmtl
Just<span>some</span>elements<span>without</span>parent
It is cold
It is not cold
<span>I love loops </span><span>I love loops </span><span>I love loops </span><span>I love loops </span><span>I love loops </span><span>I love loops </span><span>I love loops </span>
```


Binding values to child elements
--------------------------------

For more complex interfaces it is often necessary to let elements in the tree access values which are provided by a virtual parent at render time.
Examples are form fields of a form, elements of an iterator, elements which render parts of an object from a database.
One solution string-template engines often use is a global context which is populated by the according parent elements. This is a very generic approach and should be avoided in htmlgenerator. A main motivation of htmlgenerator's binding concept is to make dependencies to values in the context explicit.

Binding works in the following way: An element which will provide a value to child elements at rendertime needs to inherit from ```htmlgenerator.ValueProvider```. The class method ```ValueProvider.Binding``` will return a class which is marked as bound to the according ValueProvider class. 

![Binding schematics](./binding.svg)

Here is a more extensive example, see below for a more compact version:

```python
from htmlgenerator import DIV, ValueProvider, render

# e.g. database object, could be anything
class Book(object):
    def __init__(self, title, author, publisher):
        self.title = title
        self.author = author
        self.publisher = publisher


mybook = Book("A book", "Me", "Myself")

# make it a value provider in order to allow binding elements
class BookObject(ValueProvider):
    attributename = "book"


# a render element which renders an attribute of the book
# (the Binding method returns a class which inherits from BaseElement by default, another base class can be passed as argument to Binding, see below)
class BookValue(BookObject.Binding()):
    def __init__(self, attr):
        self.attr = attr

    def render(self, context):
        return getattr(self.book, self.attr)


print(
    render(
        BookObject(
            mybook,
            DIV("This is my book's name: ", BookValue("title")),
            DIV("It was written by: ", BookValue("author")),
            DIV("And published by: ", BookValue("publisher")),
        ),
        {},
    )
)
```

Output:

```hmtl
<div>This is my book&#x27;s name: A book</div><div>It was written by: Me</div><div>And published by: Myself</div>
```

Compact version (using the ATTR lazy object and creating a bound value in-place, no need for seperate class):

```python
from htmlgenerator import ATTR, DIV, ValueProvider, render

# e.g. database object, could be anything
class Book(object):
    attributename = "book"

    def __init__(self, title, author, publisher):
        self.title = title
        self.author = author
        self.publisher = publisher


mybook = Book("A book", "Me", "Myself")

# make it a value provider in order to allow binding elements
class BookObject(ValueProvider):
    attributename = "book"


print(
    render(
        BookObject(
            mybook,
            BookObject.Binding(DIV)("This is my book's name: ", ATTR("book.title")),
            BookObject.Binding(DIV)("It was written by: ", ATTR("book.author")),
            BookObject.Binding(DIV)("And published by: ", ATTR("book.publisher")),
        ),
        {},
    )
)
```

Example with nested objects (values will be bound correctly):

```python
# ....

mybook2 = Book("A book 2", "Me", "Myself")
print(
    render(
        BookObject(
            mybook1,
            BookObject.Binding(DIV)("This is my book's name: ", ATTR("book.title")),
            BookObject.Binding(DIV)("It was written by: ", ATTR("book.author")),
            BookObject.Binding(DIV)("And published by: ", ATTR("book.publisher")),
            DIV(
                "And soon my pulisher is going to publish: ",
                BookObject(mybook2, BookObject.Binding()(ATTR("book.title"))),
            ),
        ),
        {},
    )
)
```

Output:

```hmtl
<div>This is my book&#x27;s name: A book</div><div>It was written by: Me</div><div>And published by: Myself</div><div>And soon my pulisher is going to publish: A book 2</div>
```


More complicated example with dependent nested objects:

```python
from htmlgenerator import ATTR, DIV, ValueProvider, render


class Request:
    def __init__(self, user):
        self.user = user


class RequestContext(ValueProvider):
    attributename = "request"


class UserContext(RequestContext.Binding(ValueProvider)):
    attributename = "user"

    def __init__(self, *args, **kwargs):
        super().__init__(ATTR("request.user"), *args, **kwargs)


print(
    render(
        RequestContext(
            Request("Bob"),
            UserContext(
                DIV(
                    "Username: ",
                    UserContext.Binding(DIV)(ATTR("user")),
                ),
            ),
        ),
        {},
    )
)
```

Output:

```hmtl
<div>Username: <div>Bob</div></div>
```

Remark: This example is just for demonstration purposes. In order to achieve exactly what is shown here it would not be necessary to have a UserContext class because the user could as well be obtained via ```RequestContext.Binding(DIV)(ATTR("request.user"))```. The point is to show how chaining of ValueProviders can work.


Django integration
------------------

In order to use the element tree renderer in django html templates it is necessary to add a template tag which calls the render function.

```python
@register.simple_tag(takes_context=True)
def render_document(context, root):
    return mark_safe(layout.render(root, context.flatten()))
```

The render method of any object may also be directly passed to a HttpResponse object. This is useful if htmlgenerator should generate the complete page in function based views.

Example of a helper function to render an element tree to a response (layout is the element tree):

```python
from django.http import HttpResponse


def render_layout_to_response(request, layout, context):
    return HttpResponse(layout.render(context))
```


Rational
--------

TODO: Justify this whole code base a bit

Notes:
- Want internal/embeded DSL, access to document object model, not string interpolation
- https://wiki.python.org/moin/Templating ==> All dead links
- Existing HTML-DSL have no support for more abstract concepts like iterators and lazy values
  - https://github.com/duyixian1234/html_dsl
  - https://github.com/benwbooth/python-teacup
- We want something inspired by FRP (Functional reactive programming) and LISP like XAML (but without XML) or React/Vue (but not on the client-side)
