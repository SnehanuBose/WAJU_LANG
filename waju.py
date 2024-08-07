



################################################################
# CONSTANTS
################################################################
DIGITS = '0123456789'

#################################################################
#Token
#################################################################

# TT -> Token Type
TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MULTIPLY = 'MULTIPLY'
TT_DIVIDE = 'DIVIDE'
TT_LEFTPAREN = 'LEFTPAREN'
TT_RIGHTPAREN = 'RIGHTPAREN'

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

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
    def advance(self,current_char):
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
                tokens.append(TT_PLUS)
                self.advance()
            elif self.current_char in '-':
                tokens.append(TT_MINUS)
                self.advance()
            elif self.current_char in '*':
                tokens.append(TT_MULTIPLY)
                self.advance()
            elif self.current_char in '/':
                tokens.append(TT_DIVIDE)
                self.advance()
            elif self.current_char in '(':
                tokens.append(TT_LEFTPAREN)
                self.advance()
            elif self.current_char in ')':
                tokens.append(TT_RIGHTPAREN)
                self.advance()
            else:
                posStart=self.pos.copy()
                char=self.current_char
                self.advance()
                return [],IllegalCharacterError(posStart,self.pos,char)
        return tokens,None
    

    def makeNumber(self):

        strNum=''
        dotCount=0

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
            return Token(TT_INT, int(strNum))
        else:
            return Token(TT_FLOAT, float(strNum))
        





################################################################
# ERROR
################################################################

class Error:
    def __init__(self, errrName,errDetails,start_pos,end_pos):
        self.errName = errrName
        self.errDetails = errDetails
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def toString(self):
        return f"{self.errName}: {self.errDetails}\n File:{self.start_pos.fn} at {self.start_pos.ln+1}"
    
class IllegalCharacterError(Error):
    def __init__(self,start_pos,end_pos, char):
        super().__init__(start_pos,end_pos,"IllegalCharacterError", f"Illegal character '{char}'")



################################################################
# RUN
################################################################

def run(fn,text):
    lexer =Lexer(fn,text)
    tokens,error =lexer.makeTokens()
    return tokens,error