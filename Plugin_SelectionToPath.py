#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
TAGPATHSTROKE="_PS_"
def selectionToPath(Img, Drawable,reductionIrregular):
    imageActive = Img   #gimp.image_list()[0]
    activeLayer = Drawable  #pdb.gimp_image_get_active_layer(imageActive)
    if not pdb.gimp_item_is_layer(activeLayer) or pdb.gimp_item_is_group(activeLayer) or pdb.gimp_item_is_text_layer(activeLayer) or pdb.gimp_selection_is_empty(imageActive):
        pdb.gimp_message('Select an layer and make a selection')
        pdb.gimp_image_undo_group_start(imageActive)
        pdb.gimp_image_lower_item_to_bottom(imageActive, activeLayer)
        topLayer = gimp._id2drawable( pdb.gimp_image_get_layers(imageActive)[1][0] )
        pdb.gimp_image_set_active_layer(imageActive, topLayer)
        pdb.gimp_image_undo_group_end(imageActive)
        return

    pdb.gimp_image_undo_group_start(imageActive)
    pdb.gimp_selection_flood(imageActive)
    if reductionIrregular>0:
        pdb.gimp_selection_shrink(imageActive, reductionIrregular)
        pdb.gimp_selection_grow(imageActive, reductionIrregular)
    pdb.plug_in_sel2path(imageActive,None)
    num_vectors, vector_ids = pdb.gimp_image_get_vectors(imageActive)
    for idVector in vector_ids:
        oVector = gimp._id2vectors(idVector)
        if not oVector:continue
        if oVector.name.find(TAGPATHSTROKE)==0: continue
        oVectorOld = pdb.gimp_image_get_vectors_by_name(imageActive,TAGPATHSTROKE+activeLayer.name)
        if oVectorOld:
            pdb.gimp_image_remove_vectors(imageActive, oVectorOld)
        oVector.name= TAGPATHSTROKE + activeLayer.name
    pdb.gimp_selection_none(imageActive)
    pdb.gimp_image_lower_item_to_bottom(imageActive, activeLayer)
    topLayer = gimp._id2drawable( pdb.gimp_image_get_layers(imageActive)[1][0] )
    pdb.gimp_image_set_active_layer(imageActive, topLayer) 
    pdb.gimp_image_undo_group_end(imageActive)
    
register(
  "SelectionToPath",
  "Selection to Path.",
  "Nothing",
  "Anonymous",
  "1.1.0",
  "2019",
  "Selection to Path...",
  "RGB*, GRAY*",
  [
    (PF_IMAGE, "image",       "Input image", None),
    (PF_DRAWABLE, "drawable", "Input drawable", None),
    (PF_SPINNER, "reductionIrregular", "Reduces edge irregularities ", 0, (0, 100,1)),
  ],
  [],
  selectionToPath,
  menu="<Image>/Layer/Tools/"
  )



main()

