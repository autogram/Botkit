# Autogram Botkit

**Warning:** At this point, the framework is very much in an alpha stage and many parts will be subject to change. Do not depend on it in production. As of now, this is just the basis of my various bot projects, but I am very actively working on smoothing
out the rough parts and delivering a comprehensive demo project using the framework.

<!--
## Why Botkit?

Surveying the ecosystem of open source Telegram bots, you will find

this is in large part due to MTProto having a very confusing API, with the Bot API being a partly reflection of that.
MTProto is confusing. The Bot API is usable, but robs you of flexibility.


There have been many libraries released over the years that sought to bring basic feature sets

On Telegram specifically, we tend to build highly complex user interfaces using an API that is not made for that and

but there hasn't been any framework to make this easier
share components

- Abstractions around

-
- Less repetitive code
- Declarative: Say what you want your application to do, not how to do it
-->



## When is this framework for you?

1. You want to work on regular bots, userbots, or especially a _combination_ thereof (a.k.a. "companion bots") in
Python. Botkit makes it easy to combine multiple Bot API or MTProto clients from different (!) libraries.

2. You have some experience with another Telegram bot library that you would like to supercharge with more tools, testability, and best practices.

3. You **care about clean, maintainable code** and tend to work on large code bases over long stretches of time

4. You know the basics of **asyncio**.

5. You're not afraid of Python type annotations and using Pydantic (https://pydantic-docs.helpmanual.io/) sounds like a good idea to you.

6. You use a Python IDE that supports autocompletion (and this is a must)! Botkit is built from the ground up to provide fluent builder patterns that only work well if you can discover what features you have at your disposal.


## Roadmap

### Implemented features

- [ ] One config to rule them all: [Pyrogram and Telethon clients can be instantiated from a common `ClientConfig`](https://github.com/autogram/Botkit/blob/81cf9ec49ca0bde1a541605b62ca0bf9e2b055ef/botkit/configuration/client_config.py)

### In progress

- [ ]

### In design phase

- [ ]

### Under consideration

- [ ]

<!--
## Introduction


This library is not meant for simple bots or scripts that

- 100% type annotations
- Usage of autocompletion is a must: Built using PyCharm and that's where it thrives

in these cases you will be better off using a Telegram client library directly.




## Features


## Roadmap

- At the moment, only Pyrogram is supported, but Botkit is architected in a way that it will eventually become library-agnostic, meaning that you will be able to use any Python library underneath it.



## Design Philosophy

### Why ISomething interfaces?
https://mail.python.org/pipermail/python-3000/2007-April/006614.html




-->
