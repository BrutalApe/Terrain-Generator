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
    O.mesh.primitive_cube_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, z_scl))
    
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Cube"):
            obj.name = name

def subdivide_face(object_name, face, num_of_cuts):
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

def modify_face_vertices(object_name, size, count, z_min, z_max):
    vertex_ids = [(size*size)+1] * count  
    banned_vertex_ids = [0, 2, 4, 6]
    
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
        if vertex_id in banned_vertex_ids:
            print("bruh, no way...")
            continue
        
        vertex_ids[i] = vertex_id
        z_scl = randint(z_min, z_max)
                        
        obj.data.vertices[vertex_id].select = True
        O.object.mode_set(mode="EDIT")
        O.transform.translate(value=(0, 0, (.25*z_scl)))
        O.mesh.select_all(action = 'DESELECT')
        O.object.mode_set(mode="OBJECT")
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
    create_cube("Base", 0, 0, -0.1, base_x_scl, base_y_scl, 0.1)
    subdivide_face("Base", 5, base_size)

    z_min = 1
    z_max = 5
    count = 10 # 30 is the highest safe value, i think. at least for 10x10.
    # should find a way to calculate it algorithmically
    
    modify_face_vertices("Base", base_size, count, z_min, z_max)


if __name__ == "__main__":
    main()

