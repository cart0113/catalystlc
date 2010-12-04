# For code coloring 
import cgi, string, sys, cStringIO
import keyword, token, tokenize
import inspect

from domdom import xhtml,css

"""
::: CODE PARSER :::
"""
class Parser:
    # taken from http://code.activestate.com/recipes/52298/
    _KEYWORD = token.NT_OFFSET + 1
    _TEXT    = token.NT_OFFSET + 2
    _colors = {
        token.NUMBER:       '#800000',
        token.OP:           '#000000',
        token.STRING:       '#1A6F1A',
        tokenize.COMMENT:   '#1A6F1A',   #'#AA2020',
        token.NAME:         '#000000',
        token.ERRORTOKEN:   '#FF8080',
        _KEYWORD:           '#0000FF',
        _TEXT:              '#000000',
    }
    """ Send colored python source."""

    def __init__(self, raw):
        """ Store the source text. """
        self.out_lines = []
        for line in string.strip(string.expandtabs(raw)).split('\n'):
            self.raw = line
            self.out = ""
            self.out_lines += [self.format(None, None)]

    def format(self, formatter, form):
        """ Parse and send the colored source."""
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = string.find(self.raw, '\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        # parse the source and write it
        self.pos = 0
        text = cStringIO.StringIO(self.raw)
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            #self.out += "<h3>ERROR: %s</h3>%s\n" % (msg, self.raw[self.lines[line]:])
        
        #self.out_lines.append(self.out)
        #self.out_lines.append("")
        #self.out_lines.append("")
        #return self.out_lines
        
        return self.out

    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler."""
        if 0:
            print "type", toktype, token.tok_name[toktype], "text", toktext,
            print "start", srow,scol, "end", erow,ecol, "<br>"

        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        # handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            #self.out_lines.append(self.out.replace('\n', '<br/>'))
            #self.out = ""
            return

        # send the original whitespace, if needed
        if newpos > oldpos:
            self.out += self.raw[oldpos:newpos].replace(' ', '&nbsp;')
        
        # skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return
        
        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = Parser._KEYWORD
        color = Parser._colors.get(toktype, Parser._colors[Parser._TEXT])

        style = ''
        if toktype == token.ERRORTOKEN:
            #style = ' style="border: solid 1.5pt #FF0000;"'
            return 

        # send text
        self.out += '<font color="%s"%s>' % (color, style)
        self.out += cgi.escape(toktext)
        self.out += '</font>'
        
class div_pycode(xhtml.div):
    
    @staticmethod
    def css():
        css.prop.font_size        = css.pt(8)
        css.prop.font_weight      = css.values.font_weights.x500
        css.prop.font_family      = css.values.font_families.courier_new
        css.prop.padding          = css.pixel(10)
        css.margin_top            = css.pixel(15)
        css.margin_bottom         = css.pixel(15)
        css.prop.background_color = css.rgb(245,245,245)
        css.prop.border           = 'solid 3px rgb(200,200,200)'
    
    def __init__(self, parent, code, num_start = 0, header = True, tab_size = 4):
        xhtml.div.__init__(self, parent = parent)
        if isinstance(code, str):
            lines = Parser(raw = open(code).read()).out_lines
        else:
            source_lines = list(inspect.getsourcelines(code))[0]
            if header is False:
                source_lines.pop(0)
                for i,line in enumerate(source_lines):
                    source_lines[i] = line[tab_size:]
            lines = Parser(raw = ''.join(source_lines)).out_lines
                
        table = xhtml.table(parent = self)
        for i,line in enumerate(lines):        
            sec = tr_pycode_section(parent = table)
            if i%2 == 1:
                sec.style.background_color = css.rgb(240,240,240)
            td_pycode_number(parent = sec, text = str(i+num_start))
            td_pycode_line(parent = sec, text = line)
                    
class tr_pycode_section(xhtml.tr):
    pass
                
class td_pycode_number(xhtml.td):
    
    @staticmethod
    def css():
        css.prop.width        = css.pixel(20)
        css.prop.padding_left = css.pixel(2)

class td_pycode_line(xhtml.td):    
    @staticmethod
    def css():
        css.prop.padding_left = css.pixel(5)
        
      