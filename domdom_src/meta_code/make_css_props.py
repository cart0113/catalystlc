_org_js_props = '''
     azimuth
     background
     backgroundAttachment
     backgroundColor
     backgroundImage
     backgroundPosition
     backgroundRepeat
     border
     borderBottom
     borderBottomColor
     borderBottomStyle
     borderBottomWidth
     borderCollapse
     borderColor
     borderLeft
     borderLeftColor
     borderLeftStyle
     borderLeftWidth
     borderRight
     borderRightColor
     borderRightStyle
     borderRightWidth
     borderSpacing
     borderStyle
     borderTop
     borderTopColor
     borderTopStyle
     borderTopWidth
     borderWidth
     bottom
     captionSide
     clear
     clip
     color
     content
     counterIncrement
     counterReset
     cssFloat
     cssText
     cue
     cueAfter
     onBefore
     cursor
     direction
     display
     elevation
     emptyCells
     float
     font
     fontFamily
     fontSize
     fontSizeAdjust
     fontStretch
     fontStyle
     fontVariant
     fontWeight
     height
     left
     length
     letterSpacing
     lineHeight
     listStyle
     listStyleImage
     listStylePosition
     listStyleType
     margin
     marginBottom
     marginLeft
     marginRight
     marginTop
     markerOffset
     marks
     maxHeight
     maxWidth
     minHeight
     minWidth
     MozAppearance
     MozBackgroundClip
     MozBackgroundInlinePolicy
     MozBackgroundOrigin
     MozBinding
     MozBorderBottomColors
     MozBorderLeftColors
     MozBorderRadius
     MozBorderRadiusBottomleft
     MozBorderRadiusBottomright
     MozBorderRadiusTopleft
     MozBorderRadiusTopright
     MozBorderRightColors
     MozBorderTopColors
     MozBoxAlign
     MozBoxDirection
     MozBoxFlex
     MozBoxOrient
     MozBoxOrdinalGroup
     MozBoxPack
     MozBoxSizing
     MozColumnCount
     MozColumnGap
     MozColumnWidth
     MozFloatEdge
     MozForceBrokenImageIcon
     MozImageRegion
     MozMarginEnd
     MozMarginStart
     MozOpacity
     MozOutline
     MozOutlineColor
     MozOutlineOffset
     MozOutlineRadius
     MozOutlineRadiusBottomleft
     MozOutlineRadiusBottomtop
     MozOutlineRadiusTopleft
     MozOutlineRadiusTopright
     MozOutlineStyle
     MozOutlineWidth
     MozPaddingEnd
     MozPaddingStart
     MozUserFocus
     MozUserInput
     MozUserModify
     MozUserSelect
     opacity
     orphans
     outline
     outlineColor
     outlineStyle
     outlineWidth
     overflow
     overflowX
     overflowY
     padding
     paddingBottom
     paddingLeft
     paddingRight
     paddingTop
     page
     pageBreakAfter
     pageBreakBefore
     pageBreakInside
     parentRule
     pause
     pauseAfter
     pauseBefore
     pitch
     pitchRange
     playDuring
     position
     psuedo
     quotes
     richness
     right
     size
     speak
     speakHeader
     speakNumeral
     speakPunctuation
     speechRate
     stress
     tableLayout
     textAlign
     textDecoration
     textIndent
     textShadow
     textTransform
     top
     unicodeBidi
     verticalAlign
     visibility
     voiceFamily
     volume
     whiteSpace
     widows
     width
     wordSpacing
     zIndex 
     '''
     
_org_js_props = _org_js_props.split("\n")

py_props = []
cs_props = []
js_props = []


for prop in _org_js_props:
    if('Moz' not in prop):
        if(len(prop) > 0):
            new_prop = prop.strip()
            py_prop = ""
            cs_prop = ""
            js_prop = ""
            for let in new_prop:
                js_prop += let
                if(let.isupper()):
                    cs_prop += "-"  
                    py_prop += "_"  
                cs_prop += let.lower()
                py_prop += let.lower()
                
            cs_props.append(str(cs_prop))
            if prop not in ['psuedo']:
                js_props.append(str(js_prop))
                py_props.append(str(py_prop))
    


# NEW for css.py
if(False):
    for i,prop in enumerate(py_props):
        if(len(prop) > 1 and prop not in ['font']):
            space = (30-len(prop))*" "
            print "\t" + prop + " = " + space + "_property()"        #css_name = '" + cs_props[i] + "')"

if(False):
    for i,prop in enumerate(py_props):
        if(len(prop) > 1):
            space = (30-len(prop))*" "
            print "\t" + prop + " = " + space + "'" + cs_props[i] + "'"

if(True):
    for i,prop in enumerate(py_props):
        if(len(prop) > 1):
            space = (30-len(prop))*" "
            print "\t" + prop + " = " + space + "'" + js_props[i] + "'"     

  
if(False):
    for i in range(1,100):
        space = (4-len(str(i)))*" "
        print "\t\tx" + str(i) + "p =" + space +  '"' + str(i) + '%"'
    
if(False):
    for i in range(1,999):
        space = (4-len(str(i)))*" "
        print "\t\tx" + str(i) + "px =" + space +  '"' + str(i) + 'px"'

    for i in range(1000,10000,10):
        space = (4-len(str(i)))*" "
        print "\t\tx" + str(i) + "px =" + space +  '"' + str(i) + 'px"'







# OLD AS DIRT

if(False):
    for i,prop in enumerate(py_props):
        if(len(prop) > 1 and prop not in ['font']):
            space = (24-len(js_props[i]))*" "
            print "\t" + js_props[i] + space + "=" + 10*" " + "_property()"   #"'" + js_props[i] + "'"
            
if(False):
    for i,prop in enumerate(py_props):
        if(len(prop) > 1 and prop not in ['font']):
            space = (24-len(js_props[i]))*" "
            print "\t'" + js_props[i] + "':" + space + "'" + cs_props[i] + "',"
            