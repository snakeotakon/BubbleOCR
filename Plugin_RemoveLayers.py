#!/usr/bin/env python
from gimpfu import *
import gimpfu
import gtk
import re
layerSelected = []
def removeLayers(img, Drawable,sSelection,sName,bFullName,bRemoveGroups,bRemoveLayers):
    def remLayersChildren(G):
        for Layer in G.layers:
            Object = re.search( sName, Layer.name, flags=re.IGNORECASE)
            if pdb.gimp_item_is_group(Layer):
                remLayersChildren(Layer)
            if not Object :
                continue
            elif (pdb.gimp_item_is_group(Layer) == True and bRemoveGroups==False):
                continue
            elif  bRemoveLayers==False and pdb.gimp_item_is_group(Layer)==False:
                continue
            else:
                pdb.gimp_image_remove_layer(img, Layer)
                pdb.gimp_progress_pulse()
    def listGuiRun():
        def fillList(L,ls):
            for Layer in L.layers:
                if pdb.gimp_item_is_group(Layer):
                    if bRemoveGroups:
                        ls.append([Layer.name])
                    fillList(Layer,ls)
                    
                else:
                    if pdb.gimp_item_is_drawable(Layer):
                        if bRemoveLayers:
                            ls.append([Layer.name])
        ls = gtk.ListStore(str)
        fillList(img,ls) 
        scroll=gtk.ScrolledWindow()
        tv = gtk.TreeView(ls)
        col = gtk.TreeViewColumn("Layers/Groups", gtk.CellRendererText(), text=0)
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
              
    pdb.gimp_image_undo_group_start(img)
    if (bFullName):
        sName="^" + sName + "$"
    gimp.progress_init("REMOVING LAYERS")
    pdb.gimp_progress_end()
    if sSelection:
        remLayersChildren(img)
    else:
        listGuiRun()
        for name in layerSelected:
            Layer=pdb.gimp_image_get_layer_by_name(img, name)
            pdb.gimp_image_remove_layer(img, Layer)
    pdb.gimp_image_undo_group_end(img)

register(
  "python_fu_RemLayer",
  "Remove layers by selection or name(Regex)",
  "Nothing a",
  "Anonymous a",
  "1.1.0",
  "2020",
  "Remove Layers...",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_OPTION, "sSelection", "Remove By",0,("Layer Selection","Name")),
    (PF_STRING, "sName", "Name Layer", "Name"),
    (PF_TOGGLE, "bFullName", "Remove only if is Name Complete", True),
    (PF_TOGGLE, "bRemoveGroups", "Groups", False),
    (PF_TOGGLE, "bRemoveLayers", "Layers", True),
  ],
  [],
  removeLayers,
  menu="<Image>/Layer/Tools/"
  )
main()