#!/usr/bin/env python
from gimpfu import *
import gimpfu
import gtk
layerSelected = []
def scaleLayers(image,drawable,scale,bSelectionLayers):
    def listGuiRun():
        def fillList(L,ls):
            for Layer in L.layers:
                if pdb.gimp_item_is_group(Layer):
                    fillList(Layer,ls)
                else:
                    if pdb.gimp_item_is_drawable(Layer):
                        ls.append([Layer.name])
        ls = gtk.ListStore(str)
        fillList(image,ls) 
        scroll=gtk.ScrolledWindow()
        tv = gtk.TreeView(ls)
        col = gtk.TreeViewColumn("Layers", gtk.CellRendererText(), text=0)
        tv.set_reorderable(True)
        col.set_sort_column_id(0)
        tv.append_column(col)
        sel = tv.get_selection()
        sel.set_mode(gtk.SELECTION_MULTIPLE)
        dialog = gtk.Dialog("Selection Layers",None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,gtk.STOCK_OK, True))
        dialog.resize(400, 400)
        scroll.add_with_viewport(tv)
        scroll.show()
        dialog.vbox.pack_start(scroll)
        tv.show()
        response = dialog.run()
        (model, pathlist) = sel.get_selected_rows()
        dialog.destroy()
        if not response==True:
            return
        for path in pathlist :
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter,0)
            layerSelected.append(value)
        return
    listGuiRun()
    pdb.gimp_image_undo_group_start(image)
    scaleX=scale
    scaleY=scale
    for name in layerSelected:
        layer = pdb.gimp_image_get_layer_by_name(image,name)
        x1,y1=layer.offsets
        new_width=(layer.width*scaleX)
        new_height=(layer.height*scaleY)
        pdb.gimp_image_set_active_layer(image, layer)
        if pdb.gimp_item_is_text_layer(layer):
            font_size, unit = pdb.gimp_text_layer_get_font_size(layer)
            pdb.gimp_text_layer_set_font_size(layer, font_size*scale, unit)
            pdb.gimp_text_layer_resize(layer, new_width, new_height)
            pdb.gimp_layer_set_offsets(layer, x1*scale, y1*scale)
        else:
            pdb.gimp_layer_scale(layer, new_width, new_height, False)
    pdb.gimp_image_resize_to_layers(image)
    pdb.gimp_image_undo_group_end(image)
    
register(
  "python_fu_ScaleLayers",
  "Scale layers/Text",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Scale layers/text",
  "*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_SPINNER, "scale", "Scale Layer/text", 2, (0, 20, 0.01)),  
    (PF_BOOL,   "bSelectionLayers", "Selection Layers", True),
  ],
  [],
  scaleLayers,
  menu="<Image>/Layer/Tools/"
  )
main()

