import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# ==========================================
# CONFIGURACIÓN DEL PROYECTO
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Proyecto 3: Ciudad Entorno 3D - Equipo 5"

# Dimensiones del Terreno
ISLAND_SIZE = 40       # Radio del mundo (Total 80x80 unidades)
STEP = 0.5             # Resolución de la malla (0.5 = Alta calidad)
DIRT_DEPTH = 10        # Profundidad de la base de tierra

# Variable global para almacenar la geometría generada
vertex_data = []

# ==========================================
# LÓGICA MATEMÁTICA DEL TERRENO
# ==========================================

def get_road_center(x):
    """
    Define la trayectoria de la carretera.
    Retorna la posición Z para un X dado, creando una curva suave.
    """
    return x + 10 * math.sin(x / 12.0)

def interpolate_color(color1, color2, factor):
    """
    Función auxiliar para crear degradados suaves entre dos colores.
    factor: 0.0 (color1) a 1.0 (color2)
    """
    r = color1[0] + (color2[0] - color1[0]) * factor
    g = color1[1] + (color2[1] - color1[1]) * factor
    b = color1[2] + (color2[2] - color1[2]) * factor
    return (r, g, b)

def generate_terrain_geometry():
    """
    Genera la malla de vértices, calcula alturas y asigna colores estáticos.
    Se ejecuta una sola vez al inicio para optimizar rendimiento.
    """
    global vertex_data
    vertex_data = []
    
    # Configuración de la Montaña (Esquina Superior Derecha)
    mount_x, mount_z = 32, -32
    mount_radius = 40 

    # Iteramos sobre el área total con la resolución definida
    range_limit = int(ISLAND_SIZE * 2)
    
    for i in range(-range_limit, range_limit + 1):
        x = i / 2.0  # Ajuste por el STEP de 0.5
        row = []
        
        for j in range(-range_limit, range_limit + 1):
            z = j / 2.0
            
            # --- 1. CÁLCULO DE ALTURA ---
            base_noise = random.uniform(0.0, 0.3) # Pequeña variación natural
            y = base_noise
            
            road_z = get_road_center(x)
            dist_to_road = abs(z - road_z)
            road_width = 3.5
            
            is_road = False
            is_mount = False
            mount_height_factor = 0 # Qué tan alto estamos en la montaña (0 a 1)

            # Zona Carretera
            if dist_to_road < road_width:
                y = 0.0 
                is_road = True
            
            # Zona Terreno / Montaña
            else:
                dist_to_mount = math.sqrt((x - mount_x)**2 + (z - mount_z)**2)
                
                if dist_to_mount < mount_radius:
                    # Elevación usando Coseno para suavidad
                    factor = (dist_to_mount / mount_radius) * (math.pi / 2)
                    elevation = 15 * math.cos(factor)
                    if elevation < 0: elevation = 0
                    
                    y += elevation
                    is_mount = True
                    # Guardamos el factor de altura para el color (0 = base, 15 = pico)
                    mount_height_factor = elevation

            # --- 2. ASIGNACIÓN DE COLOR ---
            
            if is_road:
                # Gris Asfalto
                r, g, b = 0.25, 0.25, 0.25 
            
            elif is_mount:
                # Lógica de Degradado de Montaña
                
                # Definición de Colores Clave
                col_pasto = (0.1, 0.6, 0.1)       # Base (Igual al plano)
                col_bosque = (0.05, 0.25, 0.05)   # Verde Intenso Oscuro
                col_roca = (0.4, 0.35, 0.25)      # Café Roca
                col_nieve = (0.95, 0.95, 1.0)     # Blanco
                
                # Transiciones
                if y > 13: 
                    # Nieve (Pico)
                    r, g, b = col_nieve
                elif y > 10: 
                    # Roca (Parte alta)
                    r, g, b = col_roca
                else:
                    # DEGRADADO: De Pasto a Bosque Intenso
                    # Normalizamos la altura de 0 a 10 para el degradado
                    grad_factor = min(y / 10.0, 1.0)
                    r, g, b = interpolate_color(col_pasto, col_bosque, grad_factor)
                    
                    # Agregamos un mínimo de ruido para mantener textura
                    noise = random.uniform(-0.02, 0.02)
                    g += noise

            else:
                # Zona Plana (Ciudad)
                # Verde pasto con variación ligera
                noise = random.uniform(-0.05, 0.05)
                r, g, b = 0.1, 0.6 + noise, 0.1

            # Guardamos el vértice completo
            row.append({
                "coords": (x, y, z),
                "color": (r, g, b)
            })
        vertex_data.append(row)

# ==========================================
# FUNCIONES DE DIBUJADO
# ==========================================

def draw_terrain_surface():
    """Dibuja la superficie superior (pasto, carretera, montaña)."""
    rows = len(vertex_data)
    cols = len(vertex_data[0])

    glBegin(GL_QUADS)
    for r in range(rows - 1):
        for c in range(cols - 1):
            p1 = vertex_data[r][c]
            p2 = vertex_data[r+1][c]
            p3 = vertex_data[r+1][c+1]
            p4 = vertex_data[r][c+1]
            
            # Usamos el color pre-calculado del vértice
            col = p1["color"]
            glColor3f(*col)

            glVertex3f(*p1["coords"])
            glVertex3f(*p2["coords"])
            glVertex3f(*p3["coords"])
            glVertex3f(*p4["coords"])
    glEnd()

def draw_dirt_walls():
    """
    Dibuja los muros laterales de tierra.
    Se adaptan dinámicamente a la altura del terreno para evitar huecos.
    """
    rows = len(vertex_data)
    cols = len(vertex_data[0])
    
    glColor3f(0.35, 0.2, 0.05) # Color Marrón Tierra

    glBegin(GL_QUADS)
    
    # Recorremos los 4 bordes del mapa
    
    # 1. Borde Norte (z mínima)
    for c in range(cols - 1):
        p1 = vertex_data[0][c]["coords"]
        p2 = vertex_data[0][c+1]["coords"]
        # Pared conecta la superficie con la profundidad
        glVertex3f(p1[0], p1[1], p1[2])           # Arriba Izq
        glVertex3f(p2[0], p2[1], p2[2])           # Arriba Der
        glVertex3f(p2[0], -DIRT_DEPTH, p2[2])     # Abajo Der
        glVertex3f(p1[0], -DIRT_DEPTH, p1[2])     # Abajo Izq

    # 2. Borde Sur (z máxima)
    for c in range(cols - 1):
        p1 = vertex_data[rows-1][c]["coords"]
        p2 = vertex_data[rows-1][c+1]["coords"]
        glVertex3f(p2[0], p2[1], p2[2])
        glVertex3f(p1[0], p1[1], p1[2])
        glVertex3f(p1[0], -DIRT_DEPTH, p1[2])
        glVertex3f(p2[0], -DIRT_DEPTH, p2[2])

    # 3. Borde Oeste (x mínima)
    for r in range(rows - 1):
        p1 = vertex_data[r][0]["coords"]
        p2 = vertex_data[r+1][0]["coords"]
        glVertex3f(p2[0], p2[1], p2[2])
        glVertex3f(p1[0], p1[1], p1[2])
        glVertex3f(p1[0], -DIRT_DEPTH, p1[2])
        glVertex3f(p2[0], -DIRT_DEPTH, p2[2])

    # 4. Borde Este (x máxima)
    for r in range(rows - 1):
        p1 = vertex_data[r][cols-1]["coords"]
        p2 = vertex_data[r+1][cols-1]["coords"]
        glVertex3f(p1[0], p1[1], p1[2])
        glVertex3f(p2[0], p2[1], p2[2])
        glVertex3f(p2[0], -DIRT_DEPTH, p2[2])
        glVertex3f(p1[0], -DIRT_DEPTH, p1[2])
        
    # Tapa Inferior (Fondo plano para cerrar el bloque)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    
    glEnd()

def draw_road_lines():
    """Dibuja las líneas blancas discontinuas de la carretera."""
    glLineWidth(2)
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    
    step_check = 0.5
    range_val = int(ISLAND_SIZE / step_check)
    
    for i in range(-range_val, range_val):
        x = i * step_check
        # Patrón discontinuo
        if i % 8 < 4: 
            z = get_road_center(x)
            if -ISLAND_SIZE < z < ISLAND_SIZE:
                glVertex3f(x, 0.05, z) # Elevación mínima para evitar Z-fighting
                
                next_x = x + step_check
                next_z = get_road_center(next_x)
                glVertex3f(next_x, 0.05, next_z)
    glEnd()

# ==========================================
# ZONA DE COLABORACIÓN (EQUIPO)
# ==========================================
def draw_team_objects():
    """
    ESPACIO RESERVADO PARA:
    Miguel, Jesus, Jose, Axel.
    Aquí deben instanciar sus objetos (casas, árboles, coches, etc.)
    """
    pass

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
def main():
    pygame.init()
    display = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_TITLE)

    # Configuración OpenGL
    glEnable(GL_DEPTH_TEST) # Habilitar buffer de profundidad
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    # 1. Generar el mundo (Una sola vez)
    print("Generando entorno...")
    generate_terrain_geometry()
    print("Entorno listo.")

    # Variables de Cámara
    cam_x, cam_y, cam_z = 0, 40, 70 
    look_x, look_y, look_z = 0, 0, 0

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # TODO: Integrar aquí controles finales o MediaPipe
            keys = pygame.key.get_pressed()
            # Movimiento manual para pruebas de visualización
            if keys[pygame.K_LEFT]: cam_x -= 1
            if keys[pygame.K_RIGHT]: cam_x += 1
            if keys[pygame.K_UP]: cam_z -= 1 
            if keys[pygame.K_DOWN]: cam_z += 1
            if keys[pygame.K_w]: cam_y += 1 
            if keys[pygame.K_s]: cam_y -= 1

        # Renderizado
        glClearColor(0.53, 0.81, 0.92, 1) # Cielo azul claro
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Actualizar Cámara
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)

        # Dibujar Escena
        draw_terrain_surface()
        draw_dirt_walls()
        draw_road_lines()
        
        # Objetos del equipo
        draw_team_objects()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
