#terrain_gen_2
#instead of using cubes, subdivide a plane 
#raise/lower vertices to achieve same desired terrain effect
# fname = "C:/Users/scott/Documents/Projects/terrain_gen_2.py"
# exec(compile(open(fname).read(), fname, 'exec'))

import bpy
from bpy import data as D
from bpy import context as C
from bpy import ops as O
import bmesh

from mathutils import *
from math import *
from random import randint
from time import sleep

# Updates viewport while running code
def update_viewport():
    # Technically this is not a good thing to do,
    # but for testing it's fine. Remove in the future.
    # O.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    return

# Creates a cube using given parameters
# Params:
#   name - name of cube
#   x,y,z_loc - location of cube
#   x,y,z_scl - scale of cube
# Return:
#   Nothing 
def create_cube(name, x_loc, y_loc, z_loc, x_scl, y_scl, z_scl):
    print("Creating cube...")
    O.mesh.primitive_cube_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, z_scl))
    
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Cube"):
            obj.name = name

# Creates a plane using given parameters
# Params:
#   name - name of plane
#   x,y,z_loc - location of plane
#   x,y_scl - scale of plane
# Return:
#   Nothing 
def create_plane(name, x_loc, y_loc, z_loc, x_scl, y_scl):
    print("Creating plane...")
    O.mesh.primitive_plane_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, 0))
    
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Plane"):
            obj.name = name
            break

    return obj

# Triangulate-subdivides all faces with vertices of height != 0
# Params:
#   obj_name - mesh to modify
# Return:
#   Nothing 
def triangulate_edit_object(obj_name):
    for obj in C.scene.objects:
        if obj.name == obj_name:
            obj.select_set(True)

    obj = C.active_object

    O.object.mode_set(mode = 'EDIT') 
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)
    
    total_faces = 0
    for f in bm.faces:
        for v in f.verts:
            if (v.co.z != 0):
                bmesh.ops.triangulate(bm, faces=bm.faces[(f.index):(f.index+1)])
                total_faces += 1
                break
    
    print("Total faces triangulated:", total_faces)
    # Show the updates in the viewport
    # and recalculate n-gon tessellation.
    bmesh.update_edit_mesh(me, True)

# Subdivides a specific face
# Params:
#   object_name - name of object to be subdivided
#   face - index of face to be subdivided
#   num_of_cuts - how many times to subdivide
# Return:
#   Nothing 
def subdivide_face(object_name, face, num_of_cuts):
    print("Subdividing face...")
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = C.active_object

    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="FACE")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')
    
    # select the chosen face
    obj.data.polygons[face].select = True

    O.object.mode_set(mode="EDIT")
    O.mesh.subdivide(number_cuts=num_of_cuts)
    O.object.mode_set(mode="OBJECT")
    
# Subdivides a plane
# Params:
#   object_name - name of object to be subdivided
#   num_of_cuts - how many times to subdivide
# Return:
#   Nothing 
def subdivide_plane(object_name, num_of_cuts):
    print("Subdividing plane...")
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = C.active_object

    O.object.mode_set(mode="EDIT")
    O.mesh.subdivide(number_cuts=num_of_cuts)
    O.object.mode_set(mode="OBJECT")

# Deselects all vertices of mesh
# Params:
#   obj - name of object whose vertices should be deselected
# Return:
#   Nothing
def deselect_all_vertices(obj):
    O.object.mode_set(mode="OBJECT")
    v = C.object.data.vertices
    f = C.object.data.polygons
    e = C.object.data.edges
    #to deselect vertices you need to deselect faces(polygons) and edges at first
    for i in f:                   
        i.select=False               
    for i in e:
        i.select=False
    for i in v:
        i.select=False
    return

# Selects vertex of mesh
# Params:
#   obj - name of object 
#   v - index of vertex to select
# Return:
#   Nothing
def select_vertex(obj, v):
    O.object.mode_set(mode="OBJECT")
    obj.data.vertices[v].select = True
    O.object.mode_set(mode = 'EDIT')
    return

# Selects all vertices in a list
# Params:
#   obj - name of object
#   v_list - list of vertices to select
# Return:
#   Nothing
def select_vertices(obj, v_list):
    for v in v_list:
        select_vertex(obj, v)
    return

# Adjusts heights of vertices based on values in list
# Params:
#   obj - name of object
#   vertex_array - list of all vertex heights
#   vertex_ids - list of vertex ids to be adjusted
#   new_heights - list of heights; same length as vertex_ids
# Return:
#   Nothing
def adjust_vertex_height(obj, vertex_array, vertex_ids, new_heights):
    value_mod = 0
    h_idx = 0
    for v in vertex_ids:
    #     value_mod = new_height+1
    #     while(value_mod > new_height):
    #         value_mod = (round(((randint(0,10)-5)*0.25),3))
        try:
            select_vertex(obj, v)
            O.object.mode_set(mode="EDIT")
            O.transform.translate(value=(0, 0, new_heights[h_idx]))
            O.mesh.select_all(action = 'DESELECT')
            O.object.mode_set(mode="OBJECT")
            vertex_array[v] = new_heights[h_idx]
        except:
            print("index height adjustment error - ",vertex_ids)
        
        h_idx += 1

def variate_num(num, var):
    variation = ((((randint(0,20))/20) - 0.5) * var)
    # print(variation)
    return round(num + variation, 3)

def create_mountain(obj, vertex_array, z_min, z_max, size, vertex_ids, mt_levels, i):
    vertex_id = vertex_ids[i]
    mt_level = mt_levels[i]
    print(mt_level, "-", vertex_id)

    z_scl = randint(z_min, z_max)
    vertex_heights_base = list(range(0,mt_level+1))
    # vertex_heights = [round(((randint(0,10)-5)*0.1/(mt_level+1))+(1 - (n / (mt_level+1))),2) for n in vertex_heights]
    vertex_heights_base = [round((1 - (n / (mt_level+1))),2) for n in vertex_heights_base]
    # print(vertex_heights_base)
    # print("v heights:", vertex_heights)
    temp_height = round((mt_level+1)*0.1*z_scl,3)
    for h in range(mt_level+1):
        vertex_heights_base[h] = round(vertex_heights_base[h]*temp_height,3)
    # print(vertex_heights_base)
    
    extra_layers = (mt_level+2)//3
    existence_prob = [100]*(mt_level+extra_layers)

    for el in range(mt_level+extra_layers):
        if (el < mt_level):
            existence_prob[el] = (existence_prob[el]-(5*el))
        else:
            existence_prob[el] = (existence_prob[el]/(el-mt_level+2))

    vertex_to_update = [vertex_id]
    vertex_heights_to_update = [variate_num(vertex_heights_base[0], 0.4)]
    vertex_updated = []        
    v_adj = size-1
    print("Layer count: ", end="")
    for l in range(mt_level+1):
        vertices_in_layer_updated = 0
        # print("vtu", vertex_to_update)
        # print(vertex_heights_to_update)
        adjust_vertex_height(obj, vertex_array, vertex_to_update, vertex_heights_to_update)
        vertex_updated.extend(vertex_to_update)
        if (l == mt_level):
            break
        vertex_to_update[:] = []
        vertex_heights_to_update[:] = []
        for vi in range(len(vertex_updated)):
            v = vertex_updated[vi]
            if (v+v_adj not in vertex_updated) and (v+v_adj not in vertex_to_update) and (randint(1,100) <= existence_prob[l]):
                vertex_to_update.append(v+v_adj)
                vertex_heights_to_update.append(variate_num(vertex_heights_base[l+1], 0.4))
                vertices_in_layer_updated += 1
            if (v-v_adj not in vertex_updated) and (v-v_adj not in vertex_to_update) and (randint(1,100) <= existence_prob[l]):
                vertex_to_update.append(v-v_adj)
                vertex_heights_to_update.append(variate_num(vertex_heights_base[l+1], 0.4))
                vertices_in_layer_updated += 1
            if (v+1 not in vertex_updated) and (v+1 not in vertex_to_update) and (randint(1,100) <= existence_prob[l]):
                vertex_to_update.append(v+1)
                vertex_heights_to_update.append(variate_num(vertex_heights_base[l+1], 0.4))
                vertices_in_layer_updated += 1
            if (v-1 not in vertex_updated) and (v-1 not in vertex_to_update) and (randint(1,100) <= existence_prob[l]):
                vertex_to_update.append(v-1)
                vertex_heights_to_update.append(variate_num(vertex_heights_base[l+1], 0.4))
                vertices_in_layer_updated += 1
        print(vertices_in_layer_updated, end="-")
    
    # now, extra layers (existence of each vertex random):
    v_corners = [mt_level, -mt_level, ((size-1)*(mt_level)), -((size-1)*(mt_level))]
    v_corners = [(vertex_id + v) for v in v_corners]

    extra_vertex_heights_base = list(range(0,extra_layers))
    extra_vertex_heights_base = [round(((extra_layers/(extra_layers+1)) - (n / extra_layers)),2) for n in extra_vertex_heights_base]
    for h in range(extra_layers):
        extra_vertex_heights_base[h] = round(extra_vertex_heights_base[h]*vertex_heights_base[mt_level],3)
        existence_prob[h+mt_level] = (100/(h+2))
    # print(extra_vertex_heights_base)
    
    outer_ring = []
    print("\n\rExtra Layer count: ", end="")
    for e in range(extra_layers):
        vertices_in_extra_layer_updated = 0
        # print(e)
        outer_ring[:] = []

        for o in range(1,mt_level-e):
            # print(o)
            outer_ring.append(vertex_id + ((e+o)*v_adj) + (mt_level-o))
            outer_ring.append(vertex_id + ((e+o)*v_adj) - (mt_level-o))
            outer_ring.append(vertex_id - ((e+o)*v_adj) + (mt_level-o))
            outer_ring.append(vertex_id - ((e+o)*v_adj) - (mt_level-o))
        # print(outer_ring)

        for o in range(len(outer_ring)):
            # select_vertex(obj, outer_ring[o])
            v = outer_ring[o]
            # print(v)
            vertex_to_update[:] = []
            vertex_heights_to_update[:] = []
            if (v+v_adj not in vertex_updated) and (randint(1,100) <= existence_prob[e+mt_level]):
                vertex_to_update.append(v+v_adj)
                vertex_heights_to_update.append(variate_num(extra_vertex_heights_base[e], 0.2))
                vertices_in_extra_layer_updated += 1
            if (v-v_adj not in vertex_updated) and (randint(1,100) <= existence_prob[e+mt_level]):
                vertex_to_update.append(v-v_adj)
                vertex_heights_to_update.append(variate_num(extra_vertex_heights_base[e], 0.2))
                vertices_in_extra_layer_updated += 1
            if (v+1 not in vertex_updated) and (randint(1,100) <= existence_prob[e+mt_level]):
                vertex_to_update.append(v+1)
                vertex_heights_to_update.append(variate_num(extra_vertex_heights_base[e], 0.2))
                vertices_in_extra_layer_updated += 1
            if (v-1 not in vertex_updated) and (randint(1,100) <= existence_prob[e+mt_level]):
                vertex_to_update.append(v-1)
                vertex_heights_to_update.append(variate_num(extra_vertex_heights_base[e], 0.2))
                vertices_in_extra_layer_updated += 1
            vertex_updated.extend(vertex_to_update)

            adjust_vertex_height(obj, vertex_array, vertex_to_update, vertex_heights_to_update)
        print(vertices_in_extra_layer_updated, end="-")
        # print(vertex_updated)
    print("\n\r")

def create_mountains(object_name, vertex_array, mt_level_range, size, count, z_range):
    print("Creating mountains...")
    
    z_min = z_range[0]
    z_max = z_range[1]

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

#    print("Layers:")
#    print(layers)  
    
    for obj in C.scene.objects:
        if obj.name == object_name:
            obj.select_set(True)

    obj = C.active_object
    
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="VERT")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')

    available_ids = []
    # print("mt_level", mt_level)
    # for m in range(layer_count):
    #     if (m <= mt_level):
    #         continue
    #     available_ids.extend(layers[m])
    
    # if (count > len(available_ids)):
    #     print("Too many hills requested, would repeat...")
    #     return
    
#    print("Available ids:", available_ids)
    # First, can generate central locations for each mountain:
    # This can also be the place any specific groupings are determined,
    # i.e. valleys, 1 large mountain, smaller peaks;
    vertex_ids = []*count
    mt_levels = []*count

    for id in range(count):
        mt_levels.append(randint(mt_level_range[0], mt_level_range[1]))
        for m in range(layer_count):
            if (m <= mt_levels[id]):
                continue
            available_ids.extend(layers[m])

        if (count > len(available_ids)):
            print("Too many hills requested, would repeat...")
            return

        temp_id = available_ids[randint(0, len(available_ids)-1)]
        while (temp_id in vertex_ids):
            temp_id = available_ids[randint(0, len(available_ids)-1)]
        
        available_ids = [] # reset available ids
        vertex_ids.append(temp_id)

    for i in range(count):
        create_mountain(obj, vertex_array, z_min, z_max, size, vertex_ids, mt_levels, i)
        update_viewport()

    
#    print(available_ids)

def add_modifier(obj, mod_type):
    O.object.mode_set(mode="OBJECT") 
   
    obj.select_set(True)
    # O.object.modifier_add(type=mod_type)
    mod = obj.modifiers.new(mod_type, type=mod_type)
    # Apply modifier
    O.object.modifier_apply()
    return mod

def add_camera(camera_name, loc_vec):
    print("Adding camera", camera_name, "; loc =", loc_vec)
    scn = C.scene

    # create the first camera
    cam = bpy.data.cameras.new(camera_name)
    cam.lens = 18

    # create the first camera object
    cam_obj = bpy.data.objects.new(camera_name, cam)
    cam_obj.location = (loc_vec[0], loc_vec[1], loc_vec[2])
    scn.collection.objects.link(cam_obj)
    return cam_obj

def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

def select_all_meshes():
    for obj in C.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)

def remove_all_meshes():
    
    select_all_meshes()
    
    O.object.delete()

def select_flat_vertices(obj, base_size, flat_array):
    O.object.mode_set(mode = 'EDIT') 
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        face_v_count = 0
        for v in f.verts:
            if (v.co.z == 0) and (v.index >= base_size*4):
                face_v_count += 1
        if face_v_count == 4:
            for v in f.verts:
                if v.index not in flat_array:
                    # Select vertices, found a flat square face
                    flat_array.append(v.index)

def generate_building_locations(base_size, b_count, b_size_range, flat_array, b_locs):
    #don't want edges where squares could overlap;
    # create two arrays, for each edge to avoid.
    outer_edge_h = []
    outer_edge_v = []
    max_vert = (base_size+1)*(base_size+1)-1
    v_adj = base_size - 1
    for n in range(base_size-1):
        outer_edge_h.append(max_vert - n)
        outer_edge_v.append(max_vert - (n*(base_size-1)))

    b_loc_list = []
    rand_loc = 0
    b_height = 0
    b_vertices = []
    for bc in range(b_count):
        b_loc_list[:] = []
        while (True):
            b_height = randint(b_size_range[0], b_size_range[1])+1
            b_vertices[:] = []
            rand_loc = flat_array[randint(0,len(flat_array)-1)]
            for v_v in range(b_height):
                for v_h in range(b_height):
                    loc_to_add = rand_loc+(v_h)+(v_v*v_adj)
                    if (loc_to_add in flat_array) and ((v_h == b_height-1) or (loc_to_add not in outer_edge_h)) and ((v_v == b_height-1) or (loc_to_add not in outer_edge_v)):
                        b_vertices.append(loc_to_add)
            if (len(b_vertices) == ((b_height)*(b_height))):
                b_loc_list.extend(b_vertices)
                for v_r in b_vertices:
                    flat_array.remove(v_r)
                break

        b_locs[bc] = b_loc_list[:]
    print(b_locs)

def main():
    print("\n\n\n\n\nGenerating Terrain...")
 
    try:
        O.object.mode_set(mode='OBJECT', toggle=False)
    except:
        pass

    remove_all_meshes()
        
    # create base
    base_size = 30 # 2 is min size
    z_range = [8, 16]
    count = 5
    mountain_level_range = [5, 10]
    base_x_scl = base_size
    base_y_scl = base_size
    
    v_adj = base_size - 1

    # https://blender.stackexchange.com/questions/5210/pointing-the-camera-in-a-particular-direction-programmatically
    cam1_loc = [base_x_scl*1.5,0,mountain_level_range[1]*4]
    cam1_name = "Camera 1"

    try:
        D.objects[cam1_name].select_set(True)
        O.object.delete() 
        O.outliner.id_operation(type='UNLINK')
    except:
        pass

    cam1 = add_camera("Camera 1", cam1_loc)
        
#    create_cube("Base", 0, 0, -0.1, base_x_scl, base_y_scl, 0.1)
    base = create_plane("Base", 0, 0, 0, base_x_scl, base_y_scl)
    subdivide_plane("Base", base_size-1)
    
    vertex_array = [0] * (base_size + 1) * (base_size + 1)
    smooth_array = []

    create_mountains("Base", vertex_array, mountain_level_range, base_size, count, z_range)
    # print(vertex_array)

    s_group = C.object.vertex_groups.new( name = 'SMOOTH_GROUP' )
    
    # Select all but outer edge for v_group to be smoothed
    smooth_array = [vi for vi in range(len(vertex_array)) if vi >= base_size*4]

    # print(smooth_array)
    s_group.add(smooth_array, 1, 'ADD')

    O.object.mode_set(mode = 'EDIT') 

    print("Triangulating...")
    triangulate_edit_object("Base")
    update_viewport()
    print("Done.")

    print("Smoothing...")
    smooth_mod = add_modifier(base, 'SMOOTH')
    smooth_mod.vertex_group = s_group.name
    smooth_mod.iterations = 10

    update_viewport()
    print("Done.")

    look_at(cam1, base.matrix_world.to_translation())

    print("Creating Buildings...")
    # Now, select all vertices from faces who weren't triangulated
    flat_array = []
    select_flat_vertices(base, base_size, flat_array)
        
    O.object.mode_set(mode = 'OBJECT')
    

    # f_group = C.object.vertex_groups.new( name = 'FLAT_GROUP' )
    # O.object.mode_set(mode = 'OBJECT') 
    # f_group.add(flat_array, 1, 'ADD')

    # pick random location(s) for cubes (buildings)
    b_count = 3
    b_size_range = [1,3]
    b_locs = [[]] * b_count
    generate_building_locations(base_size, b_count, b_size_range, flat_array, b_locs)
    
    for bc in range(b_count):
        s_group.remove(b_locs[bc]) # uninclude buildings from smoothing
        select_vertices(base, b_locs[bc])
        O.mesh.duplicate()
        O.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 2)})
        deselect_all_vertices(base)

        # update_viewport()

    # for area in C.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         C.scene.camera = C.scene.objects[cam1_name]
    #         area.spaces[0].region_3d.view_perspective = 'CAMERA'

    #         break
        
    # for a in C.screen.areas:
    #     if a.type == 'VIEW_3D':
    #         overlay = a.spaces.active.overlay
    #         overlay.show_extra_indices = True
    # O.object.mode_set(mode = 'EDIT')  
    # O.mesh.select_mode(type="VERT")
    # O.mesh.select_all(action = 'SELECT')
    print("Done.")
    
if __name__ == "__main__":
    main()