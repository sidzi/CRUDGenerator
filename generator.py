import ply.lex as lex

colcnt = []
# List of token names.   This is always required
tokens = (
    'TNAME',
    'CNAME',
    'CVAL',
    'END',
)

tname = r'([t][n][ ][A-Za-z]+)'
tcol = r'([t][c][ ][A-Za-z]+)'
tcolval = r'([t][v][ ][A-Za-z()0-9]+)'
tend = r'([t][e][n][d])'

# table       = tname + ';'

# reserved = {
# 'tn' : 'TNAME',
# 'tc' : 'CNAME',
# }
@lex.TOKEN(tend)
def t_END(t):
    global colcnt
    cnt = 0
    t.value = "\n\t\tself.COLUMNS = \""
    iter = 0
    colcount = (len(colcnt) / 2)
    while iter < colcount:
        t.value += "{" + str(cnt) + "} {"
        cnt += 1
        t.value += str(cnt) + "}"
        if cnt < colcount:
            t.value += " , "
        else:
            pass
        cnt += 1
        iter += 1
    i = 0
    t.value += " \".format("
    while True:

        if i < len(colcnt) - 1:
            t.value += colcnt[i] + ","
        elif i == len(colcnt) - 1:
            t.value += colcnt[i]
        else:
            break
        i += 1
    t.value += ")\n"
    # The Table Creation Queries
    t.value += "\n\t\tself.cursor = self.dbcon.db.cursor()\n"
    t.value += """\n\t\tquery = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\\n(\\n" + self.COLUMNS + "\\n);"\n"""
    t.value += "\t\tself.cursor.execute(query)"
    t.value += """\n\n\tdef __del__(self):\n\t\tself.dbcon.closeConnection()\n"""
    return t


@lex.TOKEN(tname)
def t_TNAME(t):
    t.filename = str(t.value.rsplit(' ')[1])
    t.value = "from connection import DatabaseConnection\n\nclass " + t.filename + ":\n\tdef __init__(self):\n\t\tself.dbcon = DatabaseConnection()\n\n\t\tself.NAME = \"" + t.filename + "\"\n"
    return t


@lex.TOKEN(tcol)
def t_CNAME(t):
    global colcnt
    cnameval = t.value.rsplit(' ')[1]
    cname = "self.COLUMN_" + str(cnameval).swapcase()
    colcnt.append(cname)
    t.value = "\n\t\t" + cname + " = \"%s\" \n" % cnameval + "\t\t" + cname
    colcnt.append(cname + "_TYPE")
    return t


@lex.TOKEN(tcolval)
def t_CVAL(t):
    cval = t.value.rsplit(' ')[1]
    t.value = "_TYPE = \"%s\" \n\t\t" % cval
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

# Test Case
# fi = open("CRUDinput")
# data = str(fi.read())

data = '''tn users\n
tc uname\ntv varchar(250)\ntc age\ntv int\ntend'''

# Give the lexer some input
lexer.input(data)

filename = None

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    if tok.type == "TNAME":
        filename = "CRUD_" + str(tok.filename) + ".py"
        f = open(filename, 'w')
        f.close()
    f = open(filename, 'a')
    f.write(str(tok.value))
    f.close()
