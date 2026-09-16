from pathlib import Path
import random
root=Path(r'E:\P45 프로젝트')
a=root/'web/assets'
random.seed(45)
def trees(x,y,s=1):
 return f'''<g transform="translate({x} {y}) scale({s})" fill="#18312d" stroke="#18312d"><path d="M0 92C9 66 13 44 0 16L5 11C22 41 19 59 11 92Z"/><path d="M10 54-19 35M10 36 30 23M6 20-10 4" fill="none" stroke-width="3"/><path d="M-40 35q9-11 18-7 5-10 16-6 13-3 21 12-19-6-55 1M9 23q7-11 18-8 16-5 26 10-19-5-44-2M-26 6q6-10 16-7 12-5 23 9-20-6-39-2"/></g>'''
def scene(w=1200,h=260):
 mountain='M580 240Q600 227 610 208T632 181Q638 161 650 169Q658 173 667 153Q673 129 685 137Q697 138 705 108Q715 83 728 99Q738 114 745 105Q758 77 766 95Q777 114 785 109Q802 91 813 116Q824 133 832 125Q846 98 860 119Q873 146 884 138Q899 124 911 147Q925 179 940 169Q953 155 967 172L1060 254Z'
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" fill="none"><defs><filter id="edge"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="6"/></filter><linearGradient id="fade" x2="0" y2="1"><stop stop-color="#223e38"/><stop offset="1" stop-color="#748277" stop-opacity=".1"/></linearGradient><clipPath id="rock"><path d="{mountain}"/></clipPath></defs>
 <g filter="url(#edge)"><path d="M0 0H300l-39 16 46 8-29 12 44 15-25 12 39 12-36 20 49 9-38 15 43 24-44 9 19 17-47 9 27 14-54 24 39 11-20 24H0Z" fill="#1a302c" opacity=".93"/><path d="M20 0h239l-35 42 43 15-18 32 35 27-20 14 40 34-46 35 23 18-47 29H0Z" fill="#294239" opacity=".53"/></g>
 <g stroke="#93866b" opacity=".37"><path d="M27 0v260M49 0v260M70 0v260M90 0v260M17 25h89M17 63h89M17 101h89M17 139h89M17 177h89M17 215h89"/><path d="m28 26 41 38-40 37 40 37-40 39 40 38m20-190L49 64l40 37-40 37 40 39-40 38"/></g>
 <circle cx="925" cy="58" r="31" fill="#e9cb88"/><circle cx="925" cy="58" r="25" fill="#f3ddb1" opacity=".55"/>
 <path d="M604 215q15-34 38-54t42-40q22-24 38-16t27-39q23-36 42 1t33 21q20-12 37 23t30 20q22-25 43 12t35 18l38 80Z" fill="#567267" opacity=".22" filter="url(#edge)"/>
 <path d="{mountain}" fill="url(#fade)" opacity=".75" filter="url(#edge)"/>
 <g clip-path="url(#rock)" stroke="#162d28" fill="none">'''
 for i in range(165):
  x=random.randint(595,983);y=random.randint(95,248);dy=random.randint(5,30)
  svg+=f'<path d="M{x} {y}q-7 9 -4 {dy}t-9 13" opacity="{random.uniform(.08,.3):.2f}" stroke-width="{random.uniform(.5,2):.1f}"/>'
 svg+='</g>'
 for x,y,s in [(610,195,.55),(655,197,.4),(694,179,.7),(750,200,.6),(815,175,.8),(864,201,.65),(914,191,.7),(979,205,.5)]:svg+=trees(x,y,s)
 svg+='''<path d="M548 254q120-16 199-6t186-3l162 15H548" fill="#294b3e" opacity=".4"/><g stroke="#3b3529" stroke-linecap="round"><path d="M1200 20q-81 45-135 20t-68-32M1138 42q-4 42-40 60m27-49-43-49M0 234q32-77 121-116M68 159q-26-39-48-44m69 29q22-8 43-1" stroke-width="4"/><path d="m1001 7 24 13m72 82-26 14M44 184l-14-39" stroke-width="2"/></g>'''
 for x,y in [(1044,28),(1071,38),(1087,16),(1119,51),(1104,88),(1155,35),(1175,22),(1018,14),(30,148),(45,175),(60,153),(83,144),(113,123),(121,143),(27,117)]:
  svg+=f'<g transform="translate({x} {y})" fill="#d0b7a0" stroke="#815a49" stroke-width=".6"><circle cx="-4" cy="-2" r="4"/><circle cx="0" cy="-5" r="4"/><circle cx="4" cy="-1" r="4"/><circle cx="2" cy="4" r="4"/><circle cx="-3" cy="4" r="4"/><circle r="2" fill="#854732"/></g>'
 svg+='</svg>';return svg
(a/'joseon-hero-landscape.svg').write_text(scene(),encoding='utf-8')
# Reuse the same painted ridges, adding a closer pavilion and pine for the sidebar.
svg=scene().replace('viewBox="0 0 1200 260"','viewBox="580 0 450 420"')
svg=svg.replace('</svg>', '''<path d="M570 306q87-31 175-4t310-1v130H570Z" fill="#344d40" opacity=".7"/><path d="M560 341q114-24 192-4t288-7v100H560Z" fill="#142e2a"/>
<g fill="#132520" stroke="#8a9072" stroke-width="1.3"><path d="m704 278 67-38 72 38-21-5h-98Z"/><path d="M721 280h103v59H721Z" fill="#1b2a22"/><path d="M727 282h24v47h-24m36-47h20v47h-20m31-47h23v47h-23" fill="#b09a65" opacity=".6"/><path d="M716 331h117v8H716m-12 5h140v7H704"/><path d="M735 284v46m36-46v46m36-46v46"/><path d="m742 256 30-22 34 23m-101 16-12-5m146 7 15-7"/></g>'''+trees(891,218,1.4)+trees(633,258,1.1)+'</svg>')
(a/'joseon-sidebar-landscape.svg').write_text(svg,encoding='utf-8')
html=(root/'web/index.html').read_text(encoding='utf-8-sig')
# Keep all data containers and event IDs; only move the visual shell.
start=html.index('  <aside');end=html.index('  <main>')
old=html[start:end]
aside=old[:old.index('  <div class="drawer-backdrop"')]
header=old[old.index('  <header'):old.index('</header>')+9]
header=header.replace('class="mobile-header"','class="mobile-header site-hero"')
header=header.replace('<div class="mobile-brand">','<div class="hero-motto" aria-hidden="true">조선의 품격으로,<br>더 나은 내일을 봅니다.<small>기록이 쌓이는 곳, 운칠기삼</small></div><div class="mobile-brand">')
header=header.replace('</header>','<p class="hero-note" aria-hidden="true">조선의 품격,<br>데이터의 미래</p></header>')
html=html[:start]+header+'\n  <div class="dashboard-shell">\n'+aside+'  <div class="drawer-backdrop" hidden></div>\n'+html[end:]
html=html.replace('    <div class="desktop-top"><span>조선의 품격, 데이터의 미래</span><small>P45 · JOSEON HERITAGE</small></div>','')
html=html.replace('  <script src=', '  </div>\n  <div class="heritage-colophon" aria-hidden="true"><span>조선의 품격으로<br><b>다시, 가능성을 그리다.</b></span><span>한지 · 수묵 · 기록<small>P45 TRIO ORBIT</small></span></div>\n  <script src=')
html=html.replace('/styles.css?v=47','/styles.css?v=48')
(root/'web/index.html').write_text(html,encoding='utf-8')
css=(root/'web/styles.css').read_text(encoding='utf-8-sig')
css=css.split('/* Visual correction:')[0]
(root/'web/styles.css').write_text(css,encoding='utf-8')
