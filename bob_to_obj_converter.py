import struct
import os
from collections import namedtuple

BOB_FILE_ID = 45623

Vertex = namedtuple('Vertex', ['position', 'uv', 'normal'])

def read_bob(filepath):
    with open(filepath, 'rb') as file:
        def read_struct(format):
            size = struct.calcsize(format)
            return struct.unpack(format, file.read(size))

        file_id = read_struct("I")[0]
        if file_id != BOB_FILE_ID:
            raise ValueError("Invalid BOB file")

        mesh_format = read_struct("I")[0]
        vertex_count = read_struct("I")[0]
        face_count = read_struct("I")[0]

        vertices = []
        for _ in range(vertex_count):
            v = read_struct("fff HH hhh xx")
            position = v[0:3]
            uv = (v[3] / 65535, 1 - (v[4] / 65535))  # Flip V coordinate
            normal = tuple(n / 32767 for n in v[5:8])
            vertices.append(Vertex(position, uv, normal))

        faces = []
        for _ in range(face_count):
            if mesh_format == 0:
                face = read_struct("bbb")
            elif mesh_format == 1:
                face = read_struct("HHH")
            else:
                raise ValueError("Unsupported mesh format")
            faces.append(face)

    return vertices, faces

def write_obj(filepath, vertices, faces):
    with open(filepath, 'w') as file:
        file.write("# Converted from BOB format\n")
        
        for v in vertices:
            file.write(f"v {v.position[0]} {v.position[1]} {v.position[2]}\n")
        
        for v in vertices:
            file.write(f"vt {v.uv[0]} {v.uv[1]}\n")
        
        for v in vertices:
            file.write(f"vn {v.normal[0]} {v.normal[1]} {v.normal[2]}\n")
        
        for face in faces:
            # OBJ indices are 1-based
            file.write(f"f {face[0]+1}/{face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}/{face[2]+1}\n")

def convert_bob_to_obj(input_path, output_path):
    vertices, faces = read_bob(input_path)
    write_obj(output_path, vertices, faces)
    print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python bob_to_obj_converter.py input.bob output.obj")
    else:
        convert_bob_to_obj(sys.argv[1], sys.argv[2])