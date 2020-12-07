#### [Usage Question / Docs] Using @inject on free functions

If I have an inner function inside of a `configure` method, according to the following note it's not ok to use inject
there... What's the current state of this claim? Can I use it on functions or will that break in the future?

In haps, with its global container, it is absolutely encouraged

> This decorator is to be used on class constructors (or, as a convenience, on classes).
> Using it on non-constructor methods worked in the past but it was an implementation
> detail rather than a design decision.
> Third party libraries may, however, provide support for injecting dependencies
> into non-constructor methods or free functions in one form or another.
>
---- 

#### Is type inspection expensive?

---- 

I was wondering if it'd make sense to cache

---- 

#### Hear your thoughts on FastAPI

FastAPI took a slightly different approach in 



####

One of the selling points of the [dpy Library](https://github.com/search?l=Python&q=lala&type=Repositories) is that 
plain old "Python modules serve as our injection modules". Is the same possible with injector?
> Of course, you can also setup injectables behind conditionals if you like.
> 
> Modules may import their own dependencies or you might prefer to defer importing all your dependencies in a "main"
> module (or other organization). As long as all the dependencies are established at runtime, there's no problem.

I like this approach a lot to be able to pick whether a whole python module, or a specific type should be used as 
the container.

----

#### [Bug] - Provide better error message when signature is dumb

Traceback (most recent call last):
File "C:/projects/josxabot/app/clients/__init__.py", line 49, in <module>
inj.get(JosXaBotClient)
File "C:\git\injector\injector\__init__.py", line 963, in get result = scope_instance.get(interface, binding.provider)
.get(self)
File "C:\git\injector\injector\__init__.py", line 291, in get return injector.create_object(self._cls)
File "C:\git\injector\injector\__init__.py", line 990, in create_object self.call_with_injection(cls.__init__, self_
=instance, kwargs=additional_kwargs)
File "C:\git\injector\injector\__init__.py", line 1021, in call_with_injection dependencies = self.args_to_inject(
File "C:\git\injector\injector\__init__.py", line 111, in wrapper return function(*args, **kwargs)
File "C:\git\injector\injector\__init__.py", line 1069, in args_to_inject instance = self.get(interface)  # type: Any
File "C:\git\injector\injector\__init__.py", line 963, in get result = scope_instance.get(interface, binding.provider)
.get(self)
File "C:\git\injector\injector\__init__.py", line 329, in get return injector.call_with_injection(self._callable)
File "C:\git\injector\injector\__init__.py", line 1011, in call_with_injection signature = inspect.signature(callable)
File "c:\program files\python38\lib\inspect.py", line 3093, in signature return Signature.from_callable(obj,
follow_wrapped=follow_wrapped)
File "c:\program files\python38\lib\inspect.py", line 2842, in from_callable return _signature_from_callable(obj,
sigcls=cls, File "c:\program files\python38\lib\inspect.py", line 2228, in _signature_from_callable return _
signature_bound_method(sig)
File "c:\program files\python38\lib\inspect.py", line 1808, in _signature_bound_method raise ValueError('invalid method
signature')
ValueError: invalid method signature

(I was missing a `self` and PyCharm didn't catch it)
