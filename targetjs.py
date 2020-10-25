import sys
from pyjsparser import parse

test = open("test.js").read()
parsed = parse(test)
print(parsed)

class JSObject(object):
  def __init__(self, proto):
    self.storage = {}  # type: dict[unicode, JSObject]
    self.proto = proto # type: JSObject

  def apply(self, thisArg, argumentsList):
    raise Exception("Not Implemented")

  def construct(self, args):
    raise Exception("Not Implemented")

  def defineProperty(self, key, desc):
    raise Exception('Not implemented')

  def deleteProperty(self, key):
    assert isinstance(key, JSString)

    self.storage[key.string] = None

    return JSUndefined()

  def get(self, key):
    assert isinstance(key, JSString)

    val = self.storage[key.string]
    if val == None and self.proto != None:
      return self.proto.getProperty(key)
    else:
      return JSUndefined()
  
  def getOwnPropertyDescriptor(self, key):
    raise Exception('Not Implemented')

  def getPrototypeOf(self):
    raise Exception("Not Implemented")

  def has(self, key):
    assert isinstance(key, JSString)
    return JSBoolean(key.string in self.storage)

  def isExtensible(self):
    raise Exception("Not Implemented")

  def ownKeys(self):
    res = JSObject(None)
    for i, key in enumerate(self.storage.keys()):
      res.set(JSString(unicode(i)), JSString(unicode(key)))

    return res

  def preventExtensions(self):
    raise Exception('Not Implemented')
  
  def set(self, key, val):
    assert isinstance(key, JSString)
    assert isinstance(val, JSObject)

    self.storage[key.string] = val

    return JSUndefined()
  
  def setPrototypeOf(self, proto):
    raise Exception("Not Implemented")

class JSString(JSObject):
  def __init__(self, string):
    assert isinstance(string, unicode)
    JSObject.__init__(self, None)
    self.string = string

class JSUndefined(JSObject):
  def __init__(self):
    JSObject.__init__(self, None)

class JSBoolean(JSObject):
  def __init__(self, boolean):
    assert isinstance(boolean, bool)
    JSObject.__init__(self, None)
    self.boolean = boolean

class JSFuntion(JSObject):
  def __init__(self, name, numArgs, env, code):
    assert isinstance(name, unicode)
    assert isinstance(numArgs, int)
    assert isinstance(env, JSObject)
    assert isinstance(code, list)
    JSObject.__init__(self, None)
    self.name = name
    self.numArgs = numArgs
    self.env = env
    self.code = code # type: list[Bytecode]
  
class Bytecode(object): pass
class GetProperty(Bytecode): pass

class PushIdentifier(Bytecode):
  def __init__(self, name):
    assert isinstance(name, unicode)
    self.name = name

class Call(Bytecode):
  def __init__(self, num):
    assert isinstance(num, int)
    self.num = num

class PushString(Bytecode):
  def __init__(self, string):
    assert isinstance(string, unicode)
    self.string = string

class Treewalker(object):
  def walk(self, tree):
    typ = tree['type']

    if typ == u'Program':
      return self.walk_program(tree)
    elif typ == u'ExpressionStatement':
      return self.walk_expression_statement(tree)
    elif typ == u'CallExpression':
      return self.walk_call_expression(tree)
    elif typ == u'MemberExpression':
      return self.walk_member_expression(tree)
    elif typ == u'Identifier':
      return self.walk_identifier(tree)
    elif typ == u'Literal':
      return self.walk_literal(tree)
    else:
      raise Exception('Unknown node: ' + typ)
  
  def walk_program(self, tree):
    return [self.walk(node) for node in tree['body']]
  
  def walk_expression_statement(self, tree):
    return self.walk(tree['expression'])
  
  def walk_call_expression(self, node):
    callee = self.walk(node['callee'])
    arguments = self.walk_arguments(node['arguments'])
    return callee + arguments + [Call(len(node['arguments']))]

  def walk_arguments(self, args):
    return [self.walk(node) for node in args]
  
  def walk_member_expression(self, node):
    obj = self.walk(node['object'])
    prop = self.walk(node['property'])
    return obj + prop + [GetProperty()]
  
  def walk_identifier(self, node):
    name = node['name']
    return [PushIdentifier(name)]

  def walk_literal(self, node):
    v = node['raw']
    if v[0] == '"':
      return [PushString(node['value'])]
    
def interpret(env, code):
  stack = []

  if isinstance(code, PushIdentifier):
    stack.append(JSString(code.name))
  elif isinstance(code, GetProperty):
    name = stack[-1]
    obj = stack[-2]
    stack.append(obj.getProperty(name))
  elif isinstance(code, PushString):
    stack.append(JSString(code.string))
  elif isinstance(code, Call):
    # args = stack[-code.num:]
    # TODO
    pass
  else:
    raise Exception('Unknown bytecode: ' + code)

def entry_point(argv):
  try:
    walker = Treewalker()
    code = walker.walk(parsed)
    print(code)
  except SystemExit:
    return 1
  return 0

# _____ Define and setup target ___

def target(driver, args):
  driver.exe_name = 'js-%(backend)s'
  return entry_point, None

def jitpolicy(self):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

if __name__ == '__main__':
  entry_point(sys.argv)