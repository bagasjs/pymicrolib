#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bowl is a simple micro library for parsing HTML all in a single file 
and with no dependencies other than the Python Standard Library.

Copyright (c) 2025, bagasjs
License: MIT (see the details at the very bottom)
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from html.parser import HTMLParser
from html.entities import name2codepoint

# TODOs
# - in DOMNode at least in DOMNode._build_tag_index it will include itself into the indexes. This should not be happening
#   Although we don't need to remove it in DOMDocument since we might need it
# - A better HTML Parser (maybe)

class DOMNode(object):
    tag: str
    attrs: Dict[str, Any]
    children: List[Union[DOMNode, str]]

    # NOTE: This will be duplicating some indexes from DOMDocument and since an ID is unique per element there's no need to have this
    _id_to_node_map: Dict[str, DOMNode]
    _tag_to_node_map: Dict[str, List[DOMNode]]
    _class_to_node_map: Dict[str, List[DOMNode]]
    _has_id_index: bool
    _has_tag_index: bool
    _has_class_index: bool

    def __init__(self, tag: str, attrs: Dict[str, Any], children: Optional[List[Union[DOMNode, str]]] = None):
        self.tag = tag
        self.attrs = attrs
        self.children = children or []

        self._has_id_index = False
        self._id_to_node_map  = {}

        self._has_tag_index = False
        self._tag_to_node_map = {}

        self._has_class_index = False
        self._class_to_node_map = {}

    def append_child(self, child: Union[DOMNode, str]):
        self.children.append(child)

    def _render(self, indent: int = 0) -> str:
        space = "  " * indent
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attrs.items())
        open_tag = f"<{self.tag}{' ' + attrs if attrs else ''}>"
        close_tag = f"</{self.tag}>"
        parts = [f"{space}{open_tag}"]

        for child in self.children:
            if isinstance(child, DOMNode):
                parts.append(child._render(indent + 1))
            elif isinstance(child, str):
                parts.append(f"{'  ' * (indent + 1)}{child}")

        parts.append(f"{space}{close_tag}")
        return "\n".join(parts)

    def __str__(self) -> str:
        return self._render()

    def __repr__(self) -> str:
        attrs = [ f"{key}=\"{value}\"" for key, value in self.attrs.items() ]
        if len(attrs) > 0:
            attr_as_str = " ".join(attrs)
            return f"<{self.tag} {attr_as_str}>"
        else:
            return f"<{self.tag}>"

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_tag_index(self, node: DOMNode):
        if node.tag not in self._tag_to_node_map:
            self._tag_to_node_map[node.tag] = []
        self._tag_to_node_map[node.tag].append(node)
        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_tag_index(child)
        if node is self:
            self._has_tag_index = True

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_id_index(self, node: DOMNode):
        id_attr = node.attrs.get("id")
        if id_attr:
            self._id_to_node_map[id_attr] = node
        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_id_index(child)
        if node is self:
            self._has_id_index = True

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_class_index(self, node: DOMNode):
        class_attr = node.attrs.get("class")
        if class_attr:
            classes = []
            if isinstance(class_attr, str):
                classes.extend(class_attr.split())
            elif isinstance(class_attr, list):
                classes.extend(class_attr)
            else:
                classes.append(str(class_attr))
            for class_name in classes:
                if class_name not in self._class_to_node_map:
                    self._class_to_node_map[class_name] = []
                self._class_to_node_map[class_name].append(node)

        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_class_index(child)

        if node is self:
            self._has_class_index = True

    def inner_text(self) -> str:
        return "".join([str(child) for child in self.children])

    def get_by_tag(self, name: str) -> Optional[List[DOMNode]]:
        if not self._has_tag_index:
            self._build_tag_index(self)
        return self._tag_to_node_map.get(name)

    def get_by_id(self, name: str) -> Optional[DOMNode]:
        if not self._has_id_index:
            self._build_id_index(self)
        return self._id_to_node_map.get(name)

    def get_by_class_name(self, name: str) -> Optional[List[DOMNode]]:
        if not self._has_class_index:
            self._build_class_index(self)
        return self._class_to_node_map.get(name)

class DOMDocument(object):
    root: DOMNode
    page_title: Union[str, None]

    _id_to_node_map: Dict[str, DOMNode]
    _tag_to_node_map: Dict[str, List[DOMNode]]
    _class_to_node_map: Dict[str, List[DOMNode]]
    _has_id_index: bool
    _has_tag_index: bool
    _has_class_index: bool

    def __init__(self, root: DOMNode, page_title: Union[str, None]):
        self.root = root
        self.page_title = page_title
        self._has_id_index = False
        self._id_to_node_map  = {}

        self._has_tag_index = False
        self._tag_to_node_map = {}

        self._has_class_index = False
        self._class_to_node_map = {}

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_tag_index(self, node: DOMNode):
        if node.tag not in self._tag_to_node_map:
            self._tag_to_node_map[node.tag] = []
        self._tag_to_node_map[node.tag].append(node)
        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_tag_index(child)
        if node is self.root:
            self._has_tag_index = True

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_id_index(self, node: DOMNode):
        id_attr = node.attrs.get("id")
        if id_attr:
            self._id_to_node_map[id_attr] = node
        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_id_index(child)
        if node is self.root:
            self._has_id_index = True

    # TODO: since this is recursion maybe recursion unwrapping would be nice
    #       Look at https://github.com/bagasjs/algo-impl/blob/main/traversal.py
    def _build_class_index(self, node: DOMNode):
        class_attr = node.attrs.get("class")
        if class_attr:
            classes = []
            if isinstance(class_attr, str):
                classes.extend(class_attr.split())
            elif isinstance(class_attr, list):
                classes.extend(class_attr)
            else:
                classes.append(str(class_attr))
            for class_name in classes:
                if class_name not in self._class_to_node_map:
                    self._class_to_node_map[class_name] = []
                self._class_to_node_map[class_name].append(node)

        for child in node.children:
            if isinstance(child, DOMNode):
                self._build_class_index(child)

        if node is self.root:
            self._has_class_index = True

    def get_by_tag(self, name: str) -> Optional[List[DOMNode]]:
        if not self._has_tag_index:
            self._build_tag_index(self.root)
        return self._tag_to_node_map.get(name)

    def get_by_id(self, name: str) -> Optional[DOMNode]:
        if not self._has_id_index:
            self._build_id_index(self.root)
        return self._id_to_node_map.get(name)

    def get_by_class_name(self, name: str) -> Optional[List[DOMNode]]:
        if not self._has_class_index:
            self._build_class_index(self.root)
        return self._class_to_node_map.get(name)

_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", 
    "input", "link", "meta", "source", "track", "wbr"
}

class _CustomHTMLParser(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.source = source
        self.root_node = DOMNode("DOCUMENT_ROOT", {})
        self.title = None
        self.node_stack = [ self.root_node ]

    def handle_starttag(self, tag, attrs):
        dom_attrs = {}
        for key, value in attrs:
            dom_attrs[key] =  value
        dom = DOMNode(tag, dom_attrs)
        self.node_stack[-1].append_child(dom)
        if tag not in VOID_TAGS:
            self.node_stack.append(dom)

    def handle_endtag(self, tag):
        if tag == self.node_stack[-1].tag:
            dom = self.node_stack.pop()
            # print("Removed: ", dom.__repr__())

    def handle_data(self, data):
        if len(self.node_stack) > 0:
            if self.node_stack[-1].tag == "title" and self.title is None:
                self.title = data
            self.node_stack[-1].append_child(data)

    def handle_comment(self, data):
        # print("Comment  :", data)
        pass

    def handle_entityref(self, name):
        # c = chr(name2codepoint[name])
        # print("Named ent:", c)
        pass

    def handle_charref(self, name):
        # if name.startswith('x'):
        #     c = chr(int(name[1:], 16))
        # else:
        #     c = chr(int(name))
        # print("Num ent  :", c)
        pass

    def handle_decl(self, *args, **kwargs):
        # print("Decl     :", args, kwargs)
        pass

    def accumulate(self) -> Optional[DOMNode]:
        self.feed(self.source)
        assert self.root_node == self.node_stack[0]
        return self.root_node

def parse_document(source: str) -> Optional[DOMDocument]:
    parser = _CustomHTMLParser(source)
    root = parser.accumulate()
    if root:
        return DOMDocument(root, parser.title)

"""
Copyright (c) 2025 bagasjs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
