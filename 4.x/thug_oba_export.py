#
# Copyright 2026 Hardronix
# SPDX-License-Identifier: Apache-2.0
#

import bpy
import struct
import copy
import math

import mathutils
from mathutils import Quaternion
from mathutils import Vector

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

# Skeletal animation flags
flag_legacy = (1 << 31)
flag_intermediate = (1 << 30)
flag_uncompressed = (1 << 29)
flag_platform = (1 << 28)
flag_camera_data = (1 << 27)
flag_compressed_time = (1 << 26)
flag_prerotated_root = (1 << 25)
flag_object_animation = (1 << 24)
flag_use_compress_tables = (1 << 23)
flag_hires_frame_pointers = (1 << 22)
flag_custom_keys_at_60_fps = (1 << 21)
flag_cutscene_data = (1 << 20)
flag_partial_animation = (1 << 19)
flag_old_partial_animation = (1 << 18)

def bytepad(data):
    misalignment = len(data) % 4

    if misalignment != 0:
        return b"\x00" * (4 - misalignment)
    
    return b""

def xprint(message):
    print(message)
    bpy.context.workspace.status_text_set(message)

def is_mesh(object):
    if object is None:
        return False
    
    if object.type == 'MESH':
        return True
    
    return False

def is_keyframed(object):
    if object is None:
        return False
    
    if object.animation_data is None:
        return False;
    
    if object.animation_data.action is None:
        return False;
    
    for curve in object.animation_data.action.fcurves:
        if curve.data_path == "location":
            return True
        
        if curve.data_path == "rotation_quaternion":
            return True
    
    return False

@dataclass
class QKey:
    time: int
    rotation: Quaternion
    
@dataclass
class TKey:
    time: int
    translation: Vector

# Object channel entry
@dataclass
class ObjectAnimationChannel:
    object: bpy.types.Object
    
    # Used for epsilon checking to avoid duplicating keyframes
    last_rotation: Quaternion
    # Also used for same stuff
    last_translation: Vector
    
    # Actual rotation and translation data
    rotation_keys: list[QKey] = field(default_factory=list)
    translation_keys: list[TKey] = field(default_factory=list)
    
def is_different(one, two):
    return not math.isclose(one, two, abs_tol=1e-5)

def hex_or_compute_name(name):
    value = 0

    if name.startswith("0x") or name.startswith("0X"):
        try:
            value = int(name, 16)
        except ValueError:
            return None
    else:
        value = generate_crc(name)
        
    return value         
        
# This one is needed because for Blender, the world is rotated upwards, but thps_scene_io rotates it back!
ninety_deg_basis_rotation = Quaternion((0.7071068, -0.7071068, 0.0, 0.0))

# Converts the quaternion axis from blender to game
def flip_quaternion_to_game_axis(x):
    # Now, we flip the X 90 degrees!... By X! WOOAAAA xDDD
    flipped_x = x @ ninety_deg_basis_rotation

    # Immediately after, we conjugate it... This is the part I lost three years of my life on
    flipped_x.conjugate()

    # And then, we flop the flipped X to match with DirectX!
    flopped_x = Quaternion((flipped_x.w, flipped_x.x, flipped_x.z, -flipped_x.y))
    flopped_x.normalize()

    return flopped_x
        
def export(collection_name, export_path):
    # First, find the collection that contains cutscene stuff
    cutscene_collection = bpy.data.collections.get(collection_name)
    
    # Early return if didn't find anything
    if cutscene_collection is None:
        xprint(f"Failed to export OBA for {export_path}: current collection does not exist!")
        return
    
    if not cutscene_collection.objects:
        xprint(f"Failed to export OBA for {export_path}: current collection is empty!")
        return
    
    animated_object_channels = []
    
    # Collect objects which have translation/rotation keyframes as probable candidates
    for obj in cutscene_collection.objects:
        
        # Skip if not a mesh
        if not is_mesh(obj):
            continue
        
        # Skip if translation/rotation aren't animated
        if not is_keyframed(obj):
            continue
        
        entry = ObjectAnimationChannel(
            object=obj,
            last_translation=None,
            last_rotation=None
        )
        
        animated_object_channels.append(entry)
        
    bpy.context.scene.frame_set(0)

    # Collect the keyframes
    for x in range(0, bpy.context.scene.frame_end):
        current_frame = bpy.context.scene.frame_current
        
        for channel in animated_object_channels:
            absolute_translation = channel.object.matrix_world.to_translation()
            absolute_rotation = channel.object.matrix_world.to_quaternion()
            absolute_math_translation = Vector((absolute_translation.x, absolute_translation.y, absolute_translation.z))
            absolute_math_rotation = Quaternion((absolute_rotation.w, absolute_rotation.x, absolute_rotation.y, absolute_rotation.z))
            
            # Initialize last translation and rotation for delta epsilon check (deduplication)
            if channel.last_translation is None:
                channel.last_translation = absolute_math_translation
            
            if channel.last_rotation is None:
                channel.last_rotation = absolute_math_rotation
            
            # Append translation keyframe if it changed
            if is_different(channel.last_translation.x, absolute_math_translation.x) or is_different(channel.last_translation.y, absolute_math_translation.y) or is_different(channel.last_translation.z, absolute_math_translation.z):
                channel.translation_keys.append(TKey(current_frame, absolute_math_translation))
                channel.last_translation = absolute_math_translation
                
            # Append rotation keyframe if it changed
            if is_different(channel.last_rotation.w, absolute_math_rotation.w) or is_different(channel.last_rotation.x, absolute_math_rotation.x) or is_different(channel.last_rotation.y, absolute_math_rotation.y) or is_different(channel.last_rotation.z, absolute_math_rotation.z):
                channel.rotation_keys.append(QKey(current_frame, absolute_math_rotation))
                channel.last_rotation = absolute_math_rotation
            
        bpy.context.scene.frame_set(current_frame + bpy.context.scene.frame_step)
        
        # Collect totals and print debug info
        total_channels = 0
        total_rotation_keys = 0
        total_translation_keys = 0
        
        for channel in animated_object_channels:
            total_channels += 1
            total_rotation_keys += len(channel.rotation_keys)
            total_translation_keys += len(channel.translation_keys)
            
            xprint(f"{total_channels} channels, {total_rotation_keys} rotation keys, {total_translation_keys} translation keys")
        
        # Now, finally write things down!
        # Set animation flags
        ska_flags = 0
        
        # The game always requires the time to be in frames and root being pre-rotated
        ska_flags |= flag_compressed_time
        ska_flags |= flag_prerotated_root
        
        # Platform means, once again, that no compression is used =)
        ska_flags |= flag_platform
        
        # Use 16-bit unsigned integers instead of 8-bit ones for per-bone q/t keyframes
        ska_flags |= flag_hires_frame_pointers
        
        # This is indeed a hecking object animation!
        ska_flags |= flag_object_animation
        
        # Calculate frame time
        ska_time = bpy.context.scene.frame_end / bpy.context.scene.render.fps_base
        
        # And write the ska header, which goes like...
        # uint32_t version
        # uint32_t flags
        # float duration in seconds
        # uint32_t bone count
        # uint32_t total rotation keys count
        # uint32_t total translation keys count
        # uint32_t total custom keys count
        
        oba_data = struct.pack("<IIfIIII", 1, ska_flags, ska_time, len(animated_object_channels), total_rotation_keys, total_translation_keys, 0)
        
        # Now, since it's an object animation, the next should be a list of uint32_t name checksums of all objects involved! We'll go smart about it - we'll use either hex if it starts with 0x or calculate a crc32 checksum for them
        for channel in animated_object_channels:
            object_checksum = hex_or_compute_name(channel.object.name)
            
            if object_checksum is None:
                xprint(f"Failed to export OBA for {path}: Failed to derive name for {channel.object.name}! Make sure your hex is correct!")
                return
            
            oba_data += struct.pack("<I", object_checksum)
            
        # Awesome, now we write a per-channel list of q + t keyframes, q and t are two uint16_t integers, first goes rotation, then translation
        for channel in animated_object_channels:
            oba_data += struct.pack("<HH", len(channel.rotation_keys), len(channel.translation_keys))
        
        # Then, align data to 4 bytes, since the game expects aligned access
        oba_data += bytepad(oba_data)
        
        # Now, here's the funniest part! We basically need to do some lowkey insane math but it's common, so like... Yeah. I just brought it into custom functions cuz why not...
        
        # Write the rotations first
        # Each uncompressed rotation is this:
        # uint32_t time
        # float x
        # float y
        # float z
        # Each one of these needs to be flipped
        for channel in animated_object_channels:
            for qkey in channel.rotation_keys:
                dx_rotation = flip_quaternion_to_game_axis(qkey.rotation)
                
                prev_flopped_dx_rotation = None
                
                # Now we fix double cover, because Blender honestly isn't perfect and can make the camera rotate two times... I mean, you will open graph editor and fix that, right?...
                if prev_flopped_dx_rotation is not None:
                    if dx_rotation.dot(prev_flopped_dx_rotation) < 0.0:
                        dx_rotation.negate()

                prev_flopped_dx_rotation = dx_rotation

                # The sign is hidden in the timestamp! So bring it if it's negative
                if dx_rotation.w < 0.0:
                    qkey.time |= 0x8000      
                
                oba_data += struct.pack("<Ifff", qkey.time, dx_rotation.x, dx_rotation.y, dx_rotation.z)
        
        # Then, write the translations
        # Each uncompressed translation is this:
        # uint32_t time
        # float x
        # float y
        # float z
        # Each one of these needs to be flipped too
        for channel in animated_object_channels:
            for tkey in channel.translation_keys:
                oba_data += struct.pack("<Ifff", tkey.time, tkey.translation.x, tkey.translation.z, -tkey.translation.y)
                
        # And finally, save it!
        try:
            with open(export_path, "wb") as out:
                out.write(oba_data)
                xprint(f"Exported object animation into {export_path}! {total_channels} channel{"s" if total_channels > 1 else ""} (object{"s" if total_channels > 1 else ""}), {total_rotation_keys} rotation key{"s" if total_rotation_keys > 1 else ""}, {total_translation_keys} translation key{"s" if total_translation_keys > 1 else ""}")
        except OSError:
            xprint(f"Failed to write the object animation to {export_path}!")
            
# Set your path here
export("cutscene_objects", "object_animation.oba")
