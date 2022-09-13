#!/usr/bin/env python
from gimpfu import *
def quickView(image):
    def key_Q():
        import ctypes
        keybd_event = ctypes.windll.user32.keybd_event
        keybd_event(0x10 , 0, 0, 0) #shift
        keybd_event(0x51,0,0,0)#key_Q
        keybd_event(0x10 , 0, 0x0002, 0) #release shift
    pdb.gimp_selection_flood(image)
    key_Q()
    
register(
  "python_fu_QuickMaskRemoveHoles",
  "Remove the holes from the selection, and change to Quick Mask",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Change Quick Mask",
  "*",
  [
    (PF_IMAGE,"image","Input image", None),
  ],
  [],
  quickView,
  menu="<Image>/Layer/Tools/"
  )
main()

