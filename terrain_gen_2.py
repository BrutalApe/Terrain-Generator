#terrain_gen_2
#instead of using cubes, subdivide a plane 
#raise/lower vertices to achieve same desired terrain effect
# connect them
# smoothen thems

import bpy
from bpy import data as D
from bpy import context as C
from bpy import ops as O

from mathutils import *
from math import *
from random import randint
from time import sleep

def create_cube(name, x_loc, y_loc, z_loc, x_scl, y_scl, z_scl):
    print("Creating cube...")
    O.mesh.primitive_cube_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, z_scl))
    
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Cube"):
            obj.name = name

def create_plane(name, x_loc, y_loc, z_loc, x_scl, y_scl):
    print("Creating plane...")
    O.mesh.primitive_plane_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, 0))
    
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Plane"):
            obj.name = name

def subdivide_face(object_name, face, num_of_cuts):
    print("Subdividing face...")
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = bpy.context.active_object

    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="FACE")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')
    
    # select the chosen face
    obj.data.polygons[face].select = True

    O.object.mode_set(mode="EDIT")
    O.mesh.subdivide(number_cuts=num_of_cuts)
    O.object.mode_set(mode="OBJECT")
    
def subdivide_plane(object_name, num_of_cuts):
    print("Subdividing plane...")
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = bpy.context.active_object

    O.object.mode_set(mode="EDIT")
    O.mesh.subdivide(number_cuts=num_of_cuts)
    O.object.mode_set(mode="OBJECT")

def adjust_vertex_height(obj, vertex_array, vertex_id, new_height):
    obj.data.vertices[vertex_id].select = True
    O.object.mode_set(mode="EDIT")
    O.transform.translate(value=(0, 0, (new_height)))
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode="OBJECT")
    vertex_array[vertex_id] = new_height

def modify_face_vertices(object_name, vertex_array, size, count, z_min, z_max):
    print("Modifying face vertices...")
    vertex_ids = [((size+1)*(size+1))+1] * count  
    
    #33 14 15 24 18 17
    banned_vertex_ids = [57,58,66,67,75,76,84,85,93,94,102,103,111]
    
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = bpy.context.active_object
    
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="VERT")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')
    
    i = 0
    while(i < count):
        vertex_id = randint(0, size*size)
        print(vertex_id)
                
        if vertex_id in vertex_ids:
            print("oops, skipping...")
            continue
        if ((vertex_id in banned_vertex_ids)
         or (vertex_id + (size-1) >= ((size+1)*(size+1))) 
         or (vertex_id - (size-1) < ((size)*4))):
            print("bruh, no way...")
            continue
        
        vertex_ids[i] = vertex_id
        z_scl = randint(z_min, z_max)
        adjust_vertex_height(obj, vertex_array, vertex_id, 0.25*z_scl)
        adjust_vertex_height(obj, vertex_array, vertex_id+1, 0.15*z_scl)
        adjust_vertex_height(obj, vertex_array, vertex_id-1, 0.15*z_scl)
        adjust_vertex_height(obj, vertex_array, vertex_id+(size-1), 0.15*z_scl)
        adjust_vertex_height(obj, vertex_array, vertex_id-(size-1), 0.15*z_scl)
        i += 1

def select_all_meshes():
    for obj in C.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)

def remove_all_meshes():
    
    select_all_meshes()
    
    O.object.delete()
            

def main():
    print("Generating Terrain...")
    
    O.object.mode_set(mode='OBJECT', toggle=False)
    remove_all_meshes()
        
    # create base
    base_size = 10
    base_x_scl = base_size
    base_y_scl = base_size
#    create_cube("Base", 0, 0, -0.1, base_x_scl, base_y_scl, 0.1)
    create_plane("Base", 0, 0, 0, base_x_scl, base_y_scl)
    subdivide_plane("Base", base_size-1)

    z_min = 3
    z_max = 7
    count = 5 # 30 is the highest safe value, i think. at least for 10x10.
    # should find a way to calculate it algorithmically
    
    vertex_array = [0] * (base_size + 1) * (base_size + 1)
    
    modify_face_vertices("Base", vertex_array, base_size, count, z_min, z_max)
    print(vertex_array)
    O.object.mode_set(mode = 'EDIT')
    
    
    for a in C.screen.areas:
        if a.type == 'VIEW_3D':
            overlay = a.spaces.active.overlay
            overlay.show_extra_indices = True
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="VERT")
    O.mesh.select_all(action = 'SELECT')
    
    
if __name__ == "__main__":
    main()

