import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Proyecto 3: Ciudad Entorno 3D - Equipo 5"

ISLAND_SIZE = 40    
# MEJORA VISUAL: STEP 0.5 significa cubos de medio metro. 
# Mucho más detalle y curvas suaves.
STEP = 0.5            
DIRT_DEPTH = 6

vertex_data = []

# ==========================================
# LÓGICA DE TERRENO
# ==========================================

def get_road_center(x):
    # Carretera diagonal con curva suave
    return x + 10 * math.sin(x / 12.0)

def generate_terrain_geometry():
    """
    Calcula geometría y colores con alta resolución.
    """
    global vertex_data
    vertex_data = []
    
    # NUEVA UBICACIÓN: Esquina Superior Derecha (X positiva, Z negativa)
    mount_x, mount_z = 32, -32
    # RADIO AUMENTADO: 45
    mount_radius = 35 

    # Para usar STEP 0.5 con range(), multiplicamos por 2 y dividimos luego
    range_limit = int(ISLAND_SIZE * 2)
    
    for i in range(-range_limit, range_limit + 1):
        x = i / 2.0  # Convertimos de nuevo a coordenadas reales (0.5)
        row = []
        
        for j in range(-range_limit, range_limit + 1):
            z = j / 2.0
            
            # --- 1. CÁLCULO DE ALTURA (Y) ---
            
            # Altura base (Ruido ligero del suelo)
            base_noise = random.uniform(0.0, 0.3)
            y = base_noise
            
            road_z = get_road_center(x)
            dist_to_road = abs(z - road_z)
            road_width = 3.5

            is_road = False
            is_mount = False

            # Lógica de Carretera
            if dist_to_road < road_width:
                y = 0.0 
                is_road = True
            
            # Lógica de Montaña (Si no es carretera)
            else:
                dist_to_mount = math.sqrt((x - mount_x)**2 + (z - mount_z)**2)
                
                if dist_to_mount < mount_radius:
                    # Elevación suave coseno
                    factor = (dist_to_mount / mount_radius) * (math.pi / 2)
                    # Altura máxima 15
                    elevation = 15 * math.cos(factor)
                    if elevation < 0: elevation = 0
                    
                    # Sumamos elevación a la base
                    y += elevation
                    is_mount = True

            # --- 2. CÁLCULO DE COLOR (ESTÁTICO) ---
            
            if is_road:
                # Gris asfalto
                r, g, b = 0.25, 0.25, 0.25 
            elif is_mount:
                # LÓGICA DE COLORES DE MONTAÑA AJUSTADA
                # Verde hasta altura 10 (Era 4) -> Más bosque
                # Roca hasta altura 13 (Era 10) -> Menos piedra
                # Nieve solo arriba de 13 -> Solo la puntita
                
                if y > 13: # Nieve (Pico)
                    r, g, b = 0.95, 0.95, 1.0
                elif y > 10: # Roca (Franja media alta)
                    r, g, b = 0.4, 0.35, 0.25
                else: 
                    # BASE VERDE: Exactamente igual al piso para que se funda
                    # Usamos la misma lógica de "green_noise" del piso plano
                    green_noise = random.uniform(-0.05, 0.05)
                    r, g, b = 0.1, 0.6 + green_noise, 0.1
            else:
                # Piso Plano (Ciudad)
                green_noise = random.uniform(-0.05, 0.05)
                r, g, b = 0.1, 0.6 + green_noise, 0.1

            # Guardamos
            row.append({
                "coords": (x, y, z),
                "color": (r, g, b)
            })
        vertex_data.append(row)

def draw_terrain():
    rows = len(vertex_data)
    cols = len(vertex_data[0])

    glBegin(GL_QUADS)
    # Iteramos por el grid de alta resolución
    for r in range(0, rows - 1):
        for c in range(0, cols - 1):
            p1 = vertex_data[r][c]
            p2 = vertex_data[r+1][c]
            p3 = vertex_data[r+1][c+1]
            p4 = vertex_data[r][c+1]
            
            col = p1["color"]
            glColor3f(col[0], col[1], col[2])

            glVertex3f(*p1["coords"])
            glVertex3f(*p2["coords"])
            glVertex3f(*p3["coords"])
            glVertex3f(*p4["coords"])
    glEnd()

    # --- LÍNEAS DE CARRETERA (Ajustadas a la nueva resolución) ---
    glLineWidth(2)
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    # Paso más fino para que la línea siga la curva perfectamente
    x_step_road = 0.5 
    for i in range(int(-ISLAND_SIZE/x_step_road), int(ISLAND_SIZE/x_step_road)):
        x_road = i * x_step_road
        
        # Hacemos líneas discontinuas (pintamos 2, saltamos 2)
        if i % 8 < 4: 
            z_road = get_road_center(x_road)
            if -ISLAND_SIZE < z_road < ISLAND_SIZE:
                glVertex3f(x_road, 0.05, z_road)
                
                next_x = x_road + x_step_road
                next_z = get_road_center(next_x)
                glVertex3f(next_x, 0.05, next_z)
    glEnd()

    # --- BASE DE TIERRA ---
    glColor3f(0.35, 0.2, 0.05)
    glBegin(GL_QUADS)
    # Paredes laterales
    glVertex3f(-ISLAND_SIZE, 0, ISLAND_SIZE); glVertex3f(ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE); glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)

    glVertex3f(ISLAND_SIZE, 0, -ISLAND_SIZE); glVertex3f(-ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE); glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    
    glVertex3f(-ISLAND_SIZE, 0, -ISLAND_SIZE); glVertex3f(-ISLAND_SIZE, 0, ISLAND_SIZE)
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE); glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)

    glVertex3f(ISLAND_SIZE, 0, ISLAND_SIZE); glVertex3f(ISLAND_SIZE, 0, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE); glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    # Tapa
    glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE); glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, -ISLAND_SIZE)
    glVertex3f(ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE); glVertex3f(-ISLAND_SIZE, -DIRT_DEPTH, ISLAND_SIZE)
    glEnd()

# ==========================================
# MAIN
# ==========================================
def main():
    pygame.init()
    display = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_TITLE)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

    print("Generando terreno de alta resolución...")
    generate_terrain_geometry()
    print("¡Terreno listo!")

    # Cámara inicial
    cam_x, cam_y, cam_z = 0, 50, 70 
    look_x, look_y, look_z = 0, 0, 0

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Controles de debug (Flechas)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: cam_x -= 1
            if keys[pygame.K_RIGHT]: cam_x += 1
            if keys[pygame.K_UP]: cam_z -= 1 # Acercar
            if keys[pygame.K_DOWN]: cam_z += 1 # Alejar
            if keys[pygame.K_w]: cam_y += 1 # Subir altura
            if keys[pygame.K_s]: cam_y -= 1 # Bajar altura

        glClearColor(0.53, 0.81, 0.92, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)

        draw_terrain()

        # AQUÍ TUS COMPAÑEROS AGREGARÁN SUS OBJETOS
        # draw_objects_scene() 

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
