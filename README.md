# BubbleOCR 2.2
It allows you to translate any text of an image, specially designed for text bubbles/balloon

## Features
With this plugin for Gimp, it is possible to perform Optical character recognition (OCR) of images, and their translation(many language), it also allows you to edit all the text in various ways, as well as make corrections using word lists. 
It also offers spell checking through browsers or subtitle programs like Aegisub.

### Requirements:

##### GIMP The Free & Open Source Image Editor
Gimp 2.10.x  (Tested gimp-2.10.32)

https://www.gimp.org/

Note:  Version Gimp 2.10.18 has a bug, when selecting the font from a script.



##### Tesseract Open Source OCR Engine
https://github.com/tesseract-ocr/tesseract

------------


# Download
**Plugin-only Version**
Tesseract needs to be installed separately for it to work.
Waifu2x and Deep-translator.exe are optional

**Standard Version **
This is the recommended version, so that the program can work normally.
- Installer (Install.bat)
- Plugin Export_layers(.py)
- Tesseract 64 bit installer
- Waifu2x (converter-cpp.exe and ncnn-vulkan.exe)
- Deep-translator.exe
- Microsoft Visual C++ Redistributable x86 and x64 Visual Studio 2015, 2017, 2019, and 2022

**Extended Version (+2 engine OCR)**
*Standard version* + 
- Capture2Text_Cli.exe.- A variant of tesseract, it can give different results than the current version
- tesseract4Beta.exe.- A variant of tesseract it can give different results than the current version
- Aegisub-3.0.2-32.exe.- Edit the text as subtitle
- AviSynth_260.exe.- Only if you use aegisub and want to see the OCR images as video (video.avs)

------------



### Installation plug-ins:
##### Manual Installation
Copy plug-ins to %Appdata%\GIMP\2.10\plug-ins\
*or*
C:\Users\ *YOURNAME* \AppData\Roaming\GIMP\2.10\plug-ins

###### Download tesseract-ocr-w32 or  tesseract-ocr-w64
https://github.com/UB-Mannheim/tesseract/wiki
The installer will allow you to select all available languages for the OCR



------------


##### Installation
Unzip the standard or extended version, and run the bat file
Run *Install.bat*

### Usage
Start Gimp and there will be a new menu: "LAYER/TOOLS/", and a new file will be created in plug-ins\Config_OCRBalloons.ini

### Plugins

- **BubbleOCR** (*Plugin_BubbleOCR.py*).- Main plugin for OCR and translation, needs Gimp and Tesseract to work properly. All other plugins are optional.
###### Optionally, you need:
 - Deep-translator.exe (fork).- For translation with google (line commands)
 https://pypi.org/project/deep-translator/
 - Waifu2x.- to improve character recognition (noise reduction).
 - Capture2Text_CLI.- Based on Tesseract, but it can give different results than the original Tesseract.

- **Change Font** (*Plugin_ChangeFont.py*).- Change the font, size, scale and other features.
Plugin_QuickViewRemoveHoles.py.- It removes (small) holes within a selection just as it does the Quick Mask switch, and this is quite useful for making corrections to selections, for example to split a speech bubble. It is necessary to assign shortcut the letter Q, so that it works with the script Plugin_SelectionToPath_bidirectional.py.

- **Selection to Path** (*Plugin_SelectionToPath.py*).-  Save the selections as paths. Very useful when working with many images (For "Process All layers/Path" of Plugin_OCRForBalloonsText). 

- **Selection to Path <-->** (*Plugin_SelectionToPath_bidirectional.py*).- If you have something selected, it sends it to a path(save selection), and if you have nothing selected and there is a path with the name of the layer, it transforms it into a selection. And if you're in quickmask mode, it saves the selection to a path, as well as sends the layer to the bottom, and hides all layers except the first one. All of this is very useful for saving selections as paths for many layers or images. And to be able to later process all these saved selections (paths) by means of the option of Process All layers/Path of BubbleGloom. It is recommended to assign any shortcut

- **Parent Layer Group** (*Plugin_ParentGroupForLayers.py*).- It allows to group the images that are in the root within a group.

- **Remove Layers Text Empty** (*Plugin_RemoveTextEmpty.py*).- Remove the layers that have empty text, this will be useful for the new plugin, which allows automatic text detection.

- **Order Layers** (*Plugin_OrderLayers.py*).- Allows you to sort the layers.

- **Remove Layers** (*Plugin_RemoveLayers.py*).- Remove layers by name or by selection

- **Repeat Key** (*Plugin_RepeatKey.py*).- It allows repeating a key for a series of selected layers, for example a filter. It doesn't always work.

- **Scale Layers Text**(*Plugin_ScaleLayers.py*) .- Allows you to scale the selected layers
- **Show and hidden layers** (*Plugin_ShowLayer.py*).- Allows to show or hide layers

- **Scale with Waifu2X** (*Plugin_Waifu2x.py*).- It allows scaling a layer through waifu2x, the configuration is taken from the INI file of Plugin_OCRForBalloonsText.py



#### LAYER/TOOLS/BubbleGloom
#### Options
- **Process only selection**: For the selected area it will perform the OCR, all other options will affect the obtained result.
- **Process All layers/Path**: Based on the selections saved as path, it will execute all the layers that have an associated path (use Plugin_SelectionToPath.py or Plugin_SelectionToPath_bidirectional.py), all other options will affect the obtained result.
- **Only repeat OCR**: for repeat recognition OCR (useful in change engine), all other options will affect the obtained result, except for scaling with waifu2X.
- **Only repeat Translation**.- It repeats the translation, it is not affected by the engine type and scaling options. Useful when making corrections only to the source text (OCR)
- **Only repeat Fix**.- Just repeat the corrections through the word lists in ocr text or translations.
- **Only Edit text.**- Only edit the text using the selected editor, all other options do not apply.
- **Update text Translated**.- Updates the translated text in the project files, this is quite useful when making corrections from the gimp text editor. All other options will always update from the project files to gimp. Use this option if you edit text both from gimp and from the editors.
- **Load Proyect**.- You can reload your project to gimp, this will be useful for the new script (in development) that allows automatic detection of text in images
- **Show Files proyect**.- Show directory proyect saved.
- **Show Files Plugins.**- Shows the directory where the plugins are.
- **Refresh Languages OCR Engine**.- when change type Engine OCR, is necessary update languages.
- **Edit Config File INI**.- You can view or edit the plugin configuration file. 

** Fix OCR/Translation: **
Allows you to make corrections/substitutions using word lists in both OCR files and translations
In the .INI configuration file, you can specify the files that will be used to perform all the corrections, it supports two types of files, those that are simple text (filetext) or those that use regular expressions (fileregex), all can be specified the files that require (filetext1,filetext2,filetext3...) in their respective section [REPLACE OCR ENGLISH] or [REPLACE TRANSLATION ENGLISH], for the language shown in "Language OCR/Balloon" and "Language for Translation" respectively.

- **None**.- Does not make any correction
Remove line break in OCR.- Join all the lines into one (text OCR), this allows a better translation.
- **Fix OCR of list**.- Make corrections to OCR text.
- **Fix Translations of list**.- Make corrections to OCR tex
- **Fix OCR/Translations of list**.- Make corrections to both.

**Editor OCR & Translation:**

- Edit with Internet Explorer (HTA):is fast
- Edit Navigator (Edge): Has a language translator, spellscheck
- Edit Navigator (Chrome): Has a language translator, spellscheck
- Edit Subtitle(ass): for edit Subtitles "Aegisub", "Subtitle Edit"... others

**Proyect Name: **

- It is the name of the folder where all the text and image files necessary to work will be stored. It is important that each project has a different name. And once you finish your work, you can delete your project with windows explorer. This will contain many text files, as well as the images that were used for OCR.

**Proyect Directory : **
- Directory saves files necessary for translation. It is possible to edit later with these files
It is the directory where the image and text files will be stored, by default it will be in the Windows temporary directory, but you can change that location.

**Reduce filter selection:**
Reduce in pixel la selections saved, useful borders add noise (0-3 recommended)

**Detect Backcolor Ballons:**
Detect automatic color globe text, for default is white. useful globe text black or color

**Reduce Filter border in pixels:**
Reduce Edge irregularities, useful to make the selection smoother, or to eliminate small selections. Test with values of 1-20.

Using with many images
----------------------------------------------------------------
Import all the images of the project up to a maximum of 250 .
Up to 100 images recommended.
Go to the top layer, select with the magic wand the white area of the speech bubbles, the text gaps are eliminated when executing the script, or Select-Remove Holes. In some cases it will be necessary to separate the text balloons, this can be easily done by cutting them with a line using Toggle [Quick Mask](https://docs.gimp.org/2.10/en/gimp-image-window-qmask-button.html "Quick Mask"), which allows you to use tools such as a brush or pencil, to draw the selected.
Tutorial Quick Mask
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/aa4bbAYiREo/0.jpg)](https://www.youtube.com/watch?v=aa4bbAYiREo)

Once you have the selected areas (multiple speech bubbles), this can be saved with **Selection to Path** or **Selection to Path <-->**. Which will remove the gaps, will move the active layer to the last one and select the top layer. Repeat the process, but now you can use the Ctrl-F key combination, which will repeat the last action (script), without a dialog box.

#### Tip
It is recommended to hide all other images/layers so Gimp doesn't slow down. The best way to hide layers in the current level is by pressing Shift plus the left mouse button.
![](https://farm8.staticflickr.com/7725/17244826968_8e6fd5208b_o.gif)
http://ahmed.amayem.com/gimp-hide-all-layers-show-all-layers/



#### Exporting many images (Groups)
To export many grouped images, this other plugin is necessary

##### File - Export layers... (plugin)
![](https://khalim19.github.io/gimp-plugin-export-layers/images/screenshot_dialog_basic_usage.png)

https://github.com/khalim19/gimp-plugin-export-layers/releases
https://khalim19.github.io/gimp-plugin-export-layers/sections/Installation.html




# Tutorials
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/ovtaJguCYV8/0.jpg)](https://youtu.be/ovtaJguCYV8)

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/sASVPqiOojo/0.jpg)](https://youtu.be/https://youtu.be/sASVPqiOojo)



**Tips**
 - **EditOCRText.html.**- This file is used to be able to edit in a web browser, but it is also compatible with HTA, so you can change the extension from html to hta, and it will run as a program



#### LINKS.

OCR Optical character recognition or optical character reader 
Tesseract: use 4.0 alpha, is legacy tessdata 3.0 (languages)
https://sourceforge.net/projects/capture2text/files/Dictionaries/

Tesseract LSTM (5.0):  training Neural net based, is compatible NEW Tessdata 
https://tesseract-ocr.github.io/tessdoc/Home.html

OCR Tesseract Version 5.0 
https://github.com/UB-Mannheim/tesseract/wiki
https://tesseract-ocr.github.io/tessdoc/Home.html

OCR Tesseract Version 4.0
https://tesseract-ocr.github.io/tessdoc/4.0-with-LSTM.html# 400-alpha-for-windows

Information Tessdata (data languages Training)
https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html

Capture2TEXT: variant Tesseract 4.0 compatible legacy tessdata 
http://capture2text.sourceforge.net

Waifu2X (scale):improves word recognition in small images
http://waifu2x.udp.jp/index.es.html
https://github.com/DeadSix27/waifu2x-converter-cpp
https://github.com/nihui/waifu2x-ncnn-vulkan



Subtitle:
http://www.aegisub.org/		(compatible Avisynth)
https://www.nikse.dk/subtitleedit/ 		(List words, spell check, translator)


Microsoft Visual C++ Redistributable latest Visual Studio 2015, 2017, 2019, and 2022
https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170




