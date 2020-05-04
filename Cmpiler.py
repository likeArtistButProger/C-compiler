import sys, os, re, collections
import time

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])





# AST SECTION

class Tree(object):
    def __init__(self):
        self.left  = None # Left represents a type of a node it self, is it a Token or another Tree
        self.child = []
        self.data  = []

    def __len__(self):
        length = 1
        for i in range(len(self.child)):
            if(type(self.child[i].left) == type(Token('', '', '', ''))):
                length += len(self.child[i].left)//4
                print("Child is token:", len(self.child[i].left)//4)
                print(self.child[i].left)
                print("Type is: ", self.child[i].left.type)
                print("Value is: ", self.child[i].left.value)
                print("Line is: ", self.child[i].left.line)
                print("Column is: ", self.child[i].left.column)

                print("Length:", length)
            else:
                length += len(self.child[i].left)
                print("Child is node:", len(self.child[i].left))
                print(self.child[i].left)
                print("Length:", length)
        return length


    def createChildren(self, amount):
        for i in range(0, amount):
            self.child.append(Tree())

    def setChildrenValues(self, list):
        for i in range(0, len(list)):
            self.data.append(list[i])

    # def showChildrenTokens(self):
    #     print("")
    #     print("Show Children function call")
    #     print("************")
    #     print("Token of node:")
    #     print(self.left)
    #     print("Children:")
    #     print(self.child)
    #     print("Token of children:")
    #     print(len(self.child))
    #     for i in range(0, len(self.child)):
    #         print(self.child[i].left)
    #     print("***********")
    #     print("")

    def setTokensForTreePart(self):
        for i in range(0, len(self.child)):
            if(type(self.child[i].left) == type(Token('','','',''))):  #Comparing with empty token to be sure we handling a token!
                self.data.append(self.child[i].left)
                # print(self.data)

            if(type(self.child[i].left) == type(self)):
                self.data.append(self.child[i].left)

#LEXER SECTION


def lex(src_file):
    keywords = {'int', 'return'}
    token_specification =   [
        ('Openbrace', r'{'),
        ('Closebrace', r'}'),
        ('Openparenthesis', r'\('),
        ('Closeparenthesis', r'\)'),
        ('Semicolon', r';'),
        ('Identifier', r'[A-Za-z]+'),
        ('Integerliteral', r'[0-9]+'),
        ('Newline', r'\n'),
        ('Skip', r'[ \t]+'),            #Skip for tabs and spaces
        ('Mismatch', r'.')              #Any other character
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    prevTokenFlag = 0
    for mo in re.finditer(tok_regex, src_file):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if(kind == 'Integerliteral'):
            if(prevTokenFlag == 1):
                raise RuntimeError("Missing space character between identifier and value")
            value = int(value)
        elif((kind == 'Identifier') and (value in keywords)):
            if(value == "return"):
                prevTokenFlag = 1
            kind = value
        elif(kind == 'Newline'):
            line_start = mo.end()
            line_num += 1
            continue
        elif(kind == 'Skip'):
            if(prevTokenFlag == 1):
                prevTokenFlag = 0
            if(prevTokenFlag == 0):
                continue
        elif(kind == 'Mismatch'):
            raise RuntimeError(f'{value!r} unexpected line {line_num}')
        # print("Token: ", kind, " ", value, " ", line_num, " ", column, ";")
        yield Token(kind, value, line_num, column)





#PARSER SECTION

def parse_exp(tokens):
    # print("Parsing exponent!")
    exp = Tree()
    tok = next(tokens)
    if(tok.type != "Integerliteral"):
        raise RuntimeError(f'Parse_exp error, supposed to be Integer literal!')
    exp.createChildren(1)
    exp.child[len(exp.data)-1].left = tok
    exp.setTokensForTreePart()
    return exp


def parse_statement(tokens):
    statement = Tree()
    # print("Parsing statement!")
    tok = next(tokens)
    if(tok.type != "return"):
        raise RuntimeError(f'Parse_statement error, supposed to be return')

    statement.createChildren(1)
    statement.child[len(statement.data)-1].left = tok

    exp = parse_exp(tokens)
    statement.createChildren(1)
    statement.child[len(statement.data)-1].left = exp
    tok = next(tokens)
    if(tok.type != "Semicolon"):
        raise RuntimeError(f'Parse_statement error, supposed to be ;')

    statement.createChildren(1)
    statement.child[len(statement.data)-1].left = tok

    statement.setTokensForTreePart()
    return statement

# def parse_params(tokens):
#     params = Tree()
#     print("Parsing params!")
#     tok = next(tokens)
#     while(tok.type != "Closeparenthesis"):
#         if(tok.type == "Openbrace"):
#             raise RuntimeError("Parse function error, supposed to be Closeparethesis sign )")
        
#         params.createChildren(1)
#         params.child[len(params.data)-1].left = tok
#         tok = next(tokens)
#         # print("Current token is: ", tok)
#     params.setTokensForTreePart()
#     return params

def parse_function(tokens):
    function = Tree()
    # print("Parsing function")
    tok = next(tokens)
    if(tok.type != "int"):
        raise RuntimeError(f'Parse_function error, supposed to be Identifier!(int)')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok
    tok = next(tokens)
    if(tok.type != "Identifier" and tok.value != "main"):
        raise RuntimeError(f'Parse_function error, supposed to be Identifier!(main)')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok

    tok = next(tokens)
    if(tok.type != "Openparenthesis"):
        raise RuntimeError(f'Parse_function error, supposed to be Openparenthesis sign!')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok


    #-----------------------------------------------------------------------
    # tok = next(tokens)
    # print("Function data: ", function.child[len(function.data)].left)
    # params = parse_params(tokens)
    # print("Params child is: ", params)    
    # function.createChildren(len(params))
    # ----------------------------------------------------------------------  
    
    tok = next(tokens)

    # print("Token is:", tok)

    if(tok.type != "Closeparenthesis"):
        raise RuntimeError(f'Parse_function error, supposed to be Closeparenthesis sign!')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok

    tok = next(tokens)
    if(tok.type != "Openbrace"):
        raise RuntimeError(f'Parse_function error, supposed to be Openbrace sign!')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok
    statement = parse_statement(tokens)

    function.createChildren(1)
    function.child[len(function.data)-1].left = statement



    tok = next(tokens)

    
    if(tok.type != "Closebrace"):
        raise RuntimeError(f'Parse_function error, supposed to be Closebrace sign!')

    function.createChildren(1)
    function.child[len(function.data)-1].left = tok

    function.setTokensForTreePart()
    return function


def parse(tokens):
    # print("Parsing program!")
    program = Tree()
    function = parse_function(tokens)
    program.createChildren(1)
    program.child[0].left = function
    program.setTokensForTreePart()
    return program




#CODE GENERATION SECTION

#Function clear from nodes makes it easier to work with tokens only and after it we can don't care about subtrees

def clear_from_nodes(tree, data, isSubTree):

    if(isSubTree == 0):
        ASTStartData = tree.child[0].left.data
    if(isSubTree == 1):
        ASTStartData = tree

    for token in ASTStartData:

        if(type(token) == type(Token('','','',''))):
            data.append(token)
    
        else:
            clear_from_nodes(token.data, data, 1)

    return data


def generate_expression(data, i):

    generated_asm = ""

    i = i

    while(data[i].type != "Semicolon"):

        if(data[i].type == "return"):
            i += 1
            if(data[i].type == "Integerliteral"):
                generated_asm += "movl $" + str(data[i].value) + ", %eax \n"
                generated_asm += "ret \n"

        i += 1

    return generated_asm



# def generate_params(data, i):

#     generated_asm = "params: ("

#     i = i 

#     while(data[i].type != "Closeparenthesis"):
#         generated_asm += data[i].value + " "
#         i += 1

#     generated_asm += ")\n"

#     return generated_asm



def generate(tree):

    generated_asm = ""

    clear_tokens = []

    clear_from_nodes(tree, clear_tokens, 0)


    # print("Clear tokens: ", clear_tokens)

    i = 0
    func_name = ""

    while(i != len(clear_tokens)):
        # print(clear_tokens[i])
        # print(i)
        if(clear_tokens[i].type == 'int'):
            # print(clear_tokens[i])
            i += 1
            if(clear_tokens[i].type == 'Identifier'):
                func_name = clear_tokens[i].value
                i += 1
                # print(clear_tokens[i])
                if(clear_tokens[i].type == 'Openparenthesis'):
                    i += 1 
                    # print(clear_tokens[i])
                    if(clear_tokens[i].type == 'Closeparenthesis'):
                        i += 1
                        # print(clear_tokens[i])
                
                        if(clear_tokens[i].type == 'Openbrace'):
                            generated_asm += ".globl " + func_name + " \n"
                            generated_asm += func_name + ":\n"
                            func_name = ""

                            i += 1

                        while(clear_tokens[i].type != "Closebrace"):
                            
                            generated_asm += generate_expression(clear_tokens, i)

                            i += 1
        i+= 1


    print("Generated asm:\n", generated_asm)
    return generated_asm


inputFile = "out_2.c"  #sys.argv[1]

outputFile = os.path.splitext("out_2.c")[0] + ".s"


# AST itself is just an empty node for better understanding for author :)
# So to access our Tokens we need to look at !--> first child object data<--!

with open(inputFile, 'r') as infile, open(outputFile, 'w') as outfile:
    contents = infile.read()
    if(contents[-1] != "}"):
        raise(RuntimeError("Parse function error, supposed to be }"))   # Because of 
    AST = parse(lex(contents)) #parsedContents
    result = generate(AST)

    outfile.write(result)



# Use 'main' instead of '_main' if not on OS X
#assembly_format = """
#    .globl _main
#_main:
#    movl    ${}, %eax
#    ret
#"""
#source_file = sys.argv[1]
#assembly_file = os.path.splitext(source_file)[0] + ".s"

#with open(source_file, 'r') as infile, open(assembly_file, 'w') as outfile:
#    source = infile.read().strip()
#    match = re.match(source_re, source)

    # extract the named "ret" group, containing the return value
#    retval = match.group('ret')
#    outfile.write(assembly_format.format(retval))


# <<OLD>>    for i in range(0, (len(tree)//4) + 1):         #Calculation for right amount of nodes in AST, it found token if <<OLD>>
