class Triangle:
    def __init__(self) -> None:
        
        # X (Ancho): [-1, 1], izquierda a derecha
        # Y(Profundidad): [-1, 1], centro a fuera
        # Z (Altura): [-1, 1], abajo a arriba

        # x, y, z, r, g, b, s, t
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, # para establecer s, t hay que mirar x, y
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, # Xmax: s=1, Ymax: t=0
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        )

        # Queremos enviar los vértices a la tarjeta gráfica, la gráfica lee en formato de C
        # NUMPY usa este tipo de datos, por tanto pasaremos los vértices en un np.array() MUY IMPORTANTE: de 32-bit float
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertices_recuento = 3

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
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)


        # CONFIGURACIÓN DEL VAO
        # Posicion: 0 
        glEnableVertexAttribArray(0)
        # [0] -> 0: Posicion, 1: Color
        # [1] (Cuántos puntos hay en cada vertice) -> Posicion (XYZ = 3), Color (RGB = 3)
        # [2] (Tipo de datos) -> GL_FLOAT
        # [3] (Normalización de los datos) -> GL_FALSE
        # [4] (Stride: Espacio entre dos vértices consecutivos) -> (3pos + 3col) * 4bytes(cada uno) = 24
        # [5] (void_p: Espacio entre dos atributos del mismo vértifce) -> X está al principio = 0, X va después del color = 3colores * 4bytes = 12
        # Es un tipo de dato de C (void pointer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        # Color: 1
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        # TexturePosition: 2
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

    def destroy(self):
        # utilizan listas o tuplas, por eso ponemos (elemento, )
        glDeleteVertexArrays(1, (self.vao,)) 
        glDeleteBuffers(1, (self.vbo,))

