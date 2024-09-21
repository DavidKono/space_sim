import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import math

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((800,600))

# menu
menu_height = 200
menu_surf = pygame.Surface((800, menu_height), pygame.SRCALPHA)
menu_surf.fill((100,100,100))

mass_slider = Slider(screen, 100, 50, 100, 40, min=1, max=100, step=1)
mass_textbox = TextBox(screen, 100, 100, 50, 50, fontSize=30)
mass_textbox.disable()

size_slider = Slider(screen, 100, 150, 100, 40, min=1, max=100, step=1)
size_textbox = TextBox(screen, 100, 200, 50, 50, fontSize=30)
size_textbox.disable()

mouse_held = False
mouse_start = pygame.mouse.get_pos()
start_dampener = 0.01
velocity_textbox = TextBox(screen, 400, 100, 50, 50, fontSize=30)


foresight = 1
depth_future_foresight = 300
foresight_rad = 3
foresight_surf = pygame.Surface((foresight_rad*2, foresight_rad*2), pygame.SRCALPHA)
pygame.draw.circle(foresight_surf, (0, 0, 0), (foresight_rad,foresight_rad), foresight_rad)


p_bodies = [[]]
p_velocities = [[]]
p_masses = []
p_radii = []
surfs = []
num_bodies = 0

gravity_constant = 10

def add_sphere():
    global num_bodies

    rad = size_slider.getValue()
    surf = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (0, 0, 255), (rad,rad), rad)
    surfs.append(surf)

    corrected_position = tuple(a-b for a,b in zip(mouse_start, (rad,rad)))
    p_bodies[0].append(corrected_position)

    velocity = tuple((a-b)*start_dampener for a,b in zip(mouse_start,pygame.mouse.get_pos()))
    p_velocities[0].append(velocity)
    
    p_masses.append(mass_slider.getValue()*gravity_constant)
    p_radii.append(size_slider.getValue())

    num_bodies += 1

    if foresight: run_foresight_sim() 


def run_foresight_sim():
    global p_bodies
    global p_velocities
    # print("first print", p_bodies[0])
    p_bodies = [(p_bodies[0])]
    p_velocities = [p_velocities[0]]

    # print("second print", p_bodies[-1])
    for _ in range(depth_future_foresight):
        apply_gravity(True)
        update_positions(True)


def apply_gravity(foresight_sim):
    global p_bodies
    for i in range(num_bodies):
        for j in range(num_bodies):
            if i != j:

                # print("ij",i,j)
                # print(p_bodies[-1])

                dist_squared = math.dist([p_bodies[-1][i][0],p_bodies[-1][i][1]], [p_bodies[-1][j][0],p_bodies[-1][j][1]])**2
                if dist_squared == 0: dist_squared = 0.01

                x_ratio = -(p_bodies[-1][i][0] - p_bodies[-1][j][0])
                y_ratio = -(p_bodies[-1][i][1] - p_bodies[-1][j][1])
                if x_ratio == 0: x_ratio = 0.00001
                if y_ratio == 0: y_ratio = 0.00001
                ratio_total = abs(x_ratio) + abs(y_ratio)

                vel_update = (x_ratio/ratio_total / dist_squared * p_masses[j], y_ratio/ratio_total / dist_squared * p_masses[j]) 

                p_velocities.append(list(p_velocities[-1]))
                if not foresight_sim: p_velocities.pop(0)

                p_velocities[-1][i] = tuple(a+b for a,b in zip(p_velocities[-1][i], vel_update))

def update_positions(foresight_sim):
    p_bodies.append(list(p_bodies[-1]))
    if not foresight_sim: p_bodies.pop(0)

    for i in range(num_bodies):
        # print(" ")
        # print("before", p_bodies[-1])
        p_bodies[-1][i] = tuple(a+b for a,b in zip(p_bodies[-1][i], p_velocities[-1][i]))
        # print("after", p_bodies[-1])  
        # print("after full",p_bodies)  

def draw():
    screen.fill((255,255,255))
    screen.blit(menu_surf, (0,0))

    if foresight:
        draw_future_path()
    draw_surfs()


def draw_surfs():
    for i in range(num_bodies):
        for i in range(num_bodies):
            screen.blit(surfs[i], p_bodies[0][i])

def draw_future_path():
    for i in range(depth_future_foresight):
        for j in range(num_bodies):
            # print(p_radii[j])
            # pos = tuple(a+b for a,b in zip(p_bodies[i][j], (p_radii[j],p_radii[j])))
            # print(pos)
            pos = tuple(a+b-c for a,b,c in zip(p_bodies[i][j], (p_radii[j],p_radii[j]), (foresight_rad, foresight_rad)))
            screen.blit(foresight_surf, pos)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if pygame.mouse.get_pos()[1] > menu_height:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_start = pygame.mouse.get_pos()
                mouse_held = True

        if mouse_held == True and event.type == pygame.MOUSEBUTTONUP:
            print("before add p[0]", p_velocities[0])
            print("before add p[-1]", p_velocities[-1])
            add_sphere()
            print("after add", p_velocities[0])
            print("after add p[-1]", p_velocities[-1])
            mouse_held = False

    
    apply_gravity(False)
    update_positions(False)

    # print(" in loop", p_bodies)
    quit
    
    draw()

    size_textbox.setText(size_slider.getValue())
    mass_textbox.setText(mass_slider.getValue())
    velocity_textbox.setText(0)

    if mouse_held == True:
        velocity_textbox.setText(int(math.dist(mouse_start,pygame.mouse.get_pos())))
        pygame.draw.line(screen, (0,0,0), mouse_start, pygame.mouse.get_pos())

    pygame_widgets.update(events)
    pygame.display.update()

    clock.tick(60)