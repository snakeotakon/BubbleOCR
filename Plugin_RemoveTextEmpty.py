#!/usr/bin/env python
from gimpfu import *
import gimpfu
import re
def removeLayersTextEmpty(img, Drawable,bRemoveLayers):
    pdb.gimp_image_undo_group_start(img)
    gimp.progress_init("REMOVING LAYERS TEXT")
    layersBalloons=[]
    def remLayersChildren(G):
        for Layer in G.layers:
            if pdb.gimp_item_is_group(Layer):
                remLayersChildren(Layer)
            elif pdb.gimp_item_is_text_layer(Layer) and pdb.gimp_text_layer_get_text(Layer) =="":
                layerBalloon = pdb.gimp_image_get_layer_by_name(img, Layer.name.replace("_TEXT","") )
                pdb.gimp_image_remove_layer(img, Layer)
                if bRemoveLayers and layerBalloon:
                    layersBalloons.append(layerBalloon)
            pdb.gimp_progress_pulse()
    
    remLayersChildren(img)       
    gimp.progress_init("REMOVING LAYERS BALLOONS")
    for layer in layersBalloons:
        pattern="BText_(.*?)(?: #\d+)"
        p=re.search(pattern,layer.name)
        if p:
            nsmeLayerMask=p.group(1) + "_Mask"
            layerMask=pdb.gimp_image_get_layer_by_name(img, nsmeLayerMask )
            if layerMask:
                position = pdb.gimp_image_get_layer_position(img, layerMask)
                parent = pdb.gimp_item_get_parent(layer)
                pdb.gimp_image_reorder_item(img, layer, parent, position-1)
                pdb.gimp_item_set_visible(layer, True)
                pdb.gimp_item_set_visible(layerMask, True)
                pdb.gimp_layer_set_mode(layer, LAYER_MODE_ERASE)
                
                layer = pdb.gimp_image_merge_down(img, layer, 0)
        else:
            pdb.gimp_image_remove_layer(img, layer)
        pdb.gimp_progress_pulse()    
    pdb.gimp_image_undo_group_end(img)

register(
  "python_fu_RemLayerText",
  "Remove layers Empty and others",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Remove Layers Text Empty...",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_TOGGLE, "bRemoveLayers", "Remove with BalloonsEmpty", True),
  ],
  [],
  removeLayersTextEmpty,
  menu="<Image>/Layer/Tools/"
  )
main()