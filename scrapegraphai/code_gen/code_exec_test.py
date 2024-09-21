import ast
import sys
from io import StringIO
from bs4 import BeautifulSoup
import re

generated_code = "def extract_data(html: str) -> dict:\n    from bs4 import BeautifulSoup\n    import re\n\n    # Parse the HTML content using BeautifulSoup\n    soup = BeautifulSoup(html, 'html.parser')\n\n    # Initialize the projects list\n    projects = []\n\n    # Find all <a> tags that contain project entries\n    project_links = soup.find_all('a', href=True)\n\n    # Iterate through each project link to extract title and description\n    for link in project_links:\n        # Check if the link contains an image and text\n        img_tag = link.find('img')\n        if img_tag and link.string:\n            # Extract the full text and split it into title and description\n            full_text = link.string.strip()\n            # Use regex to separate title and description\n            match = re.match(r'^(.*?)(?:\\s*-\\s*(.*))?$', full_text)\n            if match:\n                title = match.group(1).strip()\n                description = match.group(2).strip() if match.group(2) else ''\n                \n                # Append the project data to the projects list\n                projects.append({\n                    'title': title,\n                    'description': description\n                })\n\n    # Return the structured data as a dictionary\n    return {\n        'projects': projects\n    }\n"
html = """
<html lang="en" class="" data-theme="dark"><head> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <title>Projects | Marco Perini</title> <meta name="author" content="Marco Perini"> <meta name="description" content="Personal Porfolio Website "> <meta name="keywords" content="jekyll, jekyll-theme, academic-website, portfolio-website, robotics, machine-learning, computer-vision, artificial-intelligence, deep-learning, data-science, data-analysis, data-visualization, reinforcement-learning, computer-science, computer-graphics, computer-architecture, computer-networks, computer-security, computer-aided-design, computer-algebra, computer-alg, hardware"> <link rel="stylesheet" href="/assets/css/bootstrap.min.css?a4b3f509e79c54a512b890d73235ef04"> <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/mdbootstrap@4.20.0/css/mdb.min.css" integrity="sha256-jpjYvU3G3N6nrrBwXJoVEYI/0zw8htfFnhT9ljN3JJw=" crossorigin="anonymous"> <link defer="" rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.22.1/dist/bootstrap-table.min.css"> <link rel="stylesheet" href="/assets/css/academicons.min.css?f0b7046b84e425c55f3463ac249818f5"> <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Roboto+Slab:100,300,400,500,700|Material+Icons"> <link rel="stylesheet" href="/assets/css/jekyll-pygments-themes-github.css?19f3075a2d19613090fe9e16b564e1fe" media="none" id="highlight_theme_light"> <link rel="shortcut icon" href="data:image/svg+xml,<svg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%20100%20100%22><text%20y=%22.9em%22%20font-size=%2290%22>%F0%9F%A6%BE</text></svg>"> <link rel="stylesheet" href="/assets/css/main.css?d41d8cd98f00b204e9800998ecf8427e"> <link rel="canonical" href="https://perinim.github.io/projects/"> <link rel="stylesheet" href="/assets/css/jekyll-pygments-themes-native.css?e74e74bf055e5729d44a7d031a5ca6a5" media="" id="highlight_theme_dark"> <script src="/assets/js/theme.js?96d6b3e1c3604aca8b6134c7afdd5db6"></script> <script src="/assets/js/dark_mode.js?9b17307bb950ffa2e34be0227f53558f"></script> <style type="text/css">/* Chart.js */
@-webkit-keyframes chartjs-render-animation{from{opacity:0.99}to{opacity:1}}@keyframes chartjs-render-animation{from{opacity:0.99}to{opacity:1}}.chartjs-render-monitor{-webkit-animation:chartjs-render-animation 0.001s;animation:chartjs-render-animation 0.001s;}</style><script id="altmetric-embed-js" src="https://d1bxh8uas1mnw7.cloudfront.net/assets/altmetric_badges-2f3c1a827c4dee5fa0ff35ec229b9204ae106583cc99636c724152d1f7acea04.js"></script><style type="text/css">.medium-zoom-overlay{position:fixed;top:0;right:0;bottom:0;left:0;opacity:0;transition:opacity .3s;will-change:opacity}.medium-zoom--opened .medium-zoom-overlay{cursor:pointer;cursor:zoom-out;opacity:1}.medium-zoom-image{cursor:pointer;cursor:zoom-in;transition:transform .3s cubic-bezier(.2,0,.2,1)!important}.medium-zoom-image--hidden{visibility:hidden}.medium-zoom-image--opened{position:relative;cursor:pointer;cursor:zoom-out;will-change:transform}</style><style type="text/css">.CtxtMenu_InfoClose {  top:.2em; right:.2em;}
.CtxtMenu_InfoContent {  overflow:auto; text-align:left; font-size:80%;  padding:.4em .6em; border:1px inset; margin:1em 0px;  max-height:20em; max-width:30em; background-color:#EEEEEE;  white-space:normal;}
.CtxtMenu_Info.CtxtMenu_MousePost {outline:none;}
.CtxtMenu_Info {  position:fixed; left:50%; width:auto; text-align:center;  border:3px outset; padding:1em 2em; background-color:#DDDDDD;  color:black;  cursor:default; font-family:message-box; font-size:120%;  font-style:normal; text-indent:0; text-transform:none;  line-height:normal; letter-spacing:normal; word-spacing:normal;  word-wrap:normal; white-space:nowrap; float:none; z-index:201;  border-radius: 15px;                     /* Opera 10.5 and IE9 */  -webkit-border-radius:15px;               /* Safari and Chrome */  -moz-border-radius:15px;                  /* Firefox */  -khtml-border-radius:15px;                /* Konqueror */  box-shadow:0px 10px 20px #808080;         /* Opera 10.5 and IE9 */  -webkit-box-shadow:0px 10px 20px #808080; /* Safari 3 & Chrome */  -moz-box-shadow:0px 10px 20px #808080;    /* Forefox 3.5 */  -khtml-box-shadow:0px 10px 20px #808080;  /* Konqueror */  filter:progid:DXImageTransform.Microsoft.dropshadow(OffX=2, OffY=2, Color="gray", Positive="true"); /* IE */}
</style><style type="text/css">.CtxtMenu_MenuClose {  position:absolute;  cursor:pointer;  display:inline-block;  border:2px solid #AAA;  border-radius:18px;  -webkit-border-radius: 18px;             /* Safari and Chrome */  -moz-border-radius: 18px;                /* Firefox */  -khtml-border-radius: 18px;              /* Konqueror */  font-family: "Courier New", Courier;  font-size:24px;  color:#F0F0F0}
.CtxtMenu_MenuClose span {  display:block; background-color:#AAA; border:1.5px solid;  border-radius:18px;  -webkit-border-radius: 18px;             /* Safari and Chrome */  -moz-border-radius: 18px;                /* Firefox */  -khtml-border-radius: 18px;              /* Konqueror */  line-height:0;  padding:8px 0 6px     /* may need to be browser-specific */}
.CtxtMenu_MenuClose:hover {  color:white!important;  border:2px solid #CCC!important}
.CtxtMenu_MenuClose:hover span {  background-color:#CCC!important}
.CtxtMenu_MenuClose:hover:focus {  outline:none}
</style><style type="text/css">.CtxtMenu_Menu {  position:absolute;  background-color:white;  color:black;  width:auto; padding:5px 0px;  border:1px solid #CCCCCC; margin:0; cursor:default;  font: menu; text-align:left; text-indent:0; text-transform:none;  line-height:normal; letter-spacing:normal; word-spacing:normal;  word-wrap:normal; white-space:nowrap; float:none; z-index:201;  border-radius: 5px;                     /* Opera 10.5 and IE9 */  -webkit-border-radius: 5px;             /* Safari and Chrome */  -moz-border-radius: 5px;                /* Firefox */  -khtml-border-radius: 5px;              /* Konqueror */  box-shadow:0px 10px 20px #808080;         /* Opera 10.5 and IE9 */  -webkit-box-shadow:0px 10px 20px #808080; /* Safari 3 & Chrome */  -moz-box-shadow:0px 10px 20px #808080;    /* Forefox 3.5 */  -khtml-box-shadow:0px 10px 20px #808080;  /* Konqueror */}
.CtxtMenu_MenuItem {  padding: 1px 2em;  background:transparent;}
.CtxtMenu_MenuArrow {  position:absolute; right:.5em; padding-top:.25em; color:#666666;  font-family: null; font-size: .75em}
.CtxtMenu_MenuActive .CtxtMenu_MenuArrow {color:white}
.CtxtMenu_MenuArrow.CtxtMenu_RTL {left:.5em; right:auto}
.CtxtMenu_MenuCheck {  position:absolute; left:.7em;  font-family: null}
.CtxtMenu_MenuCheck.CtxtMenu_RTL { right:.7em; left:auto }
.CtxtMenu_MenuRadioCheck {  position:absolute; left: .7em;}
.CtxtMenu_MenuRadioCheck.CtxtMenu_RTL {  right: .7em; left:auto}
.CtxtMenu_MenuInputBox {  padding-left: 1em; right:.5em; color:#666666;  font-family: null;}
.CtxtMenu_MenuInputBox.CtxtMenu_RTL {  left: .1em;}
.CtxtMenu_MenuComboBox {  left:.1em; padding-bottom:.5em;}
.CtxtMenu_MenuSlider {  left: .1em;}
.CtxtMenu_SliderValue {  position:absolute; right:.1em; padding-top:.25em; color:#333333;  font-size: .75em}
.CtxtMenu_SliderBar {  outline: none; background: #d3d3d3}
.CtxtMenu_MenuLabel {  padding: 1px 2em 3px 1.33em;  font-style:italic}
.CtxtMenu_MenuRule {  border-top: 1px solid #DDDDDD;  margin: 4px 3px;}
.CtxtMenu_MenuDisabled {  color:GrayText}
.CtxtMenu_MenuActive {  background-color: #606872;  color: white;}
.CtxtMenu_MenuDisabled:focus {  background-color: #E8E8E8}
.CtxtMenu_MenuLabel:focus {  background-color: #E8E8E8}
.CtxtMenu_ContextMenu:focus {  outline:none}
.CtxtMenu_ContextMenu .CtxtMenu_MenuItem:focus {  outline:none}
.CtxtMenu_SelectionMenu {  position:relative; float:left;  border-bottom: none; -webkit-box-shadow:none; -webkit-border-radius:0px; }
.CtxtMenu_SelectionItem {  padding-right: 1em;}
.CtxtMenu_Selection {  right: 40%; width:50%; }
.CtxtMenu_SelectionBox {  padding: 0em; max-height:20em; max-width: none;  background-color:#FFFFFF;}
.CtxtMenu_SelectionDivider {  clear: both; border-top: 2px solid #000000;}
.CtxtMenu_Menu .CtxtMenu_MenuClose {  top:-10px; left:-10px}
</style><style id="MJX-CHTML-styles">
mjx-container[jax="CHTML"] {
  line-height: 0;
}

mjx-container [space="1"] {
  margin-left: .111em;
}

mjx-container [space="2"] {
  margin-left: .167em;
}

mjx-container [space="3"] {
  margin-left: .222em;
}

mjx-container [space="4"] {
  margin-left: .278em;
}

mjx-container [space="5"] {
  margin-left: .333em;
}

mjx-container [rspace="1"] {
  margin-right: .111em;
}

mjx-container [rspace="2"] {
  margin-right: .167em;
}

mjx-container [rspace="3"] {
  margin-right: .222em;
}

mjx-container [rspace="4"] {
  margin-right: .278em;
}

mjx-container [rspace="5"] {
  margin-right: .333em;
}

mjx-container [size="s"] {
  font-size: 70.7%;
}

mjx-container [size="ss"] {
  font-size: 50%;
}

mjx-container [size="Tn"] {
  font-size: 60%;
}

mjx-container [size="sm"] {
  font-size: 85%;
}

mjx-container [size="lg"] {
  font-size: 120%;
}

mjx-container [size="Lg"] {
  font-size: 144%;
}

mjx-container [size="LG"] {
  font-size: 173%;
}

mjx-container [size="hg"] {
  font-size: 207%;
}

mjx-container [size="HG"] {
  font-size: 249%;
}

mjx-container [width="full"] {
  width: 100%;
}

mjx-box {
  display: inline-block;
}

mjx-block {
  display: block;
}

mjx-itable {
  display: inline-table;
}

mjx-row {
  display: table-row;
}

mjx-row > * {
  display: table-cell;
}

mjx-mtext {
  display: inline-block;
}

mjx-mstyle {
  display: inline-block;
}

mjx-merror {
  display: inline-block;
  color: red;
  background-color: yellow;
}

mjx-mphantom {
  visibility: hidden;
}

_::-webkit-full-page-media, _:future, :root mjx-container {
  will-change: opacity;
}

mjx-assistive-mml {
  position: absolute !important;
  top: 0px;
  left: 0px;
  clip: rect(1px, 1px, 1px, 1px);
  padding: 1px 0px 0px 0px !important;
  border: 0px !important;
  display: block !important;
  width: auto !important;
  overflow: hidden !important;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

mjx-assistive-mml[display="block"] {
  width: 100% !important;
}

mjx-c::before {
  display: block;
  width: 0;
}

.MJX-TEX {
  font-family: MJXZERO, MJXTEX;
}

.TEX-B {
  font-family: MJXZERO, MJXTEX-B;
}

.TEX-I {
  font-family: MJXZERO, MJXTEX-I;
}

.TEX-MI {
  font-family: MJXZERO, MJXTEX-MI;
}

.TEX-BI {
  font-family: MJXZERO, MJXTEX-BI;
}

.TEX-S1 {
  font-family: MJXZERO, MJXTEX-S1;
}

.TEX-S2 {
  font-family: MJXZERO, MJXTEX-S2;
}

.TEX-S3 {
  font-family: MJXZERO, MJXTEX-S3;
}

.TEX-S4 {
  font-family: MJXZERO, MJXTEX-S4;
}

.TEX-A {
  font-family: MJXZERO, MJXTEX-A;
}

.TEX-C {
  font-family: MJXZERO, MJXTEX-C;
}

.TEX-CB {
  font-family: MJXZERO, MJXTEX-CB;
}

.TEX-FR {
  font-family: MJXZERO, MJXTEX-FR;
}

.TEX-FRB {
  font-family: MJXZERO, MJXTEX-FRB;
}

.TEX-SS {
  font-family: MJXZERO, MJXTEX-SS;
}

.TEX-SSB {
  font-family: MJXZERO, MJXTEX-SSB;
}

.TEX-SSI {
  font-family: MJXZERO, MJXTEX-SSI;
}

.TEX-SC {
  font-family: MJXZERO, MJXTEX-SC;
}

.TEX-T {
  font-family: MJXZERO, MJXTEX-T;
}

.TEX-V {
  font-family: MJXZERO, MJXTEX-V;
}

.TEX-VB {
  font-family: MJXZERO, MJXTEX-VB;
}

mjx-stretchy-v mjx-c, mjx-stretchy-h mjx-c {
  font-family: MJXZERO, MJXTEX-S1, MJXTEX-S4, MJXTEX, MJXTEX-A ! important;
}

@font-face /* 0 */ {
  font-family: MJXZERO;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Zero.woff") format("woff");
}

@font-face /* 1 */ {
  font-family: MJXTEX;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Main-Regular.woff") format("woff");
}

@font-face /* 2 */ {
  font-family: MJXTEX-B;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Main-Bold.woff") format("woff");
}

@font-face /* 3 */ {
  font-family: MJXTEX-I;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Math-Italic.woff") format("woff");
}

@font-face /* 4 */ {
  font-family: MJXTEX-MI;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Main-Italic.woff") format("woff");
}

@font-face /* 5 */ {
  font-family: MJXTEX-BI;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Math-BoldItalic.woff") format("woff");
}

@font-face /* 6 */ {
  font-family: MJXTEX-S1;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Size1-Regular.woff") format("woff");
}

@font-face /* 7 */ {
  font-family: MJXTEX-S2;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Size2-Regular.woff") format("woff");
}

@font-face /* 8 */ {
  font-family: MJXTEX-S3;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Size3-Regular.woff") format("woff");
}

@font-face /* 9 */ {
  font-family: MJXTEX-S4;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Size4-Regular.woff") format("woff");
}

@font-face /* 10 */ {
  font-family: MJXTEX-A;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_AMS-Regular.woff") format("woff");
}

@font-face /* 11 */ {
  font-family: MJXTEX-C;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Calligraphic-Regular.woff") format("woff");
}

@font-face /* 12 */ {
  font-family: MJXTEX-CB;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Calligraphic-Bold.woff") format("woff");
}

@font-face /* 13 */ {
  font-family: MJXTEX-FR;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Fraktur-Regular.woff") format("woff");
}

@font-face /* 14 */ {
  font-family: MJXTEX-FRB;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Fraktur-Bold.woff") format("woff");
}

@font-face /* 15 */ {
  font-family: MJXTEX-SS;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_SansSerif-Regular.woff") format("woff");
}

@font-face /* 16 */ {
  font-family: MJXTEX-SSB;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_SansSerif-Bold.woff") format("woff");
}

@font-face /* 17 */ {
  font-family: MJXTEX-SSI;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_SansSerif-Italic.woff") format("woff");
}

@font-face /* 18 */ {
  font-family: MJXTEX-SC;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Script-Regular.woff") format("woff");
}

@font-face /* 19 */ {
  font-family: MJXTEX-T;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Typewriter-Regular.woff") format("woff");
}

@font-face /* 20 */ {
  font-family: MJXTEX-V;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Vector-Regular.woff") format("woff");
}

@font-face /* 21 */ {
  font-family: MJXTEX-VB;
  src: url("https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/output/chtml/fonts/woff-v2/MathJax_Vector-Bold.woff") format("woff");
}
</style><link rel="stylesheet" href="https://badge.dimensions.ai/badge.css"></head> <body class="fixed-top-nav " data-new-gr-c-s-check-loaded="14.1196.0" data-gr-ext-installed="" style="padding-top: 57px;"> <header> <nav id="navbar" class="navbar navbar-light navbar-expand-sm fixed-top"> <div class="container"> <a class="navbar-brand title font-weight-lighter" href="/"><span class="font-weight-bold">Marco&nbsp;</span>Perini</a> <button class="navbar-toggler collapsed ml-auto" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation"> <span class="sr-only">Toggle navigation</span> <span class="icon-bar top-bar"></span> <span class="icon-bar middle-bar"></span> <span class="icon-bar bottom-bar"></span> </button> <div class="collapse navbar-collapse text-right" id="navbarNav"> <ul class="navbar-nav ml-auto flex-nowrap"> <li class="nav-item "> <a class="nav-link" href="/">About</a> </li> <li class="nav-item dropdown active"> <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Projects<span class="sr-only">(current)</span></a> <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown"> <a class="dropdown-item" href="/projects/">Projects</a> <div class="dropdown-divider"></div> <a class="dropdown-item" href="/competitions/">Competitions</a> </div> </li> <li class="nav-item "> <a class="nav-link" href="/cv/">CV</a> </li> <li class="toggle-container"> <button id="light-toggle" title="Change theme"> <i class="fa-solid fa-moon"></i> <i class="fa-solid fa-sun"></i> </button> </li> </ul> </div> </div> </nav> <progress id="progress" value="40" max="140" style="top: 57px;"> <div class="progress-container"> <span class="progress-bar"></span> </div> </progress> </header> <div class="container mt-5"> <div class="post"> <header class="post-header"> <h1 class="post-title">Projects</h1> <p class="post-description"></p> </header> <article> <div class="projects"> <div class="grid" style="position: relative; height: 803.703px;"> <div class="grid-sizer"></div> <div class="grid-item" style="position: absolute; left: 0px; top: 0px;"> <a href="/projects/rotary-pendulum-rl/"> <div class="card hoverable"> <figure> <picture> <source class="responsive-img-srcset" media="(max-width: 480px)" srcset="/assets/img/rotary_pybullet-480.webp"> <source class="responsive-img-srcset" media="(max-width: 800px)" srcset="/assets/img/rotary_pybullet-800.webp"> <source class="responsive-img-srcset" media="(max-width: 1400px)" srcset="/assets/img/rotary_pybullet-1400.webp"> <img src="/assets/img/rotary_pybullet.jpg" width="auto" height="auto" alt="project thumbnail" onerror="this.onerror=null; $('.responsive-img-srcset').remove();"> </picture> </figure> <div class="card-body"> <h4 class="card-title">Rotary Pendulum RL</h4> <p class="card-text">Open Source project aimed at controlling a real life rotary pendulum using RL algorithms</p> <div class="row ml-1 mr-1 p-0"> </div> </div> </div> </a> </div> <div class="grid-sizer"></div> <div class="grid-item" style="position: absolute; left: 260px; top: 0px;"> <a href="https://github.com/PeriniM/DQN-SwingUp" rel="external nofollow noopener" target="_blank"> <div class="card hoverable"> <figure> <picture> <source class="responsive-img-srcset" media="(max-width: 480px)" srcset="/assets/img/value-policy-heatmaps-480.webp"> <source class="responsive-img-srcset" media="(max-width: 800px)" srcset="/assets/img/value-policy-heatmaps-800.webp"> <source class="responsive-img-srcset" media="(max-width: 1400px)" srcset="/assets/img/value-policy-heatmaps-1400.webp"> <img src="/assets/img/value-policy-heatmaps.jpg" width="auto" height="auto" alt="project thumbnail" onerror="this.onerror=null; $('.responsive-img-srcset').remove();"> </picture> </figure> <div class="card-body"> <h4 class="card-title">DQN Implementation from scratch</h4> <p class="card-text">Developed a Deep Q-Network algorithm to train a simple and double pendulum</p> <div class="row ml-1 mr-1 p-0"> </div> </div> </div> </a> </div> <div class="grid-sizer"></div> <div class="grid-item" style="position: absolute; left: 520px; top: 0px;"> <a href="https://github.com/PeriniM/Multi-Agents-HAED" rel="external nofollow noopener" target="_blank"> <div class="card hoverable"> <figure> <picture> <source class="responsive-img-srcset" media="(max-width: 480px)" srcset="/assets/img/multi_agents_haed.gif-480.webp"> <source class="responsive-img-srcset" media="(max-width: 800px)" srcset="/assets/img/multi_agents_haed.gif-800.webp"> <source class="responsive-img-srcset" media="(max-width: 1400px)" srcset="/assets/img/multi_agents_haed.gif-1400.webp"> <img src="/assets/img/multi_agents_haed.gif" width="auto" height="auto" alt="project thumbnail" onerror="this.onerror=null; $('.responsive-img-srcset').remove();"> </picture> </figure> <div class="card-body"> <h4 class="card-title">Multi Agents HAED</h4> <p class="card-text">University project which focuses on simulating a multi-agent system to perform environment mapping. Agents, equipped with sensors, explore and record their surroundings, considering uncertainties in their readings.</p> <div class="row ml-1 mr-1 p-0"> </div> </div> </div> </a> </div> <div class="grid-sizer"></div> <div class="grid-item" style="position: absolute; left: 0px; top: 447.453px;"> <a href="/projects/wireless-esc-drone/"> <div class="card hoverable"> <figure> <picture> <source class="responsive-img-srcset" media="(max-width: 480px)" srcset="/assets/img/wireless_esc.gif-480.webp"> <source class="responsive-img-srcset" media="(max-width: 800px)" srcset="/assets/img/wireless_esc.gif-800.webp"> <source class="responsive-img-srcset" media="(max-width: 1400px)" srcset="/assets/img/wireless_esc.gif-1400.webp"> <img src="/assets/img/wireless_esc.gif" width="auto" height="auto" alt="project thumbnail" onerror="this.onerror=null; $('.responsive-img-srcset').remove();"> </picture> </figure> <div class="card-body"> <h4 class="card-title">Wireless ESC for Modular Drones</h4> <p class="card-text">Modular drone architecture proposal and proof of concept. The project received maximum grade.</p> <div class="row ml-1 mr-1 p-0"> </div> </div> </div> </a> </div> </div> </div> </article> </div> </div> <footer class="fixed-bottom"> <div class="container mt-0"> © Copyright 2023 Marco Perini. Powered by <a href="https://jekyllrb.com/" target="_blank" rel="external nofollow noopener">Jekyll</a> with <a href="https://github.com/alshedivat/al-folio" rel="external nofollow noopener" target="_blank">al-folio</a> theme. Hosted by <a href="https://pages.github.com/" target="_blank" rel="external nofollow noopener">GitHub Pages</a>. </div> </footer> <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script> <script src="/assets/js/bootstrap.bundle.min.js"></script> <script src="https://cdn.jsdelivr.net/npm/mdbootstrap@4.20.0/js/mdb.min.js" integrity="sha256-NdbiivsvWt7VYCt6hYNT3h/th9vSTL4EDWeGs5SN3DA=" crossorigin="anonymous"></script> <script defer="" src="https://cdn.jsdelivr.net/npm/masonry-layout@4.2.2/dist/masonry.pkgd.min.js" integrity="sha256-Nn1q/fx0H7SNLZMQ5Hw5JLaTRZp0yILA/FRexe19VdI=" crossorigin="anonymous"></script> <script defer="" src="https://cdn.jsdelivr.net/npm/imagesloaded@4/imagesloaded.pkgd.min.js"></script> <script defer="" src="/assets/js/masonry.js" type="text/javascript"></script> <script defer="" src="https://cdn.jsdelivr.net/npm/medium-zoom@1.0.8/dist/medium-zoom.min.js" integrity="sha256-7PhEpEWEW0XXQ0k6kQrPKwuoIomz8R8IYyuU1Qew4P8=" crossorigin="anonymous"></script> <script defer="" src="/assets/js/zoom.js?7b30caa5023af4af8408a472dc4e1ebb"></script> <script defer="" src="https://unpkg.com/bootstrap-table@1.22.1/dist/bootstrap-table.min.js"></script> <script src="/assets/js/no_defer.js?d633890033921b33e0ceb13d22340a9c"></script> <script defer="" src="/assets/js/common.js?acdb9690d7641b2f8d40529018c71a01"></script> <script defer="" src="/assets/js/copy_code.js?07b8786bab9b4abe90d10e61f7d12ff7" type="text/javascript"></script> <script async="" src="https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js"></script> <script async="" src="https://badge.dimensions.ai/badge.js"></script> <script type="text/javascript">window.MathJax={tex:{tags:"ams"}};</script> <script defer="" type="text/javascript" id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/tex-mml-chtml.js"></script> <script defer="" src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script> <script async="" src="https://www.googletagmanager.com/gtag/js?id=G-W66CHGTB05"></script> <script>function gtag(){window.dataLayer.push(arguments)}window.dataLayer=window.dataLayer||[],gtag("js",new Date),gtag("config","G-W66CHGTB05");</script> <script type="text/javascript">function progressBarSetup(){"max"in document.createElement("progress")?(initializeProgressElement(),$(document).on("scroll",function(){progressBar.attr({value:getCurrentScrollPosition()})}),$(window).on("resize",initializeProgressElement)):(resizeProgressBar(),$(document).on("scroll",resizeProgressBar),$(window).on("resize",resizeProgressBar))}function getCurrentScrollPosition(){return $(window).scrollTop()}function initializeProgressElement(){let e=$("#navbar").outerHeight(!0);$("body").css({"padding-top":e}),$("progress-container").css({"padding-top":e}),progressBar.css({top:e}),progressBar.attr({max:getDistanceToScroll(),value:getCurrentScrollPosition()})}function getDistanceToScroll(){return $(document).height()-$(window).height()}function resizeProgressBar(){progressBar.css({width:getWidthPercentage()+"%"})}function getWidthPercentage(){return getCurrentScrollPosition()/getDistanceToScroll()*100}const progressBar=$("#progress");window.onload=function(){setTimeout(progressBarSetup,50)};</script>  <div class="hiddendiv common"></div><iframe id="LgIoc6pK" frameborder="0" src="chrome-extension://ekhagklcjbdpajgpjgmbionohlpdbjgc/translateSandbox/translateSandbox.html" style="width: 0px; height: 0px; display: none;"></iframe></body><grammarly-desktop-integration data-grammarly-shadow-root="true"></grammarly-desktop-integration></html>
"""

def extract_data(html: str) -> dict:
    from bs4 import BeautifulSoup
    import re

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize the list to hold project data
    projects = []

    # Find all anchor tags that contain project information
    for a_tag in soup.find_all('a', href=True):
        # Extract the text content of the anchor tag
        text_content = a_tag.get_text(strip=True)
        
        # Use regex to split the text content into title and description
        match = re.match(r'(.+?)\s(.+)', text_content)
        if match:
            title = match.group(1)
            description = match.group(2)
            
            # Append the project data to the list
            projects.append({
                'title': title,
                'description': description
            })

    # Structure the data according to the specified JSON schema
    result = {
        'title': 'Projects',
        'type': 'object',
        'properties': {
            'projects': {
                'title': 'Projects',
                'type': 'array',
                'items': projects
            }
        },
        'required': ['projects'],
        'definitions': {
            'Project': {
                'title': 'Project',
                'type': 'object',
                'properties': {
                    'title': {
                        'title': 'Title',
                        'description': 'The title of the project',
                        'type': 'string'
                    },
                    'description': {
                        'title': 'Description',
                        'description': 'The description of the project',
                        'type': 'string'
                    }
                },
                'required': ['title', 'description']
            }
        }
    }

    return result

def create_sandbox_and_execute(function_code, html_doc):
        # Create a sandbox environment
        sandbox_globals = {
            'BeautifulSoup': BeautifulSoup,
            're': re,
            '__builtins__': __builtins__,
        }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Execute the extract_data function with the provided HTML
            result = extract_data(html_doc)
            
            return True, result
        except Exception as e:
            return False, f"Error during execution: {str(e)}"
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
            
#execution_success, execution_result = create_sandbox_and_execute(generated_code, html)
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]


def transform_schema(pydantic_schema):
    def process_properties(properties):
        result = {}
        for key, value in properties.items():
            if 'type' in value:
                if value['type'] == 'array':
                    if '$ref' in value['items']:
                        ref_key = value['items']['$ref'].split('/')[-1]
                        result[key] = [process_properties(pydantic_schema['definitions'][ref_key]['properties'])]
                    else:
                        result[key] = [value['items']['type']]
                else:
                    result[key] = {
                        "type": value['type'],
                        "description": value.get('description', '')
                    }
            elif '$ref' in value:
                ref_key = value['$ref'].split('/')[-1]
                result[key] = process_properties(pydantic_schema['definitions'][ref_key]['properties'])
        return result

    return process_properties(pydantic_schema['properties'])


data_schema = Projects.schema()
transformed_schema = transform_schema(data_schema)
print(transformed_schema)