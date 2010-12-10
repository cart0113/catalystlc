import inspect, os

css_class = False

def get_css_name(cls):
    
    source_file = inspect.getsourcefile(cls)        

    if source_file[-3:].lower() == '.py':
        cls_name = source_file.replace(".py", "").split(os.sep)
        cls_name = cls_name[-1] + "_"
    else:
        cls_name = ""
        
    return cls_name + cls.__name__
    
class property:
    
    def __str__(self):
        return self.name
            
class prop_metaclass(type):
    
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)        
        for key,value in dict.iteritems():
            if isinstance(value, property):
                value.name = key
    
    def start_css(cls, tag, css_class = None):
        cls._css = tag
        if tag != css_class.split("_")[-1]:
            cls._css += "." + css_class
        cls._css_selector = cls._css
        cls._css += "{\n"

    def start_pseudo(cls, name):
        cls._css += "}\n\n"
        cls._css += cls._css_selector + ":" + name + "{\n"
                
    def __setattr__(cls, attr, value):        
        if attr in ['_css', '_css_selector']:
            type.__setattr__(cls, attr, value)        
        elif attr == 'pseudo':
            cls.start_pseudo(name = value)
        elif getattr(cls, '_css', None):
            type.__setattr__(cls, '_css', cls._css + "\t" + python_2_css.__dict__[attr] + ":" + " "*(20-len(attr)) + str(value) + ";\n")
        else:
            type.__setattr__(cls, attr, value)
        
    def get_css(cls):
        cls._css += "}\n"
        return cls._css
        
class prop:
    
    __metaclass__ = prop_metaclass
    
    azimuth =                        property()
    background =                     property()
    background_attachment =          property()
    background_color =               property()
    background_image =               property()
    background_position =            property()
    background_repeat =              property()
    border =                         property()
    border_bottom =                  property()
    border_bottom_color =            property()
    border_bottom_style =            property()
    border_bottom_width =            property()
    border_collapse =                property()
    border_color =                   property()
    border_left =                    property()
    border_left_color =              property()
    border_left_style =              property()
    border_left_width =              property()
    border_right =                   property()
    border_right_color =             property()
    border_right_style =             property()
    border_right_width =             property()
    border_spacing =                 property()
    border_style =                   property()
    border_top =                     property()
    border_top_color =               property()
    border_top_style =               property()
    border_top_width =               property()
    border_width =                   property()
    bottom =                         property()
    caption_side =                   property()
    clear =                          property()
    clip =                           property()
    color =                          property()
    content =                        property()
    counter_increment =              property()
    counter_reset =                  property()
    css_float =                      property()
    css_text =                       property()
    cue =                            property()
    cue_after =                      property()
    on_before =                      property()
    cursor =                         property()
    direction =                      property()
    display =                        property()
    elevation =                      property()
    empty_cells =                    property()
    float =                          property()
    font_family =                    property()
    font_size =                      property()
    font_size_adjust =               property()
    font_stretch =                   property()
    font_style =                     property()
    font_variant =                   property()
    font_weight =                    property()
    height =                         property()
    left =                           property()
    length =                         property()
    letter_spacing =                 property()
    line_height =                    property()
    list_style =                     property()
    list_style_image =               property()
    list_style_position =            property()
    list_style_type =                property()
    margin =                         property()
    margin_bottom =                  property()
    margin_left =                    property()
    margin_right =                   property()
    margin_top =                     property()
    marker_offset =                  property()
    marks =                          property()
    max_height =                     property()
    max_width =                      property()
    min_height =                     property()
    min_width =                      property()
    opacity =                        property()
    orphans =                        property()
    outline =                        property()
    outline_color =                  property()
    outline_style =                  property()
    outline_width =                  property()
    overflow =                       property()
    overflow_x =                     property()
    overflow_y =                     property()
    padding =                        property()
    padding_bottom =                 property()
    padding_left =                   property()
    padding_right =                  property()
    padding_top =                    property()
    page =                           property()
    page_break_after =               property()
    page_break_before =              property()
    page_break_inside =              property()
    parent_rule =                    property()
    pause =                          property()
    pause_after =                    property()
    pause_before =                   property()
    pitch =                          property()
    pitch_range =                    property()
    play_during =                    property()
    position =                       property()
    pseudo =                         property()
    quotes =                         property()
    richness =                       property()
    right =                          property()
    size =                           property()
    speak =                          property()
    speak_header =                   property()
    speak_numeral =                  property()
    speak_punctuation =              property()
    speech_rate =                    property()
    stress =                         property()
    table_layout =                   property()
    text_align =                     property()
    text_decoration =                property()
    text_indent =                    property()
    text_shadow =                    property()
    text_transform =                 property()
    top =                            property()
    unicode_bidi =                   property()
    vertical_align =                 property()
    visibility =                     property()
    voice_family =                   property()
    volume =                         property()
    white_space =                    property()
    widows =                         property()
    width =                          property()
    word_spacing =                   property()
    z_index =                        property()
    
    
    
class python_2_css:
    azimuth =                        'azimuth'
    background =                     'background'
    background_attachment =          'background-attachment'
    background_color =               'background-color'
    background_image =               'background-image'
    background_position =            'background-position'
    background_repeat =              'background-repeat'
    border =                         'border'
    border_bottom =                  'border-bottom'
    border_bottom_color =            'border-bottom-color'
    border_bottom_style =            'border-bottom-style'
    border_bottom_width =            'border-bottom-width'
    border_collapse =                'border-collapse'
    border_color =                   'border-color'
    border_left =                    'border-left'
    border_left_color =              'border-left-color'
    border_left_style =              'border-left-style'
    border_left_width =              'border-left-width'
    border_right =                   'border-right'
    border_right_color =             'border-right-color'
    border_right_style =             'border-right-style'
    border_right_width =             'border-right-width'
    border_spacing =                 'border-spacing'
    border_style =                   'border-style'
    border_top =                     'border-top'
    border_top_color =               'border-top-color'
    border_top_style =               'border-top-style'
    border_top_width =               'border-top-width'
    border_width =                   'border-width'
    bottom =                         'bottom'
    caption_side =                   'caption-side'
    clear =                          'clear'
    clip =                           'clip'
    color =                          'color'
    content =                        'content'
    counter_increment =              'counter-increment'
    counter_reset =                  'counter-reset'
    css_float =                      'css-float'
    css_text =                       'css-text'
    cue =                            'cue'
    cue_after =                      'cue-after'
    on_before =                      'on-before'
    cursor =                         'cursor'
    direction =                      'direction'
    display =                        'display'
    elevation =                      'elevation'
    empty_cells =                    'empty-cells'
    float =                          'float'
    font =                           'font'
    font_family =                    'font-family'
    font_size =                      'font-size'
    font_size_adjust =               'font-size-adjust'
    font_stretch =                   'font-stretch'
    font_style =                     'font-style'
    font_variant =                   'font-variant'
    font_weight =                    'font-weight'
    height =                         'height'
    left =                           'left'
    length =                         'length'
    letter_spacing =                 'letter-spacing'
    line_height =                    'line-height'
    list_style =                     'list-style'
    list_style_image =               'list-style-image'
    list_style_position =            'list-style-position'
    list_style_type =                'list-style-type'
    margin =                         'margin'
    margin_bottom =                  'margin-bottom'
    margin_left =                    'margin-left'
    margin_right =                   'margin-right'
    margin_top =                     'margin-top'
    marker_offset =                  'marker-offset'
    marks =                          'marks'
    max_height =                     'max-height'
    max_width =                      'max-width'
    min_height =                     'min-height'
    min_width =                      'min-width'
    opacity =                        'opacity'
    orphans =                        'orphans'
    outline =                        'outline'
    outline_color =                  'outline-color'
    outline_style =                  'outline-style'
    outline_width =                  'outline-width'
    overflow =                       'overflow'
    overflow_x =                     'overflow-x'
    overflow_y =                     'overflow-y'
    padding =                        'padding'
    padding_bottom =                 'padding-bottom'
    padding_left =                   'padding-left'
    padding_right =                  'padding-right'
    padding_top =                    'padding-top'
    page =                           'page'
    page_break_after =               'page-break-after'
    page_break_before =              'page-break-before'
    page_break_inside =              'page-break-inside'
    parent_rule =                    'parent-rule'
    pause =                          'pause'
    pause_after =                    'pause-after'
    pause_before =                   'pause-before'
    pitch =                          'pitch'
    pitch_range =                    'pitch-range'
    play_during =                    'play-during'
    position =                       'position'
    quotes =                         'quotes'
    richness =                       'richness'
    right =                          'right'
    size =                           'size'
    speak =                          'speak'
    speak_header =                   'speak-header'
    speak_numeral =                  'speak-numeral'
    speak_punctuation =              'speak-punctuation'
    speech_rate =                    'speech-rate'
    stress =                         'stress'
    table_layout =                   'table-layout'
    text_align =                     'text-align'
    text_decoration =                'text-decoration'
    text_indent =                    'text-indent'
    text_shadow =                    'text-shadow'
    text_transform =                 'text-transform'
    top =                            'top'
    unicode_bidi =                   'unicode-bidi'
    vertical_align =                 'vertical-align'
    visibility =                     'visibility'
    voice_family =                   'voice-family'
    volume =                         'volume'
    white_space =                    'white-space'
    widows =                         'widows'
    width =                          'width'
    word_spacing =                   'word-spacing'
    z_index =                        'z-index'
    
class python_2_js:
    azimuth =                        'azimuth'
    background =                     'background'
    background_attachment =          'backgroundAttachment'
    background_color =               'backgroundColor'
    background_image =               'backgroundImage'
    background_position =            'backgroundPosition'
    background_repeat =              'backgroundRepeat'
    border =                         'border'
    border_bottom =                  'borderBottom'
    border_bottom_color =            'borderBottomColor'
    border_bottom_style =            'borderBottomStyle'
    border_bottom_width =            'borderBottomWidth'
    border_collapse =                'borderCollapse'
    border_color =                   'borderColor'
    border_left =                    'borderLeft'
    border_left_color =              'borderLeftColor'
    border_left_style =              'borderLeftStyle'
    border_left_width =              'borderLeftWidth'
    border_right =                   'borderRight'
    border_right_color =             'borderRightColor'
    border_right_style =             'borderRightStyle'
    border_right_width =             'borderRightWidth'
    border_spacing =                 'borderSpacing'
    border_style =                   'borderStyle'
    border_top =                     'borderTop'
    border_top_color =               'borderTopColor'
    border_top_style =               'borderTopStyle'
    border_top_width =               'borderTopWidth'
    border_width =                   'borderWidth'
    bottom =                         'bottom'
    caption_side =                   'captionSide'
    clear =                          'clear'
    clip =                           'clip'
    color =                          'color'
    content =                        'content'
    counter_increment =              'counterIncrement'
    counter_reset =                  'counterReset'
    css_float =                      'cssFloat'
    css_text =                       'cssText'
    cue =                            'cue'
    cue_after =                      'cueAfter'
    on_before =                      'onBefore'
    cursor =                         'cursor'
    direction =                      'direction'
    display =                        'display'
    elevation =                      'elevation'
    empty_cells =                    'emptyCells'
    float =                          'float'
    font =                           'font'
    font_family =                    'fontFamily'
    font_size =                      'fontSize'
    font_size_adjust =               'fontSizeAdjust'
    font_stretch =                   'fontStretch'
    font_style =                     'fontStyle'
    font_variant =                   'fontVariant'
    font_weight =                    'fontWeight'
    height =                         'height'
    left =                           'left'
    length =                         'length'
    letter_spacing =                 'letterSpacing'
    line_height =                    'lineHeight'
    list_style =                     'listStyle'
    list_style_image =               'listStyleImage'
    list_style_position =            'listStylePosition'
    list_style_type =                'listStyleType'
    margin =                         'margin'
    margin_bottom =                  'marginBottom'
    margin_left =                    'marginLeft'
    margin_right =                   'marginRight'
    margin_top =                     'marginTop'
    marker_offset =                  'markerOffset'
    marks =                          'marks'
    max_height =                     'maxHeight'
    max_width =                      'maxWidth'
    min_height =                     'minHeight'
    min_width =                      'minWidth'
    opacity =                        'opacity'
    orphans =                        'orphans'
    outline =                        'outline'
    outline_color =                  'outlineColor'
    outline_style =                  'outlineStyle'
    outline_width =                  'outlineWidth'
    overflow =                       'overflow'
    overflow_x =                     'overflowX'
    overflow_y =                     'overflowY'
    padding =                        'padding'
    padding_bottom =                 'paddingBottom'
    padding_left =                   'paddingLeft'
    padding_right =                  'paddingRight'
    padding_top =                    'paddingTop'
    page =                           'page'
    page_break_after =               'pageBreakAfter'
    page_break_before =              'pageBreakBefore'
    page_break_inside =              'pageBreakInside'
    parent_rule =                    'parentRule'
    pause =                          'pause'
    pause_after =                    'pauseAfter'
    pause_before =                   'pauseBefore'
    pitch =                          'pitch'
    pitch_range =                    'pitchRange'
    play_during =                    'playDuring'
    position =                       'position'
    quotes =                         'quotes'
    richness =                       'richness'
    right =                          'right'
    size =                           'size'
    speak =                          'speak'
    speak_header =                   'speakHeader'
    speak_numeral =                  'speakNumeral'
    speak_punctuation =              'speakPunctuation'
    speech_rate =                    'speechRate'
    stress =                         'stress'
    table_layout =                   'tableLayout'
    text_align =                     'textAlign'
    text_decoration =                'textDecoration'
    text_indent =                    'textIndent'
    text_shadow =                    'textShadow'
    text_transform =                 'textTransform'
    top =                            'top'
    unicode_bidi =                   'unicodeBidi'
    vertical_align =                 'verticalAlign'
    visibility =                     'visibility'
    voice_family =                   'voiceFamily'
    volume =                         'volume'
    white_space =                    'whiteSpace'
    widows =                         'widows'
    width =                          'width'
    word_spacing =                   'wordSpacing'
    z_index =                        'zIndex'

class values:

    class displays:
        none                = 'none'                    #The element will not be displayed
        block               = 'block'                   #The element will be displayed as a block-level element, with a line break before and after the element
        inline              = 'inline'                  #Default. The element will be displayed as an inline element, with no line break before or after the element
        list_item           = 'list-item'               #The element will be displayed as a list
        run_in              = 'run-in'                  #The element will be displayed as block-level or inline element depending on context
        compact             = 'compact'                 #The element will be displayed as block-level or inline element depending on context
        marker              = 'marker'
        table               = 'table'                   #The element will be displayed as a block table (like <table>), with a line break before and after the table
        inline_table        = 'inline-table'            #The element will be displayed as an inline table (like <table>), with no line break before or after the table
        table_row_group     = 'table-row-group'         #The element will be displayed as a group of one or more rows (like <tbody>)
        table_header_group  = 'table-header-group'      #The element will be displayed as a group of one or more rows (like <thead>)
        table_footer_group  = 'table-footer-group'      #The element will be displayed as a group of one or more rows (like <tfoot>)
        table_row           = 'table-row'               #The element will be displayed as a table row (like <tr>)
        table_column_group  = 'table-column-group'      #The element will be displayed as a group of one or more columns (like <colgroup>)
        table_column        = 'table_column'            #The element will be displayed as a column of cells (like <col>)
        table_cell          = 'table_cell'              #The element will be displayed as a table cell (like <td> and <th>)
        table_caption       = 'table_caption'           #The element will be displayed as a table caption (like <caption>)

    class text_aligns:
        left    = 'left'     #Aligns the text to the left.
        right   = 'right'    #Aligns the text to the right
        center  = 'center'   #Centers the text
        justify = 'justify'

    class vertical_aligns:
        baseline       = 'baseline'    #Default. The element is placed on the baseline of the parent element
        sub            = 'sub'         #Aligns the element as it was subscript
        super          = 'super'       #Aligns the element as it was superscript
        top            = 'top'         #The top of the element is aligned with the top of the tallest element on the line
        text_top       = 'text-top'    #The top of the element is aligned with the top of the parent element's font
        middle         = 'middle'      #The element is placed in the middle of the parent element
        bottom         = 'bottom'      #The bottom of the element is aligned with the lowest element on the line
        text_bottom    = 'text-bottom' #The bottom of the element is aligned with the bottom of the parent element's font

    class colors:
        white   = 'white'
        black   = 'black'
        red     = 'red'
        blue    = 'blue'
        green   = 'green'
            
    class floats:
        left    = 'left'
        right   = 'right'
        none    = 'none'
            
    class font_families:
        # from http://www.ampsoft.net/webdesign-l/WindowsMacFonts.html
        arial                           = "Arial, Helvetica, sans-serif"
        arial_black                     = "Arial Black, Gadget, sans-serif"
        comic_sans                      = "Comic Sans MS, cursive"
        courier_new                     = "Courier New, Courier New, Courier, monospace"
        geneva                          = "Geneva, sans-serif"
        georgia                         = "Georgia, serif"
        helvetica                       = "Helvetica, sans-serif"
        impact                          = "Impact, Charcoal, sans-serif"
        lucida_console                  = "Lucida Console, Monaco, monospace"
        lucida_sans_unicode             = "Lucida Sans Unicode, Lucida Grande, sans-serif"
        palation_linotype               = "Palatino Linotype, Book Antiqua, Palatino, serif"
        sans_serif                      = "sans-serif"
        serif                           = "serif"
        symbol                          = "Symbol"
        tahoma                          = "Tahoma, Geneva, sans-serif"
        times_new_roman                 = "Times New Roman, Times, serif"
        trebuchet                       = "Trebuchet MS, Helvetica, sans-serif"
        verdana                         = "Verdana, Geneva, sans-serif"
        
    class font_stretches:
        pass
    
    class font_weights:
        normal  = 'normal'
        bold    = 'bold'
        bolder  = 'bolder'
        lighter = 'lighter'
        x100    = '100'
        x200    = '200'
        x300    = '300'
        x400    = '400'
        x500    = '500'
        x600    = '600'
        x700    = '700'
        x800    = '800'
        x900    = '900'
    
    class font_variants:
        pass
    
    class font_sizes:
        pass
   
    class font_styles:
        normal   = 'normal'
        italic   = 'italic'
        oblique  = 'oblique'
   
    class positions:
        static    = 'static'
        relative  = 'relative'
        absolute  = 'absolute'
        fixed     = 'fixed'

    class pseudos:
        hover        = 'hover'
        active       = 'active'
        link         = 'link '
        visited      = 'visited'
        first_child  = 'first-child'
        lang         = 'lang'
        
        first_letter = 'first-letter'
        first_line   = 'first-line'
        before       = 'before'
        after        = 'after'

class CSS_Number(float):

    def __add__(self, other):
        return self.__class__(float.__add__(self, other))
    
    def __radd__(self, other):
        return self.__class__(float.__radd__(self, other))
    
    def __mul__(self, other):
        return self.__class__(float.__mul__(self, other))

    def __rmul__(self, other):
        return self.__class__(float.__rmul__(self, other))

    def __div__(self, other):
        return self.__class__(float.__div__(self, other))

    def __rdiv__(self, other):
        return self.__class__(float.__rdiv__(self, other))

    def __pow__(self, other):
        return self.__class__(float.__pow__(self, other))

class pixel(CSS_Number):
        
    def __str__(self):
        return float.__str__(self) + 'px'
    
class percent(CSS_Number):

    def __str__(self):
        return float.__str__(self) + '%'
    
class em(CSS_Number):
        
    def __str__(self):
        return float.__str__(self) + 'em'
    
class inch(CSS_Number):

    def __str__(self):
        return float.__str__(self) + 'in'

class cm(CSS_Number):

    def __str__(self):
        return float.__str__(self) + 'cm'
    
class mm(CSS_Number):

    def __str__(self):
        return float.__str__(self) + 'mm'
    
class pt(CSS_Number):

    def __str__(self):
        return float.__str__(self) + 'pt'
    
class rgb(object):
    
    def __init__(self, red, green, blue):
        self.red   = red
        self.green = green
        self.blue  = blue
        
    def __str__(self):
        return 'rgb(' + str(int(self.red)) + ',' + str(int(self.green)) + ',' + str(int(self.blue)) + ')'


if(__name__ == '__main__'):
    
    tom = (8/(2*(Pixel(7) + 4 + Pixel(3))*3)/32)**2
    
    print str(tom)[0:-2]
