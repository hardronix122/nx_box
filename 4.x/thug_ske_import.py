#
# Copyright 2026 Hardronix
# SPDX-License-Identifier: Apache-2.0
#

import bpy
import math
import struct

import mathutils
from mathutils import Quaternion
from mathutils import Vector
from mathutils import Matrix

from dataclasses import dataclass, field

# 0xedb88320 LE CRC32 stuff
crc_polynomial_table = [
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba,
    0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
    0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
    0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
    0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de,
    0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec,
    0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
    0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
    0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
    0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940,
    0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116,
    0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
    0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
    0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
    0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a,
    0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818,
    0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
    0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
    0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
    0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c,
    0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2,
    0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
    0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
    0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
    0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086,
    0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4,
    0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
    0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
    0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
    0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8,
    0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe,
    0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
    0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
    0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
    0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252,
    0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60,
    0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
    0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
    0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
    0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04,
    0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a,
    0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
    0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
    0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
    0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e,
    0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c,
    0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
    0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
    0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
    0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0,
    0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6,
    0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
    0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
    0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d
]

def generate_crc(text):
    text = text.lower()
    
    crc_register = 0xFFFFFFFF

    for i in range(0, len(text)):
        crc_register = crc_polynomial_table[(crc_register ^ ord(text[i])) & 0xFF] ^ ((crc_register >> 8) & 0x00FFFFFF)

    return crc_register
    
def debug_text_clear():
    log_text_block = bpy.data.texts.get("ske_import_logs")
    
    if not log_text_block:
        return
    
    log_text_block.clear()
    
def debug_text_log(message):
    log_text_block = bpy.data.texts.get("ske_import_logs")
    
    if not log_text_block:
        log_text_block = bpy.data.texts.new("ske_import_logs")
        
    log_text_block.write(f"{message}\n")
    
def xprint(message):
    debug_text_log(message)
    print(message)
    bpy.context.workspace.status_text_set(message)
    
def debug_text_clear():
    log_text_block = bpy.data.texts.get("ske_import_logs")
    
    if not log_text_block:
        return
    
    log_text_block.clear()
    
def load_bone_name_table(path):
    fast_bone_dict = {}
    
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                name = line.strip()

                # Skip comments and empty stuff
                if not name or name.startswith("#"):
                    continue
                
                # Generate checksums for the names and populate the dictionaryt
                fast_bone_dict[generate_crc(name)] = name
 
    except OSError:
        xprint(f"Failed to open bone name table at {path}!")        
        return None
    
    return fast_bone_dict
    
@dataclass
class BonePair:
    rotation: Quaternion
    translation: Vector
    bone_name: str
    bone_name_checksum: int
    parent_bone_name: str
    parent_bone_name_checksum: int
    bone_flip_name: str
    bone_flip_name_checksum: int
    
    
def import_ske(skeleton_data_name, skeleton_object_name, path, name_map):
    if skeleton_data_name == None:
        skeleton_data_name = f"{skeleton_object_name}_data"
    
    debug_text_clear()
    
    # Let's pull bone names from the fast dictionary
    def get_bone_name(checksum):
        # Return if dictionary isn't initialized
        if not name_map:
            return f"{hex(checksum)}"
        
        checksum_name = name_map.get(checksum)
        
        # Return the name or if nothing was found, return the checksum
        return checksum_name or f"{hex(checksum)}"
    
    def parse(src):
        # The header consists of a version, flags and bone account
        version = struct.unpack("<I", src.read(4))[0]
        flags = struct.unpack("<I", src.read(4))[0]
        bone_count = struct.unpack("<I", src.read(4))[0]
        
        xprint(f"Version: {version}")
        xprint(f"Flags: {flags}")
        xprint(f"Bone count: {bone_count}")
        
        # Then, grab the bone name indices
        bone_name_checksums = []
        
        for bone_idx in range(0, bone_count):
            bone_name_checksums.append(struct.unpack("<I", src.read(4))[0])
            xprint(f"Bone name #{bone_idx:02}: {get_bone_name(bone_name_checksums[bone_idx])}")
            
        # Next, parent names table!
        # Basically parents go like [object] -> [parent]
        # For example, [badoongas] -> [torso]
        parent_bone_name_checksums = []
        
        for parent_bone_idx in range(0, bone_count):
            parent_bone_name_checksums.append(struct.unpack("<I", src.read(4))[0])
            xprint(f"Parent bone name #{parent_bone_idx:02}: {get_bone_name(parent_bone_name_checksums[parent_bone_idx])}")
         
        # And then, bone flip table. Not exactly sure what it's used for tho! But it usually contains symmetrical parts of skeleton
        bone_flip_table = []
        
        for bone_flip_idx in range(0, bone_count):
            bone_flip_table.append(struct.unpack("<I", src.read(4))[0])
            xprint(f"Bone flip #{bone_flip_idx:02}: {get_bone_name(bone_flip_table[bone_flip_idx])}")
        
        # Then, read bone entries
        bone_entry_table = []
        
        for bone_entry_idx in range(0, bone_count):
            # Rotation
            rX = struct.unpack("<f", src.read(4))[0] # X  
            rY = struct.unpack("<f", src.read(4))[0] # Y
            rZ = struct.unpack("<f", src.read(4))[0] # Z
            rW = struct.unpack("<f", src.read(4))[0] # W
            
            # Translation
            tX = struct.unpack("<f", src.read(4))[0] # X
            tY = struct.unpack("<f", src.read(4))[0] # Y
            tZ = struct.unpack("<f", src.read(4))[0] # Z
            tW = struct.unpack("<f", src.read(4))[0] # W
            # (Might be that the game forces the translation W to be 1.0?)
            
            rotation = Quaternion((rW, rX, rY, rZ))
            translation = Vector((tX, tY, tZ))
            bone_checksum = bone_name_checksums[bone_entry_idx]
            bone_name = get_bone_name(bone_checksum)
            parent_bone_checksum = parent_bone_name_checksums[bone_entry_idx]
            parent_bone_name = None
            bone_flip_name_checksum = bone_flip_table[bone_entry_idx]
            bone_flip_name = get_bone_name(bone_flip_name_checksum)
            
            # Save the parent name to avoid re-calculation
            if parent_bone_checksum != 0:
                parent_bone_name = get_bone_name(parent_bone_checksum)
            
            # Build a bone pair
            bone_pair = BonePair(
                rotation,
                translation,
                bone_name,
                bone_checksum,
                parent_bone_name,
                parent_bone_checksum,
                bone_flip_name,
                bone_flip_name_checksum
            )
            
            bone_entry_table.append(bone_pair)
            
            xprint(f"Entry #{bone_entry_idx:02} Q (xyzw): {rX: 011.6f}, {rY: 011.6f}, {rZ: 011.6f}, {rW: 011.6f} | T (xyzw): {tX: 011.6f}, {tY: 011.6f}, {tZ: 011.6f}, {tW: 011.6f} | {bone_name:<30} -> {parent_bone_name}")
            
        # Delete the old skeleton if it existed
        if skeleton_object_name in bpy.data.objects:
            old_skeleton_object = bpy.data.objects[skeleton_object_name]
            bpy.data.objects.remove(old_skeleton_object, do_unlink=True)
            
            if skeleton_data_name in bpy.data.armatures:
                bpy.data.armatures.remove(bpy.data.armatures[skeleton_data_name])
                
        # Perfect, now create a new skeleton!
        skeleton_object_data = bpy.data.armatures.new(name=skeleton_data_name)
        skeleton_object = bpy.data.objects.new(name=skeleton_object_name, object_data=skeleton_object_data)
        
        bpy.context.collection.objects.link(skeleton_object)
        bpy.context.view_layer.objects.active = skeleton_object
        
        # Then, select the skeleton object and switch to edit mode... This is so stupid!!!
        bpy.context.view_layer.objects.active = skeleton_object
        bpy.ops.object.mode_set(mode="EDIT")
        
        # And now just add bones
        local_bone_transformation_matrices = {}
        
        for bone_entry_idx in range(0, bone_count):
            bone_entry = bone_entry_table[bone_entry_idx]
            
            if bone_entry.bone_name is None:
                xprint(f"Failed to load skeleton at {path}! Bone #{bone_entry_idx} string name is None")
                return
            
            bone_tx = bone_entry.translation
            
            # Translate the bones from 3ds max to blender's coordinate system
            bone_tx = Vector((bone_tx.x, bone_tx.z, -bone_tx.y))
            
            # Invert the local rotation(?!?!)
            bone_head_rx = Quaternion((bone_entry.rotation.w, bone_entry.rotation.x, bone_entry.rotation.z, -bone_entry.rotation.y))
            bone_head_rx.invert()
            
            # Now, it's tensor time!!!
            # I lowkey hate this, but again, I'm also a graphics programmer, so... I mean...
            translation_matrix = Matrix.Translation(bone_tx)
            rotation_matrix = bone_head_rx.to_matrix().to_4x4()
            
            # Multiply these two to get the the rest pose (also known as bind pose) local transformation matrix
            local_transformation_matrix = translation_matrix @ rotation_matrix
            
            # Forward kinematics anyone?
            # Multiply parent local transformation matrix by current bone's transformation matrix if got a parent
            inherited_local_transformation_matrix = local_transformation_matrix
            
            if bone_entry.parent_bone_name_checksum is not 0:
                if bone_entry.parent_bone_name_checksum in local_bone_transformation_matrices:
                    parent_local_transformation_matrix = local_bone_transformation_matrices[bone_entry.parent_bone_name_checksum]
                    inherited_local_transformation_matrix = parent_local_transformation_matrix @ local_transformation_matrix
            
            # And preserve the calculated inherited local transformation matrix for other bones one might be a parent of
            local_bone_transformation_matrices[bone_entry.bone_name_checksum] = inherited_local_transformation_matrix
            
            # Also rotate the transformation matrix 180 degrees by X to compensate for 3ds max 5 + directx 8 stuff
            matrix_180_x_transformation = Matrix.Rotation(math.radians(180.0), 4, "X")
            final_local_bone_transformation_matrix = matrix_180_x_transformation @ inherited_local_transformation_matrix
            
            # Now, create a new bone
            bone_data = skeleton_object.data.edit_bones.new(name=bone_entry.bone_name)
            
            # Then, set its head and tail. Head is the part that sets the axis rotation point as well as the target position
            bone_data.head = final_local_bone_transformation_matrix.to_translation()
            
            # And the tail is just there. Not sure why it's exactly like that but... I just hardcoded it
            bone_tail_offset = final_local_bone_transformation_matrix.to_3x3() @ Vector((0.0, -4.0, 0.0))
            bone_data.tail = final_local_bone_transformation_matrix.to_translation() + bone_tail_offset
            
            # And just for the future, set the flip if available
            if bone_entry.bone_flip_name_checksum != 0:
                bone_data["nx_box_bone_flip"] = bone_entry.bone_flip_name
            
        # Awesome! Now link the parents
        for bone_entry in bone_entry_table:
            
            if bone_entry.parent_bone_name is None:
                continue
            
            # First get the parent bone data, because if it's null, we can cut down queries to one instead of two
            parent_bone_data = skeleton_object_data.edit_bones.get(bone_entry.parent_bone_name)
            
            if parent_bone_data is None:
                continue
            
            bone_data = skeleton_object_data.edit_bones.get(bone_entry.bone_name)
            
            if bone_data is None:
                continue
            
            bone_data.parent = parent_bone_data
            bone_data.use_connect = False
            
        # And finally, switch back to the object mode
        bpy.ops.object.mode_set(mode="OBJECT")
            
    try:
        with open(path, "rb") as src:
            parse(src)
    except OSError:
        xprint(f"Failed to open skeletal animation at {path}!")

# Set your path here, and optionally, the bone names table        
#bone_names = load_bone_name_table("/home/hardronix/.nxbox/bone_names.txt")
bone_names = None
import_ske(None, "THPS5_human", "skeleton.ske.xbx", bone_names) 
