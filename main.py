"""Affichage de simulation d'aiguille dans différents matériaux
Ce module permet d'afficher le déplacement 1D d'une aiguille
"""
import math
import imageio
import numpy as np
from glumpy import app, gloo, gl, glm

#####################################################################################################

MUR = [-0.5, 0, 0.5]
OLDMUR = {MUR[0]: 0, MUR[1]: 0, MUR[2]: 0}

#####################################################################################################

VERTEX = """
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

VERTEXM = """
  uniform float depla;
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

FRAGMENT = """
  varying vec4 v_color;    // Interpolated fragment color (in)
  void main()
  {
      gl_FragColor = v_color;
  } """

# Pour les Textures 2D #
##################################################################################
vertexX = """
	uniform float scale;
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(scale*position, 0.0, 1.0);
        v_texcoord = texcoord;
    }
"""

fragmentX = """
    uniform sampler2D texture;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(texture, v_texcoord);
    }
"""
##################################################################################


#####################################################################################################

# Build the program and corresponding buffers (with 4 vertices)
FOND = gloo.Program(VERTEX, FRAGMENT, count=4)

# Upload data into GPU
FOND['color'] = [(1, 1, 1, 1)] * 4
FOND['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
FOND['scale'] = 1.0

AIGUILLE = gloo.Program(VERTEXM, FRAGMENT, count=4)
AIGUILLE['color'] = [(0.5, 0.5, 0.5, 1), (1, 1, 1, 1), (0, 0, 0, 1), (1, 1, 1, 1)]
AIGUILLE['position'] = [(-4, -0.05), (-4, +0), (-0.6, -0.05), (-0.5, +0)]
AIGUILLE['scale'] = 1.0
AIGUILLE["depla"] = 0.0


##################################################################################
def sticky(pos_mur, pos_aig):
    """
    Compare la position du mur et de l'aiguille et retourne la déformation
    """
    dif = pos_aig-pos_mur
    posi = 0
    if OLDMUR[pos_mur] == 1:
        if dif < -0.1:
            posi = 0
            OLDMUR[pos_mur] = 0
        elif dif-0.1 < 0:
            posi = dif-0.1
    else:
        if dif > 0.1:
            posi = 0
            OLDMUR[pos_mur] = 1
        elif dif > 0:
            posi = dif
    return posi

def posmur(pos_mur, pos_aig=0):
    """
    retourne la liste correspondant aux coordonnées des triangles du mur
    """
    return [(pos_mur, -0.25), (pos_mur, -1), (pos_mur+sticky(pos_mur, pos_aig), -0),\
    (+1, -1),(+1, +1), (pos_mur+sticky(pos_mur, pos_aig), -0), (pos_mur, 1), (pos_mur, +0.25)]


##################################################################################    

MUR1 = gloo.Program(vertexX, fragmentX, count=8)
MUR1['position'] = posmur(MUR[0])
MUR1['texcoord'] = [(0.25,0.375),(0.25,0),(0.25,0.5),(1,0),(1,1),(0.25,0.5),(0.25,1),(0.25,0.625)]
MUR1['texture'] = imageio.imread("miel1.png")
MUR1['scale'] = 1
"""MUR1['texture'] = imageio.imread("miel1.png")
MUR1['u_model'] = np.eye(4, dtype=np.float32)
MUR1['u_view'] = glm.translation(0, 0, 0)
MUR1['position'] = posmur(MUR[0])
MUR1['scale'] = 1"""

MUR2 = gloo.Program(vertexX, fragmentX, count=8)
MUR2['position'] = posmur(MUR[1])
MUR2['texcoord'] = [(0.5,0.375),(0.5,0),(0.5,0.5),(1,0),(1,1),(0.5,0.5),(0.5,1),(0.5,0.625)]
MUR2['texture'] = imageio.imread("eau.png")
MUR2['scale'] = 1

MUR3 = gloo.Program(vertexX, fragmentX, count=8)
MUR3['position'] = posmur(MUR[2])
MUR3['texcoord'] = [(0.75,0.375),(0.75,0),(0.75,0.5),(1,0),(1,1),(0.75,0.5),(0.75,1),(0.75,0.625)]
MUR3['texture'] = imageio.imread("sable.png")
MUR3['scale'] = 1

"""print('position mur 1 :')
print(posmur(MUR[0]))
print('position mur 2 :')
print(posmur(MUR[1]))
print('position mur 3 :')
print(posmur(MUR[2]))"""
#####################################################################################################
# Create a window with a valid GL context
WINDOW = app.Window(800, 600)
#Calcul des parois molles

# Tell glumpy what needs to be done at each redraw
@WINDOW.event

def on_draw(dtemps):
    """
    Ce qui se passe à chaque raffraichissement
    """
    WINDOW.clear()
    FOND.draw(gl.GL_TRIANGLE_STRIP)
    AIGUILLE["depla"] += dtemps
    depla = math.sin(AIGUILLE["depla"])
    MUR1['position'] = posmur(MUR[0], depla)
    MUR1['texcoord'] = [(0.25,0.375),(0.25,0),(0.25+sticky(MUR[0], depla),0.5),(1,0),(1,1),(0.25+sticky(MUR[0], depla),0.5),(0.25,1),(0.25,0.625)]
    #print(posmur(MUR[0], depla))
    MUR1.draw(gl.GL_TRIANGLE_STRIP)
    MUR2['position'] = posmur(MUR[1], depla)
    MUR1['texcoord'] = [(0.5,0.375),(0.5,0),(0.5+sticky(MUR[1], depla),0.5),(1,0),(1,1),(0.5+sticky(MUR[1], depla),0.5),(0.5,1),(0.5,0.625)]
    #print(posmur(MUR[1], depla))
    MUR2.draw(gl.GL_TRIANGLE_STRIP)
    MUR3['position'] = posmur(MUR[2], depla)
    MUR1['texcoord'] = [(0.75,0.375),(0.75,0),(0.75+sticky(MUR[2], depla),0.5),(1,0),(1,1),(0.75+sticky(MUR[2], depla),0.5),(0.75,1),(0.75,0.625)]
    #print(posmur(MUR[2], depla))
    MUR3.draw(gl.GL_TRIANGLE_STRIP)
    AIGUILLE['position'] = [(-4, -0.05), (-4, +0), (-0.6+depla+0.5, -0.05), (-0.5+depla+0.5, +0)]
    AIGUILLE.draw(gl.GL_TRIANGLE_STRIP)

# Run the app
app.run()
