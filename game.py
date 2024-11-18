import pygame as pg
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr

class App:

    def __init__(self) -> None:
        
        # Inicializador Python
        pg.init()

        # Doublebuffering system: El tipo de display que OPENGL necesita para ejecutarse
        # Un display lo dibuja la tarjeta gráfica
        # El otro es el que se muestra por pantalla
        # De esta forma se evita dibujar sobre la pantalla que el usuario está viendo
        self.ANCHO = 640
        self.ALTO = 480
        pg.display.set_mode((self.ANCHO, self.ALTO), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        # Inicializador OpenGL
        glClearColor(0.1, 0.2, 0.2, 1)

        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        # Creación y uso de Shaders
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader) # los shaders son un programa

        # Creación Uniforme respecto shader ¿Mirar mas informacion -> 3. 13:10?
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.cube = Cube(
            position = [0, 0, -3], # x, y, z=-3
            eulers = [0, 0, 0]
        )

        self.mesh = Mesh("cube.obj")

        self.minecraft_texture = Material("gfx/grass.jpg")

        # Matriz de proyección
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy= 45, aspect= self.ANCHO/self.ALTO,
            near= 0.1, far=10, dtype= np.float32
        )

        # Envía valores de una Uniform Matrix 4x4 float value a la uniforme indicada "projection"
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), # A qué uniforme vamos a enviar la matriz de proyección (projection)
            1, GL_FALSE, projection_transform # Num.Matrices que enviamos, transponer matriz(formato row major = TRUE), referencia a la matriz de proyección

            # Basicamente estamos pasando a nuestra variable mat4 de shaders, una matriz uniforme 4x4
            # en base a la matriz de proyección generada por pyrr.matrix44...() 
        )

       # Lo usaremos en cada frame para actualizar la posicion de nuestro modelo 
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")


        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):
        """
        Compila Vertex Shader y Fragment Shader.
        Finalmente devuelve la compilación de ambos en un mismo programa
        """

        # VertexShader: Se encarga de indicar la posición de cada vértice 
        # FragmentShader: Se encarga de indicar el color de cada pixel

        with open(vertexFilepath, "r") as file:
            vertex_src = file.readlines()

        with open(fragmentFilepath, "r") as file:
            fragment_src = file.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader

    def mainLoop(self):
        running = True
        while (running):
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False 

            ### Actualización de pantalla ###

            # Actualizacion cubo

            # Los Oulers siguen la rotacion X, Z, Y
            self.cube.eulers[2] += 0.2
            if (self.cube.eulers[2] > 360):
                self.cube.eulers[2] -= 360


            # Limpia el COLOR_BUFFER:
            # Array que almacena los colores de cada bit de la pantalla
            # Cada pixel de color se guarda en un unsigned int de 32-bits (4bytes RGBA -> 0 al 255)
            # Limpiamos también DEPTH_BUFFER
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)               # utilizamos nuestros shaders
            self.minecraft_texture.use()            # utilizamos nuestra textura


            # Transformaciones vistas en el episodio 4. Aplicando Transformaciones
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            # Rotación: Eulers
            model_transform = pyrr.matrix44.multiply(
                m1= model_transform,
                m2= pyrr.matrix44.create_from_eulers(
                    eulers= np.radians(self.cube.eulers),
                    dtype= np.float32
                )
            )
            # Translacion: vectores
            model_transform = pyrr.matrix44.multiply(
                m1= model_transform,
                m2= pyrr.matrix44.create_from_translation(
                    vec= self.cube.position,
                    dtype= np.float32
                )
            )


            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)
            glBindVertexArray(self.mesh.vao)    # utlizamos nuestro modelo vao
            # PARÁMETROS: estructura usada, vértice de inicio, número de vértices
            glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertices_recuento)

            # Es igual que un update(), la diferencia es que se utiliza en DOBLLEBUFFER
            # De esta forma se hace el transpaso del display dibujo al display pantalla
            pg.display.flip()

            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        # Liberamos memoria
        self.mesh.destroy()
        self.minecraft_texture.destroy()
        glDeleteProgram(self.shader)

        pg.quit()

class Cube:
    def __init__(self, position, eulers) -> None:

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class Mesh:
    def __init__(self, filename) -> None:
        
        # X (Ancho)
        # Y (Altura)
        # Z (Profundidad)
        
        #x, y, z, s, t, nx, ny, nz
        vertices = self.loadMesh(filename)
        self.vertices_recuento = len(vertices) // 8

        # Queremos enviar los vértices a la tarjeta gráfica, la gráfica lee en formato de C
        # NUMPY usa este tipo de datos, por tanto pasaremos los vértices en un np.array() MUY IMPORTANTE: de 32-bit float
        vertices = np.array(vertices, dtype=np.float32)

        
        # VertexArrayObject: Guarda la información sobre cómo OpenGL debe interpretar los datos en los vbo
        # Tiene un vbo Integrado con el formato utilizado para los vértices
        # Parámetro: cuántos VAO quieres generar
        self.vao = glGenVertexArrays(1) 
        # Vinculamos GLOpen con nuestro vao
        glBindVertexArray(self.vao)
        
        # VertexBufferObject: Generamos un Buffer para guardar nuestros vértices
        self.vbo = glGenBuffers(1)
        # GL_ARRAY_BUFFER: Envía los DATOS a la tarjeta gráfica
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # PARÁMETROS: dónde queremos enviar los DATOS, cuántos bytes utilizamos, los DATOS, cómo usaremos los DATOS que hemos cargado
        # GL_ARRAY_BUFFER: Envía los DATOS a la tarjeta gráfica
        # GL_STATIC_DRAWY: ESCRIBIMOS una vez y LEEMOS múltiples veces | GL_DINAMIC_DRAW: ESCRIBIMOS y LEEMOS múltiples veces
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)


        # CONFIGURACIÓN DEL VAO

        # position
        glEnableVertexAttribArray(0)
        # [0] -> 0: Posicion, 1: Color
        # [1] (Cuántos puntos hay en cada vertice) -> Posicion (XYZ = 3), Color (RGB = 3)
        # [2] (Tipo de datos) -> GL_FLOAT
        # [3] (Normalización de los datos) -> GL_FALSE
        # [4] (Stride: Espacio entre dos vértices consecutivos) -> (3pos + 3col) * 4bytes(cada uno) = 24
        # [5] (void_p: Espacio entre dos atributos del mismo vértifce) -> X está al principio = 0, X va después del color = 3colores * 4bytes = 12
        # Es un tipo de dato de C (void pointer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        # texture position
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

    def loadMesh(self, filename: str) -> list[float]:

        v = list()  # vertices
        vt = list() # texture coordinates
        vn = list() # 

        vertices = list()

        with open(filename, "r") as file:
            
            lineas = file.readlines()
            for linea in lineas:

                palabras = linea.split(" ")
                match(palabras[0]):
                    case "v":
                        v.append(self.read_vertex_data(palabras))
                    case "vt":
                        vt.append(self.read_texcoord_data(palabras))
                    case "vn":
                        vn.append(self.read_normal_data(palabras))
                    case "f": 
                        self.read_face_data(palabras, v, vt, vn, vertices)
            
        return vertices


    def read_vertex_data(self, words: list[str]) -> list[float]:
        return [
            float(words[1]), # X
            float(words[2]), # Y
            float(words[3]), # Z
        ]
    def read_texcoord_data(self, words: list[str]) -> list[float]:
        return [
            float(words[1]), # S
            float(words[2]), # T
        ]
    def read_normal_data(self, words: list[str]) -> list[float]:
        return [
            float(words[1]), # X
            float(words[2]), # Y
            float(words[3]), # Z
        ]
    def read_face_data(
        self, palabras: list[str], 
        v:list[list[float]], vt:list[list[float]], 
        vn: list[list[float]], vertices: list[float]) -> None:

        # Número de tríangulos en una cara = Número de esquinas - 2 (añadimos -3 porque tenemos antes la palabra 'f')
        triangleCount = len(palabras) - 3 

        for i in range(triangleCount):
            """
            La primera esquina se usa en todas las construcciones de los triángulos para una cara (face)

            1[\  ]2         Tring1: 1-2-3
             [ \ ]          Tring2: 1-3-4  
            4[  \]3
            """
            self.make_corner(palabras[1], v, vt, vn, vertices) 
            self.make_corner(palabras[2 + i], v, vt, vn, vertices)
            self.make_corner(palabras[3 + i], v, vt, vn, vertices)
        
    def make_corner(self, corner_description: str,
        v:list[list[float]], vt:list[list[float]], 
        vn: list[list[float]], vertices: list[float]) -> None:

        v_vt_vn = corner_description.split("/") # v/vt/vn
        
        # v
        for element in v[int(v_vt_vn[0]) - 1]:  # Restamos uno para acceder a la fila correcta de nuestro .obj
            vertices.append(element)
        # vt
        for element in vt[int(v_vt_vn[1]) - 1]: 
            vertices.append(element)
        # vn
        for element in vn[int(v_vt_vn[2]) - 1]:  # Restamos uno para acceder a la fila correcta de nuestro .obj
            vertices.append(element)
            
    def destroy(self):
        # utilizan listas o tuplas, por eso ponemos (elemento, )
        glDeleteVertexArrays(1, (self.vao,)) 
        glDeleteBuffers(1, (self.vbo,))



        

class Material:
    def __init__(self, filepath) -> None:

        # Guardamos espacio en memoria para las texturas
        self.texture = glGenTextures(1)
        # Enlazamos nuestro espacio de texturas con GL_TEXTURE_2D
        glBindTexture(GL_TEXTURE_2D, self.texture)

        # Las coordenadas de una textura se indican como (s, t). Donde s y t toman valores entre [0, 1]
        # s=0 left, s=1 right; t=0 top, t=1 bottom

        # PARÁMETROS: dónde cargamos la textura, wrapping_mode, protocolo de sobrepaso de coordenadas
        
        #_MIN_FILTER: si la textura es más grande que al utilizarla; GL_NEAREST: Enfoque (no antialiasing)
        #_MAG_FILTER: si la textura es más pequeña que al utilizarla; GL_LINEAR: Desenfoque (antialiasing)
                
        # GL_REPEAT: Si por ejemplo s=1.5, pillaremos un fragmento de la siguiente textura de la misma unidad

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load(filepath).convert()
        image_width, image_height = image.get_rect().size

        # Formato Pygame -> to -> Formato GL
        image_data = pg.image.tostring(image, "RGBA") 

        # PARÁMETROS: dónde cargamos la textura, mipmaplevel, formato que cagamos, width, height, 
        # color borde, formato que cargamos (borde), formato que usamos UNSIGNED_BYTE: [0, 255], imagen
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        # Generamos un MimpmapLevel basado en lo que hemos cargado en GL_TEXTURE_2D
        # MipmapLevel: Dependiendo de la distancia del jugador se utiliza un nivel=textura u otro
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        # Activamos GL_TEXTURE0 -> Texturas simples
        # Podemos cargar más texturas a la vez usando TEXTURE1, 2, 3, ... (usos: lightmaps, glossmaps, texturas combinadas)
        glActiveTexture(GL_TEXTURE0)
        # Enlazamos nuestro espacio de texturas con GL_TEXTURE_2D
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):

        glDeleteTextures(1, (self.texture, )) # recordemos que trabajamos con listas o tuplas


if __name__ == "__main__":
    app = App()