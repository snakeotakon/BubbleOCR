#!/usr/bin/env python
from gimpfu import *
import gimpfu
import re
import subprocess
import inspect
import sys
import os
def ParentLayerGroup(img, Drawable,sPrefix,bRemove,sSufix,iOrderGroup,bRoot):
    def childrenreOrder(g):
        for layer in g.layers:
            if (type(layer) == gimp.GroupLayer):
                childrenreOrder(layer)
            else:
                pdb.gimp_image_reorder_item(img,layer,None,0)
    iOrderGroup=int(iOrderGroup)
    pdb.gimp_image_undo_group_start(img)
    if bRoot==True:
        childrenreOrder(img)
    else:
        NoLayers, IDLayers = pdb.gimp_image_get_layers(img)
        for IDLayer in IDLayers:
            Layer = gimp._id2drawable(IDLayer)
            if pdb.gimp_item_is_group(Layer) == False:
                if bRemove:
                    NameGroup = re.sub(sSufix, "", Layer.name) 
                else:
                    NameGroup = Layer.name
                layerGroup = pdb.gimp_image_get_layer_by_name(img, sPrefix + NameGroup) 
                if layerGroup is None:
                        layerGroup = pdb.gimp_layer_group_new(img)
                        layerGroup.name = sPrefix + NameGroup
                        img.add_layer(layerGroup,iOrderGroup)
                if iOrderGroup>=0:
                    pdb.gimp_image_reorder_item(img,Layer,layerGroup,iOrderGroup)
                else:
                    pdb.gimp_image_reorder_item(img,Layer,layerGroup,len(layerGroup.layers)+iOrderGroup+1)
                    
    pdb.gimp_image_undo_group_end(img)

register(
  "python_fu_ParentGroupLayer",
  "It allows to group the images that are in the root within a group",
  "Nothing",
  "Anonymous",
  "1.1.0",
  "2019",
  "ParentLayerGroup...",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_STRING, "sPrefix", "Prefix for Groups", "G_"),
    (PF_TOGGLE, "bRemove", "Remove Sufix in name file.jpg #1", False),
    (PF_STRING, "sSufix", "Remove Sufix (regEx)", r"\.\w{1,6}( #\d+)$"),
    (PF_SPINNER, "iOrderGroup", "Position layer in group", 1, (-999, 999, 1)),
    (PF_TOGGLE, "bRoot", "All layers to Root", False),
  ],
  [],
  ParentLayerGroup,
  menu="<Image>/Layer/Tools/"
  )
main()

    
