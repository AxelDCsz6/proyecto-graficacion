import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Proyecto 3: Ciudad Entorno 3D - Equipo 5"

# ==========================================
# CLASE O FUNCIONES DE AYUDA (WORLD)
# ==========================================

def draw_axes():
    """Dibuja los ejes X, Y, Z para referencia espacial."""
    glBegin(GL_LINES)
    # Eje X (Rojo)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(100, 0, 0)
    # Eje Y (Verde - Altura)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 100, 0)
    # Eje Z (Azul - Profundidad)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 100)
    glEnd()

def draw_terrain():
    """
    Dibuja el suelo de la ciudad. 
    Es una malla (grid) grande para dar sensación de profundidad.
    """
    glColor3f(0.2, 0.2, 0.2) # Color gris oscuro para las líneas
    
    tamano = 100 # Qué tan grande es el mundo
    paso = 5     # Espacio entre líneas
    
    glBegin(GL_LINES)
    for i in range(-tamano, tamano + paso, paso):
        # Líneas paralelas al eje X
        glVertex3f(-tamano, 0, i)
        glVertex3f(tamano, 0, i)
        # Líneas paralelas al eje Z
        glVertex3f(i, 0, -tamano)
        glVertex3f(i, 0, tamano)
    glEnd()

# ==========================================
# ZONA DE COLABORACIÓN
# ==========================================
# SUGERENCIA PARA COMPAÑEROS:
# Importen sus funciones de dibujo aquí o defínanlas abajo.
# Ejemplo: def dibujar_casa(): ...

def draw_objects_scene():
    """
    FUNCIÓN PRINCIPAL PARA DIBUJAR LOS 20 OBJETOS.
    Compañeros: Agreguen sus llamadas a funciones aquí.
    """
    # TODO: [Equipo] Aquí se deben instanciar los 20 objetos móviles.
    # Ejemplo placeholder (un cubo simple en el centro):
    glPushMatrix()
    glTranslatef(0, 2, 0) # Moverlo un poco arriba
    glColor3f(1, 1, 0)    # Amarillo
    # glutSolidCube(2)    # Requiere GLUT, usamos primitiva manual si no hay GLUT:
    # (Aquí irían sus funciones como draw_snowman() o draw_house())
    glPopMatrix()
    
    pass

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    # Inicializar Pygame y OpenGL
    pygame.init()
    display = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_TITLE)

    # Configuración de la Cámara (Perspectiva)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    # Variables de cámara (gluLookAt) iniciales
    # Estas variables serán las que modifique MediaPipe más adelante
    cam_x, cam_y, cam_z = 0, 10, 30  # Posición de la cámara (Ojo)
    look_x, look_y, look_z = 0, 0, 0 # A dónde mira la cámara (Centro)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # TODO: [Equipo/MediaPipe] Aquí se puede agregar input de teclado 
            # temporalmente para pruebas antes de tener MediaPipe listo.

        # 1. Limpiar pantalla y buffer de profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 2. Configurar la cámara en cada frame
        glLoadIdentity()
        
        # TODO: [MediaPipe] Aquí se actualizarán cam_x, cam_y, cam_z
        # basándose en los landmarks de la mano.
        gluLookAt(cam_x, cam_y, cam_z,  # Ojo
                  look_x, look_y, look_z, # Objetivo
                  0, 1, 0)              # Up Vector (Y es arriba)

        # 3. Dibujar el entorno estático
        draw_axes()
        draw_terrain()

        # 4. Dibujar los objetos del equipo (Casas, Snowman, Coches, etc.)
        draw_objects_scene()

        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60) # Limitar a 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
