"""Affichage de simulation d'aiguille dans différents matériaux
Ce module permet d'afficher le déplacement 1D d'une aiguille
"""
import math
import imageio
import numpy as np
import psutil, os
import sys
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen


# Example for testing multiprocessing.
import multiprocessing
import os
import time




COUNT = 100
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

def affichage(name, shareddic):
    import OpenGL
    from glumpy import app, gloo, gl, glm
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
    MUR1['texcoord'] = posmur(MUR[0])
    MUR1['texture'] = imageio.imread("miel1.png")
    MUR1['scale'] = 1
    """MUR1['texture'] = imageio.imread("miel1.png")
    MUR1['u_model'] = np.eye(4, dtype=np.float32)
    MUR1['u_view'] = glm.translation(0, 0, 0)
    MUR1['position'] = posmur(MUR[0])
    MUR1['scale'] = 1"""

    MUR2 = gloo.Program(vertexX, fragmentX, count=8)
    MUR2['position'] = posmur(MUR[1])
    MUR2['texcoord'] = posmur(MUR[1])
    MUR2['texture'] = imageio.imread("eau.png")
    MUR2['scale'] = 1

    MUR3 = gloo.Program(vertexX, fragmentX, count=8)
    MUR3['position'] = posmur(MUR[2])
    MUR3['texcoord'] = posmur(MUR[2])
    MUR3['texture'] = imageio.imread("sable.png")
    MUR3['scale'] = 1



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
        depla = shareddic['position']
        MUR1['position'] = posmur(MUR[0], depla)
        MUR1.draw(gl.GL_TRIANGLE_STRIP)
        MUR2['position'] = posmur(MUR[1], depla)
        MUR2.draw(gl.GL_TRIANGLE_STRIP)
        MUR3['position'] = posmur(MUR[2], depla)
        MUR3.draw(gl.GL_TRIANGLE_STRIP)
        AIGUILLE['position'] = [(-4, -0.05), (-4, +0), (-0.6+depla+0.5, -0.05), (-0.5+depla+0.5, +0)]
        AIGUILLE.draw(gl.GL_TRIANGLE_STRIP)

    app.run()

def compute(threadname, SHARED):
    import multicom.com as com
    """ Compute the force """
    ##################################################################################

    ###### Haptic device init

    HAPTICDEV = com.HDevice("ftdi")

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

    HAPTICDEV.launch()
    i = 0
    oldforce = 0
    oldpos = 0
    oldvit = 0
    while True:
        try:
            taille = HAPTICDEV.incommingsize() #FIFO.qsize()
            if taille >= 3:
                rec = HAPTICDEV.readarray(3)#bytearray(extract(FIFO, 3))
                taille = taille - 3
                if rec[0] != 5:
                    while rec[0] != 5:
                        rec = HAPTICDEV.readarray(1)#bytearray(extract(FIFO, 1))
                        taille = taille - 1
                    rec[1:2] = HAPTICDEV.readarray(2)#bytearray(extract(FIFO, 2))
                    taille = taille - 2
                if rec[0] == 5:
                    i += 1
                    angle = rec[1] + rec[2] * 256
                    if angle > 32767:
                        angle -= 65536
                    degre = angle*4/20000
                    SHARED['position'] = degre
                    ### Definition force des murs
                    force = (-sticky(MUR[0],degre) - sticky(MUR[1],degre)- sticky(MUR[2],degre))*300
                    ### viscosite dans mur 1 ###
                    vit = oldvit + (0.001/(0.08+0.001))*((degre-oldpos)/0.001-oldvit)
                    if OLDMUR[MUR[0]]==1 and OLDMUR[MUR[1]]==0:
                        visc = 50*vit
                        force += -visc
                    if OLDMUR[MUR[1]]==1 and OLDMUR[MUR[2]]==0:
                        visc = 25*vit
                        force += -visc
                        force += np.sin(time.clock()*2*np.pi)*20*np.sin(time.clock()*2*np.pi*0.5)+10*np.sin(time.clock()*2*np.pi*3)
                    oldpos = degre
                    oldvit = vit
                    #if degre > -0.5 and degre < -0.4:
                    #    force = -(degre+0.5)*(degre+0.5)*100*50
                    #else:
                    #    force = 0
                    HAPTICDEV.write(force)
                    oldforce = force
                    #print(angle)
                    if i >= COUNT:
                        i = 0
                        #print(degre)1122
                        sys.stdout.flush()
        except (KeyboardInterrupt, SystemExit):
            print("Exiting lecture...")
            HAPTICDEV.quit()
            print("Exiting...")
            os._exit(0)
            break

if __name__ == '__main__':
    multiprocessing.freeze_support()
    # Run the app
    MANAGER = multiprocessing.Manager()
    SHARED = MANAGER.dict()
    SHARED['position'] = 0
    COMPUTE =  multiprocessing.Process(target=compute, args=("Thread-2", SHARED))
    COMPUTE.start()
    mp = psutil.Process(COMPUTE.pid)
    mp.nice(psutil.REALTIME_PRIORITY_CLASS)
    AFFICHAGE = multiprocessing.Process(target=affichage, args=("test", SHARED))
    AFFICHAGE.start()
    #app.run()
    while True:
            try:
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                os._exit(0)
                COMPUTE.terminate()
                COMPUTE.join()
                print("Exiting...")
                AFFICHAGE.terminate()
                AFFICHAGE.join()
                print("Exiting...")
                break
