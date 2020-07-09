class Tag:
    def __init__(self, tag, html_classes=(), html_id="", is_single=False, **kwargs):
        self.tag = tag
        self.html_classes = html_classes
        self.html_id = html_id
        self.text = ""
        self.children = []
        self.is_single = is_single
        self.attributes = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __add__(self, other):
        self.children.append(other)
        return self

    def _render_html(self, indentation_level):
        css_info = ""
        attributes = ""
        if self.attributes:
            attributes = self._unpack_attributes()
        if self.html_classes:
            css_info += self._unpack_html_classes()
        if self.html_id:
            css_info += self._unpack_html_id()

        return self._construct_html_string(css_info, attributes, indentation_level)

    def _unpack_attributes(self):
        attributes = ""
        for name, value in self.attributes.items():
            attributes += f" {name}='{value}'"
        return attributes

    def _unpack_html_classes(self):
        html_classes = " ".join(self.html_classes)
        return f" class='{html_classes}'"

    def _unpack_html_id(self):
        return f" id='{self.html_id}'"

    def _construct_html_string(self, css_info, attributes, indentation_level):
        indent = " " * 4 * indentation_level
        opening = "\n" + indent + f"<{self.tag}" + css_info + attributes + ">"
        ending = f"</{self.tag}>"
        if self.is_single:
            return opening
        children = self._unpack_children(indentation_level+1)
        return opening + self.text + children + ending

    def _unpack_children(self, indentation_level):
        children = ""
        for child in self.children:
            children += child._render_html(indentation_level)
        return children


class HTML(Tag):
    def __init__(self, output=None):
        self.tag = "html"
        self.output = output
        self.children = []

    def __exit__(self, *args, **kwargs):
        if self.output:
            with open(self.output, "w") as f:
                f.write(str(self))
        else:
            print(self)

    def __str__(self):
        opening = f"<html>\n"
        ending = f"</html>"
        children = self._unpack_children(indentation_level=1)
        return opening + children + ending


class TopLevelTag(Tag):
    def __init__(self, tag):
        self.tag = tag
        self.children = []

    def _render_html(self, indentation_level):
        indent = " " * 4 * indentation_level
        opening = f"{indent}<{self.tag}>"
        ending = "\n" + indent + f"</{self.tag}>" + "\n"
        children = self._unpack_children(indentation_level+1)
        return opening + children + ending


with HTML(output="test.html") as doc:
    with TopLevelTag("head") as head:
        with Tag("title") as title:
            title.text = "hello"
            head += title
        doc += head

    with TopLevelTag("body") as body:
        with Tag("h1", html_classes=("main-text",)) as h1:
            h1.text = "Test"
            body += h1

        with Tag("div", html_classes=("container", "container-fluid"), html_id="lead") as div:
            with Tag("p") as paragraph:
                paragraph.text = "another test"
                div += paragraph

            with Tag("img", is_single=True,
                     src="/icon.png", data_image="responsive") as img:
                div += img

            body += div

        doc += body
