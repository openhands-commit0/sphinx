"""English search language: includes the JS porter stemmer."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict
import snowballstemmer
from sphinx.search import SearchLanguage
english_stopwords = set('\na  and  are  as  at\nbe  but  by\nfor\nif  in  into  is  it\nnear  no  not\nof  on  or\nsuch\nthat  the  their  then  there  these  they  this  to\nwas  will  with\n'.split())
js_porter_stemmer = '\n/**\n * Porter Stemmer\n */\nvar Stemmer = function() {\n\n  var step2list = {\n    ational: \'ate\',\n    tional: \'tion\',\n    enci: \'ence\',\n    anci: \'ance\',\n    izer: \'ize\',\n    bli: \'ble\',\n    alli: \'al\',\n    entli: \'ent\',\n    eli: \'e\',\n    ousli: \'ous\',\n    ization: \'ize\',\n    ation: \'ate\',\n    ator: \'ate\',\n    alism: \'al\',\n    iveness: \'ive\',\n    fulness: \'ful\',\n    ousness: \'ous\',\n    aliti: \'al\',\n    iviti: \'ive\',\n    biliti: \'ble\',\n    logi: \'log\'\n  };\n\n  var step3list = {\n    icate: \'ic\',\n    ative: \'\',\n    alize: \'al\',\n    iciti: \'ic\',\n    ical: \'ic\',\n    ful: \'\',\n    ness: \'\'\n  };\n\n  var c = "[^aeiou]";          // consonant\n  var v = "[aeiouy]";          // vowel\n  var C = c + "[^aeiouy]*";    // consonant sequence\n  var V = v + "[aeiou]*";      // vowel sequence\n\n  var mgr0 = "^(" + C + ")?" + V + C;                      // [C]VC... is m>0\n  var meq1 = "^(" + C + ")?" + V + C + "(" + V + ")?$";    // [C]VC[V] is m=1\n  var mgr1 = "^(" + C + ")?" + V + C + V + C;              // [C]VCVC... is m>1\n  var s_v   = "^(" + C + ")?" + v;                         // vowel in stem\n\n  this.stemWord = function (w) {\n    var stem;\n    var suffix;\n    var firstch;\n    var origword = w;\n\n    if (w.length < 3)\n      return w;\n\n    var re;\n    var re2;\n    var re3;\n    var re4;\n\n    firstch = w.substr(0,1);\n    if (firstch == "y")\n      w = firstch.toUpperCase() + w.substr(1);\n\n    // Step 1a\n    re = /^(.+?)(ss|i)es$/;\n    re2 = /^(.+?)([^s])s$/;\n\n    if (re.test(w))\n      w = w.replace(re,"$1$2");\n    else if (re2.test(w))\n      w = w.replace(re2,"$1$2");\n\n    // Step 1b\n    re = /^(.+?)eed$/;\n    re2 = /^(.+?)(ed|ing)$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      re = new RegExp(mgr0);\n      if (re.test(fp[1])) {\n        re = /.$/;\n        w = w.replace(re,"");\n      }\n    }\n    else if (re2.test(w)) {\n      var fp = re2.exec(w);\n      stem = fp[1];\n      re2 = new RegExp(s_v);\n      if (re2.test(stem)) {\n        w = stem;\n        re2 = /(at|bl|iz)$/;\n        re3 = new RegExp("([^aeiouylsz])\\\\1$");\n        re4 = new RegExp("^" + C + v + "[^aeiouwxy]$");\n        if (re2.test(w))\n          w = w + "e";\n        else if (re3.test(w)) {\n          re = /.$/;\n          w = w.replace(re,"");\n        }\n        else if (re4.test(w))\n          w = w + "e";\n      }\n    }\n\n    // Step 1c\n    re = /^(.+?)y$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      stem = fp[1];\n      re = new RegExp(s_v);\n      if (re.test(stem))\n        w = stem + "i";\n    }\n\n    // Step 2\n    re = /^(.+?)(ational|tional|enci|anci|izer|bli|alli|entli|eli|ousli|ization|ation|ator|alism|iveness|fulness|ousness|aliti|iviti|biliti|logi)$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      stem = fp[1];\n      suffix = fp[2];\n      re = new RegExp(mgr0);\n      if (re.test(stem))\n        w = stem + step2list[suffix];\n    }\n\n    // Step 3\n    re = /^(.+?)(icate|ative|alize|iciti|ical|ful|ness)$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      stem = fp[1];\n      suffix = fp[2];\n      re = new RegExp(mgr0);\n      if (re.test(stem))\n        w = stem + step3list[suffix];\n    }\n\n    // Step 4\n    re = /^(.+?)(al|ance|ence|er|ic|able|ible|ant|ement|ment|ent|ou|ism|ate|iti|ous|ive|ize)$/;\n    re2 = /^(.+?)(s|t)(ion)$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      stem = fp[1];\n      re = new RegExp(mgr1);\n      if (re.test(stem))\n        w = stem;\n    }\n    else if (re2.test(w)) {\n      var fp = re2.exec(w);\n      stem = fp[1] + fp[2];\n      re2 = new RegExp(mgr1);\n      if (re2.test(stem))\n        w = stem;\n    }\n\n    // Step 5\n    re = /^(.+?)e$/;\n    if (re.test(w)) {\n      var fp = re.exec(w);\n      stem = fp[1];\n      re = new RegExp(mgr1);\n      re2 = new RegExp(meq1);\n      re3 = new RegExp("^" + C + v + "[^aeiouwxy]$");\n      if (re.test(stem) || (re2.test(stem) && !(re3.test(stem))))\n        w = stem;\n    }\n    re = /ll$/;\n    re2 = new RegExp(mgr1);\n    if (re.test(w) && re2.test(w)) {\n      re = /.$/;\n      w = w.replace(re,"");\n    }\n\n    // and turn initial Y back to y\n    if (firstch == "y")\n      w = firstch.toLowerCase() + w.substr(1);\n    return w;\n  }\n}\n'

class SearchEnglish(SearchLanguage):
    lang = 'en'
    language_name = 'English'
    js_stemmer_code = js_porter_stemmer
    stopwords = english_stopwords