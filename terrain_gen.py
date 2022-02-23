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
     
def round_off_block(block_name, z_height):

    for obj in C.scene.objects:
        if obj.name == block_name:
            obj.select_set(True)

    obj = bpy.context.active_object
    
    O.object.mode_set(mode = 'EDIT') 
    O.mesh.select_mode(type="VERT")
    O.mesh.select_all(action = 'DESELECT')
    O.object.mode_set(mode = 'OBJECT')
    
    # select the top vertices
    obj.data.vertices[1].select = True
    obj.data.vertices[3].select = True
    obj.data.vertices[5].select = True
    obj.data.vertices[7].select = True
 
    O.object.mode_set(mode="EDIT")

    O.mesh.duplicate()
    
    O.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value":(0, 0, 0)}
    )
    
    O.transform.resize(value=(2, 2, 0))
    O.transform.translate(value=(0, 0, -(2*z_height)))
        
    O.object.mode_set(mode="OBJECT")

def bool_all_meshes(count, bool_op):
    
    O.object.mode_set(mode="OBJECT") 
    obj_done_list = [0] * (count+1)
    i = 0
    
    for obj in C.scene.objects:
        print("Using: ")
        print(obj.name)
        # Select the new object.
        obj.select_set(True)
        
        # Keep track of objects done, to avoid duplicating bools
        obj_done_list[i] = obj
        i += 1
        print("mod_objs:")
        for mod_obj in C.scene.objects:
            if mod_obj not in obj_done_list:
                print(mod_obj.name)
                # Add a modifier
                O.object.modifier_add(type='BOOLEAN')

                mod = obj.modifiers.new('Boolean', type='BOOLEAN')

                mod.operation = 'UNION'
                mod.object = mod_obj
                sleep(1)
#                # Apply modifier
                O.object.modifier_apply()
#                sleep(1)

            
def create_random_blocks(count, z_min, z_max, x_scale, y_scale):
    
    # set all to x*y + x + y, 0 indexed coordinates will max at x*y - 1
    default_coord = (2*x_scale*2*y_scale) + x_scale + y_scale
    coord_locs = [default_coord] * count  
        
    #create randomly placed cubes of random heights
    for i in range(count):
        block_name = "Block_" + str(i)
        
        x_scl = y_scl = 1
        z_scl = randint(z_min, z_max)
        z_loc = z_scl
        
        #for j in range(count):
        while(True):
            loc_exist_flag = False
            x_loc = randint(-x_scale + x_scl, x_scale - x_scl)
            y_loc = randint(-y_scale + y_scl, y_scale - y_scl)
            
            cur_loc = ((y_loc * y_scale) + (x_scale*y_scale) + x_loc + x_scale)
            
            #print("\n" + str(i) + ":")
            #print("Cur loc is:" + str(cur_loc))
            
            # check existing locations and surrounding areas for boxes;
            # [x,y], [x +- 1, y +- 1] -> loc, loc +- 1, loc +- 10
            for exist_loc in coord_locs:
                #print(exist_loc, exist_loc+1, exist_loc-1, exist_loc+10, exist_loc-10)
                if (exist_loc == default_coord):
                    break
                
                # check 3x3 grid, all spaces around center
                if ((exist_loc - 1 <= cur_loc <= exist_loc + 1) \
                or (exist_loc + y_scale - 1 <= cur_loc <= exist_loc + y_scale + 1) \
                or (exist_loc - y_scale - 1 <= cur_loc <= exist_loc - y_scale + 1)):
                    loc_exist_flag = True
                    break
            
            if (loc_exist_flag == False):
                # to avoid intersecting blocks, assign each location an integer coordinate.
                coord_locs[i] = cur_loc
                break      
        
        create_cube(block_name, x_loc, y_loc, z_loc, x_scl, y_scl, z_scl)
        
        # round off each cube as it's created
        round_off_block(block_name, z_scl)

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
    base_x_scl = 10
    base_y_scl = 10
    create_cube("Base", 0, 0, -0.1, base_x_scl, base_y_scl, 0.1)

    cube_z_min = 1
    cube_z_max = 3
    count = 5 # 30 is the highest safe value, i think. at least for 10x10.
    # should find a way to calculate it algorithmically
    
    create_random_blocks(count, cube_z_min, cube_z_max, base_x_scl, base_y_scl)
    
    bool_all_meshes(count, 'UNION')
    # combine into single object
    select_all_meshes()
    O.object.join()


if __name__ == "__main__":
    main()

