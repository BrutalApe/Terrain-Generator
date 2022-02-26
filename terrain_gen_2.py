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

def adjust_vertex_height(obj, vertex_array, vertex_ids, new_height):
    for v in vertex_ids:
        obj.data.vertices[v].select = True
        O.object.mode_set(mode="EDIT")
        O.transform.translate(value=(0, 0, (new_height)))
        O.mesh.select_all(action = 'DESELECT')
        O.object.mode_set(mode="OBJECT")
        vertex_array[v] = new_height

def modify_face_vertices(object_name, vertex_array, mt_level, size, count, z_min, z_max):
    print("Modifying face vertices...")
    
    # outer rim of ids, always determined this way, regardless of odd or even
    outermost_layer = list(range(0, size*4))
    
    # now will make list of lists of indices, 
    # where [0] is outermost, [n] is center index/group of
    layer_count = size//2 + 1
    
    layers = [[] for _ in range(layer_count)]
    layers[0] = outermost_layer  

    for i in range(1,layer_count):
        if ((i == layer_count-1) and (size%2==0)): # even and last layer; center/group of 4
            layers[i].append(size*(3+i))
        else:
            layers[i].extend(list(range(size*(3+i),(size*(3+i))+(size-(2*i)+1))))                 
            value_pair_start = size*(3+i) + (size-1)
            for j in range(size-((2*i) + 1)):
                layers[i].append(value_pair_start)
                layers[i].append(value_pair_start + (size-(2*i)))
                value_pair_start = value_pair_start + (size-1)
            layers[i].extend(list(range((size*(size+3-i))-(size-(2*i)),(size*(size+3-i))+1)))

    print("Layers:")
    print(layers)  
    
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = bpy.context.active_object
    
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="VERT")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')

    available_ids = []
    print("mt_level", mt_level)
    for m in range(layer_count):
        if (m <= mt_level):
            continue
        available_ids.extend(layers[m])
    
    if (count > len(available_ids)):
        print("Too many hills requested, would repeat...")
        return
    
    print("Available ids:", available_ids)
        
    i = 0
    while(i < count):
        skip_flag = 0
        vertex_id = available_ids[randint(0, len(available_ids)-1)]
        print(vertex_id)
        
        available_ids.remove(vertex_id)
        
        z_scl = randint(z_min, z_max)
        vertex_to_update = [vertex_id]
        vertex_updated = []
        v_adj = size-1
        for l in range(mt_level+1):
            vh = round((mt_level+1-l)*0.1*z_scl,3)
            print("L", l, "vtu", vertex_to_update)
            adjust_vertex_height(obj, vertex_array, vertex_to_update, vh)
            vertex_updated.extend(vertex_to_update)
            vertex_to_update[:] = []
            for vi in range(len(vertex_updated)):  
                v = vertex_updated[vi]
                if (v+v_adj not in vertex_updated) and (v+v_adj not in vertex_to_update):
                    vertex_to_update.append(v+v_adj)
                if (v-v_adj not in vertex_updated) and (v-v_adj not in vertex_to_update):
                    vertex_to_update.append(v-v_adj)
                if (v+1 not in vertex_updated) and (v+1 not in vertex_to_update):
                    vertex_to_update.append(v+1)
                if (v-1 not in vertex_updated) and (v-1 not in vertex_to_update):
                    vertex_to_update.append(v-1)
                    
        i += 1
    
#    print(available_ids)
    
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
    base_size = 8 # 2 is min size
    base_x_scl = base_size
    base_y_scl = base_size
#    create_cube("Base", 0, 0, -0.1, base_x_scl, base_y_scl, 0.1)
    create_plane("Base", 0, 0, 0, base_x_scl, base_y_scl)
    subdivide_plane("Base", base_size-1)

    z_min = 3
    z_max = 7
    count = 1
    mountain_level = 2
    
    vertex_array = [0] * (base_size + 1) * (base_size + 1)
    
    modify_face_vertices("Base", vertex_array, mountain_level, base_size, count, z_min, z_max)
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

