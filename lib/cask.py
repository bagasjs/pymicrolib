#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cask is a simple library for building a CLI application
all in a single file and with no dependencies other than the
Python Standard Library. If you're looking for example look 
for example_app() function.

Copyright (c) 2025, bagasjs
License: MIT (see the details at the very bottom)
"""

from __future__ import annotations, with_statement
from typing import Callable, List, Dict, Any, Tuple
from enum import StrEnum

__author__ = 'bagasjs'
__version__ = '0.0.1'
__license__ = 'MIT'

class ValueType(StrEnum):
    Int    = "Int"
    Float  = "Float"
    String = "String"
    Bool   = "Bool"

class Opt(object):
    def __init__(self, name: str, kind: ValueType, description: str = "", default_value: Any = None, short: str = ""):
        self.name = name
        self.short = short
        self.description = description
        self.kind = kind
        self.default_value = default_value

class Arg(object):
    def __init__(self, name: str, kind: ValueType, default_value: Any):
        self.name = name
        self.kind = kind
        self.default_value = default_value

CommandCallback = Callable[["Command", List[Any], Dict[str, Any]], None]
Error = str | None

def parse_value(value: str, kind: ValueType) -> Tuple[Any, Error]:
    match kind:
        case ValueType.Int:
            try:
                int_value = int(value)
                return int_value, None
            except ValueError as err:
                return 0, str(err)
        case ValueType.Float:
            try:
                float_value = float(value)
                return float_value, None
            except ValueError as err:
                return 0, str(err)
        case ValueType.String:
            return value, None
        case ValueType.Bool:
            match value:
                case "true":
                    return True, None
                case "false":
                    return False, None
                case _:
                    return value, f"Failed to parse boolean value from {value}"
        case _:
            return 0, "Unsupported types"


class Command(object):
    use: str
    description: str
    args: List[Arg]
    opts: List[Opt]

    opt_maps: Dict[str, int]
    subcommands: Dict[str, Command]
    run: CommandCallback | None

    def __init__(self, use: str, description: str, run: 
                 CommandCallback | None = None,
                 opts: List[Opt] | None = None,
                 args: List[Arg] | None = None):
        self.use = use
        self.description = description
        self.args = args if args is not None else []
        self.opts = opts if opts is not None else []
        self.opt_maps = {}
        self.subcommands = {}
        self.run = run
        if "help" not in self.opt_maps:
            self.opts.append(Opt(name="help", kind=ValueType.Bool, description="Get the `usage` information of a command"))

    def add_subcommand(self, command: Command) -> Command:
        self.subcommands[command.use] = command
        return self

    def parse_args(self, args: List[str]) -> Tuple[List[Any], Dict[str, Any], Error]:
        opts: Dict[str, Any] = {}
        parsed_args: List[Any] = []
        cmd_args_length = len(parsed_args)
        args_length = len(args)

        for i, opt in enumerate(self.opts):
            opts[opt.name] = opt.default_value
            if len(opt.short) != 0:
                self.opt_maps[opt.short] = i
            self.opt_maps[opt.name] = i

        i = 0
        while i < args_length:
            arg = args[i]
            if arg.startswith("-"):
                opt_name  = arg.lstrip("-")
                opt_value = "true" # Default for boolean flags
                if "=" in opt_name:
                    parts = opt_name.split("=", 2)
                    opt_name = parts[0]
                    opt_value = parts[1]
                else:
                    if i + 1 < len(args):
                        opt_value = args[i+1]
                        i += 1


                if opt_name in self.opt_maps:
                    opt_index = self.opt_maps[opt_name]
                    assert type(opt_index) == int
                    parsed_value, err = parse_value(opt_value, self.opts[opt_index].kind)
                    if err is not None:
                        return ([], {}, err)
                    opts[opt_name] = parsed_value
                else:
                    return ([], {}, f"Unknown option: {opt_name}")
            else:
                if len(parsed_args) + 1 <= cmd_args_length:
                    arg_info = self.args[cmd_args_length - 1]
                    parsed_arg, err = parse_value(arg, arg_info.kind)
                    if err is not None:
                        return ([], {}, err)
                    parsed_args[len(parsed_args) - 1] = parsed_arg
            i += 1

        if len(parsed_args) < cmd_args_length:
            return [], {}, "not enough arguments provided"
        return parsed_args, opts, None

    def usage(self):
        print(f"Usage: {self.use} [SUBCOMMANDS] [OPTIONS]", end="")
        for arg in self.args:
            if arg.default_value is not None:
                print(f"  [{arg.name} ({arg.kind}, default {arg.default_value})]", end="")
            else:
                print(f"  <{arg.name} ({arg.kind})>", end="")
                pass
        print(f"\n{self.description}")

        if len(self.opts) > 0:
            print("\nOptions:")
            for opt in self.opts:
                if opt.short != "":
                    print(f"  -{opt.short}, --{opt.name}", end="")
                else:
                    print(f"  --{opt.name}", end="")
                print(f" ({opt.kind})", end="")
                if opt.default_value != None:
                    print(f" [default: {opt.default_value}]", end="")
                if len(opt.description) > 0:
                    print(f" - {opt.description}", end="")
                print()

        if len(self.subcommands) > 0:
            print("\nSubcommands:")
            for name, subcommand in self.subcommands.items():
                print(f" {name}: {subcommand.description}")
        print()

    def execute(self, args: List[str]):
        for i, opt in enumerate(self.opts):
            self.opt_maps[opt.name] = i

        if len(args) == 0 and self.run is None:
            return self.usage()

        if len(args) > 0:
            subcommand_name = args[0]
            if subcommand_name in self.subcommands:
                subcommand = self.subcommands[args[0]]
                return subcommand.execute(args[1:])

        parsed_args, opts, err = self.parse_args(args)
        if err is not None:
            print("ERROR:", err, end="\n\n")
            return self.usage()

        if "help" in opts and opts["help"]:
            return self.usage()

        if self.run:
            self.run(self, parsed_args, opts)
        else:
            self.usage()

def execute(command: Command):
    import sys
    return command.execute(sys.argv[1:])

def example_app():
    cli = Command(use="cask-example", description="This is the description of cask")
    cli.add_subcommand(Command(
        use="setup",
        opts=[
            Opt(name="--assets-path", kind=ValueType.String, 
                default_value="assets/", description="Your assets path"),
        ],
        args=[
            Arg(name="some-value", kind=ValueType.String, default_value=None),
        ],
        description="Run the environment setup (i.e. initializing database)",
        run=lambda command, args, opts: (
            print("Inializing the database with --assets-path='%s' and some-value='%s'" % (
                    opts["assets-path"], args[0]))
            )
        ))

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
