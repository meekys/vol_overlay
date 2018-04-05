from PIL import Image
from OpenGL.GL import *
from ctypes import c_void_p, c_short
import itertools

class Point(object):
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

class Color(object):
    def __init__(self, r, g, b, a = 1.0):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

class Location(object):
    def __init__(self, u, v):
        self.u = float(u)
        self.v = float(v)

class ProgressBar(object):
    def __init__(self, x, y, width, height, depth = 0, min = 0, max = 100, colour = None):

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.colour = colour
        self.min = min
        self.max = max
        self.value = min
        self.rectangle = None
        self.lastValue = min - 1

    def draw(self, s, texture):

        if self.value != self.lastValue:
            self.lastValue = self.value

            if self.rectangle is not None:
                self.rectangle.release()

            percentage = self.value / float(self.max - self.min)

            self.rectangle = Rectangle(
                self.x,
                self.y,
                self.width * percentage,
                self.height,
                self.depth,
                self.colour)

        self.rectangle.draw(s, texture)


class Triangle(object):
    def __init__(self, points, colours = None, locations = None):

        if len(points) != 3:
            raise ValueError("points should contain 3 elements")

        if colours is None:
            colours = Color(1.0, 1.0, 1.0)

        if not isinstance(colours, list):
            colours = [colours] * len(points)

        if locations is None:
            locations = [Location(0,0), Location(0, 1), Location(1,1)]

        faces = [(0, 1, 2)]

        self.buffer = Buffer(points, faces, colours, locations)

    def draw(self, s, texture):
        self.buffer.draw(s, texture)

class Rectangle(object):
    def __init__(self, x, y, width, height, depth = 0, colour = None):

        self.quad = Quad(
            [
                Point(x, y, depth),
                Point(x + width, y, depth),
                Point(x + width, y + height, depth),
                Point(x, y + height, depth)
            ],
            colour,
            [
                Location(0, 0),
                Location(1, 0),
                Location(1, 1),
                Location(0, 1)
            ]
            )

    def draw(self, s, t = None):
        self.quad.draw(s, t)

    def release(self):
        self.quad.release()

class Quad(object):
    def __init__(self, points, colours = None, locations = None):

        if len(points) != 4:
            raise ValueError("points should contain 4 elements")

        if colours is None:
            colours = Color(1.0, 1.0, 1.0)

        if not isinstance(colours, list):
            colours = [colours] * len(points)

        if locations is None:
            locations = [Location(0, 0), Location(1, 0), Location(1, 1), Location(0, 1)]

        faces = [(0, 1, 2), (2, 3, 0)]

        self.buffer = Buffer(points, faces, colours, locations)

    def draw(self, s, texture = None):
        self.buffer.draw(s, texture)

    def release(self):
        self.buffer.release()

class Buffer(object):
    """Hold a pair of Buffer Objects to draw a part of a model"""
    def __init__(self, points, faces, colours, locations):
        """Generate a vertex buffer to hold data and indices"""
        points = [[p.x, p.y, p.z] for p in points]

        faces=[[c_short(f[0]), c_short(f[1]), c_short(f[2])] for f in faces]
        colours = [[c.r, c.g, c.b, c.a] for c in colours]
        locations = [[l.u, l.v] for l in locations]
        # normals=[[] for p in pts]
        # for f in faces:
        #     a,b,c=f[0:3]
        #     n=tuple(vec_normal(vec_cross(vec_sub(pts[b],pts[a]),vec_sub(pts[c],pts[a]))))
        #     for x in f[0:3]:
        #         normals[x].append(n)
        # for i,N in enumerate(normals):
        #     if len(N)==0:
        #         normals[i]=(0,0,.01)
        #         continue
        #     s=1.0/len(N)
        #     normals[i]=tuple( vec_normal( [sum(v[k] for v in N) for k in range(3)] ) )
        #
        #vertexData = [p + c for p, c in zip (points, colours)]
        vertexData = [p + c + l for p, c, l in zip(points, colours, locations)]
        vertexData = list(itertools.chain.from_iterable(vertexData))

        facesData = list(itertools.chain.from_iterable(faces))

        self.vertexBuffer, self.elementBuffer = glGenBuffers(2)

        self.select()

        glBufferData(
            GL_ARRAY_BUFFER,
            len(vertexData) * 4,
            (ctypes.c_float * len(vertexData))(*vertexData),
            GL_STATIC_DRAW)

        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            len(facesData) * 2,
            (ctypes.c_short * len(facesData))(*facesData),
            GL_STATIC_DRAW)

        self.ntris = len(faces)

    def select(self):
        """Makes our buffers active"""
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.elementBuffer)

    def draw(self, s, texture = None):
        self.select()

        # stride = (3 + 4 + 2) * sizeof(float)
        # pointer = (0 || 3 || 3 + 4) * sizeof(float)
        glVertexAttribPointer(s.attr_vertex, 3, GL_FLOAT, 0, 36, c_void_p(0))
        glVertexAttribPointer(s.attr_color, 4, GL_FLOAT, 0, 36, c_void_p(12))
        glVertexAttribPointer(s.attr_textureUV, 2, GL_FLOAT, 0, 36, c_void_p(28))

        glEnableVertexAttribArray(s.attr_vertex)
        glEnableVertexAttribArray(s.attr_color)
        glEnableVertexAttribArray(s.attr_textureUV)

        if texture is not None:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture.textureId)
            glUniform1i(s.texture1, 0)

        glDrawElements(GL_TRIANGLES, self.ntris * 3, GL_UNSIGNED_SHORT, None)

    def release(self):
        glDeleteBuffers(2, [self.vertexBuffer, self.elementBuffer])

class Texture(object):
    def __init__(self, filename):
        image = Image.open(filename)
        try:
            data = image.tobytes("raw", "RGBA", 0, -1)
        except SystemError:
            data = image.tobytes("raw", "RGBX", 0, -1)
        assert image.width * image.height * 4 == len(data), """Image size != expected array size"""

        print "Loaded " + filename + " (" + str(image.width) + "x" + str(image.height) + ")"

        self.textureId = glGenTextures(1)

        self.select()

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def select(self):
        glBindTexture(GL_TEXTURE_2D, self.textureId)

class Shader(object):
    def __init__(self):
        """Prepares a shader for 3d point + normal"""

        self.vshader_source = """
              attribute vec3 vertex;
              attribute vec4 vertexColor;
              attribute vec2 vertexUV;

              varying vec4 fragmentColor;
              varying vec2 fragmentUV;

              void main(void) {
                // Translate to (0,0)-(1,1) coordinate space
                // + Scale x/y by 2.0
                // + Translate x/y by -1.0
                // + Flip y coordintes
                vec3 translated = (vertex * vec3(2.0, 2.0, 1.0) - vec3(1.0, 1.0, 0.0)) * vec3(1.0, -1.0, 1.0);
                gl_Position = vec4(translated, 1.0);
                fragmentColor = vertexColor;
                fragmentUV = vertexUV;
              }"""

        self.fshader_source = """
              varying vec4 fragmentColor;
              varying vec2 fragmentUV;

              uniform sampler2D texture1;

              void main(void) {
                //gl_FragColor = vec4(1,1,1,1);
                //gl_FragColor = fragmentColor;
                gl_FragColor = texture2D(texture1, fragmentUV * vec2(1.0, -1.0)).rgba * fragmentColor;
              }"""

        vshader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vshader, self.vshader_source, 0)
        glCompileShader(vshader)
        self.showlog(vshader)

        fshader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fshader, self.fshader_source, 0)
        glCompileShader(fshader)
        self.showlog(fshader)

        program = glCreateProgram()
        glAttachShader(program, vshader)
        glAttachShader(program, fshader)
        glLinkProgram(program)
        self.showprogramlog(program)

        self.program = program

        self.attr_vertex = glGetAttribLocation(program, "vertex")
        self.attr_color = glGetAttribLocation(program, "vertexColor")
        self.attr_textureUV = glGetAttribLocation(program, "vertexUV")

        self.texture1 = glGetUniformLocation(program, "texture1")

        self.select()

    def select(self):
        """Makes this shader active"""
        glUseProgram(self.program)

    def showlog(self, shader):
        """Prints the compile log for a shader"""
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)

        if not result:
            raise RuntimeError(glGetShaderInfoLog(shader))

    def showprogramlog(self, program):
        """Prints the compile log for a program"""
        result = glGetProgramiv(program, GL_LINK_STATUS)

        if not result:
            raise RuntimeError(glGetProgramInfoLog(program))
