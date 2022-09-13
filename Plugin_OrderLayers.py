#!/usr/bin/env python
from gimpfu import *
import re
nameLayers=[]
def orderLayers(image, drawable,bInverse):
    if drawable:
        parent = pdb.gimp_item_get_parent(drawable)
        if not parent:
            parent=image
    pdb.gimp_image_undo_group_start(image)
    for layer in parent.layers:
        nameLayers.append(layer.name)
    if parent==image:
        parent = None
    for namelayer in natural_sort(nameLayers,not bInverse):
        item = pdb.gimp_image_get_layer_by_name(image, namelayer)
        pdb.gimp_image_reorder_item(image, item, parent, 0)
    pdb.gimp_image_undo_group_end(image)
    
        
def natural_sort(l,Reverse=False): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key, reverse=Reverse)
register(
  "python_fu_OrderLayers",
  "Sort the layers",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Order Layers...",
  "*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_TOGGLE, "bInverse", "Reverse", False),
  ],
  [],
  orderLayers,
  menu="<Image>/Layer/Tools/"
  )
main()