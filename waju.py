################################################################
# IMPORTS
################################################################

from string_with_arrows import *

################################################################
# CONSTANTS
################################################################
DIGITS = '0123456789'

#################################################################
#Token
#################################################################

# TT -> Token Type
TT_INT = 'TT_INT'
TT_FLOAT = 'TT_FLOAT'
TT_PLUS = 'TT_PLUS'
TT_MINUS = 'TT_MINUS'
TT_MULTIPLY = 'TT_MULTIPLY'
TT_DIVIDE = 'TT_DIVIDE'
TT_POWER = 'TT_POWER'
TT_LEFTPAREN = 'TT_LEFTPAREN'
TT_RIGHTPAREN = 'TT_RIGHTPAREN'
TT_EOF = 'TT_EOF'

class Token:
    def __init__(self, type_, value=None,pos_start=None,pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end
				
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

#####################################################################
# POSITION
#####################################################################

class Position:
    def __init__(self,idx,ln,col,fn,ftxt):
        self.ln = ln
        self.col = col
        self.idx = idx
        self.fn = fn
        self.ftxt = ftxt
    def advance(self,current_char = None):
        self.idx+=1
        self.col+= 1

        if current_char == '\n':
            self.ln+= 1
            self.col = 0
        return self
    def copy(self):
        return Position(self.idx, self.ln, self.col,self.fn,self.ftxt)

#####################################################################
# Lexer
#####################################################################

class Lexer:
    def __init__(self, fn,text):
        self.text = text
        self.fn = fn
        self.pos = Position(-1,0,-1,fn,text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
            self.current_char = None

    def makeTokens(self): 
        tokens=[]

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.makeNumber())
                self.advance()
            elif self.current_char in '+':
                tokens.append(Token(TT_PLUS,pos_start=self.pos))
                self.advance()
            elif self.current_char in '-':
                tokens.append(Token(TT_MINUS,pos_start=self.pos))
                self.advance()
            elif self.current_char in '*':
                tokens.append(Token(TT_MULTIPLY,pos_start=self.pos))
                self.advance()
            elif self.current_char in '/':
                tokens.append(Token(TT_DIVIDE,pos_start=self.pos))
                self.advance()
            elif self.current_char in '(':
                tokens.append(Token(TT_LEFTPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char in ')':
                tokens.append(Token(TT_RIGHTPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char in '^':
                tokens.append(Token(TT_POWER,pos_start=self.pos))
                self.advance()
            else:
                posStart=self.pos.copy()
                char=self.current_char
                self.advance()
                return [],IllegalCharacterError(posStart,self.pos,char)
            

        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens,None
    
    def makeNumber(self):

        strNum=''
        dotCount=0
        start_pos = self.pos.copy()

        while self.current_char!=None and (self.current_char in DIGITS or self.current_char=='.'):
            if self.current_char=='.':
                dotCount+=1
                if dotCount>1:
                    raise ValueError("Invalid number format")
                strNum+='.'
            else:
                strNum+=self.current_char
            self.advance()
        
        if dotCount == 0:
            return Token(TT_INT, int(strNum),start_pos,self.pos)
        else:
            return Token(TT_FLOAT, float(strNum),start_pos,self.pos)
        

################################################################
# RUNTIME RESULT
################################################################

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self,res):
        if res.error:
            self.error = res.error
        return res.value
    
    def success(self,value):
        self.value = value
        return self
    def failure(self,error):
        self.error = error
        return self

################################################################
# ERROR
################################################################

class Error:
    def __init__(self, errrName,errDetails,start_pos,end_pos):
        self.errName = errrName
        self.errDetails = errDetails
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def asString(self):
        return f"{self.errName}: {self.errDetails}\n File:{self.start_pos.fn} at {self.start_pos.ln+1} \n\n {string_with_arrows(self.start_pos.ftxt, self.start_pos, self.end_pos)}"
    
class IllegalCharacterError(Error):
    def __init__(self,start_pos,end_pos, char):
        super().__init__(start_pos,end_pos,"IllegalCharacterError", f"Illegal character '{char}'")

class InvalidSyntaxError(Error):
    def __init__(self,start_pos,end_pos, char):
        super().__init__(start_pos,end_pos,"InvalidSyntaxError", f"Invalid Syntax '{char}'")

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context
    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):	
        result = ''
        pos = self.pos_start
        ctx = self.context
        while ctx:
			
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback (most recent call last):\n' + result

################################################################
#Nodes
################################################################

class NumberNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end  = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'
    
class BinaryOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end  # Assuming the operator's position is the end of the operator's token. If not, this needs to be updated.

    def __repr__(self):
        return f'({self.left_node} , {self.op_tok} , {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.end_pos = node.pos_end
    
    def __repr__(self):
        return f'({self.op_tok} , {self.node})'
    
###############################################################
# PARSE RESULT
###############################################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self,result):
        if isinstance(result,ParseResult):
            if self.error is None:
                self.error = result.error
            return result.node
        return result

    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

###############################################################
# PARSER
###############################################################

class Parser:
    def __init__(self, tokens):
        # print(tokens)
        self.tokens = tokens
        self.current_token_idx=-1
        self.advance()
    
    def advance(self):
        self.current_token_idx += 1
        if self.current_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.current_token_idx]
        return self.current_token
    
    def atom(self):
        res = ParseResult()
        token = self.current_token
        if token.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            # print(f'Hello {self.current_token}')
            return res.success(NumberNode(token))
        elif token.type in TT_LEFTPAREN:
            res.register(self.advance())
            expr_res = res.register(self.expr())
            if res.error or self.current_token.type!= TT_RIGHTPAREN:
                res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,"Expected ')'"))
            res.register(self.advance())
            return res.success(expr_res)
        return res.failure(InvalidSyntaxError(token.pos_start, token.pos_end,'Expected INT or FLOAT'))
            
    def power(self):
        return self.binaryOperation(self.atom,(TT_POWER, ),self.factor)
        
    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS,TT_MINUS):
            res.register(self.advance())
            factor= res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(token, factor))
        return self.power()

    def binaryOperation(self,func_a,op,func_b=None):

        if func_b is None:
            func_b = func_a# Assuming equality and inequality as binary operators. Replace with the correct operator.

        res =ParseResult()

        left = res.register(func_a())

        if res.error: 
            return res
        
        while self.current_token.type in op:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(func_b())
            if res.error:
                return res
            left = BinaryOpNode(left,op_tok,right)
        return res.success(left)
    
    def term(self):
        return self.binaryOperation(self.factor,(TT_MULTIPLY,TT_DIVIDE))
    def expr(self):
        return self.binaryOperation(self.term,(TT_PLUS,TT_MINUS))
        
    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != TT_EOF:
            res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,"Expected '+', '-', '*' or '/'"))
        # print(f'res = {res}')
        return res
    
################################################################
# Values
################################################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.setContext()
    
    def set_pos(self,pos_start=None,pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def setContext(self,context=None):
        self.context = context
        return self

    def addedto(self,other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setContext(self.context),None
        else:
            raise TypeError('Unsupported operand type(s) for +: "Number" and "{type(other).__name__}"')

    def subbed_by(self,other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context),None
        else:
            raise TypeError('Unsupported operand type(s) for -: "Number" and "{type(other).__name__}"')

    def multed_by(self,other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context),None
        else:
            raise TypeError('Unsupported operand type(s) for *: "Number" and "{type(other).__name__}"')

    def divideby(self,other):
        if isinstance(other, Number):
            if other.value == 0:
                return None,RuntimeError(other.pos_start,other.pos_end,"Division by Zero",self.context)
            return Number(self.value / other.value).setContext(self.context),None
        else:
            raise TypeError('Unsupported operand type(s) for /: "Number" and "{type(other).__name__}"')

    def powerRaisedTo(self,other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).setContext(self.context),None
        else:
            raise TypeError('Unsupported operand type(s) for **: "Number" and "{type(other).__name__}"')

    def __repr__(self):
        return f'Number({self.value})'


################################################################
# INTERPRETER
################################################################

class Intepreter:
    def visit(self,node,context):
        method_name = f'visit_{type(node).__name__}'

        method = getattr(self,method_name,self.no_visit_method)
        return method(node,context)
    
    def no_visit_method(self,node,context):
        raise NotImplementedError(f'No visit_{type(node).__name__} method defined')
    

    def visit_NumberNode(self,node,context):
        return RTResult().success(Number(node.token.value).setContext(context).set_pos(node.pos_start,node.pos_end))

    def visit_BinaryOpNode(self,node,context):

        res = RTResult()

        left = res.register(self.visit(node.left_node,context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node,context))
        if res.error:
            return res

        if node.op_tok.type == TT_PLUS:
            result,error =  left.addedto(right)
        elif node.op_tok.type == TT_MINUS:
            result,error = left.subbed_by(right)
        elif node.op_tok.type == TT_MULTIPLY:
            result,error = left.multed_by(right)
        elif node.op_tok.type == TT_DIVIDE:
            result,error = left.divideby(right)
        elif node.op_tok.type == TT_POWER:
            result,error = left.powerRaisedTo(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end)) 

    def visit_UnaryOpNode(self,node,context):
        res = RTResult()
        number = res.register(self.visit(node.node,context))
        if res.error:
            return res
        
        error  = None

        if node.op_tok.type == TT_MINUS:
            number,error  = number.multed_by(Number(-1))
        
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.end_pos))
        

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

################################################################
# RUN
################################################################

def run(fn,text):
    #generate Tokens
    lexer =Lexer(fn,text)
    tokens,error =lexer.makeTokens()
    if error: return None ,error

    # generate AST 
    parser = Parser(tokens)
    ast = parser.parse()

    #Run the Program
    intepreter =Intepreter()
    context = Context('<Program>')
    result = intepreter.visit(ast.node,context)

    return result.value,result.error