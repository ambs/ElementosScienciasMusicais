#!/usr/bin/python3

"""
Pandoc filter to process raw latex tikz environments into images.
Assumes that pdflatex is in the path, and that the standalone
package is available.  Also assumes that ImageMagick's convert
is in the path. Images are put in the tikz-images directory.
"""

import pprint
import hashlib
import re
import os
import sys
import shutil
from pandocfilters import toJSONFilter, Para, Image, RawBlock
from subprocess import Popen, PIPE, call
from tempfile import mkdtemp

imagedir = "tikz-images"

def sha1(x):
  return hashlib.sha1(x.encode('utf-8')).hexdigest()

def tikz2image(tikz, filetype, outfile):
  tmpdir = mkdtemp()
  olddir = os.getcwd()
  os.chdir(tmpdir)
  f = open('tikz.tex', 'w')
  f.write("""\\documentclass[12pt]{standalone}
\\usepackage[utf8]{inputenc}
\\usepackage{tikz}
\\usetikzlibrary{positioning}
\\usetikzlibrary{arrows,arrows.meta,automata,decorations.pathmorphing}
\\usepackage{xcolor}
\\usepackage{colortbl}
\\usepackage{pgfplots}
\\usepackage{mymathmacros}
\\usetikzlibrary{shapes,snakes}
             \\begin{document}
             """)
  f.write(tikz)
  f.write("\n\\end{document}\n")
  f.close()
  p = call(["pdflatex", 'tikz.tex'], stdout=sys.stderr)
  os.chdir(olddir)
  if filetype == 'pdf':
    shutil.copyfile(tmpdir + '/tikz.pdf', outfile + '.pdf')
  else:
    call(["convert","-density","120", tmpdir + '/tikz.pdf', "-trim", outfile + '.' + filetype])
  shutil.rmtree(tmpdir)

def getOptions(code):
  patt = re.compile(r'{tikzpicture}({[^}]+})')
  match = patt.search(code)
  options = match.group(1)
  code = patt.sub("{tikzpicture}", code)

  options = re.split(r'\s*,\s*', re.sub(r'[{}]', "", options))

  opts = {}
  for opt in options:
    sides = re.split(r'\s*=\s*', opt)
    opts[sides[0]] = sides[1]

  return (code, opts)

def latex(s):
  return RawBlock('latex', s)

def html(s):
  return RawBlock('html', s)

def tikz(key, value, format, meta):
  if key == 'RawBlock':
    [fmt, code] = value
    if (fmt == "latex"  or fmt == "tex") and re.match(r'\\begin{tikzpicture}', code):
      (code, options) = getOptions(code)

      caption = options['caption'] if 'caption' in options else ""

      outfile = imagedir + '/' + sha1(code)
      if format == "latex":
        filetype = "pdf"
      else:
        filetype = "png"

      if format != "latex":
        src = outfile + '.' + filetype
        if not os.path.isfile(src):
          try:
            os.mkdir(imagedir)
            sys.stderr.write('Created directory ' + imagedir + '\n')
          except OSError:
            pass
          tikz2image(code, filetype, outfile)
          sys.stderr.write('Created image ' + src + '\n')

        if format == "html5" or format == "html":
          alt = ""
          if caption != "":
            alt = " alt=\"" + caption + "\""
            caption = "<figcaption>" + caption + "</figcaption>"
            if 'label' in options:
              code = "<figure id=\""+ options['label'] +"\"><img src=\"" + src + "\"" + alt + "/>" + caption + "</figure>"                            
            else:
              code = "<figure><img src=\"" + src + "\"" + alt + "/>" + caption + "</figure>"              
            return html(code)
            
        else: # generic stuff,
          return Para([ Image(['', [], []], [], [src,""]) ])
      else:
        if caption != "":
           if 'label' in options:
             caption += "\\label{" + options['label'] + "}"

           caption = "\n\\textit{" + caption + "}"
        if 'label' in options:
            code = "\\hypertarget{" + options['label'] + "}{" + code + "}"

        code = "\\vspace{5mm}\\begin{center}\n" + code + "\n\n" + caption + "\n\\end{center}\\vspace{5mm}\n"
        return latex(code)

if __name__ == "__main__":
  toJSONFilter(tikz)

