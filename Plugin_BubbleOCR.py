#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
from io import BytesIO
from string import Template
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import codecs
import subprocess
import re
import glob
import inspect
import sys
import os
import traceback
import SimpleHTTPServer
import SocketServer
import HTMLParser
import cgi
import xml.etree.ElementTree as ET
import urllib
import threading
import tempfile
import datetime
import time
import ConfigParser
import multiprocessing
g_limitThreads=multiprocessing.cpu_count()
# s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

#Path Plugin GIMP
g_PathPlugin = os.path.dirname(inspect.getfile(inspect.currentframe()))
g_pathFileINI = os.path.join(g_PathPlugin , r"Config_BubbleOCR.ini")
os.chdir(g_PathPlugin)
g_imageTemp= r"_imgTemp_"
g_prefixName = u"OcrImage"
g_ExtensionOCR = u".png"
g_ExtensionWeb = u".jpg"
TXT=u".txt"
HOCR=u".hocr"
T_TXT=u"-T.txt"
OK = "ok.txt"
BText = "BText"#Tag balloon WHITE/EMPTY
CARRIAGERETURN="\r\n"
TAGPATHSTROKE=u"_PS_"
TAGPREFIXGROUP = u"G_"
g_nameDocument = u"MyDocument"
g_namePageHTML = "EditOCRText.html"
g_nameFileImageOCR = g_prefixName + g_ExtensionOCR
g_nameFileTXTOCR = g_prefixName
g_nameFileTranslation = g_prefixName + T_TXT
g_fileASS = "subtitle.ass"
g_fileAVS= "video.avs"
g_pathProyectWeb=""
g_pathProyectWeb_Images=""
g_typeFont=""
g_sizeFont=""
g_colorFont=""
g_thresholdWhiteBalloon=660 #86% threshold White for detection background
g_pathListImages=[] #listimages /images
g_port = 0
g_ip=""
g_translationweb=""
g_activeLayer = None
g_imageActive = None
g_programOCR=[]
g_pathTessdata=[]
g_navigators={}
g_argsOCR=[]
g_nameEngineOCRs=[]
g_translators=[]
g_Waifu2X=[]
g_scaleWaifu2x=2
g_noiseWaifu2x=3


class parameter:
    indexEngineOCR=0
    bWaifu2x=False
    indexLanguageOCR=0
    iOrientation=0
    indexFix=0
    caseOCR=0
    bTranslation=False
    caseTranslation=0
    indexLanguageTranslation=0
    nameProyect=""
    pathProyect=""
    indexEditor=0
    iFilterBorder=0
    bColorBalloonAutomatic=False #Detects color textballoon automatically, default white
pC=parameter()

g_bHocr=True #Information position text (HOCR)
g_srcCodeLanguage =""
g_targetCodeLanguage =""
g_srcLanguage =""
g_targetLanguage =""
g_bRepeatOCR=False
g_listWordsSplitImage = [] #["NO","No","no","YES","yes","To","TO","FOR","YOU"]
g_bMessageToConsole=True #message to console
g_notOCR=0
g_notExportedImage=0
g_notRemoveImageDetection = 0
#Divisions Image BETA
g_divisions=0 
g_reductionIrregular = 0
g_thresholdBW = 0
g_areaSelection = 0
g_minLengthCharacter = 0
g_lettersOCR=""
g_replaceOCR=[]
g_replaceTarget=[]
g_listReplaceOCR=[]
g_listReplaceTarget=[]
g_aSelectionEditor = ""
aSelectionCase = ("none","lowercase", "UPPERCASE", "Capitalize", "Sentence")
aSelectionMain = ("Process only selection", "Process All layers/Path","Only Repeat OCR","Only Repeat Translation","Only Repeat Fix's","Only Edit Text","Update Text Translated","Load Proyect","Show Files Proyect","Show Files Plugins","Edit Config File INI","Refresh Languages OCR Engine")
defaultINI = r"""
[OCR TESSERACT]
programocr = "C:\Program Files\Tesseract-OCR\tesseract.exe"
pathtessdata= ""
argsocr="${NAMEFILEIMAGEOCR} ${NAMEFILEOUTOCR} --psm ${ORIENTATION} -l ${DESTLANGUAGEOCR} hocr"

[OCR TESSERACT x32]
programocr = "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
pathtessdata= ""
argsocr="${NAMEFILEIMAGEOCR} ${NAMEFILEOUTOCR} --psm ${ORIENTATION} -l ${DESTLANGUAGEOCR} hocr"

[OCR TESSERACT PORTABLE]
programocr = "utils\OCR\tesseract4Beta.exe"
pathtessdata= "utils\OCR\tessdata"
argsocr="${NAMEFILEIMAGEOCR} ${NAMEFILEOUTOCR} --psm ${ORIENTATION} --tessdata-dir ${PATHTESSDATA} -l ${DESTLANGUAGEOCR} hocr"

[OCR CAPTURE2TEXT]
programocr = "utils\OCR\Capture2Text_CLI.exe"
pathtessdata= ""
argsocr="-l ${DESTLANGUAGEFULLOCR} -b -i ${NAMEFILEIMAGEOCR} -o ${NAMEFILEOUTOCR}.txt ${ORIENTATIONVERTICAL} "

[WAIFU2X CPP]
programwaifu2x = "utils\waifu2x\converter-cpp\waifu2x-converter-cpp.exe"
pathmodelswaifu2x = ""
argswaifu2x = "--noise-level {} --scale-ratio {}"

[WAIFU2X VULKAN]
programwaifu2x = "utils\waifu2x\ncnn-vulkan\waifu2x-ncnn-vulkan.exe"
pathmodelswaifu2x = ""
argswaifu2x = "-n {} -s {} -t 256"

[TRANSLATOR GOOGLE]
programtranslator = "utils\translator\deep-translator.exe"

[NAVIGATOR EDGE x86]
programweb = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
optionsweb = "-inprivate --start-maximized --user-data-dir="%appdata%\OCREdge""

[NAVIGATOR EDGE]
programweb = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
optionsweb = "-inprivate --start-maximized --user-data-dir="%appdata%\OCREdge""

[NAVIGATOR CHROME x86]
programweb = "C:\Program Files (x86)\google\chrome\application\chrome.exe"
optionsweb = "--new-window --incognito --start-maximized --user-data-dir="%appdata%\OCRChrome""

[NAVIGATOR CHROME]
programweb = "C:\Program Files\google\chrome\application\chrome.exe"
optionsweb = "--new-window --incognito --start-maximized --user-data-dir="%appdata%\OCRChrome""

[REPLACE OCR ENGLISH]
filetext1 = "utils\list_replace_characters_english.txt"
fileregex1 = "utils\list_Cleanup_All.txt"

[REPLACE OCR SPANISH]
filetext1 = ""
fileregex1 = "utils\list_Cleanup_All.txt"

[REPLACE OCR JAPANESE VERT]
filetext1=
fileregex1 = "utils\list_Cleanup_All.txt"

[REPLACE OCR JAPANESE]
filetext1=
fileregex1 = "utils\list_Cleanup_All.txt"

[REPLACE TRANSLATION SPANISH]
filetext1=""
fileregex1 = "utils\list_Cleanup_All.txt"

[CONFIGURATION]
ip=127.0.0.1
port = 8000
font = Arial
sizefont = 28
translationweb = 
noisewaifu2x = 3
scalewaifu2x = 2

[DEBUG]
hocr=1
notexportedimage=0
notocr=0
notremoveimagedetection=0
messageconsole=0
"""
headASS = r"""[Script Info]
; Script generated by Aegisub 3.2.2
; http://www.aegisub.org/
PlayResX: 640
PlayResY: 480
YCbCr Matrix: None
WrapStyle: 0
ScaledBorderAndShadow: no

[Aegisub Project Garbage]
Last Style Storage: Default
Video File: video.avs
Video AR Value: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Translate,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,9,10,10,10,1
Style: OCR,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,3,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
headAVS=r"""
global Width=640
global Height=480
global fps=24
global AspectGlobal = 1.0*Width/Height
function ImageOCR (name)
{
   c=ImageReader(name, start=0, end=23, fps=fps)
   Global AspectImage=1.0*c.Width/c.Height
   Img= ( AspectImage>=AspectGlobal  ) ?  c.BilinearResize(Width,int(Width/AspectImage)) : c.BilinearResize(int(Height*AspectImage),Height)
   BorderLeft=0
   BorderTop=Height-Img.Height
   BorderRight=Width-Img.Width
   BorderBottom=0
   return  Img.AddBorders(BorderLeft, BorderTop, BorderRight, BorderBottom, color=$000000)
}

"""
sHTA = r"""<!DOCTYPE html>
<HTML>
    <meta http-equiv="x-ua-compatible" content="ie=11" content="text/html" charset="UTF-8">
    <script type="text/javascript" src="ListFilesImage.js"></script>
    <SCRIPT LANGUAGE="javascript">
        document.documentElement.lang = languageSource;
        //isHTA=(window.location.protocol!="http:")
        var isHTA = (window.external == null)
        var aOTextAreaOCR = []
        //Array textArea OCR
        var aOTextAreaTranslated = []
        //Array textArea Translated
        var aDivTranslated = []
        //Array preTranslates
    </SCRIPT>
    <HEAD>
        <link href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABAAQMAAACQp+OdAAAABlBMVEVRvwEKuFF1eVo5AAAAAXRSTlMAQObYZgAAASFJREFUKM9lkbFOAzEMhm1FIhtZGRB5hXZjQHevVLYOkbiNBYkXQDwJw6EOXSpegfQNglgyRGfs2EUVnOTk0zmxf/8BiA0AwgIwckCkc+gphjtAyhAEAjWFkUjh4ZtmAVwgZgFXwRUBnwGrQJgAEsNV5ILDhSzSgoPvcwtOw5bDC1SBmZfC4U6AWeMPvFd/rJx3uxa+msD+8nr9IvDhb/FJ4OBX2P8c3ArbxqBu7Eyxw+teZ/96c/92Kii38MgtpM7/7qown0v9Fd9sHOweSnqxkf2nmRCeZ7Ulnowa2Dov1iUkNbM6IpoCYPHUDXc5PFJl8HMEmhnCNOgzRUj6cEOXwZCw6OPWrlKEdnEC3XSBqDtsB4OUDMZqEItBsDI6LH8/eLeIjMFBtLwAAAAASUVORK5CYII=" rel="icon" type="image/png" />
        <HTA:APPLICATION ID="oApp" APPLICATIONNAME="OCR TEXT" BORDER="thick" CAPTION="yes" SHOWINTASKBAR="yes" SINGLEINSTANCE="no" SYSMENU="yes" WINDOWSTATE="normal" SCROLL="yes" SCROLLFLAT="yes" VERSION="1.0" INNERBORDER="yes" SELECTION="yes" MAXIMIZEBUTTON="yes" MINIMIZEBUTTON="yes" NAVIGABLE="yes" CONTEXTMENU="yes" BORDERSTYLE="normal"/>
        <style>
            html, body {
                height: 100%;
            }

            img {
                max-width: 100%;
                max-height: 100%;
                display: block;
            }

            th, td {
                width: auto;
                padding: 5px;
                border: 1px solid gray;
            }
			a:link {
			  color: #00d900;
			  background-color: transparent;
			  text-decoration: none;
			}

			a:visited {
			  color: yellow;
			  background-color: transparent;
			  text-decoration: none;
              
			}
            #idArrow {
                position: absolute;
                offset-position: 100 300;
                top: -100px;
                left: 0px;
                height: auto;
                width: auto;
                background-color: white;
                font: 36px;
                border: 2px solid blue;
                display: inline-block;
                opacity: 90%;
                transform: rotate(0deg);
            }

            .divleft {
                width: 100%;
                height: 100%;
                float: left;
                top: 60px;
            }
            #idPanelLeft {
                width: 60%;
                height: 100%;
				/*display: inline-block;*/
            }
            #idPanelRight {
				position: fixed ;
				right:0px;
				top:35px;			
                width: 35%;
                height: 90%;
				max-width: 100%;
                max-height: 100%;
				display: inline-block;
				z-index:1;
				border: 0px solid yellow;
            }

            .headers {
                width: 100%;
                top: 0px;
                left: 0px;
                height: 15px;
                position: fixed;
                padding: 10px 5px;
                background-color: #5F5F5F;
				z-index:2
            }
            .divLeftUp {
                position: fixed;
                top: 35px;
                left: 5px;
                height: 50%;
                width: 64%;
                max-width: 100%;
                max-height: 100%;
                background-color: white;
                opacity: 100%;
				border: 0px solid blue;
            }
			#idTitlepage{
				display: inline-block;
			}
			
            .divRight {
                position: relative ;
                right: 0px;
                top: 0px;
                width: 100%;
				height:100%;
                border: 0px solid green;
            }

            .divElements {
                border: 1px solid gray;
                display: inline-block;
                width: auto;
                height: auto;
                vertical-align: middle;
                padding: 4px;
            }

            .divElementsSlider {
                display: inline-block;
                position: absolute;
                padding: 0px;
                width: 100%;
            }            
			.divElementsSliderPreview {
				display:none;
				position: absolute;
				left: 400px;
                top: 10px;
				border: 1px solid gray;
            }

            .areaReplace {
                height: 100%;
                width: 98%;
				overflow-x: scroll;
				white-space: pre ;

            }

            .divTopLeft {
                height: 55%;
            }
			#idTextTranslated {
				position: absolute;
				display:none;
			}
            textarea {
                width: 100%;
                height: 100%;
                autocomplete: on;
                spellcheck: false;
                autocapitalize: sentences;
            }

            .hidden {
                display: none;
            }

            .cellTranslation {
                width: 25%;
                height: 150px;
            }

            .preTranslator {
                width: 250px;
                height: 100%;
                overflow: auto;
                background-color: #F4F4F4
            }


            #myProgress {
                width: 10%;
                float: right;
                right: 40px;
                top: 10px;
                border: 1px solid black;
            }

            #myBar {
                float: left;
                width: 0%;
                height: 20px;
                background-color: #4CAF50;
                text-align: left;
                margin: auto;
                color: white;
                font-size: 100%;
                opacity: 50%;
                border: 1px white;
            }

            #idTitleNumberbar {
                float: left;
                width: 300px
            }

            #idNameImage {
                float: right;
                display: inline-block;
                width: auto;
                display: inline-block;
                text-align: center;
                color: white;
                padding: 0px 4px;
                border: 1px solid black;

            }

            #idNext {
                position: absolute;
                display: inline-block;
                width: auto;
                right: 0px;
                display: inline-block;
                text-align: center;
                background-color: white;
                padding: 10px 10px;
                opacity: 0.6;
                border: 1px solid black;
                cursor: pointer;
            }

            #idPrev {
                position: absolute;
                display: inline-block;
                width: auto;
                left: 0px;
                display: inline-block;
                text-align: center;
                background-color: white;
                padding: 10px 10px;
                opacity: 0.6;
                border: 1px solid black;
                cursor: pointer;
            }

            #IdpageImage {
                position: absolute;
                display: inline-block;
                width: auto;
                left: 80px;
                display: inline-block;
                text-align: center;
				background-color: white;
                opacity: 0.8;
                border: 1px solid black;
            }

            input[type="range"] {
            }

            .titletable {
                display: inline-block;
                width: 24%;
                text-align: center;
                color: white;
                background-color: #5F5F5F;
            }
        </style>
    </HEAD>
    <BODY>
        <div class="headers skiptranslate" style="text-align:center ">
            <button style="float: left;" type="button" onclick="SaveFiles()">Accept / Save Changes</button>
            <div id="myProgress">
                <div id="myBar">
                    <div id="idTitleNumberbar"></div>
                </div>
            </div>
			<div id="idNameImage">Names Images</div>
            <button style="float: right;margin: 0px 20px" type="button" onclick="previewImage()">Preview</button>
			<div id="idTitlepage">
             <strong><a href="https://github.com/snakeotakon/BubbleOCR" target="_blank" title="Homepage" style="color: white"> BubbleOCR 2.2 </a></strong>
            <a href="https://lens.google.com/search?p" target="_blank" title="Copy image and in Google Lens Control+v for paste image(side right) "> Google Lens </a> <font color="#FFFFFF">
			<a href="https://www.deepl.com/translator" target="_blank"> Deepl -</a>
			<a href="https://translate.google.com/" target="_blank"> Google -</a>
			<a href="https://www.bing.com/translator" target="_blank"> Bing -</a>
			<a href="https://translate.yandex.com/" target="_blank"> Yandex -</a>
			<a href="https://mymemory.translated.net/" target="_blank"> Mymemory -</a>
			<a href="https://mt.qcri.org/api/" target="_blank"> Qcri -</a>
			<a href="https://papago.naver.com/" target="_blank"> Papago -</a>
			<a href="https://libretranslate.com/" target="_blank"> LibreTranslate -</a>
            </font>
			</diV>
			
        </div>
        <form enctype="multipart/form-data" method="post" name="formTextOCRTranslations" id="idformTextOCRTranslations" onsubmit=""></form>
        <form enctype="multipart/form-data" method="post" name="myFormOK" id="idmyFormOK" onsubmit="">
            <input type="hidden" name="ok.txt" value="ok">
        </form>
        <form enctype="multipart/form-data" method="post" name="myFormSaveSearch" id="idmyFormSaveSearch" onsubmit=""></form>

		<div id="idPanelLeft">

        <div class="divleft">
            <div class="divTopLeft"></div>
            <div style="height:auto;">
                <table id="idTableImageOCR" border="0" style="width:100%;height:100%"></table>
            </div>
        </div>
        <div class="divLeftUp skiptranslate">
            <div style="float: left; width: 45%;height:95%">
                <img id="idViewPortImageOCR" src="" alt="Image OCR Selected">
            </div>
            <div style="float: right;  width: 55%;height: 93%; ">
                <div style="height: 100%; ">
                    <div style="height: 100%;width: 65%;display:inline-block;">
                        <textarea wrap="off" class="areaReplace" id="idAreaTextReplace" title="Perform the replacement based on a list of words, separated by a tab. It allows the use of regular expressions, and the flags are: gimsuy : g - Global search, i - Case-insensitive search, m - Multi-line search, s - Allows . to match newline characters,u - unicode; treat a pattern as a sequence of unicode code points. y - Perform a sticky search that matches starting at the current position in the target string." name="SavedSearch.txt" form="idmyFormSaveSearch"></textarea>
                    </div>
                    <div id="some_id" style="position: absolute;display:inline-block;width: 18%;border: 0px solid gray;">
                        <div class="divElements">
                            Word(s) Search
			<input type="text" id="idWordSearh" style="width:100%">
                            <br>
                            Word(s) Replace
			<input type="text" id="idWordReplaces" style="width:100%">
                            <span id="idSpanComments" style="display:none">
                                Comments
			<input type="text" id="idComments">
                            </span>
                            <input type="button" value="Add words(s)" onclick="addWordtoReplace()">
                            RegEx
			<input type="checkbox" id="idCheckRegEx" value="0">
                            <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions" target="_blank">? </a>
                        </div>
                        <div class="divElements">
                            Add
			  
                            <select id="idHelpRegEx" name="Help RegEx" title="Help for change text" style="height: 100%;width:100%">
                                <option value="0"></option>
                                <option value="1">CLEAR ALL</option>
                                <option value="2">Join line break separated with(-)</option>
                                <option value="3">Join all lines break</option>
                                <option value="4">Remove spaces duplicates</option>
                                <option value="5">Remove all spaces</option>
                                <option value="6">Remove phrase small</option>
                                <option value="7">Remove space character special OCR</option>
                                <option value="8">Remove space begin line</option>
                                <option value="9">Add a point to the end of the line</option>
                            </select>
                        </div>
                        <div class="divElements">
                            <input type="radio" checked name="radioSelection" value="Selected">
                            Selected
			<input type="radio" name="radioSelection" value="All">All
			
                        </div>
                        <div class="divElements">
                            <input type="radio" checked name="radioOCR" value="OCR">
                            OCR
			<input type="radio" name="radioOCR" value="Translations">Translations
			
                        </div>
                        <div class="divElements">
                            Case
			  
                            <select id="idChangeCase" name="ChangeCase" title="Change case">
                                <option value="0">None</option>
                                <option value="1">lowercase</option>
                                <option value="2">UPPERCASE</option>
                                <option value="3">Capitalize</option>
                                <option value="4" Title="The change text. After point.">Sentence</option>
                            </select>
                        </div>
                        <div class="divElements">
                            <button type="button" onclick="replaceText()">Replace Text</button>
                            <button type="button" onclick="saveSearch()">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="skiptranslate" style="top:50%; position:fixed;width:62%; ">
            <div class="divElements" title="Show all lines">
                <label>
                    <input type="checkbox" id="idShowLines" value="0" onclick="saveTextArea();createRowsForImageOCR()">Show all Lines
                </label>
            </div>
            <div class="divElements" id="divUpdateTranslations" title="When activated, it allows automatic translations made by Chrome. You write on the left side and the translation on the right side is updated.">
                <label>
                    <input type="checkbox" id="idUpdateTranslations" value="0">Update  &#129034;&#129034;&#129034;
                </label>
            </div>
            <div class="divElementsSlider">
                SizeFont<input type="range" id="idChangeSizeFont" min="0" max="400" value="20">
            </div>
            <br>
            <div class="titletable" id="idTitle1">TEXT OCR </div>
            <div class="titletable" id="idTitle2">IMAGE OCR</div>
            <div class="titletable" id="idTitle3">TRANSLATIONS</div>
            <div class="titletable" id="idTitle4" style="width:auto">Google/Edge</div>
        </div>
		</div>
		<div id="idPanelRight" class="skiptranslate" >
			<div class="divRight">
				<div id="idTextTranslated"> </div>
				
				<div id="idNext" title="ShortCut Key: Page Down" onclick="nextImage()">NEXT</div>
				<div id="IdpageImage">
					<input id="idrangePage" type="range" min="0" value="0"><div id="idNumberImages"> </div>
				</div>
				<div id="idChangeFontPreview" class="divElementsSliderPreview">
                Font Size<input type="range" id="idChangeSizeFontPreview" min="1" max="300" value="100">
				</div>
				<div id="idPrev" title="ShortCut Key: Page Up" onclick="prevImage()">PREV</div>
				<div id="idArrow">
					<font size="36" color="#0000ff">&#8608;</font>
				</div>
				<img id="idViewPortImage"  src="" alt="Image Page" usemap="#workmap" onload="loadAreas()">
				<map id="idMapImageViewport" name="workmap"></map>
			</div>
		</div>
        <SCRIPT language="JavaScript">
            
            var nameImageSelected = "";
            var nameImageSelectedOCR = "";
            var noFilesOCR = listImageOCR.length
            var aTextOCR = new Array(noFilesOCR);
            var aTextTranslated = new Array(noFilesOCR);
            window.onload = onLoad;
			document.body.onkeydown=keyEvent;
			
			function keyEvent(e)
			{
				if (idPanelLeft.style.position == "fixed")
				{
					if (e.target.isContentEditable) return;
					(e.ctrlKey==false && e.altKey==false && e.shiftKey==false && e.code=="ArrowLeft")&&prevImage();
					(e.ctrlKey==false && e.altKey==false && e.shiftKey==false && e.code=="ArrowRight")&&nextImage();
				}
				(e.ctrlKey==false && e.altKey==false && e.shiftKey==false && e.code=="PageUp")&&prevImage();
				(e.ctrlKey==false && e.altKey==false && e.shiftKey==false && e.code=="PageDown")&&nextImage();
				
			}
			function previewImage()
			{
				if (idPanelLeft.style.position != "fixed")
				{
					idArrow.style.display = "none";
					idPanelLeft.style.position = "fixed";
					idPanelRight.style.width = "100%";
					idPanelRight.style.height = "auto";
					idPanelRight.style.position="relative";
					idNext.style.position="fixed";
					idPrev.style.position="fixed";
					IdpageImage.style.position="fixed";
					idTextTranslated.style.display="inline-block"
					idViewPortImage.style.width="100%"
					idChangeFontPreview.style.display = "inline-block";
					idTitlepage.style.display = "none";
					updateDivText();
					loadAreas();
				}
				else
				{
					idChangeFontPreview.style.display = "none";
					idArrow.style.display = "inline-block";
					idTitlepage.style.display = "inline-block";
					//idPanelLeft.style.display = "inline-block";
					idPanelLeft.style.position =""
					idPanelRight.style.width = "35%";
					idPanelRight.style.height = "90%";
					idPanelRight.style.position="fixed";
					idNext.style.position="absolute";
					idPrev.style.position="absolute";
					IdpageImage.style.position="absolute";


					idTextTranslated.style.display="none";
					idViewPortImage.style.width="auto";
					loadAreas();
					
				}
				
			}
			
            function loadAreas() {
                //remove all areas the idMapImageViewport	
                while (idMapImageViewport.hasChildNodes()) {
                    idMapImageViewport.removeChild(idMapImageViewport.firstChild);
                }
                while (idTextTranslated.hasChildNodes()) {
                    idTextTranslated.removeChild(idTextTranslated.firstChild);
                }

                //remove http://zzz/images/07.jpg to 07, is name layer webp,png, gif in Gimp
                var nameImagenRoot = getNameImageViewPortSRC().replace("images/", "")
                for (var i = 0; i < noFilesOCR; i++) {
                    //regex= RegExp(nameImagenRoot+'.*/BTEXT_.*OCRImage',"i");
                    regex = RegExp('(.*)/BTEXT_.*OCRImage', "i");
                    var match = listImageOCR[i].match(regex);
                    if (match) {
                        //Remove ext ".jpg"  (layers in gimp 01.jpg,02.jpg )

                        if (removeExtension(match[1]) == removeExtension(nameImagenRoot) || match[1] == removeExtension(nameImagenRoot)) {
                            var oArea = document.createElement("area");
                            var oText = document.createElement("div");
							var boundBox, sizeFont;
							info = readMapFileInfo(match[0] + ".info");
                            oArea.coords=info.coordXY;
							boundBox=info.boundBox;
                            oArea.shape = "poly";
                            oArea.name = match[0];
                            oArea.onclick = focusTextAreaMap;
                            oArea.style.cursor = "pointer";
                            oArea.onmouseover = mouseOverTextAreaMap;
							oText.setAttribute("name",match[0] );
							oText.style.position="absolute";
							oText.style.whiteSpace="pre-wrap"
							oText.style.width=boundBox[2]-boundBox[0]+"px"
							oText.style.height=boundBox[3]-boundBox[1]+"px"
							oText.style.left=boundBox[0]+"px";
							oText.style.top=boundBox[1]+"px";
							oText.style.border="10px solid black";
							oText.style.textAlign = "center";
							//oText.style.textTransform  = "uppercase";
							oText.style.background="white"
							oText.style.textShadow="-2px -2px 0 white,2px -2px 0 white,-2px 2px 0 white,2px 2px 0 white"
							oText.style.fontSize=info.sizeFont * info.ratio*(idChangeSizeFontPreview.value/100) +"px"
							oText.contentEditable="true"
							oText.onkeyup=function (e){
							nameTTxt = e.target.getAttribute("name") + "-T.txt";
							document.getElementsByName(nameTTxt)[0].value=e.target.innerText;
							}
                            idMapImageViewport.appendChild(oArea);
                            idTextTranslated.appendChild(oText);
                        }
                    }

                }
				updateDivText();
				document.documentElement.scrollTop=1;

            }
            function updateWidthTitle() {
                if (idTableImageOCR.children[0]) {
                    textW = "WIDTHpx".replace("WIDTH", idTableImageOCR.children[0].children[0].offsetWidth);
                    idTitle1.style.width = textW.replace("WIDTH", idTableImageOCR.children[0].children[0].offsetWidth);
                    idTitle2.style.width = textW.replace("WIDTH", idTableImageOCR.children[0].children[1].offsetWidth);
                    idTitle3.style.width = textW.replace("WIDTH", idTableImageOCR.children[0].children[2].offsetWidth);
                    idTitle4.style.width = textW.replace("WIDTH", idTableImageOCR.children[0].children[3].offsetWidth);
                }
            }
            function removeExtension(text) {
                return text.replace(/\.[^.$]+$/, '')
            }
            function mouseOverTextAreaMap(e) {
                e.target.title = document.getElementById(e.target.name + ".png").parentElement.parentElement.children[2].children[0].value;
            }
            function focusTextAreaMap(e) {
                //get name, find cellImageOCR->Row->CellTextArea->TextArea
                document.getElementById(e.target.name + ".png").parentElement.parentElement.children[2].children[0].focus();
            }


            function focusOutAreaText(e) {
                //Change Color not selected row
                e.target.parentElement.parentElement.style.backgroundColor = "transparent"
            }
            function focusAreaText(e) {
                //get name row = name imagen OCR
                var oNodeAreaText = e.target;
                changeImageSelectionOCR(oNodeAreaText.parentElement.parentElement.name)
                //Change Color Selected row
                oNodeAreaText.parentElement.parentElement.style.backgroundColor = "#f0f0f0"
                document.documentElement.scrollTop = oNodeAreaText.offsetParent.offsetTop;
                nameImagen = getNameImageRootChildren(oNodeAreaText.parentElement.parentElement.name)
                changeImageViewPort(nameImagen)
                //get name ID for extract number row
                UpdateTitle(getNumerId(oNodeAreaText.id) + 1, listImageOCR.length)
            }
            function getNumerId(nameID) {
                var myRe = /\d+$/;
                var myArray = myRe.exec(nameID);
                if (myArray)
                    return parseInt(myArray[0]);
                else
                    return 0;
            }
            function updateTranslation(e) {
                idNameTextAreaTranslated = e.target.id.replace("idareatextPreTranslator_", "idareatextTranslated_");
                document.getElementById(idNameTextAreaTranslated).value = e.target.innerText

            }
            function UpdateTitle(number, Total) {
                var elem = document.getElementById("idTitleNumberbar");
                elem.innerHTML = number + "/" + Total;
            }

            function UpdateBar(number, Total) {
                var elem = document.getElementById("myBar");
                var width = (number / Total * 100).toFixed(2);
                elem.style.width = (width > 100 ? 100 : width) + '%';
                width = (number / Total * 100).toFixed(2)
            }

            function disabledComment() {
                if ((document.getElementById("idCheckRegEx").checked))
                    document.getElementById("idSpanComments").style.display = "block";
                else
                    document.getElementById("idSpanComments").style.display = "none";

            }



            function onLoad() {
                
                document.getElementById("idHelpRegEx").addEventListener("change", addExamplesTextArea);
                idChangeSizeFont.addEventListener("change", changeSizeFontAreaText);
                idChangeSizeFontPreview.addEventListener("change", changeSizeFontPreview);
                document.getElementById("idCheckRegEx").addEventListener("change", disabledComment);
                document.getElementById("idAreaTextReplace").value = readFileText("SavedSearch.txt");

                idrangePage.max = listImage.length - 1
                idrangePage.addEventListener("change", function() {
                    changeImageViewPort(listImage[this.value]);
                });
				idrangePage.oninput  = updateRangeText
				updateRangeText()
                nameImageSelected = listImage[0]
                createRowsForImageOCR();


                window.addEventListener('resize', resizeWindows);
                changeImageViewPort(nameImageSelected)
                if (isHTA) {
                    document.getElementById("divUpdateTranslations").style.display = "none"
                    document.getElementById("idTitle4").style.display = "none"
                }
                updateWidthTitle()
            }
            function changeSizeFontAreaText(e) {

				changeSizeFont(e,'.changeFont')
   
            }       
			function changeSizeFontPreview(e) {

				//changeSizeFont(e,'.FontPreview')
				loadAreas();
				
            }
            function changeSizeFont(e,name) {

                changeStyle(name, 'fontSize', e.target.value+"px");
                function changeStyle(selector, prop, val) {
                    var elems = document.querySelectorAll(selector);
                    Array.prototype.forEach.call(elems, function(ele) {
                        ele.style[prop] = val;
                    });
                }

            }
			
			
            function addExamplesTextArea(e) {
                var lineText = "";
                switch (e.target.selectedIndex) {
                case 1:
                    idAreaTextReplace.value = ""
                    return;
                case 2:
                    lineText = "-[\\r\\n]		g	#Join line break separated with(-)";
                    break;

                case 3:
                    lineText = "\\s+	 	g	#Join all lines break and remove spaces";
                    break;

                case 4:
                    lineText = "[ ]+	 	g	#Remove spaces duplicates";
                    break;

                case 5:
                    lineText = "[ ]+		g	#Remove all spaces";
                    break;

                case 6:
                    lineText = "^.{1,3}$		g	#Remove phrase small (3 letters)";
                    break;

                case 7:
                    lineText = "^$		g	#Remove space character special OCR";
                    break;

                case 8:
                    //Remove space begin line
                    lineText = "^[ ]		gm	#Remove space begin line";
                    break;

                case 9:
                    //add a point to the end of the line
                    lineText = "([^.])$	$1.	gm	#add point end line";
                    break;
                default:
                    break;
                }
                addLineTextAreaReplace(lineText);
            }
            function addWordtoReplace() {
                oIdWordSearh = document.getElementById("idWordSearh")
                oIdWordReplaces = document.getElementById("idWordReplaces")
                oIdComments = document.getElementById("idComments")
                oIdCheckRegEx = document.getElementById("idCheckRegEx")

                if (oIdCheckRegEx.checked) {
                    var comments = "";
                    if (oIdComments.value != comments)
                        comments = "\t#" + oIdComments.value

                    lineText = oIdWordSearh.value + "\t" + oIdWordReplaces.value + "\t" + "g" + comments

                } else {

                    lineText = oIdWordSearh.value + "\t" + oIdWordReplaces.value

                }

                addLineTextAreaReplace(lineText)

                oIdWordSearh.focus();
                oIdWordSearh.value = "";
                oIdWordReplaces.value = "";

            }

            function addLineTextAreaReplace(lineText) {
                var textArea = document.getElementById("idAreaTextReplace").value

                if (textArea == "") {
                    textArea = lineText;
                } else {
                    textArea = textArea + "\r\n" + lineText;
                }
                document.getElementById("idAreaTextReplace").value = textArea;
            }

            function selectionRow(e) {
                if (e.target.tagName == "TD") {
                    oNodeCell = e.target
                    oNodeRow = oNodeCell.parentElement
                } else {
                    oNodeCell = e.target.parentElement
                    oNodeRow = oNodeCell.parentElement
                }
                changeImageSelectionOCR(oNodeRow.name)
                nameImagen = getNameImageRootChildren(oNodeRow.name)
                changeImageViewPort(nameImagen)
                //Change Color Selected row
                oNodeRow.style.backgroundColor = "#f0f0f0"
                document.documentElement.scrollTop = oNodeCell.offsetTop;
                //get name ID for extract number cell
                UpdateTitle(getNumerId(oNodeRow.children[0].children[0].id) + 1, listImageOCR.length)

            }
            function createRowsForImageOCR() {
                var cols = 4;
                var fileOCRImage;
                aOTextAreaOCR = []
                aOTextAreaTranslated = []
                while (idTableImageOCR.firstChild) {
                    idTableImageOCR.removeChild(idTableImageOCR.firstChild)
                }
                for (i = 0; i < listImageOCR.length; i++) {
                    fileOCRImage = listImageOCR[i]
                    if ((getNameImageRootChildren(fileOCRImage) != nameImageSelected) && !idShowLines.checked)
                        continue;
                    var row = document.createElement("tr");
                    row.name = fileOCRImage;
                    row.onclick = selectionRow;
                    //row.onmouseenter = function(){changeImageViewPort(this.name) };
                    var preTranslators = document.createElement("div");
                    aDivTranslated.push(preTranslators)
                    preTranslators.className = "PreTranslator"
                    preTranslators.lang = languageSource;
                    for (var c = 0; c < cols; c++) {
                        var cell = document.createElement("td");
                        cell.className = "cellTranslation";

                        if (c == 0 || c == 2) {
                            child = document.createElement("textarea");
                            child.method = "post"
                            child.className = "changeFont"
                            child.setAttribute('form', "idformTextOCRTranslations")
                            child.style.fontSize = idChangeSizeFont.value+"px";
                            child.addEventListener("focus", focusAreaText)
                            child.addEventListener("blur", focusOutAreaText)
                            if (c == 0) //AREA TEXT OCR/SOURCE
                            {
                                nameFileText = fileOCRImage.substr(0, fileOCRImage.lastIndexOf(".")) + ".txt"
                                if (aTextOCR[i] === undefined) {
                                    aTextOCR[i] = readFileText(nameFileText)
                                }
                                child.lang = languageSource
                                child.name = nameFileText;
                                child.value = aTextOCR[i];
                                child.id = "idareatextOCR_" + i;
                                preTranslators.innerText = aTextOCR[i];
                                child.addEventListener("keydown", areaTextListenerSource(preTranslators, child))
                                aOTextAreaOCR.push(child);
                            }
                            if (c == 2) //AREA TEXT TRANSLATED
                            {
                                nameFileText = fileOCRImage.substr(0, fileOCRImage.lastIndexOf(".")) + "-T.txt"
                                if (aTextTranslated[i] === undefined) {
                                    aTextTranslated[i] = readFileText(nameFileText)
                                }
                                child.name = nameFileText
                                child.lang = languageDestiny
                                child.value = aTextTranslated[i];
                                child.id = "idareatextTranslated_" + i;
                                child.style.fontSize = idChangeSizeFont.value+"px";
                                aOTextAreaTranslated.push(child)
                                //observe change in div hidden(made translator) for put areatext
                                divListenerSource(preTranslators, child)
                            }
                        } else if (c == 1) {
                            child = document.createElement("img");
                            child.src = fileOCRImage;
                            child.title = fileOCRImage;
                            child.loading = "lazy"
                            if (isHTA)
                                child.style.width = "30%";
                            child.id = fileOCRImage;
                            //"idImageOCR_"+i;
                        }

                        if (c == 3) {
                            preTranslators.id = "idareatextPreTranslator_" + i;
                            preTranslators.addEventListener("click", updateTranslation)
                            preTranslators.className = "preTranslator"
                            cell.appendChild(preTranslators)
                            //For translators(Google,Bing,Yandex)
                            if (isHTA)
                                cell.style.display = "none"
                        } else {
                            cell.appendChild(child);
                        }
                        row.appendChild(cell)
                    }
                    idTableImageOCR.appendChild(row);
                }

            }
            function getNameImageViewPortSRC() {
                var match = idViewPortImage.src.match(/images.*/g);
                if (match)
                    return match[0]
                else
                    return ""

            }
            function prevImage() {
                var imagePrev = "";
                var indexPrev = 0;
                indexImageActual = listImage.indexOf(getNameImageViewPortSRC())
                if (indexImageActual == 0)
                    indexPrev = listImage.length - 1;
                else if (indexImageActual < 0)
                    return;
                else
                    indexPrev = indexImageActual - 1;
                imagePrev = listImage[indexPrev];
                changeImageViewPort(imagePrev)
            }

            function nextImage() {
                var match = idViewPortImage.src.match(/images.*/g);
                var imageNext = "";
                var indexNext = 0;
                indexImageActual = listImage.indexOf(getNameImageViewPortSRC())
                if (indexImageActual == listImage.length - 1)
                    indexNext = 0;
                else if (indexImageActual < 0)
                    return;
                else
                    indexNext = indexImageActual + 1;
                imageNext = listImage[indexNext];
                changeImageViewPort(imageNext)

            }

            //get name File image 20.jpg/BText_20.jpg #1_OcrImage.png
            function getNameImageRootChildren(nameImagenOCR) {
                //name layer in Gimp ex. 20.jpg
                nameImagenRoot = nameImagenOCR.split("/")[0]

                // compare images/20 in ['images/01.png','images/02.png'...]
                result = listImage.filter(function(n) {
                    if ("images/" + removeExtension(nameImagenRoot) == removeExtension(n))
                        return true
                    else if ("images/" + nameImagenRoot == removeExtension(n))
                        return true
                        // FOR  images/01.png.jpg  
                    else
                        return false
                })
                if (result)
                    return result[0]
            }


            function changeImageViewPort(nameImagen) {

                nameImageSelected = nameImagen
                idrangePage.value = listImage.indexOf(nameImagen)
                if (!idViewPortImage.src.match(nameImagen)) {
                    idViewPortImage.src = nameImagen;
                    saveTextArea();
                    if (!idShowLines.checked)
                        createRowsForImageOCR()
                }
                idNameImage.innerHTML = nameImagen;
				updateRangeText( )
            }
			function updateRangeText( )
			{
				idNumberImages.innerText=(parseInt(idrangePage.value) +1) +"/" + (parseInt(idrangePage.max)+1);
			}
            function changeImageSelectionOCR(nameImagen) {

                //Optimization, no change the image if is same.
                if (!idViewPortImageOCR.src.match(nameImagen)) {

                    idViewPortImageOCR.src = nameImagen;
                }

                //obtain cooordinates balloon empty (top-left - bottom-right)
                nameImageSelectedOCR = nameImagen;
                var x1 = 0
                  , y1 = 0
                  , x2 = 200
                  , y2 = 200;
                text = readFileText(nameImagen.slice(0, -4) + ".info")

                positionLayer = getPositionFileInfo(text)

                aBounds = text.match(/Bounds.*/m);
                if (aBounds) {
                    axy = aBounds[0].match(/[0-9]+/g)
                    x1 = axy[0];
                    y1 = axy[1];
                    x2 = axy[2];
                    y2 = axy[3];
                }
                ratio = idViewPortImage.width / idViewPortImage.naturalWidth;
                offsetx = -48;
                offsety = -2;
                document.getElementById('idArrow').style.top = ((y1 - positionLayer.y) * ratio + offsety) + "px";
                document.getElementById('idArrow').style.left = ((x1 - positionLayer.x) * ratio + offsetx) + "px";
            }

            function readMapFileInfo(fileName) {
                var coordXY=[],boundBox=[0,0,50,100],sizeFont=18;
                var ratio = idViewPortImage.offsetWidth / idViewPortImage.naturalWidth;
                text = readFileText(fileName);
                positionLayer = getPositionFileInfo(text)
                var match = text.match(/\[.*\]/g);
                if (match) {
                    var s = match[0];
                    s = s.substring(2, s.length - 2);
                    coordXY = s.replace(/[() ]/g, "")
                }                
				var mB = text.match(/BoundsBalloon:\( ?(-?\d+), ?(-?\d+), ?(-?\d+), ?(-?\d+)\)/);
                if (mB) {
                    boundBox=[ 
					(parseInt(mB[1])- positionLayer.x)*ratio,
					(parseInt(mB[2])- positionLayer.y)*ratio,
					(parseInt(mB[3])- positionLayer.x)*ratio,
					(parseInt(mB[4])- positionLayer.y)*ratio
					];
                }
				var mF = text.match(/SizeFont:(\d+)/);
				if (mF) {
						sizeFont = parseInt(mF[1]);
                }
                atemp = coordXY.split(",");
                aCoordinates = [];
                for (var i = 0; i < atemp.length; i++) {
                    if (i % 2 == 0)
                        aCoordinates.push((parseFloat(atemp[i]) - positionLayer.x) * ratio)
                    else
                        aCoordinates.push((parseFloat(atemp[i]) - positionLayer.y) * ratio)
                }
                coordXY = aCoordinates.join(",")
                return {coordXY:coordXY,boundBox:boundBox,sizeFont: sizeFont ,ratio:ratio}
            }

            function getPositionFileInfo(text) {
                //position Layer in gimp offset layer image
                aPositionLayer = text.match(/PositionLayer.*/m);
                if (aPositionLayer) {
                    axy = aPositionLayer[0].match(/[0-9]+/g)
                    ix = parseInt(axy[0]);
                    iy = parseInt(axy[1]);
                } else {
                    ix = 0;
                    iy = 0;
                }

                return {
                    x: ix,
                    y: iy,
                };

            }
            function areaTextListenerSource(oDivHidden, oAreaTextSource) {
                var timer = 0;
                return function() {
                    clearTimeout(timer);

                    timer = setTimeout(function() {
                        if (oDivHidden.innerHTML != oAreaTextSource.value)
                            oDivHidden.innerHTML = oAreaTextSource.value
                    }, 1000);
                }

            }
            function divListenerSource(oDivHidden, oAreaTextObjetive) {

                if ("MutationObserver"in window) {
                    var observer = new MutationObserver(function(mutations) {
                        if (idUpdateTranslations.checked) {
                            oAreaTextObjetive.value = mutations[0].target.innerText
							var divPreviewTextTranlated= document.getElementsByName(oAreaTextObjetive.name.slice(0,-6))[0]
							divPreviewTextTranlated.innerText=mutations[0].target.innerText
                            UpdateBar(getNumerId(oAreaTextObjetive.id) + 1, listImageOCR.length)
                        }

                    }
                    );
                    var config = {
                        attributes: true,
                        childList: true,
                        characterData: true
                    }
                    observer.observe(oDivHidden, config);
                }
            }

            function readFileText(fileTxt) {
                sText = "";
                if (isHTA) {
                    var adTypeText = 2;
                    var stream = new ActiveXObject("ADODB.Stream");
                    stream.Type = adTypeText;
                    stream.Charset = "utf-8";
                    stream.Open();
                    stream.LoadFromFile(decodeURIComponent(fileTxt));
                    sText = stream.ReadText();
                    stream.close();
                } else {
                    var client = new XMLHttpRequest();
                    client.open('GET', fileTxt, false);
                    try {
                        client.send(null);
                        //if(client.status === 200)
                        sText = client.responseText
                    } catch (error) {
                        sText = error;
                    }
                }
                return sText
            }
            function readFileTextASync(fileTxt, oElement) {
                var client = new XMLHttpRequest();
                client.open('GET', fileTxt, true);
                client.onload = function() {
                    if (oElement.tagName == "TEXTAREA")
                        oElement.value = client.response;
                    else if (oElement.tagName == "PRE")
                        oElement.innerText = client.response;
                }
                ;
                client.send();
            }

            function writeFilelocal(file, data) {
                if (data == "")
                    data = "";
                //Bug when data is empty to WriteText?
                var adTypeBinary = 1;
                var adTypeText = 2;
                var adSaveCreateOverwrite = 2;
                var stream = new ActiveXObject("ADODB.Stream");
                stream.Type = adTypeText;
                stream.Charset = "utf-8";
                stream.Open();
                stream.WriteText(data);
                stream.SaveToFile(file, 2);
                stream.close();
            }
            function saveSearch(text) {
                if (isHTA) {
                    writeFilelocal(decodeURIComponent("SavedSearch.txt"), idAreaTextReplace.value);
                } else {
                    submitForm(document.getElementById("idmyFormSaveSearch"), false);
                    //
                }

            }

            function updateDivText() {
                for (i = 0; i < aOTextAreaTranslated.length; i++) {
                    elementT = document.getElementsByName( aOTextAreaTranslated[i].name.slice(0,-6))
					if (elementT[0])
					{
						if (aOTextAreaTranslated[i].value!="")
						{
							elementT[0].style.display = 'inline-block';
							elementT[0].innerHTML=aOTextAreaTranslated[i].value
						}
						else
						{
							elementT[0].style.display = 'none';
						}
					
					}
                }

            } 
			function saveTextArea() {
                for (i = 0; i < aOTextAreaTranslated.length; i++) {
                    aTextOCR[getNumerId(aOTextAreaOCR[i].id)] = aOTextAreaOCR[i].value
                    aTextTranslated[getNumerId(aOTextAreaTranslated[i].id)] = aOTextAreaTranslated[i].value
                }

            }
            function SaveFiles() {
                saveTextArea()
                if (!isHTA)
                    var formData = new FormData();
                for (var i = 0; i < noFilesOCR; i++) {
                    try {
                        fileOCRImage = listImageOCR[i];
                        nameFileOCR = fileOCRImage.substr(0, fileOCRImage.lastIndexOf(".")) + ".txt"
                        nameFileTranslated = fileOCRImage.substr(0, fileOCRImage.lastIndexOf(".")) + "-T.txt"
                        if (aTextOCR[i] !== undefined) {

                            if (isHTA)
                                writeFilelocal(decodeURIComponent(nameFileOCR), aTextOCR[i]);
                            else
                                formData.append(nameFileOCR, aTextOCR[i]);

                        }

                        if (aTextTranslated[i] !== undefined) {

                            if (isHTA)
                                writeFilelocal(decodeURIComponent(nameFileTranslated), aTextTranslated[i]);
                            else
                                formData.append(nameFileTranslated, aTextTranslated[i]);

                        }

                    }
                    catch (error) {
                        alert("Error save File:" + error)
                        break;
                    }
                }
                if (isHTA) {
                    writeFilelocal("ok.txt", "ok");
                    //Flag Ok
                    window.close();
                } else {
                    //document.getElementById("myForm").submit();
                    formData.append("ok.txt", "ok");
                    submitFormData(formData, true);

                }
            }
            function submitFormData(formData, bClose) {
                var xhr = new XMLHttpRequest();
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        if (bClose) {
                            window.close();
                        }
                    } else
                        alert(xhr.responseText);
                }
                // success case
                xhr.onerror = function() {
                    alert("Error save file :" + xhr.responseText);
                }
                // failure case
                xhr.open("POST", document.URL, true);
                xhr.send(formData);
                return 0;
            }
            function submitForm(oFormElement, bClose) {
                var xhr = new XMLHttpRequest();
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        if (bClose) {
                            window.close();
                        }
                    } else
                        alert(xhr.responseText);
                }
                // success case
                xhr.onerror = function() {
                    alert("Error save file :" + xhr.responseText);
                }
                // failure case
                xhr.open(oFormElement.method, oFormElement.action, true);
                xhr.send(new FormData(oFormElement));
                return false;
            }
            function closeHTA() {
                close();
            }

            function resizeWindows() {
                loadAreas();
                updateWidthTitle();
            }

            function replaceText() {
                var bRadioOCR = false;
                var bradioSelected = false;
                var ele = document.getElementsByTagName('input');
                for (i = 0; i < ele.length; i++) {
                    if (ele[i].type == "radio") {
                        if (ele[i].checked) {
                            if (ele[i].value == "OCR")
                                bRadioOCR = true;
                            if (ele[i].value == "Selected")
                                bradioSelected = true;
                        }
                    }
                }
                for (i = 0; i < aOTextAreaTranslated.length; i++) {
                    if (bradioSelected && nameImageSelectedOCR.slice(0, -4) != aOTextAreaOCR[i].name.slice(0, -4))
                        continue;
                    if (bRadioOCR) {
                        //aOTextAreaOCR[i].focus();
                        var sText = replaceRegEx(aOTextAreaOCR[i].value)
                        if (aOTextAreaOCR[i].value != sText) {
                            aOTextAreaOCR[i].value = sText;
                            nameidDivHidden = aOTextAreaOCR[i].id.replace("idareatextOCR_", "idareatextPreTranslator_")
                            oDivHidden = document.getElementById(nameidDivHidden);
                            oDivHidden.innerHTML = aOTextAreaOCR[i].value;
                        }
                    }
                    else {
                        aOTextAreaTranslated[i].value = replaceRegEx(aOTextAreaTranslated[i].value);
                    }
                    if (bradioSelected)
                        break;
                }

                function replaceRegEx(text) {
                    textFindReplace = document.getElementById("idAreaTextReplace").value
                    var lines = textFindReplace.split(String.fromCharCode(10));
                    //NEW LINE /n bug python export backslash
                    for (var i = 0; i < lines.length; i++) {
                        var tabsText = lines[i].split(String.fromCharCode(9));
                        // tab /t
                        len = tabsText.length;
                        if (len == 2) {
                            text = text.replaceAll(tabsText[0], tabsText[1]);
                        }
                        else if (len >= 3) {
                            flags = tabsText[2].toLowerCase();

                            if (RegExp('[^gim]', "g").test(flags))
                                flags = "g"

                            try {
                                text = text.replace(new RegExp(tabsText[0],flags), tabsText[1]);
                            } catch (e) {}
                        }

                    }
                    return changeCase(text);
                }
                function changeCase(text) {
                    var select = document.getElementById('idChangeCase');
                    switch (select.selectedIndex) {
                    case 1:
                        //lowercase
                        text = text.toLowerCase()
                        break;

                    case 2:
                        //UPPERCASE
                        text = text.toUpperCase()
                        break;

                    case 3:
                        //Capitalize
                        text = text.toLowerCase().replace(/( [a-záéíóú])/g, function(a) {
                            return a.toUpperCase()
                        })
                        break;

                    case 4:
                        //Sentence
                        text = text.toLowerCase().replace(/^[a-záéíóú]|[?!.] [a-záéíóú]/gm, function(a) {
                            return a.toUpperCase()
                        })
                        break;
                    }
                    return text;
                }
            }
            String.prototype.replaceAll = function(search, replacement) {
                var target = this;
                return target.split(search).join(replacement);
            }
            ;
        </script>
    </BODY>
</HTML>
"""
languagueCode = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'Chinese - Simplified',
    'zh-tw': 'Chinese - Traditional',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'English',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'French',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'German',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'Korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'Portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'Spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
}
languageOCR = {
    "afr": "Afrikaans",
    "sqi": "Albanian",
    "amh": "Amharic",
    "grc": "Ancient Greek",
    "ara": "Arabic",
    "asm": "Assamese",
    "aze_cyrl": "Azerbaijani (Alternate)",
    "aze": "Azerbaijani",
    "eus": "Basque",
    "bel": "Belarusian",
    "ben": "Bengali",
    "bos": "Bosnian",
    "bul": "Bulgarian",
    "mya": "Burmese",
    "cat": "Catalan",
    "ceb": "Cebuano",
    "khm": "Central Khmer",
    "chr": "Cherokee",
    "chi_sim": "Chinese - Simplified",
    "chi_tra": "Chinese - Traditional",
    "hrv": "Croatian",
    "ces": "Czech",
    "dan_frak": "Danish (Alternate)",
    "dan": "Danish",
    "nld": "Dutch",
    "dzo": "Dzongkha",
    "eng": "English",
    "epo": "Esperanto",
    "est": "Estonian",
    "fin": "Finnish",
    "frk": "Frankish",
    "fra": "French",
    "glg": "Galician",
    "kat_old": "Georgian (Old)",
    "kat": "Georgian",
    "deu_frak": "German (Alternate)",
    "deu": "German",
    "ell": "Greek",
    "guj": "Gujarati",
    "hat": "Haitian",
    "heb": "Hebrew",
    "hin": "Hindi",
    "hun": "Hungarian",
    "isl": "Icelandic",
    "inc": "Indic",
    "ind": "Indonesian",
    "iku": "Inuktitut",
    "gle": "Irish",
    "ita_old": "Italian (Old)",
    "ita": "Italian",
    "jpn": "Japanese",
    "jpn_vert": "Japanese Vert",
    "jav": "Javanese",
    "kan": "Kannada",
    "kaz": "Kazakh",
    "kir": "Kirghiz",
    "kor": "Korean",
    "kru": "Kurukh",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "mkd": "Macedonian",
    "msa": "Malay",
    "mal": "Malayalam",
    "mlt": "Maltese",
    "mar": "Marathi",
    "equ": "Math/Equations",
    "enm": "Middle English (1100-1500)",
    "frm": "Middle French (1400-1600)",
    "nep": "Nepali",
    "nor": "Norwegian",
    "ori": "Odiya",
    "pan": "Panjabi",
    "fas": "Persian",
    "pol": "Polish",
    "por": "Portuguese",
    "pus": "Pushto",
    "ron": "Romanian",
    "rus": "Russian",
    "san": "Sanskrit",
    "srp": "Serbian",
    "sin": "Sinhala",
    "slk_frak": "Slovak (Alternate)",
    "slk": "Slovak",
    "slv": "Slovenian",
    "spa_old": "Spanish (Old)",
    "spa": "Spanish",
    "srp_latn": "srp_latn",
    "swa": "Swahili",
    "swe": "Swedish",
    "syr": "Syriac",
    "tgl": "Tagalog",
    "tgk": "Tajik",
    "tam": "Tamil",
    "tel": "Telugu",
    "tha": "Thai",
    "bod": "Tibetan",
    "tir": "Tigrinya",
    "tur": "Turkish",
    "uig": "Uighur",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "uzb_cyrl": "Uzbek (Alternate)",
    "uzb": "Uzbek",
    "vie": "Vietnamese",
    "cym": "Welsh",
    "yid": "Yiddish"
}
languageOCRAvaible = ("Not Found Languages",)
def writeFileUTF(pathFile,Text):
    try:
        if not os.path.exists(os.path.dirname(pathFile)):
            os.makedirs(os.path.dirname(pathFile))
        f = codecs.open(pathFile,"w", encoding='utf-8')
        f.write(Text)
        f.close()
    except Exception as e:
        pdb.gimp_message("Error WRITE:"  + str(traceback.format_exc()) + CARRIAGERETURN + pathFile + CARRIAGERETURN + Text )    
def readFileUTF(pathFile):
    try:
        f = codecs.open(pathFile, encoding='utf-8-sig')
        Text = f.read()
        f.close()
        return Text
    except Exception as e:
        pdb.gimp_message("ERROR READ:" +  str(traceback.format_exc())  )    
        return ""
def loadFileINI():
    def findINI(section,stringFind,default=""):
        if configINI.has_option(section, stringFind):
            return configINI.get(section, stringFind).strip(r'"')
        else:
            return default
    def removeQuotes(s):# remove " quotes 
        return s.strip(r'"').strip()
        # return s.encode('unicode_escape').decode()
    def strTobool(s):
        if s.lower() == 'True'.lower():
             return True
        elif s.lower() == 'False'.lower():
             return False 
        else:
            return False 
    global g_nameEngineOCRs,g_programOCR,g_pathTessdata,g_argsOCR,g_noiseWaifu2x,g_scaleWaifu2x,\
    g_port,g_ip,g_typeFont,g_sizeFont,g_bHocr,\
    g_divisions,g_reductionIrregular,g_thresholdBW,g_areaSelection,g_minLengthCharacter,g_notRemoveImageDetection,g_lettersOCR,g_listWordsSplitImage,\
    g_bMessageToConsole,g_aSelectionEditor,g_navigators,g_translationweb
    
    for s in [ss for ss in configINI.sections() if ss.startswith("OCR")]:
        if configINI.has_option(s, "programocr"):
            p=findINI(s, "programocr")
            if p and os.path.exists(p):
                g_nameEngineOCRs.append(s)
                g_programOCR.append  (p )  
                g_pathTessdata.append(findINI(s, "pathtessdata") )
                g_argsOCR.append     (findINI(s, "argsocr") )

    if not g_nameEngineOCRs:
        g_nameEngineOCRs=["ERROR NOT FOUND ENGINE/OCR"]
    
    g_navigators={}
    
    for s in [ss for ss in configINI.sections() if ss.startswith("NAVIGATOR")] :
        if configINI.has_option(s, "programweb"):
            p=findINI(s, "programweb")
            if p and os.path.exists(p):
                g_navigators["Edit " + s.title() ]= [ p,findINI(s, "optionsweb") ]

    #'deepl', 'google', 'libre', 'linguee', 'microsoft', 'mymemory', 'papago', 'pons', 'qcri', 'yandex', SOME REQUIRED KEYS
    for s in [ss for ss in configINI.sections() if ss.startswith("TRANSLATOR")] :
        if configINI.has_option(s, "programtranslator"):
            p=findINI(s, "programtranslator")
            if p and os.path.exists(p):
                g_translators.append( [ p,findINI(s, "optionstranslator") ] )

    for s in [ss for ss in configINI.sections() if ss.startswith("TRANSLATOR")] :
        if configINI.has_option(s, "programtranslator"):
            p=findINI(s, "programtranslator")
            if p and os.path.exists(p):
                g_translators.append( [ p,findINI(s, "optionstranslator") ] )

    for s in [ss for ss in configINI.sections() if ss.startswith("REPLACE OCR")] :
        for i in configINI.items(s):
            nameLang=s.replace("REPLACE OCR","").strip().lower() 
            if "filetext" in i[0] and i[1]:
                g_replaceOCR.append( [nameLang,removeQuotes(i[1]),False] )
            elif "fileregex" in i[0] and i[1]:
                g_replaceOCR.append( [nameLang,removeQuotes(i[1]),True] )

    for s in [ss for ss in configINI.sections() if ss.startswith("REPLACE TRANSLATION")] :
        for i in configINI.items(s):
            nameLang=s.replace("REPLACE TRANSLATION","").strip().lower() 
            if "filetext" in i[0] and i[1]:
                g_replaceTarget.append( [nameLang,removeQuotes(i[1]),False] )
            elif "fileregex" in i[0] and i[1]:
                g_replaceTarget.append( [nameLang,removeQuotes(i[1]),True] )


    for s in [ss for ss in configINI.sections() if ss.startswith("WAIFU2X")] :
        if configINI.has_option(s, "programwaifu2x"):
            p=findINI(s, "programwaifu2x")
            if p and os.path.exists(p):
                g_Waifu2X.append( [ p ,findINI(s, "argswaifu2x"),findINI(s, "pathmodelswaifu2x") ] )
    
    g_aSelectionEditor=["none","Edit HTA/IE","Edit Subtitle(ASS)"]+list(g_navigators.keys())
        
     
    pC.indexEngineOCR = int ( findINI("SAVEDPLUGIN","engineocr",0) )
    pC.bWaifu2x = strTobool ( findINI("SAVEDPLUGIN","waifu2x","False") )
    pC.indexLanguageOCR = int ( findINI("SAVEDPLUGIN","languageocr",0) )
    pC.iOrientation = int ( findINI("SAVEDPLUGIN","orientation",0) )
    pC.indexFix = int ( findINI("SAVEDPLUGIN","indexFix",0) )
    pC.caseOCR = int ( findINI("SAVEDPLUGIN","caseocr",0) )
    pC.bTranslation = strTobool ( findINI("SAVEDPLUGIN","translation","False") )
    pC.caseTranslation = int ( findINI("SAVEDPLUGIN","casetranslation",0) )
    pC.indexLanguageTranslation = int ( findINI("SAVEDPLUGIN","languagetranslation",0) )
    pC.pathProyect =  findINI("SAVEDPLUGIN","pathProyect","")
    pC.indexEditor = int ( findINI("SAVEDPLUGIN","editor",1) )
    pC.iFilterBorder = float ( findINI("SAVEDPLUGIN","filterborder",1) )
    pC.bColorBalloonAutomatic = strTobool ( findINI("SAVEDPLUGIN","colorballoonautomatic","False") )
    if not os.path.exists(pC.pathProyect):
        pC.pathProyect = tempfile.gettempdir()
    
    
    g_ip = findINI("CONFIGURATION","ip","127.0.0.1")
    g_typeFont = findINI("CONFIGURATION","font","Arial")
    g_translationweb = findINI("CONFIGURATION","translationweb","")
    g_sizeFont = int(findINI("CONFIGURATION","sizefont",28))
    g_port= int( findINI("CONFIGURATION","port",8000) )
    g_scaleWaifu2x= int( findINI("CONFIGURATION","scalewaifu2x",2) )
    g_noiseWaifu2x= int( findINI("CONFIGURATION","noisewaifu2x",3) )
    
    g_notExportedImage= int( findINI("DEBUG","notexportedimage",0) )
    g_notOCR= int( findINI("DEBUG","notocr",0) )
    g_bHocr = bool( int( findINI("DEBUG","hocr",True) ) )
    g_notRemoveImageDetection = bool(  int( findINI("DEBUG","notremoveimagedetection",0) ) )
    g_bMessageToConsole= bool(int(findINI("DEBUG","messageconsole",0)))
    
    g_divisions = int( findINI("DETECTIONAUTOMATIC","divisions",2) )
    g_reductionIrregular = int( findINI("DETECTIONAUTOMATIC","reductionirregular",30) )
    g_thresholdBW = float( findINI("DETECTIONAUTOMATIC","thresholdbw",0.95) )
    g_areaSelection = int( findINI("DETECTIONAUTOMATIC","areaselection",4) )
    g_minLengthCharacter = int( findINI("DETECTIONAUTOMATIC","minlengthcharacter",4) )
    g_lettersOCR = findINI("DETECTIONAUTOMATIC","lettersocr","")
    g_listWordsSplitImage = findINI("DETECTIONAUTOMATIC","wordsocr","").split(",")
def saveFileINI():
    if not configINI.has_section("SAVEDPLUGIN"):
        configINI.add_section("SAVEDPLUGIN")
    configINI.set('SAVEDPLUGIN', 'engineocr', pC.indexEngineOCR)
    configINI.set('SAVEDPLUGIN', 'waifu2x', pC.bWaifu2x)
    configINI.set('SAVEDPLUGIN', 'languageocr', pC.indexLanguageOCR)
    configINI.set('SAVEDPLUGIN', 'orientation', pC.iOrientation)
    configINI.set('SAVEDPLUGIN', 'indexFix', pC.indexFix)
    configINI.set('SAVEDPLUGIN', 'caseocr', pC.caseOCR)
    configINI.set('SAVEDPLUGIN', 'translation', pC.bTranslation)
    configINI.set('SAVEDPLUGIN', 'casetranslation', pC.caseTranslation)
    configINI.set('SAVEDPLUGIN', 'languagetranslation', pC.indexLanguageTranslation)
    configINI.set('SAVEDPLUGIN', 'pathproyect', pC.pathProyect)
    configINI.set('SAVEDPLUGIN', 'editor', pC.indexEditor)
    configINI.set('SAVEDPLUGIN', 'filterborder', pC.iFilterBorder)
    configINI.set('SAVEDPLUGIN', 'colorballoonautomatic', pC.bColorBalloonAutomatic)
    with codecs.open(g_pathFileINI,"w", encoding='utf-8') as f:    # save
        configINI.write(f)    
def showFiles(path):
    sCommand = r'start explorer.exe ' + path
    subprocess.call(sCommand, shell=True)
def dialogBox(text):
            try:
                import gtk
                label = gtk.Label(text)
                dialog = gtk.Dialog("Warning",None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,gtk.STOCK_OK, True))
                dialog.vbox.pack_start(label)
                label.show()
                response = dialog.run()
                dialog.destroy()
                if response == 1:
                    return True
                else:
                    return False
            except:
                pdb.gimp_message('not gtk/only for validation in process duplicates')
                return False
def selectionListGUI(listS):
    try:
        if not listS:return listS
        import gtk
        listSelected=[]
        ls = gtk.ListStore(str)
        for lk in listS:
            ls.append([lk])
        # fillList(image,ls) 
        scroll=gtk.ScrolledWindow()
        tv = gtk.TreeView(ls)
        col = gtk.TreeViewColumn("name", gtk.CellRendererText(), text=0)
        tv.set_reorderable(True)
        col.set_sort_column_id(0)
        tv.append_column(col)
        sel = tv.get_selection()
        sel.set_mode(gtk.SELECTION_MULTIPLE)
        sel.select_all()
        dialog = gtk.Dialog("Selection list",None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,gtk.STOCK_OK, True))
        dialog.resize(400, 400)
        scroll.add_with_viewport(tv)
        scroll.show()
        dialog.vbox.pack_start(scroll)
        tv.show()
        response = dialog.run()
        (model, pathlist) = sel.get_selected_rows()
        dialog.destroy()
        if not response==True:
            return []
        for path in pathlist :
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter,0)
            listSelected.append(value)
        return listSelected
    except:
         pdb.gimp_message('not gui/gtk, not posibility selection')
         return listS
def valueDictionary(dictionary,valuetofind):
    v = [key for key, value in dictionary.items() if value.upper() == valuetofind.upper()]
    if len(v)>0:
        return v[0]
    else:
        return ""
def changeCaseText(text,indexCase):
    if aSelectionCase[indexCase]=="lowercase":
        return text.lower()
    elif aSelectionCase[indexCase]=="UPPERCASE":
        return text.upper()
    elif aSelectionCase[indexCase]=="Capitalize":
        return text.capitalize()
    elif aSelectionCase[indexCase]=="Sentence":
        return re.sub(r"^\w|[?!.] \w",lambda x:x.group(0).upper(),text.lower(),flags=re.M)
    else:
        return text
def automaticSelection():
    def divisions(divisions):
        hDivision = int( layer.height/divisions )
        for i in range(divisions):
            layerNew = pdb.gimp_layer_copy(layer,False)
            layerNew.name=g_imageTemp
            pdb.gimp_image_insert_layer(g_imageActive, layerNew, None, 0)
            pdb.gimp_drawable_threshold(layerNew, 0, g_thresholdBW, 1)
            if (divisions>1):
                pdb.gimp_selection_none(g_imageActive)
                pdb.gimp_image_select_rectangle(g_imageActive, 2, 0, hDivision*i, layer.width, hDivision)
                pdb.gimp_selection_invert(g_imageActive)
                pdb.gimp_edit_fill(layerNew, FILL_WHITE)
                pdb.gimp_selection_none(g_imageActive)
            nameImageExported=layerNew.name
            pathImageExportedLayer = os.path.join(g_pathProyectWeb_Images,layerNew.name+g_ExtensionOCR)
            exporterImage(g_imageActive,layerNew,pathImageExportedLayer,layerNew.name)
            imagetoOCR(pathImageExportedLayer,True,11,True)
            translationFile(os.path.splitext(pathImageExportedLayer)[0]+TXT)
            pathFileOCR = pathImageExportedLayer.replace(g_ExtensionOCR,".hocr")
            readHOCROnlyLetter(pathFileOCR,layerNew,points)
            pdb.gimp_image_remove_layer(g_imageActive, layerNew)
        if os.path.exists(pathImageExportedLayer) and not g_notRemoveImageDetection:
            os.remove( pathImageExportedLayer )
        if os.path.exists(pathFileOCR) and not g_notRemoveImageDetection:
            os.remove( pathFileOCR )
    for layer in g_imageActive.layers:
        points=[]
        divisions(1)
        if g_divisions>1:
            divisions(g_divisions)
        if(len(points)>0):
            selectionToPathPoints(layer,points) 
def readHOCROnlyLetter(pathFile,layer,points):
    if os.path.exists(pathFile):
        tree = ET.parse(pathFile)
        streamXML = readFileUTF(pathFile)
        root = tree.getroot()
        nameSpace = root.tag.replace("}html","}") #xmlns="http://www.w3.org/1999/xhtml"
        i=0
        for word in root.iter( nameSpace + 'span'):#required namespace for find class
            if word.get("class")=='ocrx_word':
                text = "".join(word.itertext())
                # if (not re.search(r"[^A-Z?!]",text) and len(text)>=g_minLengthCharacter) or text in g_listWordsSplitImage :
                if (len(text)>=g_minLengthCharacter) or text in g_listWordsSplitImage :
                    i=i+1
                    c =  word.get("title").split() #bbox 264 1292 387 1335
                    points.append( [ c[1],c[2], text] )
def selectionToPathPoints(layer,points):
    xOffset,yOffset =layer.offsets
    pdb.gimp_context_set_sample_threshold_int(g_areaSelection)
    color=None
    for p in points:
        x=int(p[0])
        y=int(p[1])
        t=p[2]
        gen = ((j, i) for i in range(0,50,3) for j in range(0,50,3))
        for i, j in gen: #prevent areas dark
            if(x+i>layer.width or y+j>layer.height):
                break;
            try: 
                color = pdb.gimp_color_picker(g_imageActive, layer, x+i+xOffset, y+j+yOffset, False, False, 1)#get position image, not layer
                if sum(color[:-1])>g_thresholdWhiteBalloon:
                    if g_bMessageToConsole: pdb.gimp_message("POINT TEXT:{} x={},y={} : x+i={} y+j={} ".format(t,x,y,x+i,y+j ))
                    break
                else:
                    if g_bMessageToConsole: pdb.gimp_message("POINT DARK:{:.0%} x={},y={} : x+i={} y+j= {}  {} ".format(1-sum(color[:-1])/765.0,x,y,x+i,y+j, t ))
            except Exception as e:
                if g_bMessageToConsole: pdb.gimp_message("Error: x={}, y= {}".format( x+i+xOffset, y+j+yOffset) )
                break
        if color:
            pdb.gimp_image_select_contiguous_color(g_imageActive, 0, layer, x+i, y+j)
            
    if g_areaSelection==0: return
    # pdb.gimp_selection_grow(g_imageActive, 0)
    # pdb.gimp_selection_shrink(g_imageActive, 0)
    pdb.gimp_selection_flood(g_imageActive)
    if g_reductionIrregular>0:
        pdb.gimp_selection_shrink(g_imageActive, g_reductionIrregular)
        pdb.gimp_selection_grow(g_imageActive, g_reductionIrregular)
    if pdb.gimp_selection_is_empty(g_imageActive):
        return
    selectionToVector(layer)
def selectionToVector(layer):
    pdb.plug_in_sel2path(g_imageActive,None)
    # pdb.plug_in_sel2path_advanced(g_imageActive, None, 0.5, 60, 4, 100, 0.4, 1, 10, 60, 0.5, 3, 3, 0, 0.010,0.5,0.01,1, 0.1, 4, 0.03, 3)
    
    num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)
    for idVector in vector_ids:
        oVector = gimp._id2vectors(idVector)
        if not oVector:continue
        if oVector.name.find(TAGPATHSTROKE)==0: continue
        oVectorOld = pdb.gimp_image_get_vectors_by_name(g_imageActive,TAGPATHSTROKE+layer.name)
        if oVectorOld:
            pdb.gimp_image_remove_vectors(g_imageActive, oVectorOld)
        oVector.name= TAGPATHSTROKE + layer.name
    pdb.gimp_selection_none(g_imageActive)
def generateFilesWeb(pathImagesOCR):
    #FOR ORDER FIRST IMAGE ".jpg_OCRimage"  ".jpg #1" 
    pathImagesOCR = [w.replace('%20%23', '_ZZZ%20%23') for w in pathImagesOCR]
    pathImagesOCR = natural_sort(pathImagesOCR,False)
    pathImagesOCR = [w.replace('_ZZZ%20%23', '%20%23') for w in pathImagesOCR]
    varJS = u'var languageSource="{}";var languageDestiny="{}";'\
    .format(g_srcCodeLanguage if g_translationweb=="" else g_translationweb, g_targetCodeLanguage)
    varJS = varJS + u"var listImageOCR = ['{}']; var listImage = ['{}'];".format(  "','".join(pathImagesOCR)  ,  "','".join(  natural_sort(set(g_pathListImages),False)  ) )
    writeFileUTF(  os.path.join(g_pathProyectWeb , "ListFilesImage.js" )  ,varJS)
    fileSaveSearch=os.path.join(g_pathProyectWeb , "SavedSearch.txt")
    if not os.path.exists(fileSaveSearch):
        writeFileUTF(fileSaveSearch,"ListWordsSeparated\tByTab\r\nWord search\tWords replaced")
def natural_sort(l,Reverse=False): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key, reverse=Reverse)
def loadProyect():
    def importMaskSVG(pathFileSVG):
        nameMask=file + "_Mask"
        layerMask=pdb.gimp_image_get_layer_by_name(g_imageActive,nameMask)
        if (layerMask):
            return
        if os.path.exists(pathFileSVG):
            layerFile=pdb.gimp_image_get_layer_by_name(g_imageActive,file)

            #make layer based color background
            buffer_name = pdb.gimp_edit_named_copy(layerFile, "TEMPIMAGE")
            imageMask = pdb.gimp_edit_named_paste_as_new_image(buffer_name)
            pdb.gimp_layer_add_alpha(imageMask.layers[0])
            pdb.gimp_buffer_delete(buffer_name)
            pdb.gimp_selection_all(imageMask)
            pdb.gimp_drawable_edit_clear(imageMask.layers[0])# Make Transparent
            # pdb.gimp_selection_none(imageMask)
            parentLayer=pdb.gimp_item_get_parent(layerFile)
            for layerB in parentLayer.layers:
                if layerB.name.startswith("BText") and not layerB.name.endswith("_TEXT"):
                    pdb.gimp_item_set_visible(layerB, True)
                    buffer_name = pdb.gimp_edit_named_copy(layerB, "ColorBackground")
                    layer_copy = pdb.gimp_layer_new_from_drawable(layerB, imageMask)
                    pdb.gimp_image_insert_layer(imageMask, layer_copy, None, 0)
                    pdb.gimp_buffer_delete(buffer_name)
                    pdb.gimp_item_set_visible(layerB, False)
                    # pdb.gimp_message(layerB.name)
            layerMerge = pdb.gimp_image_merge_visible_layers(imageMask, 1)
            layerMergeTemp = pdb.gimp_layer_new_from_drawable(layerMerge, g_imageActive)
            pdb.gimp_image_insert_layer(g_imageActive, layerMergeTemp, None, 0)
            pdb.gimp_image_delete(imageMask)
            
            #create selection based file SVG
            pdb.gimp_selection_none(g_imageActive)
            num_vectors, vectors_ids = pdb.gimp_vectors_import_from_file(g_imageActive, pathFileSVG, False, False)
            for idVector in vectors_ids:
                oVector = gimp._id2vectors(idVector)
                if oVector is None: continue
                #gimp_image_select_item has Bug add selection (intersections)
                # pdb.gimp_image_select_item(g_imageActive, CHANNEL_OP_ADD, oVector)
                
                path_type, path_closed, num_path_point_details, points_pairs = pdb.gimp_path_get_points(g_imageActive, oVector.name )
                #[x0,y1,Control0,x1,y1,Control1....]
                pointsXYC=[points_pairs[0+9*n:3+9*n] for n in range(0,len(points_pairs)/9)]
                aCoordsXY=[]
                for p in pointsXYC: 
                    if p[2]==3:#Is point new and path last is closed/terminated (2 Point coltrol, 1 PointXY)
                        pdb.gimp_image_select_polygon(g_imageActive, 0, len(aCoordsXY), aCoordsXY)
                        aCoordsXY=[]
                    aCoordsXY.extend([p[0],p[1]])
                if(aCoordsXY):
                    pdb.gimp_image_select_polygon(g_imageActive, 0, len(aCoordsXY), aCoordsXY)
                
                pdb.gimp_selection_flood(g_imageActive)
                
            
            # floating_sel = pdb.gimp_edit_named_paste(layerMask, buffer_name, 1)
            # pdb.gimp_floating_sel_anchor(floating_sel)
            
            
            buffer_name = pdb.gimp_edit_named_copy(layerMergeTemp, "ColorBackground")
            layerMask = pdb.gimp_edit_named_paste(layerFile, buffer_name, 1)
            layerMask.name=nameMask
            pdb.gimp_buffer_delete(buffer_name)
            pdb.gimp_image_remove_layer(g_imageActive, layerMergeTemp)
            # buffer_name = pdb.gimp_edit_named_copy(layerBackground, "BackgroundText")
            # pdb.gimp_edit_fill(layerMask, FILL_WHITE)
            pdb.gimp_selection_none(g_imageActive)
    def importTreeLayer(pathLayer):
        for r, d, f  in os.walk(pathLayer):
            aXY=[]
            layer=None
            for file in natural_sort(f,False):
                name,ext = os.path.splitext(file)
                if ext.lower() in [".info"]:
                    pdb.gimp_progress_pulse()
                    nameLayerBalloonfile = file.replace("_OcrImage.info","")
                    # pdb.gimp_message(nameLayerBalloonfile)
                    if pdb.gimp_image_get_layer_by_name(g_imageActive,nameLayerBalloonfile):
                        continue
                    
                    fInfo=open(os.path.join(r,file), "r")
                    infoText=fInfo.read()
                    fInfo.close()
                    coordsXY = re.findall("\[\((.*)\)\]",infoText)
                    if not coordsXY:
                        pdb.gimp_message("Problem format coords XY in " + file + " : " + infoText)
                        continue
                    aCoordsXY = re.sub("[()]", "", coordsXY[0]).split(",")
                    if(len(aCoordsXY)<4):
                        pdb.gimp_message("Points insufficients " + file + " : " + str(aCoordsXY))
                        continue
                    backG = re.search("ColorBackground:rgba(.*)",infoText)
                    
                    colorBackground=(255,255,255,255)
                    colorFont=(0,0,0,255)
                    if backG:
                        # pdb.gimp_message(backG.group(1))
                        colorBackground = eval( backG.group(1) )
                    
                    pdb.gimp_context_set_foreground( colorBackground )
                    
                    layer=pdb.gimp_image_get_layer_by_name(g_imageActive,os.path.basename(r))

                    pdb.gimp_image_select_polygon(g_imageActive, 2, len(aCoordsXY), aCoordsXY)
                    buffer_name = pdb.gimp_edit_named_copy(layer, "TEMP")
                    floating_sel = pdb.gimp_edit_named_paste(layer, buffer_name, 1)
                    pdb.gimp_buffer_delete(buffer_name)
                    floating_sel.name=nameLayerBalloonfile
                    fileImage = os.path.join(r,file.replace(".info",".png"))
                    if not os.path.exists( fileImage ):
                        exporterImage(g_imageActive,floating_sel, fileImage  ,"")
                    pdb.gimp_edit_fill(floating_sel, FILL_FOREGROUND)
                    aXY.append(aCoordsXY)
                    loadText(   os.path.join(r,file.replace(".info","-T.txt") ) )
                    
                    if layerMask:
                        pdb.gimp_item_set_visible(floating_sel, False)
                else:
                    continue
            # For save Rute/Paths()
            if(aXY and layer):
                for xy in aXY:
                    pdb.gimp_image_select_polygon(g_imageActive, CHANNEL_OP_ADD, len(xy), xy)
                selectionToVector(layer)
    def fixName(name): #remove double ext .png.jpg to .png
        if re.search(r"\..{1,5}\.jpg$",name):
            name=re.sub('\.jpg$', '', name)
        return name
    
    nameLayersForImage=[]
    gimp.progress_init("LOADING")
    files = filter(lambda x: os.path.isfile( os.path.join(g_pathProyectWeb_Images,x) ),  os.listdir(g_pathProyectWeb_Images))
    for file in selectionListGUI(natural_sort(files,True)):
        pdb.gimp_progress_pulse()
        pathImage= os.path.join(g_pathProyectWeb_Images,file)
        nameLayersForImage.append(file)
        file = fixName(file)
        layerImage = pdb.gimp_image_get_layer_by_name(g_imageActive,file)
        if not layerImage:
            layerImage = pdb.gimp_file_load_layer(g_imageActive, pathImage)
            pdb.gimp_image_insert_layer(g_imageActive, layerImage, None, 0)
            layerImage.name= fixName(layerImage.name)
        if not pdb.gimp_item_get_parent(layerImage):
            layerGroup = pdb.gimp_image_get_layer_by_name(g_imageActive,TAGPREFIXGROUP + file)
            if not layerGroup:
                layerGroup = pdb.gimp_layer_group_new(g_imageActive)
                layerGroup.name = TAGPREFIXGROUP + file
                g_imageActive.add_layer(layerGroup,0)
            pdb.gimp_image_reorder_item(g_imageActive, layerImage, layerGroup, 99999)
            pdb.gimp_image_resize_to_layers(g_imageActive)
            layerMask=pdb.gimp_image_get_layer_by_name(g_imageActive,file + "_Mask")
            importTreeLayer(os.path.join(g_pathProyectWeb,file))
            if layerMask:
                position = pdb.gimp_image_get_layer_position(g_imageActive, layerImage)
                pdb.gimp_image_reorder_item(g_imageActive, layerMask, layerGroup, position-1)
            importMaskSVG( os.path.join(g_pathProyectWeb,"paths", file + ".svg" ) )
            # pdb.gimp_image_remove_layer(g_imageActive, layerGroup)
    

    pdb.gimp_progress_end() 
def obtainNamesLayers(selection):
    # 0 Layer selected
    # 1 All layers/Curves 
    
    num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)
    nameLayers =[]
    #find layers name = PathStroke _PS_Name
    for idVector in vector_ids:
        oVector = gimp._id2vectors(idVector)
        if oVector is None: continue
        if oVector.name.find(TAGPATHSTROKE)==0:
            nameLayerPath = oVector.name.replace(TAGPATHSTROKE,"")
        else:
            #rename all path stroke
            oVectorOld= pdb.gimp_image_get_vectors_by_name(g_imageActive, TAGPATHSTROKE + g_activeLayer.name)
            if oVectorOld is not None:
                pdb.gimp_image_remove_vectors(g_imageActive, oVectorOld)
            #rename Path Stroke
            oVector.name = TAGPATHSTROKE + g_activeLayer.name
            nameLayerPath = g_activeLayer.name
        layer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerPath) 
        if layer is None:
            continue
        if selection==0 and nameLayerPath == g_activeLayer.name:
            nameLayers = [nameLayerPath]
        elif selection==1:
            if nameLayerPath in nameLayers:
                continue
            else:
                nameLayers.append(nameLayerPath)
    return nameLayers
def applyInfoText(textTranslation,nameLayerBalloonEmpty,fileInfo):
        infoText = readFileUTF(fileInfo)
        font_size=g_sizeFont
        layerBalloonEmpty = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerBalloonEmpty)
        if not layerBalloonEmpty:
            if g_bMessageToConsole:
                pdb.gimp_message("Not Found Layer:{}".format(nameLayerBalloonEmpty) )
            return
        pdb.gimp_image_set_active_layer(g_imageActive, layerBalloonEmpty)
        layerGroup = pdb.gimp_item_get_parent(layerBalloonEmpty)
        cXb1, cYb1 = layerBalloonEmpty.offsets# Balloon Empty
        cXb2 = cXb1 + layerBalloonEmpty.width
        cYb2 = cYb1 + layerBalloonEmpty.height
        #define position pixels globals width and height text box
        cXTxt1=cXb1
        cYTxt1=cYb1
        cXTxt2=cXb2
        cYTxt2=cYb2
        
        #position image OCR (PARENT)
        # coordXY=re.findall("(\d+)\.\d+, (\d+)\.\d+",text)
        b = re.search("bbox_(\d+)_(\d+)_(\d+)_(\d+)",infoText)#coord local BOX text OCR(Tesseract)
        if b is not None:
            x1,y1,x2,y2 = b.groups()
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)#coord local BOX text
            if pC.bWaifu2x:#IMPORTANT: fix position waifu2X for Scale
                x1,y1,x2,y2 = int(x1/g_scaleWaifu2x),int(y1/g_scaleWaifu2x),int(x2/g_scaleWaifu2x),int(y2/g_scaleWaifu2x)
            x1G,y1G,x2G,y2G = cXb1+x1, cYb1+y1, cXb1+x2, cYb1+y2 #coord global text in Imagen(Full)
            cXTxt1=x1G
            cYTxt1=y1G
            #for ajust position, pendient
            # xleft = max([int(x) for x,y in coordXY if int(x)<x1G])
            # yleft = min([int(y) for x,y in coordXY if int(y)>y1G])
            # xright = min([int(x) for x,y in coordXY if int(x)>x2G])
            # yright = max([int(y) for x,y in coordXY if int(y)<y2G])

            #align smart
            if (1):
                xcenterlocal=int((cXb2-x1G)/2)
                ycenterlocal=int((cYb2-y1G)/2)
                cXTxt1 = cXb1 + int(layerBalloonEmpty.width/2) -  xcenterlocal 
                cXTxt2 = cXb1 + int(layerBalloonEmpty.width/2) +  xcenterlocal
                cYTxt1 = cYb1 + int(layerBalloonEmpty.height/2) -  ycenterlocal 
                cYTxt2 = cYb1 + int(layerBalloonEmpty.height/2) +  ycenterlocal 
        f = re.search("(?:fn_|SizeFont:)(\d+)",infoText)
        if f is not None:
            font_size = int(f.group(1))
            if pC.bWaifu2x:#fix Scale waifu2X
                font_size = ((font_size/g_scaleWaifu2x)*1.3)
        
        colorFont=(0,0,0,255)
        cFont = re.search("ColorFont:rgba(.*)",infoText)
        if cFont:
            colorFont = eval( cFont.group(1) )

        nameLayerText = layerBalloonEmpty.name + "_TEXT"
        layerText = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerText)
        if not layerText:
            layerText = addLayerText(nameLayerText,font_size,cXTxt1,cYTxt1,cXTxt2,cYTxt2,layerGroup)
            pdb.gimp_text_layer_set_color(layerText, colorFont)
        if ( pdb.gimp_item_is_text_layer(layerText) ):
            pdb.gimp_text_layer_set_text(layerText, textTranslation)
        else:
            pdb.gimp_message("Not set text for:" + layerText.name )
def loadText(fileTranslated):
    pattern = "(" + BText + ".*?)_OcrImage"   
    m = re.search(pattern,fileTranslated) #FIND BText###_
    if m:
        nameLayerBalloonEmpty = m.group(1)
        # if layerText is not None:
            # if(textTranslation==""):
            # textTranslation = "NOT OCR/TRANSLATION"
        textTranslation = readFileUTF(fileTranslated)
        # pdb.gimp_message(nameLayerBalloonEmpty)
        applyInfoText(textTranslation,nameLayerBalloonEmpty,fileTranslated.replace("-T.txt",".info"))
def exportImageSelectioned(nameLayer):
    #activeLayer is layer active for path 
    colorBalloon = (255,255,255)
    activeLayer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayer)
    if activeLayer is not None:
        pdb.gimp_image_set_active_layer(g_imageActive, activeLayer)
    else:
        if g_bMessageToOConsole: pdb.gimp_message("Not found layer: " + nameLayer)
        return None, None
        
    layerGroup = pdb.gimp_item_get_parent(activeLayer)
    if not layerGroup:
        layerGroup = pdb.gimp_image_get_layer_by_name(g_imageActive, TAGPREFIXGROUP + nameLayer)
        if not layerGroup:
            pdb.gimp_message("Not find group;")
    
        
        
    non_empty, Coordx1, Coordy1, Coordx2, Coordy2 = pdb.gimp_selection_bounds(g_imageActive)
    if not non_empty:
        if g_bMessageToConsole: pdb.gimp_message("Not Selection for:" + nameLayer) 
        return None, None
    else:
        if Coordx2-Coordx1<10:
            if g_bMessageToConsole:  pdb.gimp_message("Filter Selection small 10:" + str(Coordx2-Coordx1)  ) 
            return None, None
    #get color Balloon Dialogue
    try:
        xColor, yColor = getPositionSelection(g_imageActive, Coordx1, Coordy1, Coordx2, Coordy2)
    except Exception as e:
        pdb.gimp_message("Error position Selection:"  + str(traceback.format_exc()) +  str(Coordx1) + str(Coordy1) + str(Coordx2) + str(Coordy2))   
    if pC.bColorBalloonAutomatic:
        try:        
            colorBalloon = pdb.gimp_image_pick_color(g_imageActive, activeLayer, xColor, yColor, False, False, 0)
            # remove alpha (1,1,1,1) for sum color
            if sum(colorBalloon[:-1])>g_thresholdWhiteBalloon: 
                colorBalloon = (255,255,255) #white
        except Exception as e:
            pdb.gimp_message("Error image_pick_color:%s \r\n %s"%(activeLayer.name, str(e))) 
    buffer_name="OCRIMAGE"
    # pdb.gimp_edit_copy_visible(g_imageActive)
    #ADD BACKGROUND TO IMAGE FOR OCR AND FOR GLOBE TEXT EMPTY TO IMAGE
    buffer_name = pdb.gimp_edit_named_copy(activeLayer, buffer_name)
    # pdb.gimp_edit_copy(activeLayer)
    # imageSelection=pdb.gimp_edit_paste_as_new_image()
    imageSelection=pdb.gimp_edit_named_paste_as_new_image(buffer_name)
    layer_GlobeText = pdb.gimp_layer_new_from_drawable(imageSelection.layers[0], g_imageActive)
    layer_GlobeText.name = BText + "_"+ unicode(activeLayer.name) #Name Baloon Text
    pdb.gimp_image_insert_layer(g_imageActive, layer_GlobeText, layerGroup, 0)
    # pdb.gimp_layer_set_lock_alpha(layer_GlobeText, True)
    #set color background of Balloon (frame-square)
    layer_Background = pdb.gimp_layer_copy(imageSelection.layers[0], False)
    pdb.gimp_context_set_opacity(100)#overwrite changes user for prevent 
    pdb.gimp_context_set_paint_mode(0)#overwrite changes user for prevent 
    pdb.gimp_context_set_background(colorBalloon)
    pdb.gimp_drawable_fill(layer_Background, FILL_BACKGROUND)
    pdb.gimp_image_insert_layer(imageSelection, layer_Background, None, 1)

    layerMerge = pdb.gimp_image_merge_visible_layers(imageSelection, CLIP_TO_IMAGE)
    #EXPORT IMAGE
    pathImageRelative = os.path.join(activeLayer.name , layer_GlobeText.name + "_"+ g_nameFileImageOCR)
    pathImageOCR =os.path.join( g_pathProyectWeb , pathImageRelative)
    
    exporterImage(imageSelection,layerMerge,pathImageOCR,g_nameFileImageOCR)
    pdb.gimp_layer_set_offsets(layer_GlobeText, Coordx1, Coordy1)
    # pdb.gimp_context_set_background(colorBalloon)
    pdb.gimp_drawable_edit_fill(layer_GlobeText, FILL_BACKGROUND)
    #Color background image-OCR
    colorBackup = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(colorBackup)
    pdb.gimp_image_delete(imageSelection)
    pdb.gimp_buffer_delete(buffer_name)
    if pC.bWaifu2x and g_Waifu2X:
        pathFullProgram = os.path.join(g_PathPlugin , g_Waifu2X[0][0])
        if not os.path.exists( pathFullProgram ):
            pathFullProgram = g_Waifu2X[0][0]
        if (not os.path.exists(g_Waifu2X[0][2]) ):
            pathModels = os.path.dirname( pathFullProgram)
        else:
            pathModels=g_Waifu2X[0][2]
        
        sCommand=r'{program} -i "{input}" -o "{output}" {args}'.format(program=pathFullProgram,input=pathImageOCR,output=pathImageOCR,  args=g_Waifu2X[0][1].format(g_noiseWaifu2x,g_scaleWaifu2x)  )
        commandSTR(sCommand,pathModels)
    return pathImageRelative,(Coordx1, Coordy1, Coordx2, Coordy2)
def exporterImage(image,layer,pathFile,name):
    try:
        if g_notExportedImage:
            return
        if not os.path.exists(os.path.dirname(pathFile)):
            os.makedirs(os.path.dirname(pathFile))    
        if os.path.splitext(pathFile)[1] == g_ExtensionOCR:
            pdb.file_png_save(image, layer, pathFile,name, 0,5, 0, 0, 0, 0, 0)
        else:
            pdb.gimp_file_save(image,layer,pathFile,name)
    except Exception as e:
        pdb.gimp_message("Error save image exported" + pathFile + " : \r\n" + str(traceback.format_exc()))
        return None
def addLayerText(nameLayerText,font_size, Coordx1,Coordy1,Coordx2,Coordy2,layerGroup):
    #ADD LAYER TEXT
    layerText = pdb.gimp_text_layer_new(g_imageActive,"--IN PROGRESS OCR/TRANSLATION--", g_typeFont, g_sizeFont, 0)
    layerText.name = nameLayerText
    pdb.gimp_image_insert_layer(g_imageActive, layerText, layerGroup, -1)
    pdb.gimp_layer_set_offsets(layerText, Coordx1, Coordy1)
    pdb.gimp_text_layer_resize(layerText, Coordx2-Coordx1, Coordy2-Coordy1)
    pdb.gimp_text_layer_set_color(layerText, g_colorFont)
    pdb.gimp_text_layer_set_justification(layerText, TEXT_JUSTIFY_CENTER)
    pdb.gimp_text_layer_set_font_size(layerText, font_size, PIXELS)
    return layerText
def getPositionSelection(g_imageActive, Coordx1, Coordy1, Coordx2, Coordy2):
    for y in range (Coordy1+8,Coordy2,2):
        for x in range(Coordx1+8,Coordx2,2):
            # is in selection
            inArea = pdb.gimp_selection_value(g_imageActive, x, y)
            if (inArea == 255):
                return x,y
    return 0,0
def commandSTR(sCommand,sPath):#only use function after dialog window main 
    try:
        process = subprocess.Popen(sCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=sPath)
        output=process.communicate()
        if( process.returncode!=0):
            pdb.gimp_message("----- ERROR  -----")
            pdb.gimp_message("COMAND: " + sCommand)
            pdb.gimp_message("PATH: " + sPath)
            pdb.gimp_message(str(output[1]))
    except Exception:
        pdb.gimp_message("----- ERROR POPEN -----" )
        pdb.gimp_message( str( sys.exc_info() ) )
        pdb.gimp_message("Command:" + str(sCommand) )
        pdb.gimp_message("Path:" + str(sPath) )
def imagetoOCR(fileImageForOCR,bHocr=True,pOrientation=None,automaticSelection=False):
    Command=""
    try:
        if(pC.indexLanguageOCR==-1):
            return "Error:Select a language for OCR"
            
        fileOCROutput = os.path.splitext(fileImageForOCR)[0]
        fileHocr = fileOCROutput + HOCR
        if os.path.exists(fileHocr):
            os.remove( fileHocr )
        # fileOCROutput = fileImageForOCR.replace(g_ExtensionOCR,"")
        destLanguageOcr = valueDictionary( languageOCR, languageOCRAvaible[pC.indexLanguageOCR] )
        destLanguageFullOcr = languageOCRAvaible[pC.indexLanguageOCR]
        iOrientation=3 #default for Tesseract
        OrientationVertical=""
        
        if pC.iOrientation==1:
            iOrientation=6
        elif pC.iOrientation==2:
            iOrientation=5
            OrientationVertical="--vertical"
        if pOrientation:
            iOrientation=pOrientation
        delimiter = "|"
        argsCommand=Template(g_argsOCR[pC.indexEngineOCR].replace(" ",delimiter)).safe_substitute(\
        PATHTESSDATA=g_pathTessdata[pC.indexEngineOCR],\
        NAMEFILEIMAGEOCR=fileImageForOCR,\
        NAMEFILEOUTOCR=fileOCROutput,\
        ORIENTATION=iOrientation,\
        DESTLANGUAGEOCR=destLanguageOcr,\
        DESTLANGUAGEFULLOCR=destLanguageFullOcr,\
        ORIENTATIONVERTICAL = OrientationVertical
        )
        Command = [g_programOCR[pC.indexEngineOCR]]
        Command.extend( argsCommand.strip().split(delimiter) )
        if (automaticSelection and g_lettersOCR!=""):
            Command.insert(-1,"-c")
            Command.insert(-1,"tessedit_char_whitelist=" + g_lettersOCR)
        if bHocr==False:
            if u"hocr" in Command:
                Command.remove(u"hocr")
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=g_PathPlugin)
        output = process.communicate()
        if( process.returncode!=0):
            # fix problems errors training tesseract
            if(output[1].find("IntDotProductSSE")>0):
                Command.insert(-1,"--oem")
                Command.insert(-1,"0")
                process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=g_PathPlugin)
                output = process.communicate()
        
        if( process.returncode!=0):
            pdb.gimp_message(str(output[1]))
            return output[1]    
        if g_bRepeatOCR:
            fixOCR(fileOCROutput)
    except Exception as e:
        pdb.gimp_message("Error OCR:" + str(traceback.format_exc()) )
        pdb.gimp_message("Error Command:" + str(Command) )
def imageOCRInfoText(fileImageForOCR, positionLayer,boundsBalloonEmpty, pointsSelection = [(0,0)] ):# [(0,0),(454,121)...] 
    imagetoOCR(fileImageForOCR,g_bHocr)
    fileOCROutput = os.path.splitext(fileImageForOCR)[0] 
    try:
        readHOCR(fileOCROutput,positionLayer,boundsBalloonEmpty,pointsSelection)
        fixOCR(fileOCROutput)
    except Exception as e:
        pdb.gimp_message("Error OCR:" + str(traceback.format_exc()) )
    translationFile(fileOCROutput+TXT)    
def fixOCR(fileOCROutput):
    OCRText = readFileUTF(fileOCROutput+TXT)
    #FIX TESSERACT 4.1 END FILE
    OCRText = re.sub(r"", "", OCRText, flags=re.UNICODE)
    
    if pC.indexFix==1:
        OCRText = OCRText.replace("-\r\n", "")#remove guion for conti- nuation
        OCRText = re.sub(r"\s+", " ", OCRText, flags=re.UNICODE)
    
    OCRText = changeCaseText(OCRText,pC.caseOCR)
    
    if pC.indexFix in (2,4): #Fix OCR of List or Fix OCR/Tranlation of List
        OCRText=replaceCharacters(g_listReplaceOCR,OCRText)


    # if (0):
        # subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(OCRText.encode("UTF-16"))
    

    
    writeFileUTF(fileOCROutput + TXT,OCRText)
    if (not g_bRepeatOCR):
        writeFileUTF(fileOCROutput + "-T" + TXT,OCRText)
    if g_bMessageToConsole: pdb.gimp_message(fileOCROutput + "\r\n" + OCRText)
def listReplace(aReplace,lang): # [lang, Path, Text/Regex]
    listR=[]
    for r in [rr for rr in aReplace if rr[0].lower()==lang.lower()] :
        if os.path.exists(r[1]):
            text=readFileUTF(r[1])
            for line in text.splitlines():
                words=line.split("\t")
                if len(words)>=2:
                    listR.append([words[0],words[1],r[2]])
    return listR
def replaceCharacters(listC,text):
    for lr in listC:
        if lr[2]:
            try:
                text=re.sub(lr[0],lr[1],text)
            except Exception as e:
                pdb.gimp_message('Error in Regular expression: "{}"  -> "{}"'.format(lr[0],lr[1]) )
                pdb.gimp_message(str(traceback.format_exc()))
        else:
            text=text.replace(lr[0],lr[1])
    return text
def translationFile(fileOCR):
    fileT=fileOCR.replace(".txt","-T.txt")
    textTranslation="Not Found Translation"
    if pC.bTranslation:
        try:
            # shlex.split(g_translators[0][1], posix=False)
            process=subprocess.Popen(
            [g_translators[0][0],"--langsource" ,g_srcCodeLanguage ,"--langtarget" , g_targetCodeLanguage ,"--filesource" ,fileOCR], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output=process.communicate()
            textTranslation = output[0].decode("UTF-8")
            if( process.returncode!=0):
                pdb.gimp_message("----- ERROR  TRANSLATION-----")
                pdb.gimp_message(str(output[1]))
                return "Error: Translation"
        except Exception as e:
            pdb.gimp_message("Error Translation" + str(traceback.format_exc()) )
            return "Error: Translation"
    else:
        textTranslation=readFileUTF(fileT)
        
    if pC.indexFix==3 or pC.indexFix==4:#Fix Translation of List or Fix OCR/Tranlation of List
        textTranslation = replaceCharacters(g_listReplaceTarget,textTranslation)
    
    textTranslation = changeCaseText(textTranslation,pC.caseTranslation)
    writeFileUTF(fileT,textTranslation)
    if g_bMessageToConsole: pdb.gimp_message(textTranslation)
def readHOCR(pathFile,positionLayer,boundsBalloonEmpty,pointsSelection):
    OCRText = ""
    size=0
    sizeFont=""
    bbox=""
    lines=""
    if os.path.exists(pathFile + ".hocr"):
        tree = ET.parse(pathFile + ".hocr")
        streamXML = readFileUTF(pathFile + ".hocr")
        x_size = re.findall("x_size (\d+)", streamXML, re.U)
        if x_size != []:
            x_size = list(map(lambda x: int(x) , x_size))#convert number unicode [u'1234',] a int [1234,]
            size = sum(x_size)/len(x_size) 
        if size>5:
            sizeFont= "\r\n" + "SizeFont:"+str(size)

        m = re.search("id=.block.*?(bbox \d+ \d+ \d+ \d+)", streamXML, flags=re.IGNORECASE)
        if m :
            bbox =  m.group(1)
            bbox = bbox.replace(" ","_")

        textXML = re.findall(r"<span.*?>(.*?)</span>",streamXML)


        # OCRText = "".join(tree.getroot().itertext())
        root = tree.getroot()
        nameSpace = root.tag.replace("}html","}") #xmlns="http://www.w3.org/1999/xhtml"
        for word in root.iter( nameSpace + 'span'):#required namespace for find class
            if word.get("class")=='ocr_line':
                OCRText = OCRText + CARRIAGERETURN
            else:
                OCRText = OCRText + "".join(word.itertext()) + " " # word.text fail tags aditionals <strong></strong> 
        OCRText = re.sub(r"\s\s+",CARRIAGERETURN,OCRText).strip()
        
        aLines = re.findall("class=.ocr_line.*?(bbox \d+ \d+ \d+ \d+)", streamXML, flags=re.IGNORECASE)
        lines = CARRIAGERETURN + CARRIAGERETURN.join(aLines)
        #fix space start and end
        OCRText = OCRText.strip()
        #fix lines empty (only space)
        OCRText = re.sub("\r\n *\r\n",CARRIAGERETURN,OCRText) 
        #fix &#39; '
        OCRText = HTMLParser.HTMLParser().unescape(OCRText)
        writeFileUTF(pathFile + TXT,OCRText)
    writeFileUTF(pathFile + ".info","PositionLayer:"+str(positionLayer) + CARRIAGERETURN + "BoundsBalloon:"+str(boundsBalloonEmpty) + CARRIAGERETURN + bbox + sizeFont + lines + CARRIAGERETURN + str(pointsSelection)   )
def editOCR(selectedEditor):
    outputOCR=""
    translation=""
    # destLanguageOcr = [key for key, value in languageOCR.items() if value == languageOCRAvaible[pC.indexLanguageOCR]][0]
    # srcLanguage= "sp" + str(pC.indexLanguageOCR)
    PathHTA = os.path.join(g_pathProyectWeb , g_namePageHTML)
    writeFileUTF(PathHTA,sHTA)
    if  selectedEditor == "Edit HTA/IE":
        Command = ["start","/wait",'mshta',PathHTA]
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=g_pathProyectWeb)
        process.communicate()
    elif selectedEditor.startswith("Edit Navigator"):
        webServer(selectedEditor)
    elif selectedEditor == "Edit Subtitle(ASS)":
        filePathASS =os.path.join(g_pathProyectWeb,g_fileASS)
        filePathAVS =os.path.join(g_pathProyectWeb,g_fileAVS)
        editSubtitleAss(filePathASS,filePathAVS)
        timeLastModification = os.path.getmtime(filePathASS)
        Command = ["start","/wait","Title Subtitle",filePathASS]
        subprocess.call(Command,shell=True,cwd=g_pathProyectWeb)
        if os.path.getmtime(filePathASS)>timeLastModification:
            exportTXTSubtitle(filePathASS)
    else:
        return
def editSubtitleAss(filePathASS,filePathAVS):
    #FOR Subtitle Aegisub, and video AVS
    count=0
    fwAss =open(filePathASS,"wb")
    fwAss.write(headASS)
    fwAvs =open(filePathAVS,"wb")
    fwAvs.write(headAVS)

    for r, d, f  in os.walk(g_pathProyectWeb):
        for file in f:
            name,ext = os.path.splitext(file)
            if file.endswith(g_nameFileImageOCR):
                fileOCR = os.path.join(r,name+TXT)
                fileTranslation = os.path.join(r,name + T_TXT)
                textOCR = readFileUTF(fileOCR).replace("\r\n",r"\N").replace("\n",r"\N")
                textTranslation = readFileUTF(fileTranslation).replace("\r\n",r"\N").replace("\n",r"\N")
                begin = time.strftime("%H:%M:%S", time.gmtime(count))
                end= time.strftime("%H:%M:%S", time.gmtime(count+1))
                sDialogue = r"Dialogue: 0,{}.00,{}.00,{},{}/{},0,0,0,,{}".format(begin,end,"OCR",os.path.basename(r),name,textOCR)
                fwAss.write(sDialogue + CARRIAGERETURN)
                sDialogue = r"Dialogue: 0,{}.00,{}.00,{},{}/{},0,0,0,,{}".format(begin,end,"Translate",os.path.basename(r),name,textTranslation)
                fwAss.write(sDialogue + CARRIAGERETURN)
                sImage=r'+ImageOCR("{}")\ '.format(  os.path.join(  os.path.basename(r),file )   )
                fwAvs.write(sImage + CARRIAGERETURN)
                count+=1
    fwAvs.write(CARRIAGERETURN + "ConvertToRGB32()")
    fwAvs.close()
    fwAss.close()
def exportTXTSubtitle(filePathASS):
    fh = open( filePathASS )
    while True:
        line = fh.readline()
        if not line:
            break
        g = re.search("Dialogue.*?(OCR|Translate),(.*),0,0,0,,(.*)",line)
        if g:
            if (g.group(1)=="Translate"):
                ext=T_TXT
            elif(g.group(1)=="OCR"):
                ext=TXT
            else:
                break
            nameFile = g.group(2)+ext
            contentText = g.group(3).replace(r"\N","\r\n")
            # if(contentText==""):
                # pdb.gimp_message(nameFile)
            writeFileUTF(os.path.join(g_pathProyectWeb,nameFile),contentText)
        # check if line is not empty
    fh.close()
    writeFileUTF(os.path.join(g_pathProyectWeb,OK) ,"OK")    
def webServer(selectedEditor):
    import socket;
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((g_ip,g_port))
    sock.close()
    if result != 0:
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer((g_ip, g_port), StoreHandler)
        thread = threading.Thread(None, httpd.serve_forever)
        thread.start()
        sCommand=r'start /wait "Title Web" "{program}" {ip}:{port} {options}'.format(program=g_navigators[selectedEditor][0] ,ip=g_ip, port=g_port, options=g_navigators[selectedEditor][1])
        process = subprocess.call(sCommand, shell=True)
        httpd.shutdown()
        httpd.server_close()
        thread.join()
    else:
        pdb.gimp_message( "Error: port in use:{} change a other port".format(g_port) )
class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
        try:
            for name in form.keys():
                nameFile = os.path.join(g_pathProyectWeb , urllib.url2pathname(name))
                with open(nameFile,"wb") as f:
                    f.write(form[name].value)
            self.respond("OK Saved")
        except Exception as e:
            self.send_error(500,'ERROR:%s %s'%(str(traceback.format_exc()),file) )
            pdb.gimp_message(traceback.format_exc())
        return

    def do_GET(self):
        if self.path=="/":
            self.path=g_namePageHTML
        try:
            #Check the file extension required and
            #set the right mime type
            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".htm"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".txt"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".ico"):
                mimetype='image/ico'
                sendReply = True
            if self.path.endswith(".png"):
                mimetype='image/png'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            if self.path.endswith(".info"):
                mimetype='text/css'
                sendReply = True
            if sendReply == True:
                #decoding spaces of URL
                selfpath = urllib.url2pathname( self.path.lstrip("/") )
                #Open the static file requested and send it
                file = os.path.join(g_pathProyectWeb , selfpath)
                with open(file,'rb') as f:
                    response = f.read()
                self.respond(response,mimetype,200)
            else:
                self.respond("Unknown request extension",status=404)
        except Exception as e:
            self.send_error(500,'ERROR:%s File=%s SelfPah=%s'%(str(e),file, self.path) )
    def tryAgain_response(self,status,retries=0):
        if retries > 3:  raise NameError('Error Send Status: %s'%status)
        try:self.send_response(status)
        except: self.tryAgain_response(retries+1)
    def respond(self, response,mimetype="text/html", status=200):
        self.protocol_version = 'HTTP/1.1'
        self.tryAgain_response(status)
        self.send_header("Content-type",mimetype)
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)
def waitThreading(threads):
    for th in threads:
        if threading.activeCount() <= g_limitThreads:
            break;
        th.join()
        threads.remove(th)
def bubbleOCR(*args):
    pdb.gimp_image_undo_group_start(args[0])
    # pdb.gimp_image_undo_disable(args[0])
    processBalloonText(*args)
    # pdb.gimp_image_undo_enable(g_imageActive)
    pdb.gimp_image_undo_group_end(g_imageActive)  
def processBalloonText(Img, Drawable,indexSelectionMain,indexEngineOCR,bWaifu2x,indexLanguageOCR,oOrientation,indexFix,caseOCR,bTranslation,caseTranslation,indexLanTrans,nameDocument,pathProyect,indexEditor,iFilterBorder,bColorBalloonAutomatic):
        
    global g_imageActive,g_activeLayer,g_pathProyectWeb,g_pathProyectWeb_Images,g_pathListImages,\
    g_colorFont,g_nameDocument,g_bRepeatOCR,g_srcCodeLanguage,g_targetCodeLanguage,g_srcLanguage,g_targetLanguage
    
    selectionOptionMain = aSelectionMain[indexSelectionMain]
    pC.indexEngineOCR = indexEngineOCR
    pC.bWaifu2x=bWaifu2x
    pC.iFilterBorder=iFilterBorder
    pC.indexEditor=indexEditor
    pC.indexFix=indexFix
    pC.bTranslation=bTranslation
    pC.caseTranslation=caseTranslation
    pC.caseOCR = caseOCR
    pC.iOrientation = oOrientation
    pC.indexLanguageTranslation = indexLanTrans
    pC.bColorBalloonAutomatic = bColorBalloonAutomatic
    pC.indexLanguageOCR = indexLanguageOCR
    
    g_colorFont=(0.0, 0.0, 0.0)#colorFont
    g_srcLanguage = languageOCRAvaible[pC.indexLanguageOCR];
    g_srcCodeLanguage = valueDictionary(languagueCode,g_srcLanguage.replace(" Vert",""));
     # = languagueCode.items()[indexLanTrans][0];
    g_targetLanguage = sorted(languagueCode.values())[indexLanTrans];
    g_targetCodeLanguage = languagueCode.keys()[languagueCode.values().index(g_targetLanguage)]
    
    # languagueCode.items()[indexLanTrans][1];
    selectedEditor = g_aSelectionEditor[pC.indexEditor]

    bEditText=False
    nameLayers =[]
    pathImagesOCR=[]
    pC.pathProyect = pathProyect 
    g_nameDocument = nameDocument
    g_pathProyectWeb = os.path.join(pC.pathProyect , g_nameDocument )
    g_pathProyectWeb_Images = os.path.join(g_pathProyectWeb,"images")
    g_imageActive = Img #get imageActive gimp active
    g_activeLayer = pdb.gimp_image_get_active_layer(g_imageActive) #get layer selected
    
    if "ERROR" in g_nameEngineOCRs[indexEngineOCR]:
        pdb.gimp_message("Download tesseract or check installation in file:" + g_pathFileINI)
        subprocess.call(r"start https://github.com/UB-Mannheim/tesseract/wiki", shell=True)
        subprocess.call(r"start " + g_pathFileINI, shell=True)
        return
    
    if pC.bWaifu2x and not g_Waifu2X:
        pC.bWaifu2x=False
        pdb.gimp_message("Not Found Program for Super-Resolution and noise reduction (Waifu2x):" + g_Waifu2X[0][0])
    if pC.bTranslation and not g_translators:
        pC.bTranslation=False
        pdb.gimp_message("Not Found Program Translation" )
    if selectionOptionMain == "Refresh Languages OCR Engine":
        saveFileINI()
        return
    if selectionOptionMain == "Edit Config File INI":
        Command = ["start","/wait","File configuration",g_pathFileINI]
        subprocess.call(Command,shell=True)
        return
    if selectionOptionMain == "Show Files Proyect":    
        showFiles(g_pathProyectWeb)
        return
    if selectionOptionMain == "Show Files Plugins":    
        showFiles(g_PathPlugin)
        return

    g_listReplaceOCR.extend( listReplace(g_replaceOCR, g_srcLanguage) )
    g_listReplaceTarget.extend( listReplace(g_replaceTarget, g_targetLanguage) )
        
    if selectionOptionMain in ["Selection Automatic","Process Full"]:#BETA FOR DETECTION AUTOMATIC(LETTERS) WITH TESSERACT
        automaticSelection()
        if selectionOptionMain == "Selection Automatic":
            saveFileINI()
            return

    if selectionOptionMain in ["Process All layers/Path","Process Full"]:
        num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)
        if num_vectors==0:
            pdb.gimp_message("Not found Paths/Curves")
            return
        if os.path.exists( os.path.join(g_pathProyectWeb,g_namePageHTML) ) :
            if not dialogBox("Find data existing in proyect/Process all layers to OCR(Add new layers)?"):
                return

    if selectionOptionMain == "Process only selection":
        if not pdb.gimp_item_is_layer(g_activeLayer) or pdb.gimp_item_is_group(g_activeLayer) or pdb.gimp_item_is_text_layer(g_activeLayer) or pdb.gimp_selection_is_empty(g_imageActive):
            pdb.gimp_message('Select an layer and make a selection')
            return

    if selectionOptionMain == "Load Proyect":
        if os.path.exists(g_pathProyectWeb_Images):
            loadProyect()
            nameLayers = obtainNamesLayers(1)#all layers/curves
        else:
            pdb.gimp_message("Not found Proyect in directory:" + g_pathProyectWeb_Images)
            return
    threads = list()   
    if selectionOptionMain == "Only Repeat OCR":
        g_bRepeatOCR=True
        gimp.progress_init("ONLY Repeat OCR")
        for r, d, f  in os.walk(g_pathProyectWeb):
            for file in f:
                if file.endswith(g_nameFileImageOCR):
                    pathImage= os.path.join(r,file)
                    tOCR = threading.Thread(target=imagetoOCR, args=( pathImage , False))
                    threads.append(tOCR)
                    tOCR.start()
                    waitThreading(threads)
                    pdb.gimp_progress_pulse()
        for tOCR in threads:
            tOCR.join()        
        nameLayers = obtainNamesLayers(1)#all layers/curves
        pdb.gimp_progress_end()

   
    if selectionOptionMain == "Only Repeat Translation":
        gimp.progress_init("Only Repeat Translation")
        for r, d, f  in os.walk(g_pathProyectWeb):
            for file in f:
                if file.endswith(g_nameFileImageOCR):
                    pathImage= os.path.join(r,file)
                    translationFile(os.path.splitext(pathImage)[0]+TXT)
                    time.sleep(0.5)#delay 1/2 second
                    pdb.gimp_progress_pulse()
        nameLayers = obtainNamesLayers(1)#all layers/curves
        pdb.gimp_progress_end() 
    
    
    if selectionOptionMain == "Only Repeat Fix's":
        gimp.progress_init("Only Repeat Fix's")
        for r, d, f  in os.walk(g_pathProyectWeb):
            for file in f:
                if file.endswith(g_nameFileImageOCR):
                    pathImage= os.path.join(r,file)
                    g_bRepeatOCR=True
                    fixOCR(os.path.splitext(pathImage)[0])
                    translationFile(os.path.splitext(pathImage)[0]+TXT)
                    pdb.gimp_progress_pulse()
        nameLayers = obtainNamesLayers(1)#all layers/curves
        pdb.gimp_progress_end()    

 

    if selectionOptionMain in ["Only Edit Text" , "Only Repeat OCR", "Only Repeat Fix's","Only Repeat Translation","Update Text Translated","Load Proyect"] :
        if not (os.path.isfile( os.path.join(g_pathProyectWeb, g_namePageHTML) )):
            pdb.gimp_message("NOT FOUND PROYECT")
            pdb.gimp_message(os.path.join(g_pathProyectWeb, g_namePageHTML))
            return
        
        gimp.progress_init("PROCESSING NAMES")
        for r, d, f  in os.walk(g_pathProyectWeb):
            for file in f:
                if file.endswith(g_nameFileImageOCR):
                    pathImageRelativeExported = os.path.join(os.path.basename(r),file)
                    pathImageRelativeExportedEncHTML=urllib.pathname2url(pathImageRelativeExported.encode("UTF-8"))
                    pathImagesOCR.append(pathImageRelativeExportedEncHTML)
                if os.path.basename(r) == "images":
                    pathImageRelativeExportedb = os.path.join(os.path.basename(r),file)
                    pathImageRelativeExportedEncHTMLb=urllib.pathname2url(pathImageRelativeExportedb.encode("UTF-8"))
                    g_pathListImages.append(pathImageRelativeExportedEncHTMLb)
                if file[-6:] == T_TXT and selectionOptionMain =="Update Text Translated":
                    nameLayerText = file.replace("_OcrImage-T.txt","_TEXT")
                    layer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerText)
                    if layer:
                        if pdb.gimp_item_is_text_layer(layer):
                            textLayer = pdb.gimp_text_layer_get_text(layer)
                            if textLayer is not None:
                                writeFileUTF( os.path.join(r,file) , textLayer)
                            else:
                                textLayer= pdb.gimp_text_layer_get_markup(layer)
                                pdb.gimp_message( textLayer )
                                textLayer = ''.join(ET.fromstring(textLayer).itertext())
                                pdb.gimp_message("Warning Text Markup:" + nameLayerText)
                                writeFileUTF( os.path.join(r,file) , textLayer)
                    else:
                        if g_bMessageToConsole: pdb.gimp_message("not found layer:" + nameLayerText)
            pdb.gimp_progress_pulse()
        nameLayers = obtainNamesLayers(1)#all layers/curves
        pdb.gimp_progress_end()

    if selectionOptionMain in ["Process only selection","Process All layers/Path","Process Full"]:
        pdb.gimp_selection_flood(g_imageActive)
        #Selection to Path
        if not pdb.gimp_selection_is_empty(g_imageActive):
            pdb.plug_in_sel2path(g_imageActive,None)
        # Obtain Layers for process (Path/Curves or selection)
        if selectionOptionMain == "Process only selection":
            nameLayers = obtainNamesLayers(0)
        else:
            nameLayers = obtainNamesLayers(1)
        gimp.progress_init("PROCESSING GROUPS")
        for nameLayer in nameLayers:
            olayer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayer)
            pdb.gimp_item_set_visible(olayer, True)
            layerGroup = pdb.gimp_item_get_parent(olayer)
            if layerGroup==None:
                layerGroup = pdb.gimp_layer_group_new(g_imageActive)
                layerGroup.name = TAGPREFIXGROUP + olayer.name
                g_imageActive.add_layer(layerGroup,0)
                pdb.gimp_image_reorder_item(g_imageActive,olayer,layerGroup,0)
            pdb.gimp_progress_pulse()
        pdb.gimp_progress_end()
    
        gimp.progress_init("EXPORTING IMAGES/PATHS")
        
        threads = list()
        for nameLayer in nameLayers:
            oVector = pdb.gimp_image_get_vectors_by_name(g_imageActive, TAGPATHSTROKE + nameLayer)
            if oVector is None: continue
            
            layer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayer)
            if layer is not None:
                # add extension jpg, but not duplicate if existing (.)(?<!.jpg)$    \g<1>.jpg
                nameImageExported=re.sub(r"(.)(?<!" + g_ExtensionWeb + ")$", "\g<1>"+ g_ExtensionWeb, nameLayer,flags=re.I)
                pathImageExportedLayer = os.path.join(g_pathProyectWeb_Images,nameImageExported)
                
                g_pathListImages.append( urllib.pathname2url("images/" + nameImageExported.encode("UTF-8")) )
                if not os.path.exists(pathImageExportedLayer):
                    exporterImage(g_imageActive,layer,pathImageExportedLayer,nameLayer)
                    
            num_strokes, stroke_ids = pdb.gimp_vectors_get_strokes(oVector)
            for idStroke in stroke_ids:
                pdb.gimp_selection_none(g_imageActive)
                type, num_points, controlpoints, closed = pdb.gimp_vectors_stroke_get_points(oVector, idStroke)
                
                vBuffer = pdb.gimp_vectors_new(g_imageActive, "Buffer")
                stroke_id = pdb.gimp_vectors_stroke_new_from_points(vBuffer, type, num_points, controlpoints, closed)
                controlpointsXYSelection= list( zip(controlpoints[2::6], controlpoints[3::6]) )
                pdb.gimp_image_insert_vectors(g_imageActive, vBuffer, None, 0)
                pdb.gimp_image_select_item(g_imageActive, 2, vBuffer)
                
                # Filter Pixel Border
                pdb.gimp_selection_shrink(g_imageActive, pC.iFilterBorder)
                #Export image
                pathImageRelativeExported,boundsBalloonEmpty = exportImageSelectioned(nameLayer)
                if pathImageRelativeExported is not None:
                    positionLayer=layer.offsets
                    fileImageForOCR = os.path.join( g_pathProyectWeb  ,  pathImageRelativeExported)
                    tOCR = threading.Thread(target=imageOCRInfoText, args=( fileImageForOCR,positionLayer,boundsBalloonEmpty,controlpointsXYSelection  ) )
                    threads.append(tOCR)
                    tOCR.start()
                    waitThreading(threads)
                    if pC.bTranslation:#when translation, only use one thread
                        tOCR.join()
                    pathImageRelativeExportedEncHTML=urllib.pathname2url(pathImageRelativeExported.encode("UTF-8"))
                    pathImagesOCR.append(pathImageRelativeExportedEncHTML)
                pdb.gimp_progress_pulse()
                pdb.gimp_image_remove_vectors(g_imageActive, vBuffer)
        for tOCR in threads:
            tOCR.join()
            
        pdb.gimp_progress_end()
        pdb.gimp_selection_none(g_imageActive)
        pdb.gimp_image_set_active_layer(g_imageActive, g_activeLayer)

            


    generateFilesWeb (pathImagesOCR)
    editOCR(selectedEditor)
    
    bLoadTranslation=False
    if os.path.exists( os.path.join( g_pathProyectWeb ,OK)):
        os.remove( os.path.join(g_pathProyectWeb , OK))
        bLoadTranslation = True
    
    if bLoadTranslation ==True or pC.bTranslation:
        gimp.progress_init("LOADING TRANSLATION")
        for nameLayer in nameLayers:
            filterFilesTranslation = os.path.join(g_pathProyectWeb , nameLayer , u"*-T.txt")
            for fileTranslated in glob.glob(filterFilesTranslation):
                loadText(fileTranslated)
                pdb.gimp_progress_pulse()
        pdb.gimp_progress_end()  

    if g_activeLayer is not None:
        pdb.gimp_image_set_active_layer(g_imageActive, g_activeLayer)       
 
    saveFileINI()
    return

configINI = ConfigParser.RawConfigParser()
if not os.path.exists(g_pathFileINI):
    writeFileUTF(g_pathFileINI,defaultINI)
with codecs.open(g_pathFileINI, 'r', encoding='utf-8') as f:
    configINI.readfp(f)

loadFileINI()

if g_programOCR:
    pC.indexEngineOCR = pC.indexEngineOCR if pC.indexEngineOCR<len(g_programOCR) else 0
    if (os.path.isfile( g_programOCR[pC.indexEngineOCR] )):
        Command = [ g_programOCR[pC.indexEngineOCR] ]
        bCapture2Text=False
        if g_programOCR[pC.indexEngineOCR].find("tesseract")>-1:
            Command.append("--list-langs")
        elif g_programOCR[pC.indexEngineOCR].find("Capture2Text_CLI")>-1:
            Command.append("--show-languages")
            bCapture2Text=True
        else:
            Command=["exit"]
        if g_pathTessdata[pC.indexEngineOCR]:
            Command.append("--tessdata-dir")
            Command.append(g_pathTessdata[pC.indexEngineOCR])
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=g_PathPlugin)
        output = process.communicate()[0]
        langsOCRTraining = re.split(r"\r\n",output)[1:-1]
        lngA = langsOCRTraining if bCapture2Text else filter(None, [languageOCR.get(x) for x in langsOCRTraining] )
        if lngA :
            languageOCRAvaible=lngA
register(
    "python_fu_BubbleOCR",
    "It allows you to translate any text of an image, specially designed for text bubbles/balloon",
    "Nothing",
    "Anonymous",
    "2.2.0",
    "2019",
    "BubbleOCR 2.2...",
    "*",
    [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_OPTION,"indexSelectionMain", "OCR/Edit", 0, aSelectionMain,),
    (PF_OPTION,"indexEngineOCR", "Type Engine OCR", pC.indexEngineOCR, g_nameEngineOCRs),
    (PF_BOOL,"bWaifu2x","Scalex2 and noise reduction (Waifu2x)", pC.bWaifu2x),
    (PF_OPTION,"indexLanguageOCR", "Language OCR/Balloon", pC.indexLanguageOCR, languageOCRAvaible),
    (PF_OPTION,"oOrientation", "Orientation Text", pC.iOrientation, ("Auto", "Horizontal", "Vertical") ),
    (PF_OPTION,"indexFix","Fix OCR/Translation", pC.indexFix, ("None", "Remove line break in OCR", "Fix OCR of List","Fix Translation of List", "Fix OCR/Tranlation of List" )),
    (PF_OPTION,"caseOCR", "Change case OCR text", pC.caseOCR,aSelectionCase),
    (PF_BOOL,"bTranslation","Translation", pC.bTranslation),
    (PF_OPTION,"caseTranslation", "Change case Translation", pC.caseTranslation,aSelectionCase),
    (PF_OPTION,"indexLanTrans", "Language For Translation", pC.indexLanguageTranslation,sorted(languagueCode.values())),
    (PF_STRING,"nameDocument", "Proyect Name", "My Proyect"),
    (PF_DIRNAME,"pathProyect", "Proyect Directory", pC.pathProyect),
    (PF_OPTION,"indexEditor", "Editor OCR & Translation", pC.indexEditor,g_aSelectionEditor),
    (PF_SPINNER, "iFilterBorder", "Reduce/Filter border in pixel in your selections", pC.iFilterBorder, (0, 500, 1)),
    (PF_BOOL,"bColorBalloonAutomatic","Detect Backcolor Balloons", pC.bColorBalloonAutomatic),
    ],
    [],
    bubbleOCR,
    menu="<Image>/Layer/Tools/"
)    
main()
