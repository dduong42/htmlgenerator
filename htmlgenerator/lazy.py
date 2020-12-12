import collections


def resolve_lazy(value, context, element):
    """Shortcut to resolve a value in case it is a Lazy value"""
    # from .base import BaseElement

    while isinstance(value, Lazy):
        value = value.resolve(context, element)
    # if isinstance(value, BaseElement):
    # value = value.render(context)
    return value


def getattr_lazy(lazyobject, attr):
    """Takes a lazy object and returns a new lazy object which will resolve the attribute of the object"""
    return F(lambda c, e: getattr(resolve_lazy(lazyobject, c, e), attr))


class Lazy:
    """Lazy values will be evaluated at render time via the resolve method."""

    def resolve(self, context, element):
        raise NotImplementedError("Lazy needs to be subclassed")


class ContextValue(Lazy):
    def __init__(self, value):
        assert isinstance(
            value, collections.Hashable
        ), "ContextValue needs to be hashable"
        self.value = value

    def resolve(self, context, element):
        if isinstance(self.value, str):
            for accessor in self.value.split("."):
                if hasattr(context, accessor):
                    context = getattr(context, accessor)
                else:
                    context = context.get(accessor)
            return context
        return context[self.value]


class ContextFunction(Lazy):
    """Call a function a render time, usefull for calculation of more complex """

    def __init__(self, func):
        assert callable(func), "ContextFunction needs to be callable"
        self.func = func

    def resolve(self, context, element):
        return self.func(context, element)


class ElementAttribute(Lazy):
    """Get an attribute from an element, usefull for consumers of ValueProvider"""

    def __init__(self, attribname, element=None):
        self.attribname = attribname
        self.element = element

    def resolve(self, context, element):
        element = self.element or element
        for accessor in self.attribname.split("."):
            element = getattr(element, accessor)
        return element


C = ContextValue
ATTR = ElementAttribute
F = ContextFunction
