#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
import re
import codecs
selectionCase = ("none","lowercase", "UPPERCASE", "Capitalize", "Sentence","Title")
def py_group_chfont(img, tdraw, bfont, font, bcolorfont, colorFont, bsize,size, bscale,scale,bletterspacing,letter_spacing,blinespacing,line_spacing,cremovestyle,achangeCase,allgroup,rec):
### nested function to parse group layers ###
        def dogroup(group):
              ll = group.layers
              for layer in ll:
### recursion for nested groups ###
                 pdb.gimp_progress_pulse()
                 if (type(layer) == gimp.GroupLayer):
                   if rec: 
                     dogroup(layer)
### actual action ###
                 else:
                    if pdb.gimp_item_is_text_layer(layer):
                       if bfont:
                         pdb.gimp_text_layer_set_font(layer, font)
                       if bcolorfont:
                         pdb.gimp_text_layer_set_color(layer, colorFont)
                       if bsize:
                         pdb.gimp_text_layer_set_font_size(layer, size, 0)
                       if bscale:
                         font_size, unit = pdb.gimp_text_layer_get_font_size(layer)
                         pdb.gimp_text_layer_set_font_size(layer, font_size*scale, 0)
                       if bletterspacing:
                         pdb.gimp_text_layer_set_letter_spacing(layer, letter_spacing)
                       if blinespacing:
                         pdb.gimp_text_layer_set_line_spacing(layer, line_spacing)
                       if cremovestyle:
                         text=pdb.gimp_text_layer_get_markup(layer) 
                         if text is not None:
                           text=re.sub("<.*?>", "",text)
                           pdb.gimp_text_layer_set_text(layer,text)
                       
                       if achangeCase>0:
                         text=pdb.gimp_text_layer_get_text(layer) 
                         if text is not None:
                           text=changeCaseText(text.decode("utf-8"),achangeCase)
                           pdb.gimp_text_layer_set_text(layer,text)
### main function ###
        pdb.gimp_image_undo_group_start(img)
### get active layer             
        draw = img.active_layer

### only do if active layer is a group
        if allgroup:
              dogroup(img)
        elif (type(draw) == gimp.GroupLayer):
              dogroup(draw)
        pdb.gimp_image_undo_group_end(img)
def changeCaseText(text,indexCase):
    # REMOVE Byte Order Mark \xef\xbb\xbf
    text=text.lstrip(codecs.BOM_UTF8.decode("utf8", "strict"))
    if selectionCase[indexCase]=="lowercase":
        return text.lower()
    elif selectionCase[indexCase]=="UPPERCASE":
        return text.upper()
    elif selectionCase[indexCase]=="Title":
        return text.title()
    elif selectionCase[indexCase]=="Capitalize":
        # pdb.gimp_message(text)
        # pdb.gimp_message(text.capitalize())
        return text.capitalize()
    elif selectionCase[indexCase]=="Sentence":
        return re.sub(r"(^|[?!.] )(\w)",lambda x:x.group(0).upper(),text.lower())
    else:
        return text
register(
  "python_fu_changeFont",
  "Change Font, size, letter spacing, line spacing, remove style",
  "Nothing",
  "Anonymous",
  "1.1.0",
  "2019",
  "Change Font...",
  "*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_TOGGLE, "bfont", "Change font", True),
    (PF_FONT, "font", "Font", "Sans"),
    (PF_TOGGLE, "bcolorfont", "Change font color", False),
    (PF_COLOUR,"colorFont", "Font color",(0.0, 0.0, 0.0)),
    (PF_TOGGLE, "bsize", "Change font size", False),
    (PF_SPINNER, "size", "Font size", 10, (1, 8192, 1)),
    (PF_TOGGLE, "bscale", "Change font scale", False),
    (PF_SPINNER, "scale", "Font scale", 1, (0.1, 10, 0.01)),
    (PF_TOGGLE, "bletterspacing", "Change letter spacing", False),
    (PF_SPINNER, "letterspacing", "letter spacing", 0, (-100, 100, 0.1)),
    (PF_TOGGLE, "blinespacing", "Change line spacing", False),
    (PF_SPINNER, "linespacing", "line spacing", 0, (-100, 100, 0.1)),
    (PF_TOGGLE, "cremovestyle", "Change remove style", False),
    (PF_OPTION,"changeCase", "Change case", 0,selectionCase),
    (PF_TOGGLE, "allgroup", "All Groups", True),
    (PF_TOGGLE, "rec", "Recurse nested groups", True)
  ],
  [],
  py_group_chfont,
  menu="<Image>/Layer/Tools/"
  )

main()

