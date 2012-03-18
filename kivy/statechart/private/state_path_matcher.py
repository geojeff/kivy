# ================================================================================
# Project:   Kivy.Statechart - A Statechart Framework for Kivy
# Copyright: (c) 2010, 2011 Michael Cohen, and contributors.
# Python Port: Jeff Pittman, ported from SproutCore, SC.Statechart
# ================================================================================

""" @class

  The `StatePathMatcher` is used to match a given state path match expression 
  against state paths. A state path is a basic dot-notion consisting of
  one or more state names joined using '.'. Ex: 'foo', 'foo.bar'. 
  
  The state path match expression language provides a way of expressing a state path.
  The expression is matched against a state path from the end of the state path
  to the beginning of the state path. A match is true if the expression has been
  satisfied by the given path. 
  
  Syntax:
  
    expression -> <this> <subpath> | <path>
    
    path -> <part> <subpath>
    
    subpath -> '.' <part> <subpath> | empty
  
    this -> 'this'
    
    part -> <name> | <expansion>
    
    expansion -> <name> '~' <name>
    
    name -> [a-z_][\w]*
    
  Expression examples:
  
    foo
    
    foo.bar
    
    foo.bar.mah
    
    foo~mah
    
    self.foo
    
    self.foo.bar
    
    self.foo~mah
    
    foo.bar~mah
    
    foo~bar.mah

  @extends Object
  @author Michael Cohen
"""
class StatePathMatcher:
    """
      A parsed set of tokens from the matcher's given expression
      
      @field {Array}
      @see #expression
    """
    tokens = ListProperty()
  
    lastPart = StringProperty(None)

    def __init__(self):
        """
          The state that is used to represent 'self' for the
          matcher's given expression.
          
          @field {State}
          @see #expression
        """
        state = None

        """
          The expression used by this matcher to match against
          given state paths
              
          @field {String}
        """
        self.expression = None
          
        def tokensChanged(*l):
            self.lastPart = self_lastPart()

        self.bind(tokens=tokensChanged)

        self._parseExpression()
  
    """ @private 
  
    Will parse the matcher's given expession by creating tokens and chaining them
      together.
      
      Note: Because the DSL for state path expressions is tiny, a simple hand-crafted 
      parser is being used. However, if the DSL becomes any more complex, then it will 
      probably be necessary to refactor the logic in order follow a more conventional 
      type of parser.
      
      @see #expression
    """
    def _parseExpression(self):
        parts = self.expression.split('.') if self.expression else []
        part = ''
        chain = None
        token = ''
        tokens = []
      
        for i in range(len(parts)):
            part = parts[i]
      
            if part.find('~') >= 0:
                part = part.split('~')
                if len(part) > 2:
                    raise "Invalid use of '~' at part {0}".format(i)
                token = StatePathMatcher._ExpandToken({ start: part[0], end: part[1] })
            elif part is self:
                if len(tokens) > 0:
                    raise "Invalid use of 'this' at part {0}".format(i)
                token = StatePathMatcher._ThisToken()
            else:
                token = StatePathMatcher._BasicToken({ value: part })
            
            token.owner = self
            tokens.append(token)
      
        self.tokens = tokens
      
        stack = tokens[:]
        chain = stack.pop() # [TODO] pop
        self._chain = chain
        while True:
            chain.nextToken = stack.pop()
            chain = token
            if len(stack) is 0:
                break
  
    """
      Returns the last part of the expression. So if the
      expression is 'foo.bar' or 'foo~bar' then 'bar' is returned
      in both cases. If the expression is 'self' then 'self is
      returned. 
    """
    def _lastPart(self):
        numberOfTokens = len(self.tokens) if self.tokens else 0
        token = tokens[numberOfTokens-1] if numberOfTokens > 0 else None
        return token.lastPart
    
    """
      Will make a state path against this matcher's expression. 
      
      The path provided must follow a basic dot-notation path containing
      one or dots '.'. Ex: 'foo', 'foo.bar'
      
      @param path {String} a dot-notation path
      @return {Boolean} true if there is a match, otherwise false
    """
    def match(self, path):
        self._stack = path.split('.')
        if path is None or isinstance(path, String):
            return False
        return self._chain.match()
  
    """ @private """
    def _pop(self):
        self._lastPopped = self._stack.pop() # [TODO] pop
        return self._lastPopped

""" @private @class

  Base class used to represent a token the expression
"""
class _Token:
    def __init__(self): 
        """ The type of this token """
        self.tokenType = None
  
        """ The state path matcher that owns this token """
        self.owner = None
  
        """ The next token in the matching chain """
        self.nextToken = None
        
        """ 
          The last part the token represents, which is either a valid state
          name or representation of a state
        """
        self.lastPart = None
  
    """ 
      Used to match against what is currently on the owner's
      current path stack
    """
    def match(self):
        return False

""" @private @class

  Represents a basic name of a state in the expression. Ex 'foo'. 
  
  A match is true if the matcher's current path stack is popped and the
  result matches this token's value.
"""
class _BasicToken(_Token):
    value = StringProperty(None)
    lastPart = StringProperty(None)

    def __init__(self):
        self.tokenType = 'basic'
    
        def valueChanged(self):
            self.lastPart = self.value
    
        self.bind(value=valueChanged)
   
    def match(self):
        part = self.owner._pop() # [TODO] pop
        token = self.nextToken

        if self.value is not part:
            return False
    
        return token.match() if token else True
  
""" @private @class

  Represents an expanding path based on the use of the '<start>~<end>' syntax.
  <start> represents the start and <end> represents the end. 
  
  A match is true if the matcher's current path stack is first popped to match 
  <end> and eventually is popped to match <start>. If neither <end> nor <start>
  are satisfied then false is returned.
"""
class _ExpandToken(_Token):
    lastPart = StringProperty(None)
    end = StringProperty(None)

    def __init__(self):
        self.tokenType = 'expand'
        self.start = None
        self.end = None
  
        def endChanged(*l):
            self.lastPart = self_lastPart()

        self.bind(end=endChanged)

    def _lastPart(self):
        self.lastPart = self.end

    def match(self):
        start = self.start
        end = self.end
        part = ''
        token = self.nextToken
          
        part = self.owner._pop()
        if part is not end:
            return False
      
        while True:
            part = self.owner._pop()
            if part is start:
                return token.match() if token else True
            if len(self.owner) is 0:
                break
      
        return False

""" @private @class
  
  Represents a this token, which is used to represent the owner's
  `state` property.
  
  A match is true if the last path part popped from the owner's
  current path stack is an immediate substate of the state this
  token represents.
"""
class _ThisToken(_Token):
    def __init__(self):
        self.tokenType = 'self'
        self.lastPart = 'self'
  
    def match(self):
        state = self.owner.state
        substates = state.substates
        
        part = self.owner._lastPopped

        if part is None or len(self.owner._stack) is not 0:
            return False
    
        for i in range(len(self.substates)):
            if substates[i]['name'] is part:
                return True
    
        return False
