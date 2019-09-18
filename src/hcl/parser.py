from os.path import abspath, dirname, exists, join
import sys

from .lexer import Lexer
from ply import lex, yacc

import inspect

DEBUG = False

# When using something like pyinstaller, the __file__ attribute isn't actually
# set correctly, so the parse file isn't able to be saved anywhere sensible.
# In these cases, just use a temporary directory, it doesn't take too long to
# generate the tables anyways...

if exists(dirname(__file__)):
    pickle_file = abspath(join(dirname(__file__), 'parsetab.dat'))
else:
    import tempfile

    fobj = tempfile.NamedTemporaryFile()
    pickle_file = fobj.name


if sys.version_info[0] < 3:

    def iteritems(d):
        return iter(d.iteritems())


else:

    def iteritems(d):
        return iter(d.items())


class HclParser(object):

    #
    # Tokens
    #

    tokens = (
        'BOOL',
        'FLOAT',
        'NUMBER',
        'COMMA',
        'COMMAEND',
        'IDENTIFIER',
        'EQUAL',
        'STRING',
        'ADD',
        'MINUS',
        'MULTIPLY',
        'DIVIDE',
        'LEFTBRACE',
        'RIGHTBRACE',
        'LEFTBRACKET',
        'RIGHTBRACKET',
        'PERIOD',
        'EPLUS',
        'EMINUS',
        'LEFTPAREN',
        'RIGHTPAREN',
        'QMARK',
        'COLON',
        'ASTERISK_PERIOD',
        'GT',
        'LT',
        'EQ',
        'NE',
        'LE',
        'GE',
        'AND',
        'OR',
        'NOT',
        'EQGT'
    )

    #
    # Yacc parser section
    #
    def objectlist_flat(self, lt, replace):
        '''
            Similar to the dict constructor, but handles dups
            
            HCL is unclear on what one should do when duplicate keys are
            encountered. These comments aren't clear either:
            
            from decoder.go: if we're at the root or we're directly within
                             a list, decode into dicts, otherwise lists
                
            from object.go: there's a flattened list structure
        '''
        d = {}

        for k, v in lt:
            if k in d.keys() and not replace:
                if type(d[k]) is list:
                    d[k].append(v)
                else:
                    d[k] = [d[k], v]
            else:
                if isinstance(v, dict):
                    dd = d.setdefault(k, {})
                    for kk, vv in iteritems(v):
                        if type(dd) == list:
                            dd.append({kk: vv})
                        elif kk in dd.keys():
                            if hasattr(vv, 'items'):
                                for k2, v2 in iteritems(vv):
                                    dd[kk][k2] = v2
                            else:
                                d[k] = [dd, {kk: vv}]
                        else:
                            dd[kk] = vv
                else:
                    d[k] = v

        return d

    def p_top(self, p):
        "top : objectlist"
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[1], True)

    def p_objectlist_0(self, p):
        "objectlist : objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1]]

    def p_objectlist_1(self, p):
        "objectlist : objectlist objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[2]]

    def p_objectlist_2(self, p):
        "objectlist : objectlist COMMA objectitem"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[3]]

    def p_object_0(self, p):
        "object : LEFTBRACE objectlist RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[2], False)

    def p_object_1(self, p):
        "object : LEFTBRACE objectlist COMMA RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = self.objectlist_flat(p[2], False)

    def p_object_2(self, p):
        "object : LEFTBRACE RIGHTBRACE"
        if DEBUG:
            self.print_p(p)
        p[0] = {}

    def p_objectkey_0(self, p):
        '''
        objectkey : IDENTIFIER
                  | STRING
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_objectkey_1(self, p):
        '''
        objectkey : NOT objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + self.flatten(p[2])

    def p_objectkey_2(self, p):
        '''
        objectkey : objectkey MULTIPLY IDENTIFIER
                  | objectkey ADD objectkey
                  | objectkey MINUS objectkey
                  | objectkey MULTIPLY objectkey
                  | objectkey DIVIDE objectkey
                  | objectkey ADD function
                  | objectkey MINUS function
                  | objectkey MULTIPLY function
                  | objectkey DIVIDE function
                  | IDENTIFIER ADD number
                  | IDENTIFIER ADD IDENTIFIER
                  | IDENTIFIER MINUS number
                  | IDENTIFIER MULTIPLY number
                  | IDENTIFIER MULTIPLY IDENTIFIER
                  | IDENTIFIER DIVIDE number
                  | number ADD IDENTIFIER
                  | number MINUS IDENTIFIER
                  | number MULTIPLY IDENTIFIER
                  | number DIVIDE IDENTIFIER
                  | function ADD function
                  | function MINUS function
                  | function MULTIPLY function
                  | function DIVIDE function
                  | function MULTIPLY IDENTIFIER
                  | function ADD number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1]) + " " + str(p[2]) + " " + self.flatten(p[3])

    def p_objectkey_3(self, p):
        '''
        objectkey : objectkey LEFTBRACKET listitem RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + str(p[3]) + p[4]

    def p_forexp_0(self, p):
        '''
        forexp : LEFTBRACKET objectkey objectkey objectkey objectkey COLON forexp RIGHTBRACKET
                       | LEFTBRACKET objectkey listitems objectkey objectkey COLON forexp RIGHTBRACKET
                       | LEFTBRACKET objectkey objectkey objectkey function COLON function RIGHTBRACKET
                       | LEFTBRACKET objectkey objectkey objectkey ternary COLON object RIGHTBRACKET
                       | LEFTBRACKET objectkey objectkey objectkey objectkey COLON objectkey RIGHTBRACKET
                       | LEFTBRACKET objectkey objectkey objectkey objectkey COLON function RIGHTBRACKET
                       | LEFTBRACKET objectkey objectkey objectkey objectkey COLON object RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + self.flatten(p[2]) + " " + self.flatten(p[3]) + " " + self.flatten(p[4]) + " " + self.flatten(p[5]) + p[6] + self.flatten(p[7]) + p[8]

    def p_forexp_1(self, p):
        '''
        forexp : LEFTBRACE objectkey objectkey objectkey objectkey COLON objectkey EQGT objectkey RIGHTBRACE
                       | LEFTBRACE objectkey objectkey objectkey objectkey COLON objectkey EQGT function RIGHTBRACE
                       | LEFTBRACKET objectkey objectkey objectkey objectkey COLON objectkey objectkey booleanexp RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + self.flatten(p[2]) + " " + self.flatten(p[3]) + " " + self.flatten(p[4]) + " " + self.flatten(p[5]) + p[6] + self.flatten(p[7]) + self.flatten(p[8]) + self.flatten(p[9]) + p[10]

    def p_objectbrackets_0(self, p):
        '''
        objectbrackets : IDENTIFIER LEFTBRACKET objectbrackets RIGHTBRACKET
                       | IDENTIFIER LEFTBRACKET objectkey RIGHTBRACKET
                       | IDENTIFIER LEFTBRACKET NUMBER RIGHTBRACKET
                       | IDENTIFIER LEFTBRACKET function RIGHTBRACKET
                       | listitem LEFTBRACKET objectkey RIGHTBRACKET
                       | listitem LEFTBRACKET number RIGHTBRACKET
                       | function LEFTBRACKET objectkey RIGHTBRACKET
                       | function LEFTBRACKET number RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1]) + p[2] + self.flatten(p[3]) + p[4]

    def p_objectbrackets_1(self, p):
        '''
        objectbrackets : IDENTIFIER LEFTBRACKET objectkey RIGHTBRACKET PERIOD IDENTIFIER
                       | IDENTIFIER LEFTBRACKET NUMBER RIGHTBRACKET PERIOD IDENTIFIER
                       | IDENTIFIER LEFTBRACKET MULTIPLY RIGHTBRACKET PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + str(p[3]) + p[4] + p[5] + p[6]

    def p_objectitem_0(self, p):
        '''
        objectitem : objectkey EQUAL number
                   | objectkey EQUAL BOOL
                   | objectkey EQUAL STRING
                   | objectkey EQUAL IDENTIFIER
                   | objectkey EQUAL object
                   | objectkey EQUAL objectkey
                   | objectkey EQUAL list
                   | objectkey EQUAL objectbrackets
                   | objectkey EQUAL listitem
                   | objectkey EQUAL function
                   | objectkey EQUAL booleanexp
                   | objectkey EQUAL ternary
                   | objectkey EQUAL forexp
                   | objectkey COLON number
                   | objectkey COLON BOOL
                   | objectkey COLON STRING
                   | objectkey COLON IDENTIFIER
                   | objectkey COLON object
                   | objectkey COLON objectkey
                   | objectkey COLON list
                   | objectkey COLON objectbrackets
                   | objectkey COLON booleanexp
                   | objectkey COLON ternary
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], p[3])

    def p_objectitem_1(self, p):
        "objectitem : block"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_ternary_0(self, p):
        '''
        ternary : objectkey QMARK ternary COLON ternary
                | objectkey QMARK objectkey COLON ternary
                | objectkey QMARK number COLON ternary
                | objectkey QMARK BOOL COLON ternary
                | objectkey QMARK function COLON ternary
                | objectkey QMARK ternary COLON number
                | objectkey QMARK ternary COLON objectkey
                | objectkey QMARK ternary COLON booleanexp
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1]) + p[2] + self.flatten(p[3]) + p[4] + self.flatten(p[5])

    def p_ternary_1(self, p):
        '''
        ternary : booleanexp QMARK objectkey COLON objectkey
                | objectkey QMARK objectbrackets COLON objectkey
                | objectkey QMARK objectbrackets COLON objectbrackets
                | objectkey QMARK objectkey COLON objectkey
                | objectkey QMARK listitem COLON listitem
                | objectkey QMARK objectkey COLON number
                | objectkey QMARK objectkey COLON BOOL
                | objectkey QMARK objectkey COLON function
                | objectkey QMARK objectkey COLON booleanexp
                | objectkey QMARK number COLON objectkey
                | objectkey QMARK BOOL COLON objectkey
                | objectkey QMARK function COLON function
                | objectkey QMARK function COLON objectkey
                | objectkey QMARK function COLON number
                | objectkey QMARK number COLON number
                | objectkey QMARK number COLON BOOL
                | objectkey QMARK number COLON function
                | objectkey QMARK BOOL COLON number
                | objectkey QMARK BOOL COLON function
                | objectkey QMARK BOOL COLON BOOL
                | objectkey QMARK BOOL COLON booleanexp
                | objectkey QMARK booleanexp COLON objectkey
                | objectkey QMARK booleanexp COLON number
                | NUMBER QMARK function COLON listitem
                | NUMBER QMARK function COLON objectkey
                | NUMBER QMARK objectkey COLON objectkey
                | NUMBER QMARK objectkey COLON NUMBER
                | NUMBER QMARK NUMBER COLON NUMBER
                | BOOL QMARK BOOL COLON BOOL
                | BOOL QMARK objectkey COLON objectkey
                | booleanexp QMARK listitem COLON listitem
                | booleanexp QMARK listitem COLON function
                | booleanexp QMARK objectkey COLON number
                | booleanexp QMARK objectkey COLON BOOL
                | booleanexp QMARK objectkey COLON function
                | booleanexp QMARK function COLON objectkey
                | booleanexp QMARK function COLON number
                | booleanexp QMARK function COLON BOOL
                | booleanexp QMARK number COLON objectkey
                | booleanexp QMARK number COLON number
                | booleanexp QMARK number COLON BOOL
                | booleanexp QMARK number COLON function
                | booleanexp QMARK BOOL COLON objectkey
                | booleanexp QMARK BOOL COLON number
                | booleanexp QMARK BOOL COLON function
                | booleanexp QMARK BOOL COLON BOOL
                | booleanexp QMARK ternary COLON objectkey

                | function QMARK listitem COLON listitem
                | function QMARK objectkey COLON number
                | function QMARK objectkey COLON BOOL
                | function QMARK objectkey COLON function
                | function QMARK function COLON objectkey
                | function QMARK function COLON number
                | function QMARK function COLON BOOL
                | function QMARK number COLON objectkey
                | function QMARK number COLON number
                | function QMARK number COLON BOOL
                | function QMARK number COLON function
                | function QMARK BOOL COLON objectkey
                | function QMARK BOOL COLON number
                | function QMARK BOOL COLON function
                | function QMARK BOOL COLON BOOL
                | function QMARK ternary COLON objectkey
                | list QMARK list COLON objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1]) + p[2] + self.flatten(p[3]) + p[4] + self.flatten(p[5])

    def p_operator_0(self, p):
        '''
        operator : EQ
                 | NE
                 | LT
                 | GT
                 | LE
                 | GE
                 | AND
                 | OR
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_booleanexp_0(self, p):
        '''
        booleanexp : LEFTPAREN booleanexp RIGHTPAREN
                   | booleanexp operator booleanexp
                   | booleanexp operator objectkey
                   | booleanexp operator number
                   | objectkey operator booleanexp
                   | objectkey operator function
                   | objectkey operator objectbrackets
                   | objectkey operator objectkey
                   | objectkey operator number
                   | function operator number
                   | function operator STRING
                   | function operator function
                   | function operator objectkey
                   | number operator objectkey
                   | BOOL operator objectkey
                   | objectkey operator BOOL
                   | objectkey operator ternary
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1]) + p[2] + self.flatten(p[3])

    def p_block_0(self, p):
        "block : objectkey object"
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], p[2])

    def p_block_1(self, p):
        "block : objectkey block"
        if DEBUG:
            self.print_p(p)
        p[0] = (p[1], {p[2][0]: p[2][1]})

    def p_list_0(self, p):
        '''
        list : LEFTBRACKET listitems RIGHTBRACKET
             | LEFTBRACKET listitems COMMA RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[2]

    def p_list_1(self, p):
        '''
        list : LEFTBRACKET RIGHTBRACKET
             | LEFTPAREN RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = []

    def p_list_2(self, p):
        '''
        list : LEFTPAREN LEFTBRACKET listitems RIGHTBRACKET PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[3]] + [p[5] + p[6] + p[7]]

    def p_list_of_lists_0(self, p):
        '''
        list_of_lists : list COMMA list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1], p[3]

    def p_list_of_lists_1(self, p):
        '''
        list_of_lists : list_of_lists COMMA list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + (p[3],)

    def p_function_0(self, p):
        '''
        function : IDENTIFIER LEFTPAREN listitems RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list_of_lists RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[4]

    def p_function_1(self, p):
        '''
        function : IDENTIFIER LEFTPAREN listitems COMMA RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list COMMA RIGHTPAREN
                 | IDENTIFIER LEFTPAREN list_of_lists COMMA RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[5]

    def p_function_2(self, p):
        '''
        function : IDENTIFIER LEFTPAREN list PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = p[1] + p[2] + self.flatten(p[3]) + p[4] + p[5] + p[6] + p[7]

    def p_function_3(self, p):
        '''
        function : IDENTIFIER LEFTPAREN LEFTBRACKET list_of_lists RIGHTBRACKET PERIOD PERIOD PERIOD RIGHTPAREN
        '''
        if DEBUG:
            self.print_p(p)

        p[0] = (
            p[1] + p[2] + p[3] + self.flatten(p[4]) + p[5] + p[6] + p[7] + p[8] + p[9]
        )

    def flatten(self, value):
        returnValue = ""
        if type(value) is dict:
            returnValue = (
                "{"
                + ",".join(key + ":" + self.flatten(value[key]) for key in value)
                + "}"
            )
        elif type(value) is list:
            returnValue = ",".join(self.flatten(v) for v in value) if value else "[]"
        elif type(value) is tuple:
            returnValue = " ".join(self.flatten(v) for v in value)
        elif type(value) is not str:
            returnValue = str(value)
        else:
            returnValue = value
        return returnValue

    def p_listitems_0(self, p):
        '''
        listitems : listitem
                  | function
                  | forexp
                  | object COMMA
                  | objectkey COMMA
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1]]

    def p_listitems_1(self, p):
        '''
        listitems : listitems COMMA listitem
                  | listitems COMMA function
                  | listitems COMMA ternary
                  | listitems COMMA objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + [p[3]]

    def p_listitems_2(self, p):
        '''
        listitems : object COMMA object
                  | object COMMA objectkey
                  | objectkey COMMA objectkey
                  | objectkey COMMA object
                  | objectkey COMMA list
                  | objectkey COMMA ternary
                  | objectkey COMMA number
                  | objectkey COMMA function
                  | objectkey COMMA BOOL
                  | list COMMA objectkey
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1], p[3]]

    def p_listitems_3(self, p):
        '''
        listitems : objectkey COMMA IDENTIFIER ASTERISK_PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = [p[1], p[3] + p[4] + p[5]]

    def p_listitems_4(self, p):
        '''
        listitems : objectkey list
        '''
        if DEBUG:
            self.print_p(p)
        p[2].insert(0, p[1])
        p[0] = p[2]

    def p_listitem_0(self, p):
        '''
        listitem : number
                 | BOOL
                 | object
                 | objectkey
                 | objectbrackets
                 | ternary
                 | booleanexp
                 | list
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = self.flatten(p[1])

    def p_listitem_1(self, p):
        '''
        listitem : IDENTIFIER ASTERISK_PERIOD IDENTIFIER
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[2] + p[3]

    def p_listitem_2(self, p):
        '''
        listitem : LEFTBRACKET listitem RIGHTBRACKET
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + self.flatten(p[2]) + p[3]

    def p_number_0(self, p):
        "number : int"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_number_1(self, p):
        "number : float"
        if DEBUG:
            self.print_p(p)
        p[0] = float(p[1])

    def p_number_2(self, p):
        "number : int exp"
        if DEBUG:
            self.print_p(p)
        p[0] = float("{0}{1}".format(p[1], p[2]))

    def p_number_3(self, p):
        "number : float exp"
        if DEBUG:
            self.print_p(p)
        p[0] = float("{0}{1}".format(p[1], p[2]))

    def p_number_4(self, p):
        '''
        number : number ADD number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] + p[3]

    def p_number_5(self, p):
        '''
        number : number MINUS number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] - p[3]

    def p_number_6(self, p):
        '''
        number : number MULTIPLY number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] * p[3]

    def p_number_7(self, p):
        '''
        number : number DIVIDE number
        '''
        if DEBUG:
            self.print_p(p)
        p[0] = p[1] / p[3]

    def p_int_0(self, p):
        "int : MINUS int"
        if DEBUG:
            self.print_p(p)
        p[0] = -p[2]

    def p_int_1(self, p):
        "int : NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = p[1]

    def p_float_0(self, p):
        "float : MINUS float"
        p[0] = p[2] * -1

    def p_float_1(self, p):
        "float : FLOAT"
        p[0] = p[1]

    def p_exp_0(self, p):
        "exp : EPLUS NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = "e{0}".format(p[2])

    def p_exp_1(self, p):
        "exp : EMINUS NUMBER"
        if DEBUG:
            self.print_p(p)
        p[0] = "e-{0}".format(p[2])

    # useful for debugging the parser
    def print_p(self, p):
        if DEBUG:
            name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
            print(
                '%20s: %s' % (name, ' | '.join([str(p[i]) for i in range(0, len(p))]))
            )

    def p_error(self, p):
        # Derived from https://groups.google.com/forum/#!topic/ply-hack/spqwuM1Q6gM

        # Ugly hack since Ply doesn't provide any useful error information
        try:
            frame = inspect.currentframe()
            cvars = frame.f_back.f_locals
            expected = "; expected %s" % (
                ', '.join(cvars['actions'][cvars['state']].keys())
            )
        except:
            expected = ""

        if p is not None:
            msg = "Line %d, column %d: unexpected %s%s" % (
                p.lineno,
                p.lexpos,
                p.type,
                expected,
            )
        else:
            msg = "Unexpected end of file%s" % expected

        raise ValueError(msg)

    def __init__(self):
        self.yacc = yacc.yacc(
            module=self, debug=False, optimize=1, picklefile=pickle_file
        )

    def parse(self, s):
        return self.yacc.parse(s, lexer=Lexer())
