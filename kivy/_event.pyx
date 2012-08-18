'''
Event dispatcher
================

All objects that produce events in Kivy implement :class:`EventDispatcher`,
providing a consistent interface for registering and manipulating event
handlers.

.. versionchanged:: 1.0.9
    Properties discovering and methods have been moved from
    :class:`~kivy.uix.widget.Widget` to :class:`EventDispatcher`

To use :class:`EventDispatcher`, create a subclass that follows the rules
outlined below for registering an event, including a default handler method,
and making appropriate dispatch() calls. Observer methods in related
classes should have a calling signature matching the dispatch() arguments
for an observed event. See individual method sections for the full complement
of available functionality, but here are minimal examples of creating custom
events and usage::

    class Worker(EventDispatcher):
        
        def __init__(self, **kwargs):
            super(Worker, self).__init__(**kwargs)
            self.register_event_type('on_start')

        def on_start(self):
            pass

        def work_start_method(self):
            # Initialize some work...
            self.dispatch('on_start')

    # A class that uses a Worker, and observes its on_start event:
    class WorkObserver(Widget):
        
        worker = ObjectProperty(None)

        def __init__(self, **kwargs):
            super(WorkObserver, self).__init__(**kwargs)
            self.worker = Worker()
            self.worker.bind(on_start=self.on_start_callback)
    
        def on_start_callback(*largs):
            print 'worker start callback called', largs

The example above could also report progress by passing a progress value along
with the event name in the dispatch() call (See work_method() dispatch call):

    class Worker(EventDispatcher):

        def __init__(self, **kwargs):
            super(Worker, self).__init__(**kwargs)
            self.register_event_type('on_start')
            self.register_event_type('on_progress')

        def on_start(self):
            pass

        def on_progress(self, progress):
            pass

        def work_start_method(self):
            # Initialize some work...
            self.dispatch('on_start')

        def work_method(self):
            progress = calculate_progress()
            self.dispatch('on_progress', progress)

        def calculate_progress(self):
            # Calculate progress, perhaps based on time elapsed from start.
            pass

    class WorkObserver(Widget):
        
        worker = ObjectProperty(None)

        def __init__(self, **kwargs):
            super(WorkObserver, self).__init__(**kwargs)
            self.worker = Worker()
            self.worker.bind(on_start=self.on_start_callback,
                             on_progress=self.on_progress_callback)
    
        def on_start_callback(self, *largs):
            print 'worker start callback called', largs

        # This callback gets a progress argument.
        def on_progress_callback(self., progress, *args):
            print 'worker progress callback called', args
            print 'progress value =', progress

Another way to use the event system in operations within a class is to create
a property, and add a method that starts with 'on_' and ends with the property
name in question, as with 'on_progress'. This method will be called
automatically when the progress property changes::

    class Worker(EventDispatcher):

        progress = NumericProperty(0)

        def __init__(self, **kwargs):
            super(Worker, self).__init__(**kwargs)
            self.register_event_type('on_start')

        def on_start(self):
            pass

        def some_worker_method(self):
            # Do work. Update self.progress.

        def on_progress(self, progress):
            # Do something as a result of progress changing.

Also, for property observing external to a class, bind a callback to the
property by referring to the property name (last line of code example)::

    class Worker(EventDispatcher):

        progress = NumericProperty(0)

        def __init__(self, **kwargs):
            super(Worker, self).__init__(**kwargs)
            self.register_event_type('on_start')

        def on_start(self):
            pass

        def some_worker_method(self):
            # Do work. Update self.progress.

        def on_progress(self, progress):
            # Do something as a result of progress changing.

    # Elsewhere in your program:
    def progress_changed(worker, progress):
        print 'worker', worker, 'made progress:', progress

    worker = Worker()
    worker.bind(progress=progress_changed)
'''

__all__ = ('EventDispatcher', )


from functools import partial
from kivy.weakmethod import WeakMethod
from kivy.properties cimport Property, ObjectProperty

cdef tuple forbidden_properties = ('touch_down', 'touch_move', 'touch_up')
cdef int widget_uid = 0
cdef dict cache_properties = {}

cdef class EventDispatcher(object):
    '''Generic event dispatcher interface.

    See the module docstring for usage.
    '''

    cdef dict __event_stack
    cdef dict __properties

    def __cinit__(self, *largs, **kwargs):
        global widget_uid, cache_properties
        cdef dict widget_dict = self.__dict__
        cdef dict cp = cache_properties
        cdef dict attrs_found
        cdef list attrs
        cdef Property attr
        cdef str k
        self.__event_stack = {}
        __cls__ = self.__class__

        # XXX for the moment, we need to create a uniq id for properties.
        # Properties need a identifier to the class instance. hash() and id()
        # are longer than using a custom __uid. I hope we can figure out a way
        # of doing that without require any python code. :)
        widget_uid += 1
        widget_dict['__uid'] = widget_uid
        widget_dict['__storage'] = {}

        if __cls__ not in cp:
            attrs_found = cp[__cls__] = {}
            attrs = dir(__cls__)
            for k in attrs:
                uattr = getattr(__cls__, k)
                if not isinstance(uattr, Property):
                    continue
                if k in forbidden_properties:
                    raise Exception('Property <%s> has a forbidden name' % k)
                attrs_found[k] = uattr
        else:
            attrs_found = cp[__cls__]

        # First loop, link all the properties storage to our instance
        for k in attrs_found:
            attr = attrs_found[k]
            attr.link(self, k)

        # Second loop, resolve all the reference
        for k in attrs_found:
            attr = attrs_found[k]
            attr.link_deps(self, k)

        self.__properties = attrs_found

    def __init__(self, **kwargs):
        cdef str func, name, key
        cdef dict properties
        super(EventDispatcher, self).__init__()

        # Auto bind on own handler if exist
        properties = self.properties()
        for func in dir(self):
            if not func.startswith('on_'):
                continue
            name = func[3:]
            if name in properties:
                self.bind(**{name: getattr(self, func)})

        # Apply the existing arguments to our widget
        for key, value in kwargs.iteritems():
            if key in properties:
                setattr(self, key, value)

    def register_event_type(self, str event_type):
        '''Register an event type with the dispatcher.

        Registering event types allows the dispatcher to validate event handler
        names as they are attached, and to search attached objects for suitable
        handlers. Each event type declaration must :

            1. start with the prefix `on_`
            2. have a default handler in the class
        '''

        if not event_type.startswith('on_'):
            raise Exception('A new event must start with "on_"')

        # Ensure the user have at least declare the default handler
        if not hasattr(self, event_type):
            raise Exception(
                'Missing default handler <%s> in <%s>' % (
                event_type, self.__class__.__name__))

        # Add the event type to the stack
        if not event_type in self.__event_stack:
            self.__event_stack[event_type] = []

    def unregister_event_types(self, str event_type):
        '''Unregister an event type in the dispatcher.
        '''
        if event_type in self.__event_stack:
            del self.__event_stack[event_type]

    def is_event_type(self, str event_type):
        '''Return True if the event_type is already registered.

        .. versionadded:: 1.0.4
        '''
        return event_type in self.__event_stack

    def bind(self, **kwargs):
        '''Bind an event type or a property to a callback

        Usage::

            # With properties
            def my_x_callback(obj, value):
                print 'on object', obj, 'x changed to', value
            def my_width_callback(obj, value):
                print 'on object', obj, 'width changed to', value
            self.bind(x=my_x_callback, width=my_width_callback)

            # With event
            self.bind(on_press=self.my_press_callback)

        Usage in a class::

            class MyClass(BoxLayout):
                def __init__(self):
                    super(MyClass, self).__init__(**kwargs)
                    btn = Button(text='click on')
                    btn.bind(on_press=self.my_callback) #bind event
                    self.add_widget(btn)

                def my_callback(self,obj,value):
                    print 'press on button', obj, 'with date:', value

        '''
        for key, value in kwargs.iteritems():
            if key[:3] == 'on_':
                if key not in self.__event_stack:
                    continue
                # convert the handler to a weak method
                handler = WeakMethod(value)
                self.__event_stack[key].append(handler)
            else:
                self.__properties[key].bind(self, value)

    def unbind(self, **kwargs):
        '''Unbind properties from callback functions.

        Same usage as :func:`bind`.
        '''
        for key, value in kwargs.iteritems():
            if key[:3] == 'on_':
                if key not in self.__event_stack:
                    continue
                # we need to execute weak method to be able to compare
                for handler in self.__event_stack[key]:
                    if handler() != value:
                        continue
                    self.__event_stack[key].remove(handler)
                    break
            else:
                self.__properties[key].unbind(self, value)

    def dispatch(self, str event_type, *largs):
        '''Dispatch an event across all the handlers added in bind().
        As soon as a handler returns True, dispatching stops.

        An event_type, the name of the event_type as a string, is required.
        Typical usage is to simply dispatch the event name, which will begin
        with 'on_'::

            self.dispatch('on_start')

        However, you may need to pass other arguments to event handlers. For
        example, in a widget that customizes animation, there may be several
        steps in the animation start() method, before the 'on_start' event is
        fired, and the dispatch() call could include the widget::

            def start(self, widget):
                self.stop(widget)
                self._initialize(widget)
                self._register()
                self.dispatch('on_start', widget)

        The required matching on_start() default event handler, declared in
        the class where the on_start event is registered, would be::

            def on_start(self, widget):
                pass

        And, in a class containing an animation, in its __init__(), a binding
        to the on_start event could be created for an event-handling method::

            self.my_animation.bind(on_start=self.on_animation_start)

        See module docs and animation.py for examples of event dispatching,
        including use of multiple additional arguments in dispatch() calls.
        '''
        cdef list event_stack = self.__event_stack[event_type]
        cdef object remove = event_stack.remove
        for value in event_stack[:]:
            handler = value()
            if handler is None:
                # handler have gone, must be removed
                remove(value)
                continue
            if handler(self, *largs):
                return True

        handler = getattr(self, event_type)
        return handler(*largs)

    #
    # Properties
    #
    def __proxy_setter(self, dstinstance, name, instance, value):
        self.__properties[name].__set__(dstinstance, value)

    def __proxy_getter(self, dstinstance, name, instance):
        return self.__properties[name].__get__(dstinstance)

    def setter(self, name):
        '''Return the setter of a property. Useful if you want to directly bind
        a property to another.

        .. versionadded:: 1.0.9

        For example, if you want to position one widget next to another::

            self.bind(right=nextchild.setter('x'))
        '''
        return partial(self.__proxy_setter, self, name)

    def getter(self, name):
        '''Return the getter of a property.

        .. versionadded:: 1.0.9
        '''
        return partial(self.__proxy_getter, self, name)

    def property(self, name):
        '''Get a property instance from the name.

        .. versionadded:: 1.0.9

        :return:

            A :class:`~kivy.properties.Property` derived instance
            corresponding to the name.
        '''
        return self.__properties[name]

    cpdef dict properties(self):
        '''Return all properties in the class as a dictionary of
        key/property class. Can be used for introspection.

        .. versionadded:: 1.0.9
        '''
        cdef dict ret, p
        ret = {}
        p = self.__properties
        for x in self.__dict__['__storage'].keys():
            ret[x] = p[x]
        return ret

    def create_property(self, name):
        '''Create a new property at runtime.

        .. versionadded:: 1.0.9

        .. warning::

            This function is designed for the Kivy language. Don't use it in
            your code. You should declare properties in your class instead of
            using this method.

        :Parameters:
            `name`: string
                Name of the property

        The class of the property cannot be specified. It will always be an
        :class:`~kivy.properties.ObjectProperty` class. The default value of
        the property will be None, until you set a new value.

        >>> mywidget = Widget()
        >>> mywidget.create_property('custom')
        >>> mywidget.custom = True
        >>> print mywidget.custom
        True
        '''
        prop = ObjectProperty(None)
        prop.link(self, name)
        prop.link_deps(self, name)
        self.__properties[name] = prop
        setattr(self.__class__, name, prop)
