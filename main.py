import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Proyecto 3: Ciudad Flotante - Equipo 5"

# Dimensiones de la isla
ISLAND_SIZE = 40    # Tamaño total (40x40 unidades)
STEP = 2            # Cada cuánto dibujamos un cuadro (resolución de la malla)
DIRT_DEPTH = 5      # Qué tan gruesa es la capa de tierra hacia abajo

# Listas para guardar la geometría del terreno y no recalcularla siempre
vertex_data = []

# ==========================================
# GENERACIÓN DE TERRENO (Arquitectura)
# ==========================================

def generate_terrain_geometry():
    """
    Genera los vértices del terreno una sola vez al iniciar el programa.
    Crea relieves aleatorios pero deja un camino plano para la carretera.
    """
    global vertex_data
    vertex_data = []
    
    # Recorremos el área de la isla en cuadrícula
    for x in range(-ISLAND_SIZE, ISLAND_SIZE, STEP):
        row = []
        for z in range(-ISLAND_SIZE, ISLAND_SIZE, STEP):
            
            # --- Lógica de Relieve ---
            # Si estamos en el centro (donde va la calle), altura 0 (plano)
            if -6 < x < 6: 
                y = 0 
            else:
                # En el pasto, altura aleatoria suave (entre 0 y 1.5)
                y = random.uniform(0, 1.5)
            
            row.append((x, y, z))
        vertex_data.append(row)

def draw_floating_island():
    """
    Dibuja la isla completa: Pasto, Carretera y el bloque de tierra (base).
    """
    rows = len(vertex_data)
    cols = len(vertex_data[0])

    # 1. DIBUJAR LA SUPERFICIE (Pasto y Carretera)
    glBegin(GL_QUADS)
    for r in range(rows - 1):
        for c in range(cols - 1):
            # Obtenemos los 4 puntos del cuadro actual
            x1, y1, z1 = vertex_data[r][c]
            x2, y2, z2 = vertex_data[r+1][c]
            x3, y3, z3 = vertex_data[r+1][c+1]
            x4, y4, z4 = vertex_data[r][c+1]

            # Definir color según la zona
            # Si la coordenada X está en el centro, es carretera (Gris)
            if -6 < x1 < 6:
                glColor3f(0.3, 0.3, 0.3) # Gris asfalto
            else:
                # Pasto: Variamos un poco el verde para que se vea texturizado
                glColor3f(0.0, 0.6 + (y1/10), 0.0) 

            # Dibujar el quad superior
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
            glVertex3f(x3, y3, z3)
            glVertex3f(x4, y4, z4)
    glEnd()

    # 2. DIBUJAR LÍNEAS DE LA CARRETERA (Detalle)
    # Dibujamos líneas blancas en el centro
    glLineWidth(3)
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex3f(0, 0.1, -ISLAND_SIZE) # Un poquito arriba (0.1) para que no se traslape
    glVertex3f(0, 0.1, ISLAND_SIZE)
    glEnd()

    # 3. DIBUJAR EL BLOQUE DE TIERRA (Los costados y el fondo)
    # Esto da el efecto de isla flotante arrancada del suelo
    glColor3f(0.35, 0.2, 0.05) # Marrón oscuro

    glBegin(GL_QUADS)
    # Tapa inferior (Fondo plano)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    
    # Paredes laterales (Simplificadas para el borde exterior)
    # Lado Izquierdo
    glVertex3f(-ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    # Lado Derecho
    glVertex3f(ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    # Lado Frontal
    glVertex3f(-ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    # Lado Trasero
    glVertex3f(ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glEnd()


# ==========================================
# ZONA DE COLABORACIÓN (Objetos)
# ==========================================
def draw_objects_scene():
    """
    Aquí tus compañeros (Miguel, Jesus, Jose, Axel) agregarán sus objetos.
    """
    # Placeholder: Un cubo rojo flotando sobre la carretera para referencia
    glPushMatrix()
    glTranslatef(0, 2, 0) 
    glColor3f(1, 0, 0)
    # glutSolidCube(2) # Usar si GLUT está disponible, sino dibujar manual
    glPopMatrix()
    pass

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    pygame.init()
    display = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_TITLE)

    glEnable(GL_DEPTH_TEST) # Importante: Activar profundidad para que no se vea transparente lo de atrás
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    # Generamos el terreno UNA vez antes del bucle
    generate_terrain_geometry()

    # Variables de cámara iniciales
    cam_x, cam_y, cam_z = 30, 25, 50 
    look_x, look_y, look_z = 0, 0, 0 

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Color de fondo (Cielo etéreo - Azul claro casi blanco)
        glClearColor(0.5, 0.8, 0.9, 1) 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        
        # Cámara mirando hacia el centro de la isla
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)

        # Dibujar nuestra arquitectura base
        draw_floating_island()

        # Dibujar los objetos del equipo
        draw_objects_scene()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
