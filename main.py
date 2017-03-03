from glumpy import app, gloo, gl
import math

vertex = """
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

vertexm = """
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

fragment = """
  varying vec4 v_color;
  void main()
  {
      gl_FragColor = v_color;
  } """

# Build the program and corresponding buffers (with 4 vertices)
quad = gloo.Program(vertex, fragment, count=4)


# Upload data into GPU
quad['color'] = [ (1,1,1,1), (1,1,1,1), (1,1,1,1), (1,1,1,1) ]
quad['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]
quad['scale'] = 1.0

seri = gloo.Program(vertexm, fragment, count=4)
seri['color'] = [ (0.5,0.5,0.5,1), (1,1,1,1), (0,0,0,1), (1,1,1,1) ]
seri['position'] = [ (-4,-0.05),   (-4,+0),   (-0.6,-0.05),   (-0.5,+0)   ]
seri['scale'] = 1.0
seri["depla"] = 0.0

quadb = gloo.Program(vertex, fragment, count=8)
quadb['color'] = [ (1,0,0,1), (1,0,0,1), (1,0,0,1), (1,0,0,1), (1,0,0,1) , (1,0,0,1), (1,0,0,1), (1,0,0,1)]
quadb['position'] = [   (-0.5,-0.25),(-0.5,-1),   (-0.3,-0), (+1,-1),  (+1,+1), (-0.3,-0),  (-0.5,1) ,   (-0.5,+0.25)  ]
quadb['scale'] = 1

mur2 = gloo.Program(vertex, fragment, count=8)
mur2['color'] = [ (1,1,0,1), (1,1,0,1), (1,1,0,1), (1,1,0,1), (1,1,0,1) , (1,1,0,1), (1,1,0,1), (1,1,0,1)]
mur2['position'] = [   (0,-0.25),(0,-1),   (0.3,-0), (+1,-1),  (+1,+1), (0.3,-0),  (0,1) ,   (0,+0.25)  ]
mur2['scale'] = 1

mur3 = gloo.Program(vertex, fragment, count=8)
mur3['color'] = [ (0,0,1,1), (0,0,1,1), (0,0,1,1), (0,0,1,1), (0,0,1,1) , (0,0,1,1), (0,0,1,1), (0,0,1,1)]
mur3['position'] = [   (0.5,-0.25),(0.5,-1),   (0.7,-0), (+1,-1),  (+1,+1), (0.7,-0),  (0.5,1) ,   (0.5,+0.25)  ]
mur3['scale'] = 1

# Create a window with a valid GL context
window = app.Window(800,600)
# Tell glumpy what needs to be done at each redraw
@window.event
def on_draw(dt):
    window.clear()
    quad.draw(gl.GL_TRIANGLE_STRIP)
    seri["depla"]+=dt
    depla=math.sin(seri["depla"])
    if depla>=-0.5 and depla <= -0.3:
        deplam1=depla+0.5
    else:
        deplam1=0.0
    quadb['position'] = [   (-0.5,-0.3),(-0.5,-1),(-0.5+deplam1,-0), (+1,-1),  (+1,+1), (-0.5+deplam1,-0),  (-0.5,1) ,   (-0.5,0.3)  ]
    quadb.draw(gl.GL_TRIANGLE_STRIP)
    if depla>=0 and depla <= 0.2:
        deplam2=depla
    else:
        deplam2=0.0
    mur2['position'] = [   (0,-0.25),(0,-1),   (0+deplam2,-0), (+1,-1),  (+1,+1), (0+deplam2,-0),  (0,1) ,   (0,+0.25)  ]
    mur2.draw(gl.GL_TRIANGLE_STRIP)
    if depla>=0.5 and depla <= 0.7:
        deplam3=depla-0.5
    else:
        deplam3=0.0
    mur3['position'] = [   (0.5,-0.25),(0.5,-1),   (0.5+deplam3,-0), (+1,-1),  (+1,+1), (0.5+deplam3,-0),  (0.5,1) ,   (0.5,+0.25)  ]
    mur3.draw(gl.GL_TRIANGLE_STRIP)

    seri['position'] = [ (-4,-0.05),   (-4,+0),   (-0.6+depla+0.5,-0.05),   (-0.5+depla+0.5,+0)   ]
    seri.draw(gl.GL_TRIANGLE_STRIP)

# Run the app
app.run()