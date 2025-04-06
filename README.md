# pymicrolib
A list of single file micro library for Python

### List of library

| Name      | Status          | Description                                                     |
|-----------|-----------------|-----------------------------------------------------------------|
| cask.py   | Usable          | Cask is a simple library for building a CLI application         |
| barrel.py | Inconvenient    | Barrel is a simple ORM library that only supports SQLite3       |
| bucket.py | Not Implemented | Bucket is a small library for building simple web applications. |


### FAQ

#### What Status Means?
- Usable
The library is already implemented

- Inconvinient
The library has an implementation, but not really usable or maybe inconvenient to use.

- Not Implemented
There's a design or idea for this library but there's no implementation currently

#### How do I use the library?
The idea behind these libraries is that they're easy to distribute and deploy because 
all the code is contained in a single file. You can just take the source code and 
put it into your project without the need of PIP or other package manager. If this sounds
familiar to you, maybe you come from the C programming language, where we have the concept
of header-only library. If you're not then take a look at [bottle.py](https://bottlepy.org),
which is one of the inspiration for the libraries

I, myself, usually put the libraries in a directory named **lib** if I use multiple libraries.
Sometime, I just copy paste the source code of the library into my source file since it's more
convenient

#### Is the library safe?
I never thought about safety when developing this libraries. You can use these libraries for
prototyping. I recommend use another libraries like FastAPI, Django, Flask, SQLAlchemy, etc.

#### Why Python?
I, actually, have implemented these of libraries in another language (which is Go) first, 
but I am not publishing it. I reimplement it in Python since I am very comfortable with Python,
I love using Python for prototyping ideas, and I don't like package manager.
