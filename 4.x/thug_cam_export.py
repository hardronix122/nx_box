import bpy
import struct
import copy
import math

import mathutils
from mathutils import Quaternion

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

# This one is needed because for Blender, the world is rotated upwards, but thps_scene_io rotates it back!
ninety_deg_basis_rotation = Quaternion((0.7071068, -0.7071068, 0.0, 0.0))

def export(path):
    ska_rotations = []
    ska_translations = []

    bpy.ops.screen.animation_cancel(restore_frame=False)

    
    main_cam = bpy.data.objects["main_camera"]

    if not main_cam:
        print("Failed to find the main camera! Make sure to label it \"main_camera\"!")
        return

    bpy.context.scene.frame_set(0)

    # Collect the keyframes
    for x in range(0, bpy.context.scene.frame_end):
        print(f"Frame: {bpy.context.scene.frame_current}")

        ska_rotations.append(copy.copy(main_cam.rotation_quaternion))
        ska_translations.append(copy.copy(main_cam.location))

        bpy.context.scene.frame_set(bpy.context.scene.frame_current + bpy.context.scene.frame_step)

    ska_version = 1

    ska_flags = 0

    # Platform means that the animation doesn't use any compression
    ska_flags |= flag_platform

    # High resolution frame pointers use 16-bit unsigned integers instead of 8-bit unsigned ones
    ska_flags |= flag_hires_frame_pointers

    # Camera data means is that no pre-rotation is genuinely needed for the root, and other stuff.
    ska_flags |= flag_camera_data

    # Uncompressed means we use the uncompressed body format and we don't use any kind of lookup tables (standardkeyQ.bin/standardkeyT.bin)
    ska_flags |= flag_uncompressed

    # The time is specified in seconds, not frames... Although, what's funny is that the game expects them in frames yet consumes seconds(? xDDD)
    ska_time = bpy.context.scene.frame_end / 60

    # Since it's just a camera, it'll be a single bone
    bones_count = 1

    rotation_keys_count = len(ska_rotations)
    translation_keys_count = len(ska_translations)
    custom_keys_count = 0

    # Write the header
    ska_data = struct.pack("<IIfIIIIHH", ska_version, ska_flags, ska_time, bones_count, rotation_keys_count, translation_keys_count, custom_keys_count, rotation_keys_count, translation_keys_count)

    # Write rotations first
    prev_flopped_x = None

    for idx, x in enumerate(ska_rotations):
        time = idx
        
        # Honestly, not sure what that means, past me though it was necessary, found that during RE of Tony Hawk's Underground 2 ^^''
        time |= time & 0x7FF

        # Now, we flip the X 90 degrees!... By X! WOOAAAA xDDD
        flipped_x = x @ ninety_deg_basis_rotation

        # Immediately after, we conjugate it... This is the part I lost three years of my life on
        flipped_x.conjugate()

        # And then, we flop the flipped X to match with DirectX!
        flopped_x = Quaternion((flipped_x.w, flipped_x.x, flipped_x.z, -flipped_x.y))
        flopped_x.normalize()

        # Now we fix double cover, because Blender honestly isn't perfect and can make the camera rotate two times... I mean, you will open graph editor and fix that, right?...
        if prev_flopped_x is not None:
            if flopped_x.dot(prev_flopped_x) < 0.0:
                flopped_x.negate()

        prev_flopped_x = flopped_x

        # The sign is hidden in the timestamp! So bring it if it's negative
        if flopped_x.w < 0.0:
            time |= 0x8000

        # The first frame should always be negated
        if idx == 0 and flopped_x.w < 0.0:
            flopped_x.negate()

        # And finally, write the rotations down
        ska_data += struct.pack("Ifff", time, flopped_x.x, flopped_x.y, flopped_x.z)

    # Then, write translations! We go x, z, -y because again, the world is rotated 90 degrees and blender's Z (height) is Y in DirectX, and Y is Z, but inverse!
    for idx, x in enumerate(ska_translations):
        ska_data += struct.pack("Ifff", idx, x.x, x.z, -x.y)

    try:
        with open(path, "wb") as out:
            out.write(ska_data)
            bpy.context.workspace.status_text_set(f"Exported camera animation into {path}!")
    except OSError:
        print(f"Failed to write the camera animation to {path}!")

# Set your path here
export("animation.cam")
