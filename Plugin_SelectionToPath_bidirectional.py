#!/usr/bin/env python
from gimpfu import *
import time
import ctypes
def pathToSelect(image):
    if not pdb.gimp_image_get_active_layer(image):
        key_Q()
    active_layer = pdb.gimp_image_get_active_layer(image)
    if not active_layer:
        return
    pdb.gimp_image_undo_group_start(image)
    is_empty = pdb.gimp_selection_is_empty(image)
    if is_empty:
        vectors = pdb.gimp_image_get_vectors_by_name(image, "_PS_" + active_layer.name)
        if vectors:
            pdb.gimp_image_select_item(image, 0, vectors)        
    else:
        pdb.python_fu_SelectionToPath(image, active_layer, 0)
        pdb.python_fu_ShowHiddenLayers(image, True, True, False)
    pdb.gimp_image_undo_group_end(image)

def key_Q():
    keybd_event = ctypes.windll.user32.keybd_event
    keybd_event(0x10 , 0, 0, 0) #shift
    keybd_event(0x51,0,0,0)#key_Q
    keybd_event(0x10 , 0, 0x0002, 0) #release shift
register(
  "python_fu_pathToSelectionPS",
  "Selections to Path or Path to Selection",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Selection to Path <-->",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
  ],
  [],
  pathToSelect,
  menu="<Image>/Layer/Tools/"
  )
main()