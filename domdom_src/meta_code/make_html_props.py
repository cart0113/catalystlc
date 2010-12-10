

props = """
    * <a>
    * <abbr>
    * <acronym>
    * <address>
    * <applet>
    * <area>
    * <b>
    * <base>
    * <basefont>
    * <bdo>
    * <big>
    * <blockquote>
    * <body>
    * <br>
    * <button>
    * <caption>
    * <center>
    * <cite>
    * <code>
    * <col>
    * <colgroup>
    * <dd>
    * <del>
    * <dfn>
    * <dir>
    * <div>
    * <dl>
    * <dt>
    * <em>
    * <fieldset>
    * <font>
    * <form>    
    * <frame>
    * <frameset>
    * <h1>
    * <h2>
    * <h3>
    * <h4>
    * <h5>
    * <h6>
    * <head>
    * <hr>
    * <html>
    * <i>
    * <iframe>
    * <img>
    * <input>
    * <ins>
    * <isindex>
    * <kbd>
    * <label>
    * <legend>
    * <li>
    * <link>
    * <map>
    * <menu>
    * <meta>
    * <noframes>
    * <noscript>
    * <object>
    * <ol>
    * <optgroup>
    * <option>
    * <p>
    * <param>
    * <pre>
    * <q>
    * <s>
    * <samp>
    * <script>
    * <select>
    * <small>
    * <span>
    * <src>
    * <strike>
    * <strong>
    * <sub>
    * <sup>
    * <table>
    * <tbody>
    * <td>
    * <textarea>
    * <tfoot>
    * <th>
    * <thead>
    * <title>
    * <tr>
    * <tt>
    * <u>
    * <ul>
    * <var>
"""

import css
output = "class atts:\n"
for prop in props.replace("\n", "").replace("\t", "").replace(" ", "").replace(">", "").replace("*", "").split("<"):
    if(len(prop) > 1 and prop not in css.prop.__dict__):
        space = (20-len(prop))*" "
        output += "\t" + prop + " =" + space + "'" + prop + "'\n"
    
print output 