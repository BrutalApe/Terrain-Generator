#terrain_gen_2
#instead of using cubes, subdivide a plane 
#raise/lower vertices to achieve same desired terrain effect
# fname = "C:/.../terrain_gen_2.py"
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
# https://blender.stackexchange.com/questions/40823/alternative-to-redraw-timer
# Params:
#   Nothing
# Return:
#   Nothing
def update_viewport():
    # Technically this is not a good thing to do, but for testing it's fine. Remove in the future.
    # O.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    return

# Selects object of given name
# Params:
#   obj_name - name of object to be selected
# Return:
#   Nothing
def select_object(obj_name):
    for obj in C.scene.objects:
        if obj.name == obj_name:
            obj.select_set(True)
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
    
    # set Cube's name to name
    for obj in C.selected_objects:
        if (obj.type == "MESH") and (obj.name == "Cube"):
            obj.name = name

# Creates a plane using given parameters
# Params:
#   name - name of plane
#   x,y,z_loc - location of plane
#   x,y_scl - scale of plane
# Return:
#   Created plane object 
def create_plane(name, x_loc, y_loc, z_loc, x_scl, y_scl):
    print("Creating plane...")
    O.mesh.primitive_plane_add(location=(x_loc,y_loc,z_loc))
    O.transform.resize(value=(x_scl, y_scl, 0))
    
    # Set plane's name to name
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
    select_object(obj_name)
    obj = C.active_object

    O.object.mode_set(mode = 'EDIT') 
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)
    
    total_faces = 0
    for f in bm.faces:
        for v in f.verts:
            if (v.co.z != 0):
                # If any vertex of face is higher than 0 on z-axis, triangulate it.
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
    select_object(object_name)
    obj = C.active_object

    # Deselect all faces
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="FACE")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')
    
    # select the chosen face
    obj.data.polygons[face].select = True

    # Subdivide
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
    select_object(object_name)
    obj = C.active_object

    O.object.mode_set(mode="EDIT")
    O.mesh.subdivide(number_cuts=num_of_cuts)
    O.object.mode_set(mode="OBJECT")

# Deselects all vertices of mesh
# https://blender.stackexchange.com/questions/154787/is-it-possible-to-deselect-vertices-in-python
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

# Adds small random variation to number
# Params:
#   num - number to be modified
#   var - variation amount
# Return:
#   resulting number rounded 3
def variate_num(num, var):
    variation = ((((randint(0,20))/20) - 0.5) * var)
    return round(num + variation, 3)

# Creates single mountain on plane
# Params:
#   obj - object to create mountain on (plane)
#   vertex_array - list of all vertices of plane, modifed to show z-location
#   z_min - minimum height of mountain peak
#   z_max - maximum height of mountain peak
#   size - size of plane
#   vertex_ids - list of peak vertex locations
#   mt_levels - list of mountain 'levels', measure of how wide they are
#   i - index of which values in vertex_ids and mt_levels to use for current mountain
# Return:
#   Nothing
def create_mountain(obj, vertex_array, z_min, z_max, size, vertex_ids, mt_levels, i):
    # Get peak vertex and mt level for current mountain
    vertex_id = vertex_ids[i]
    mt_level = mt_levels[i]
    print(mt_level, "-", vertex_id)

    # Set height for mountain, set base heights for each layer below peak
    z_scl = randint(z_min, z_max)
    vertex_heights_base = list(range(0,mt_level+1))
    vertex_heights_base = [round((1 - (n / (mt_level+1))),2) for n in vertex_heights_base]
    temp_height = round((mt_level+1)*0.1*z_scl,3)
    for h in range(mt_level+1):
        vertex_heights_base[h] = round(vertex_heights_base[h]*temp_height,3)
    
    # existence of each vertex random
    extra_layers = (mt_level+2)//3
    existence_prob = [100]*(mt_level+extra_layers)
    # Extra layers even less likely than normal mountain.
    # All this randomness adds more variability between each mountain, more natural look.
    for el in range(mt_level+extra_layers):
        if (el < mt_level):
            # Regular layers have 100%, 95%, 90%...peak always exists, other layers diminishing likelihood
            # This could be a problem if mt_level is higher than 20; fix later.
            existence_prob[el] = (existence_prob[el]-(5*el)) 
        else:
            # Extra layers have 1/2, 1/3, 1/4...chance of existing. Makes base of mountain look like rolling hills, somewhat.
            existence_prob[el] = (existence_prob[el]/(el-mt_level+2))

    # Now, create the mountain.
    vertex_to_update = [vertex_id]
    vertex_heights_to_update = [variate_num(vertex_heights_base[0], 0.4)] # Variate peak by a small amount
    vertex_updated = []        
    v_adj = size-1
    print("Layer count: ", end="")

    # For each layer in mountain level, raise the current vertices to update by their height values,
    # then reset the vertex lists and add all adjacent vertices to previous layer (away from center)
    for l in range(mt_level+1):
        # Modify current vertex_to_update list with heights
        vertices_in_layer_updated = 0
        adjust_vertex_height(obj, vertex_array, vertex_to_update, vertex_heights_to_update)

        # Record vertices updated
        vertex_updated.extend(vertex_to_update)

        # If lowest level, done
        if (l == mt_level):
            break

        # Clear lists
        vertex_to_update[:] = []
        vertex_heights_to_update[:] = []

        # For each vertex that has already been updated, check adjacent vertices;
        # If that adjacent vertex hasn't been updated, isn't already in the list, and based on existence probability value,
        # Add it to the list of vertices to update
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
    
    # Now, extra layers.
    # Set base heights for each extra layer
    extra_vertex_heights_base = list(range(0,extra_layers))
    extra_vertex_heights_base = [round(((extra_layers/(extra_layers+1)) - (n / extra_layers)),2) for n in extra_vertex_heights_base]
    for h in range(extra_layers):
        extra_vertex_heights_base[h] = round(extra_vertex_heights_base[h]*vertex_heights_base[mt_level],3)
        existence_prob[h+mt_level] = (100/(h+2))
    
    outer_ring = []
    print("\n\rExtra Layer count: ", end="")

    # For each layer in extra layers, get outer_ring; then update vertices based on that ring.
    # Basically, the outer ring code keeps mountain from looking too diamond-shaped at the bottom;
    # if each vertex always showed, the mountains would have an octagonal base.
    for e in range(extra_layers):
        vertices_in_extra_layer_updated = 0
        outer_ring[:] = []

        for o in range(1,mt_level-e):
            outer_ring.append(vertex_id + ((e+o)*v_adj) + (mt_level-o))
            outer_ring.append(vertex_id + ((e+o)*v_adj) - (mt_level-o))
            outer_ring.append(vertex_id - ((e+o)*v_adj) + (mt_level-o))
            outer_ring.append(vertex_id - ((e+o)*v_adj) - (mt_level-o))

        for o in range(len(outer_ring)):
            v = outer_ring[o]
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
    print("\n\r")

# Create mountains on mesh (plane)
# Params:
#   object_name - name of plane to use
#   vertex_array - list of all vertices of plane, modifed to show z-location
#   mt_level_range - lower and upper bounds of mountain levels
#   size - size of plane
#   count - how many mountains to create
#   z_range - upper and lower bounds of mountain peak heights
# Return:
#   Nothing
def create_mountains(object_name, vertex_array, mt_level_range, size, count, z_range):
    print("Creating mountains...")
    
    z_min = z_range[0]
    z_max = z_range[1]

    # outer rim of ids, always determined this way, regardless of odd or even
    outermost_layer = list(range(0, size*4))
    
    # now will make list of lists of indices, 
    # where [0] is outermost, [n] is center index/group
    layer_count = size//2 + 1
    
    layers = [[] for _ in range(layer_count)]
    layers[0] = outermost_layer  

    # Get vertex indices for each layer, from the bottom up
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
    
    select_object(object_name)
    obj = C.active_object
    deselect_all_vertices(obj)

    available_ids = []
    # First, can generate central locations for each mountain:
    # This can also be the place any specific groupings are determined,
    # i.e. valleys, 1 large mountain, smaller peaks;
    vertex_ids = []*count
    mt_levels = []*count

    for id in range(count):
        # Pick a random mt_level in range
        mt_levels.append(randint(mt_level_range[0], mt_level_range[1]))

        # Fill available_ids only with layers that will prevent a mountain of level_width from reaching edge
        for m in range(layer_count):
            if (m <= mt_levels[id]):
                continue
            available_ids.extend(layers[m])

        # If more mountains requested than can be fit in space, stop creating mountains.
        if (count > len(available_ids)):
            print("Too many mountains requested, not enough space...")
            return

        # From available ids, pick a mountain peak vertex.
        temp_id = available_ids[randint(0, len(available_ids)-1)]
        while (temp_id in vertex_ids):
            temp_id = available_ids[randint(0, len(available_ids)-1)]
        
        available_ids[:] = [] # reset available ids
        vertex_ids.append(temp_id) # Add to list of vertex ids to use

    # Create each mountain using vertices collected
    for i in range(count):
        create_mountain(obj, vertex_array, z_min, z_max, size, vertex_ids, mt_levels, i)
        update_viewport()

# Adds a modifier to a mesh object
# Params:
#   obj - name of object to modify
#   mod_type - mod to add to object
# Return:
#   modifier created
def add_modifier(obj, mod_type):
    O.object.mode_set(mode="OBJECT") 
    obj.select_set(True)
    mod = obj.modifiers.new(mod_type, type=mod_type)
    # Apply modifier
    O.object.modifier_apply()
    return mod

# Creates a camera in the scene
# Params:
#   camera_name - name of camera to be created
#   loc_vec - location of camera
# Return:
#   camera object created
def add_camera(camera_name, loc_vec):
    print("Adding camera", camera_name, "; loc =", loc_vec)
    scn = C.scene

    # create the camera
    cam = bpy.data.cameras.new(camera_name)
    cam.lens = 18

    # create the camera object
    cam_obj = bpy.data.objects.new(camera_name, cam)
    cam_obj.location = (loc_vec[0], loc_vec[1], loc_vec[2])
    scn.collection.objects.link(cam_obj)
    return cam_obj

# Points camera at specific location
# https://blender.stackexchange.com/questions/5210/pointing-the-camera-in-a-particular-direction-programmatically
# Params:
#   obj_camera - camera object to rotate
#   point - x,y,z coordinates to look at
# Return:
#   Nothing
def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

# Selects all meshes in scene
# Params:
#   Nothing
# Return:
#   Nothing
def select_all_meshes():
    for obj in C.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)

# Removes all meshes in scene
# Params:
#   Nothing
# Return:
#   Nothing
def remove_all_meshes():
    select_all_meshes()
    O.object.delete()

# Gets all vertices of object connected to a face at z = 0
# Params:
#   obj - object to modify (plane)
#   base_size - size of plane
#   flat_array - array to be filled with flat face vertices
# Return:
#   Nothing
def get_flat_vertices(obj, base_size, flat_array):
    O.object.mode_set(mode = 'EDIT') 
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        face_v_count = 0
        # Check all vertices in current face:
        for v in f.verts:
            if (v.co.z == 0) and (v.index >= base_size*4):
                # If height of zero and not on very edge, increment this value
                face_v_count += 1
        # If incremented 4 times, face is acceptable; add all face's vertices to flat_array
        if face_v_count == 4:
            for v in f.verts:
                if v.index not in flat_array:
                    # add vertices, found a flat square face
                    flat_array.append(v.index)

# Generates location indices for buildings (cubes) on plane
# Params:
#   base_size - size of plane
#   b_count - how many buildings desired
#   b_size_range - lower and upper bounds of size of buildings (width)
#   flat_array - array of usable vertices
#   b_locs - list of lists, filled with vertices of each building
# Return:
#   Nothing
def generate_building_locations(base_size, b_count, b_size_range, flat_array, b_locs):
    # Create outer edge arrays; if a building would generate here, it could wrap 
    # around to the other side of the plane due to the way vertices are indexed.
    # Easier to just avoid these locations altogether for any building vertex.
    outer_edge_h = []
    outer_edge_v = []
    max_vert = (base_size+1)*(base_size+1)-1
    v_adj = base_size - 1
    for n in range(base_size-1):
        outer_edge_h.append(max_vert - n)
        outer_edge_v.append(max_vert - (n*(base_size-1)))

    # Values used for each building
    b_loc_list = []
    rand_loc = 0
    b_size = 0
    b_vertices = []
    
    # For each buidling, pick a size (in range) and vertex location 
    # (using bottom right, so all other vertices in building will be greater than that value).
    # Then check each vertex of building and ensure it is in flat array and not on outer edge (unless it's the last edge of building)
    for bc in range(b_count):
        b_loc_list[:] = []
        while (True):
            # Get building size and location
            b_size = randint(b_size_range[0], b_size_range[1])+1
            b_vertices[:] = []
            rand_loc = flat_array[randint(0,len(flat_array)-1)]

            # For each vertex in building, make sure they meet criteria mentioned above.
            # There will be (b_size+1)^2 vertices; i.e. a building of size 2 will be 9 vertices.
            for v_v in range(b_size):
                for v_h in range(b_size):
                    loc_to_add = rand_loc+(v_h)+(v_v*v_adj)
                    if (loc_to_add in flat_array) and ((v_h == b_size-1) or (loc_to_add not in outer_edge_h)) and ((v_v == b_size-1) or (loc_to_add not in outer_edge_v)):
                        b_vertices.append(loc_to_add)

            # If the correct amount of vertices are in b_vertices, add them to b_loc_list and remove from flat array (don't want to use them again).
            if (len(b_vertices) == ((b_size)*(b_size))):
                b_loc_list.extend(b_vertices)
                for v_r in b_vertices:
                    flat_array.remove(v_r)
                break
        
        # Add current building vertices to list of lists
        b_locs[bc] = b_loc_list[:]
    print(b_locs)

def main():
    print("\n\n\n\n\nGenerating Terrain...")
    
    # Set board to object mode if it already isn't
    try:
        O.object.mode_set(mode='OBJECT', toggle=False)
    except:
        pass

    # Clear scene
    remove_all_meshes()
        
    # create base
    base_size = 30                  # 2 is min size
    z_range = [8, 16]               # Range of heights of peaks
    count = 5                       # Number of mountains to create
    mountain_level_range = [5, 10]  # Range of mountain levels
    
    # For now, using square base, but other shaped planes should be possible
    base_x_scl = base_size
    base_y_scl = base_size
    
    # Value used in vertex selection; in a plane, adjacent vertices (not on outside edge) are +1,-1,+v_adj,-v_adj away
    v_adj = base_size - 1

    # Details of camera to be used; placed at edge of plane, 4 times higher than biggest mountain level
    cam1_loc = [base_x_scl*1.5,0,mountain_level_range[1]*4]
    cam1_name = "Camera 1"

    # Delete and unlink camera 1 if it exists
    try:
        D.objects[cam1_name].select_set(True)
        O.object.delete() 
        O.outliner.id_operation(type='UNLINK')
    except:
        pass

    # Add camera 1 to scene
    cam1 = add_camera("Camera 1", cam1_loc)
        
    # Create plane and subdivide to create base for terrain
    base = create_plane("Base", 0, 0, 0, base_x_scl, base_y_scl)
    subdivide_plane("Base", base_size-1)
    
    # Vertex array used to hold all vertex heights
    vertex_array = [0] * (base_size + 1) * (base_size + 1)
    
    # Smooth array holds vertices to be smoothed
    smooth_array = []

    # Create mountains first
    create_mountains("Base", vertex_array, mountain_level_range, base_size, count, z_range)
    
    # Create vertex group 
    s_group = C.object.vertex_groups.new( name = 'SMOOTH_GROUP' )
    smooth_array = [vi for vi in range(len(vertex_array)) if vi >= base_size*4] # Select all but outer edge for v_group to be smoothed
    s_group.add(smooth_array, 1, 'ADD') # Add smooth_array to s_group 

    # Triangulate all mountain-vertices (looks better, for example if 1 vertex is raised above others, a square face would render weird.)
    O.object.mode_set(mode = 'EDIT') 
    print("Triangulating...")
    triangulate_edit_object("Base")
    update_viewport()
    print("Done.")

    # Add smooth modifier using smooth_array
    print("Smoothing...")
    smooth_mod = add_modifier(base, 'SMOOTH')
    smooth_mod.vertex_group = s_group.name
    smooth_mod.iterations = 10
    update_viewport()
    print("Done.")

    # Point camera at center of base plane
    look_at(cam1, base.matrix_world.to_translation())

    # Create buildings
    print("Creating Buildings...")
    flat_array = []
    get_flat_vertices(base, base_size, flat_array)
    O.object.mode_set(mode = 'OBJECT')

    b_count = 3                 # How many buldings to create
    b_size_range = [1,3]        # Range of building sizes (widths)
    b_locs = [[]] * b_count
    generate_building_locations(base_size, b_count, b_size_range, flat_array, b_locs)

    # Use vertices found for building locations, duplicate and extrude them
    # Must be duplicated, otherwise larger buildings (any size that simply raises a vertex instead of creating a new one) 
    # will change vertex id pattern used throughout.    
    for bc in range(b_count):
        s_group.remove(b_locs[bc]) # uninclude buildings from smoothing
        select_vertices(base, b_locs[bc])
        O.mesh.duplicate()
        O.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 2)})
        deselect_all_vertices(base)

        # update_viewport()

    # Set perspective to camera view
    # for area in C.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         C.scene.camera = C.scene.objects[cam1_name]
    #         area.spaces[0].region_3d.view_perspective = 'CAMERA'
    #         break

    #         
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