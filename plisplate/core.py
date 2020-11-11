import copy


def render(root, basecontext):
    return "".join(root.render(basecontext))


def _try_render(elements, context):
    for element in elements:
        if isinstance(element, str):
            if "{" in element or "}" in element:
                yield htmlescape(element.format(**context))
            else:
                yield htmlescape(element)
        elif hasattr(element, "render"):
            yield from element.render(context)
        else:
            yield htmlescape(str(element))


def htmlescape(s):
    return s


def flatattrs(attrs):
    """Converts a dictionary to a string of XML-attributes.
    Leading underscores are removed and underscores are replaced with dashes."""
    attlist = []
    for key, value in attrs.items():
        if key[0] == "_":
            key = key[1:]
        key = key.replace("_", "-")
        if isinstance(value, bool) and key != "value":
            if value is True:
                attlist.append(f"{key}")
        else:
            attlist.append(f'{key}="{value}"')
    return " ".join(attlist)


class BaseElement(list):
    def __init__(self, *children):
        super().__init__(children)

    def render_children(self, context):
        """Returns a list of strings which represents the output"""
        yield from _try_render(self, context)

    def filter(self, filter_func):
        def walk(element):
            for e in element:
                if isinstance(e, BaseElement):
                    if filter_func(e):
                        yield e
                    yield from walk(e)

        return walk(self)

    def copy(self):
        return copy.deepcopy(self)

    def __repr__(self):
        children = ", ".join([i.__repr__() for i in self])
        return f"{self.__class__.__name__}({children})"


class Raw(BaseElement):
    def render(self, context):
        for i in self:
            yield str(i)


class HTMLElement(BaseElement):
    tag = None

    def __init__(self, *children, **attributes):
        assert self.tag is not None
        super().__init__(*children)
        self.attributes = attributes

    def render(self, context):
        yield f"<{self.tag} {flatattrs(self.attributes)}>"
        yield from super().render_children(context)
        yield f"</{self.tag}>"


class VoidElement(HTMLElement):
    """Wrapper for elements without a closing tag, cannot have children"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, context):
        yield f"<{self.tag} {flatattrs(self.attributes)} />"


class If(BaseElement):
    def __init__(self, condition, true_child, false_child=None):
        super().__init__()
        self.condition = condition
        self.true_child = true_child
        self.false_child = false_child

    def render(self, context):
        if self.condition(context):
            yield from _try_render((self.true_child,), context)
        elif self.false_child is not None:
            yield from _try_render((self.false_child,), context)
        else:
            yield ""


class Iterator(BaseElement):
    def __init__(self, iterator, variablename, *children):
        """iterator: can be a string which will be looked up in the context, a python iterator or a callable which accepts the current context as argument and returns an iterator"""
        super().__init__(*children)
        self.iterator = iterator
        self.variablename = variablename

    def render(self, context):
        c = dict(context)
        if isinstance(self.iterator, str):
            iterator = context[self.iterator]
        elif callable(self.iterator):
            iterator = self.iterator(c)
        else:
            iterator = self.iterator
        for obj in iterator:
            c[self.variablename] = obj
            yield from super().render_children(c)
