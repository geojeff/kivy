# ================================================================================
# Project:   Kivy.Statechart - A Statechart Framework for Kivy
# Copyright: (c) 2010, 2011 Michael Cohen, and contributors.
# Python Port: Jeff Pittman, ported from SproutCore, SC.Statechart
# ================================================================================

class StatechartSequenceMatcher:
    def __init__(self, statechartMonitor):
        self.statechartMonitor = statechartMonitor
        self.match = None
        self.MISMATCH = {}
  
    def begin(self):
        self._stack = []
        self.beginSequence()
        self._start = self._stack[0]
        return self
  
    def end(self):
        self.endSequence()
    
        if len(self._stack) > 0:
            raise "can not match sequence. sequence matcher has been left in an invalid state"
    
        monitor = self.statechartMonitor
        result = self._matchSequence(self._start, 0) is length(monitor.sequence)

        self.match = result
    
        return result
  
    def entered(self, *arguments):
        self._addStatesToCurrentGroup('entered', arguments) # [PORT] js arguments, so *arguments added here
        return self
  
    def exited(self):
        self._addStatesToCurrentGroup('exited', arguments)
        return self
  
    def beginConcurrent(self):
        group = { type: 'concurrent', values: [] }

        if self._peek():
            self._peek().values.append(group)

        self._stack.append(group)

        return self
  
    def endConcurrent(self):
        self._stack.pop()
        return self
  
    def beginSequence(self):
        group = { type: 'sequence', values: [] }

        if self._peek():
            self._peek().values.append(group)
        self._stack.append(group)
        return self
  
    def endSequence(self):
        self._stack.pop()
        return self
  
    def _peek(self):
        return None if len(self._stack) is 0 else self._stack[len(self._stack)-1]
  
    def _addStatesToCurrentGroup(self, action, states):
        group = self._peek()

        for i in range(len(states)):
            group.values.append({ action: action, state: states[i] })
  
    def _matchSequence(self, sequence, marker):
        values = sequence.values
        numberOfValues = len(values)
        val = ''
        monitor = self.statechartMonitor
        
        if numberOfValues is 0:
            return marker

        if marker > len(monitor.sequence):
            return self.MISMATCH
        
        for i in range(numberOfValues):
            val = values[i]
      
            if val.tokenType is 'sequence':
                marker = self._matchSequence(val, marker)
            elif val.tokenType is 'concurrent':
                marker = self._matchConcurrent(val, marker)
            elif not self._matchItems(val, monitor.sequence[marker]):
                return self.MISMATCH
            else:
                marker += 1
      
            if marker is self.MISMATCH:
                return self.MISMATCH
    
        return marker

    # A
    # B (concurrent [X, Y])
    #   X
    #     M
    #     N
    #   Y
    #     O
    #     P
    # C
    # 
    # 0 1  2 3 4   5 6 7  8
    #      ^       ^
    # A B (X M N) (Y O P) C
    #      ^       ^
    # A B (Y O P) (X M N) C
  
    def _matchConcurrent(self, concurrent, marker):
        values = concurrent.values[:]
        numberOfValues = len(values)
        val = ''
        tempMarker = marker
        match = false
        monitor = self.statechartMonitor
        
        if numberOfValues is 0:
            return marker
    
        if marker > len(monitor.sequence):
            return self.MISMATCH
    
        while len(values) > 0:
            for i in range(numberOfValues):
                val = values[i]
      
                if val.tokenType is 'sequence':
                    tempMarker = self._matchSequence(val, marker)
                elif val.tokenType is 'concurrent':
                    tempMarker = self._matchConcurrent(val, marker)
                elif not self._matchItems(val, monitor.sequence[marker]):
                    tempMarker = self.MISMATCH
                else:
                    tempMarker = marker + 1
      
                if tempMarker is not self.MISMATCH:
                    break
      
                if tempMarker is self.MISMATCH:
                    return self.MISMATCH

                del values[i] # [PORT] was removeAt
              
                marker = tempMarker
    
            return marker
  
    def _matchItems(self, matcherItem, monitorItem):
        if matcherItem is None or monitorItem is None:
            return False
  
        if matcherItem.action is not monitorItem.action:
            return False
    
        if isintance(matcherItem.state, Object) and matcherItem.state is monitorItem.state:
            return True
    
        if matcherItem.state is monitorItem.state.name:
            return True
  
        return False
