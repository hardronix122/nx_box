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

# This one is needed because for Blender, the world is rotated upwards, but thps_scene_io rotates it back!
ninety_deg_basis_rotation = Quaternion((0.7071068, -0.7071068, 0.0, 0.0))

def bytepad(data):
    misalignment = len(data) % 4

    if misalignment != 0:
        return b"\x00" * (4 - misalignment)
    
    return b""

def xprint(message):
    print(message)
    bpy.context.workspace.status_text_set(message)

def export(path):
    ska_rotations = []
    ska_translations = []
    ska_custom_keys = []
    
    camera_fov = None
    last_camera_fov = None
    camera_fov_keys = []

    bpy.ops.screen.animation_cancel(restore_frame=False)

    
    main_cam = bpy.data.objects["main_camera"]

    if not main_cam:
        xprint("Failed to find the main camera! Make sure to label it \"main_camera\"!")
        return

    bpy.context.scene.frame_set(0)

    # Collect the keyframes
    for x in range(0, bpy.context.scene.frame_end):
        frame = bpy.context.scene.frame_current
        
        print(f"Frame: {frame}")

        ska_rotations.append(copy.copy(main_cam.rotation_quaternion))
        ska_translations.append(copy.copy(main_cam.location))

        # Also, collect Camera's FOV and deduplicate it on the fly
        camera_fov = main_cam.data.lens
        
        camera_lens_width = main_cam.data.sensor_width
        
        if last_camera_fov is None:
            camera_fov_keys.append((frame, camera_fov, camera_lens_width))
            last_camera_fov = camera_fov
        else:
            if not math.isclose(camera_fov, last_camera_fov, rel_tol=1e-5):
                camera_fov_keys.append((frame, camera_fov, camera_lens_width))
                last_camera_fov = camera_fov
        
        bpy.context.scene.frame_set(bpy.context.scene.frame_current + bpy.context.scene.frame_step)
        
    # Collect custom keys (they're unordered so like...)
    for m in bpy.context.scene.timeline_markers:
        cmd, arg = m.name.split(" ", 1)
        
        if cmd == "runscript" or cmd == "fov":
            if not arg:
                xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - empty arguments!")
                return

            ska_custom_keys.append((m.frame, cmd, arg))
        
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
    
    # The game requires the root to be pre-rotated and the time to be in frames... Like, always, I guess...
    ska_flags |= flag_prerotated_root
    ska_flags |= flag_compressed_time
    
    ska_time = bpy.context.scene.frame_end / 60

    # Since it's just a camera, it'll be a single bone
    bones_count = 1

    rotation_keys_count = len(ska_rotations)
    translation_keys_count = len(ska_translations)
    
    ska_taken_frames = {x[0] for x in ska_custom_keys}
    actual_camera_keys_count = 0
    
    for x in camera_fov_keys:
        if x[0] in ska_taken_frames:
            continue
        
        actual_camera_keys_count += 1
    
    
    custom_keys_count = len(ska_custom_keys) + actual_camera_keys_count

    # Write the header
    ska_data = struct.pack("<IIfIIIIHH", ska_version, ska_flags, ska_time, bones_count, rotation_keys_count, translation_keys_count, custom_keys_count, rotation_keys_count, translation_keys_count)

    # Pad the header
    ska_data += bytepad(ska_data)

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
        
    # This will be common for custom marker-driven and camera-driven keys, containing a tuple (frame, type, data)
    custom_frames_combined = []
    
    # Then, write custom marker-driven keys
    for custkey in ska_custom_keys:
        cust_frame = custkey[0];
        cust_cmd = custkey[1];
        cust_arg = custkey[2];
        
        # Runscript custom keyframe (index 4), takes a single parameter (32-bit 0xedb88320 unsigned script checksum")
        if cust_cmd == "runscript":
            script_checksum = None
            
            # If we get a hex
            if cust_arg.startswith("0x") or cust_arg.startswith("0X"):
                try:
                    script_checksum = int(cust_arg, 16)        
                except ValueError:
                    xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - non-hex value ({cust_arg}")
                    return
            # Otherwise, calculate the checksum
            else:
                if not cust_arg:
                    xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - empty arguments!")
                    return
                
                script_checksum = generate_crc(cust_arg)
            
            if script_checksum is None:
                xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - checksum calculation failure ({cust_arg})!")
                return
            
            custom_frames_combined.append((cust_frame, 4, script_checksum))
 
            
        # FOV custom keyframe (index 1), takes a single parameter (a float of FOV)
        if cust_cmd == "fov":
            focal_length = None
            
            try:
                focal_length = math.radians(float(cust_arg))
            except ValueError:
                xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - invalid float argument!")
                return
            
            if focal_length is None:
                xprint(f"Failed to parse a custom key at frame {cust_frame} (`{cust_cmd}`) - NoneType float argument!")
                return
            
            custom_frames_combined.append((cust_frame, 1, focal_length))
        
    # Collect taken frames beforehand, tech bros say its faster xD
    prev_taken_frames = {x[0] for x in custom_frames_combined}
        
    # And finally, here we finish collecting custom keyframes by taking camera ones and avoiding the already set ones
    for custkey in camera_fov_keys:
        frame = custkey[0]
        fov = custkey[1]
        sensor_width = custkey[2]
        
        # Do not append if taken
        if frame in prev_taken_frames:
            continue
        
        fov = 2.0 * math.atan2(sensor_width, 2.0 * fov)
        
        custom_frames_combined.append((frame, 1, fov))
    
    # Sort custom keyframes... The game hates unsorted ones
    custom_frames_combined.sort(key=lambda x: x[0])
    
    # Finally, write the custom keys
    for x in custom_frames_combined:
        if x[1] == 1:
            # Write the focal length key!
            # uint32_t frame
            # uint32_t keyType
            # uint32_t size
            # float focalLength
            ska_data += struct.pack("IIIf", x[0], 1, 16, x[2])
        
        if x[1] == 4:
            # Write the runscript key!
            # uint32_t frame
            # uint32_t keyType
            # uint32_t size
            # uint32_t scriptChecksum
            ska_data += struct.pack("IIII", x[0], 4, 16, x[2])
            
        # After each keyframe, we need to pad things!
        ska_data += bytepad(ska_data)

    try:
        with open(path, "wb") as out:
            out.write(ska_data)
            xprint(f"Exported camera animation into {path}! {len(ska_rotations)} rotations, {len(ska_translations)} translations, {len(custom_frames_combined)} custom keys")
    except OSError:
        print(f"Failed to write the camera animation to {path}!")

# Set your path here
export("animation.cam")
