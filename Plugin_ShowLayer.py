#!/usr/bin/env python
from gimpfu import *
import gimpfu
import re
import subprocess
import os
import inspect
layerSelected = []
def layerShow(image, bLayerActive,bVisible,bProgress):
    def listGuiRun():
        def fillList(L,ls):
            for Layer in L.layers:
                if pdb.gimp_item_is_group(Layer):
                    fillList(Layer,ls)
                else:
                    if pdb.gimp_item_is_drawable(Layer):
                        ls.append([Layer.name])
        import gtk
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
    def doShow(group):
        ll = group.layers
        for layer in ll:
            ### recursion for nested groups ###
            if (type(layer) == gimp.GroupLayer):
                doShow(layer)
            else:
                if bProgress: pdb.gimp_progress_pulse()
                if layer.name in layerSelected:
                    pdb.gimp_item_set_visible(layer, bVisible)
                else:
                    pdb.gimp_item_set_visible(layer, not bVisible)
    if bProgress: gimp.progress_init("Show/Hidden Layers")
    if bLayerActive:
        layerSelected.append( pdb.gimp_image_get_active_layer(image).name )
    else:
        listGuiRun()
    pdb.gimp_image_undo_group_start(image)
    doShow(image)
    if bProgress: pdb.gimp_progress_end()
    pdb.gimp_image_undo_group_end(image)

register(
  "python_fu_ShowHiddenLayers",
  "Show layers selected and hidden all",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Show and hidden layers",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_TOGGLE, "bLayerActive", "Only Layer Active", False),
    (PF_TOGGLE, "bVisible", "Selection is Visible", True),
    (PF_TOGGLE, "bProgress", "Progress", True),
  ],
  [],
  layerShow,
  menu="<Image>/Layer/Tools/"
  )
main()