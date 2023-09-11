#!/usr/bin/env python
from gimpfu import *
import gimpfu
import subprocess
import os
import inspect
import ConfigParser
import codecs
g_PathPlugin = os.path.dirname(inspect.getfile(inspect.currentframe()))
g_pathFileINI=os.path.join(g_PathPlugin , r"Config_BubbleOCR.ini")
os.chdir(g_PathPlugin)
layerSelected = []
g_pWaifu2X=[]
waifuAvailables=[]


configINI = ConfigParser.RawConfigParser()
def loadFileINI():
    def findINI(section,stringFind,default=""):
        if configINI.has_option(section, stringFind):
            return configINI.get(section, stringFind).strip(r'"')
        else:
            return default
    for s in [ss for ss in configINI.sections() if ss.startswith("WAIFU2X")] :
        if configINI.has_option(s, "programwaifu2x"):
            p=findINI(s, "programwaifu2x")
            if p and os.path.exists(p):
                pathProgram=os.path.join(g_PathPlugin,p)
                if not os.path.exists(pathProgram):
                    pathProgram=p
                g_pWaifu2X.append( [s.title(), pathProgram ,findINI(s, "argswaifu2x"),findINI(s, "pathmodelswaifu2x") ] )
    waifuAvailables.extend( [ w[0] for w in g_pWaifu2X ])
if os.path.exists(g_pathFileINI):
    with codecs.open(g_pathFileINI, 'r', encoding='utf-8') as f:
        configINI.readfp(f)
    loadFileINI()
    
def waifu2x(image, drawable,indexW,scale,noise,blayers,bNewLayer,scaleQ,sufix):
    old_width, old_height = pdb.gimp_image_width(image), pdb.gimp_image_height(image)
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
    filename= os.path.join (g_PathPlugin, r"waifuTmp.png")
    if blayers:
        listGuiRun()
    else:
        layerSelected.append(drawable.name)
    gimp.progress_init("Scale with Waifu2X")
    pdb.gimp_image_undo_group_start(image)
    for name in layerSelected:
        layer = pdb.gimp_image_get_layer_by_name(image,name)
        # pdb.file_png_save_defaults(image, layer, filename, filename)
        pdb.file_png_save(image, layer, filename,filename, 0,0, 0, 0, 0, 0, 0)
        sCommand=r'{} -i "{}" -o "{}" {}'\
        .format(g_pWaifu2X[indexW][1],filename,filename,  g_pWaifu2X[indexW][2].format(noise,scale)  )
        
        if os.path.exists(g_pWaifu2X[indexW][3]):
            sPath=g_pWaifu2X[indexW][3]
        else:
            sPath = os.path.dirname(g_pWaifu2X[indexW][1])
        try:
            process = subprocess.Popen(sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=sPath)
            pdb.gimp_progress_set_text(layer.name)
            output=process.communicate()
            pdb.gimp_progress_pulse()
            if( process.returncode!=0):
                pdb.gimp_message("----- ERROR  -----")
                pdb.gimp_message("COMAND: " + sCommand)
                pdb.gimp_message("PATH: " + sPath)
                pdb.gimp_message(str(output[1]))
                pdb.gimp_image_undo_group_end(image)
                return
        except Exception:
            pdb.gimp_message("----- ERROR POPEN -----" )
            pdb.gimp_message( str( sys.exc_info() ) )
            pdb.gimp_message("Command:" + str(sCommand) )
            pdb.gimp_message("Path:" + str(sPath) )
            pdb.gimp_message(layer.name)
            pdb.gimp_image_undo_group_end(image)
            return

        layerNew = pdb.gimp_file_load_layer(image, filename)
        os.remove(filename)
        layerNew.name = layer.name + sufix
        parent = pdb.gimp_item_get_parent(layer)
        position = pdb.gimp_image_get_item_position(image, layer)
        x,y = layer.offsets
        pdb.gimp_layer_set_offsets(layerNew, x, y)
        pdb.gimp_image_insert_layer(image, layerNew, parent, position)
        new_width = int(layer.width * scale)
        new_height = int(layer.height * scale)
        x_offset = (layer.width - old_width) // 2
        y_offset = (layer.height - old_height) // 2
        if not bNewLayer:
            nameB = layer.name
            pdb.gimp_image_remove_layer(image, layer)
            layerNew.name = nameB
        if scaleQ:
            pdb.gimp_image_resize(image, new_width, new_height, x_offset, y_offset)
    pdb.gimp_progress_end()
    pdb.gimp_image_undo_group_end(image)
register(
  "python_fu_waifu2X",
  "Scale with Waifux.",
  "Nothing",
  "Anonymous",
  "1.1.0",
  "2020",
  "Scale with Waifu2x...",
  "RGB*, GRAY*",
  [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_OPTION, "indexW", "Waifu2x", 0, waifuAvailables),
    (PF_SPINNER, "scale", "Scale", 1, (1, 999, 0.05)),
    (PF_OPTION, "noise", "Reduction Noise", 3,("0", "1", "2", "3")),
    (PF_BOOL,   "blayers", "Select multiple layers?", False),
    (PF_BOOL,   "bNewLayer", "Add as New Layer", True),
    (PF_BOOL,   "scaleQ", "Scale Layer to Output" , False),
    (PF_STRING, "sufix", "Sufix for New Layer", "_Waifu2x"),
  ],
  [],
  waifu2x,
  menu="<Image>/Layer/Tools/"
  )
main()
