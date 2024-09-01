# This example is heavily inspired by minpng.py:
# https://gitlab.com/drj11/pypng/-/blob/main/code/minpng.py?ref_type=heads

from typing import List, Tuple
import struct
import zlib


def write_chunk(f, chunk_type, data):
    f.write(struct.pack(">L",len(data)))
    f.write(chunk_type)
    f.write(data)
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data,checksum)
    f.write(struct.pack(">L",checksum))


def png_save(filename:str, pixels:List[List[int]]):
    with open(filename,'wb') as f:
        f.write(bytes([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
        write_chunk(f, b"IHDR", struct.pack(">2L5B", len(pixels[0]), len(pixels), 8, 6, 0, 0, 0))
        buf = bytearray()
        for row in pixels:
            buf.append(0)
            buf.extend(struct.pack(f">{len(pixels[0])}L",*row))

        write_chunk(f, b"IDAT", zlib.compress(buf))
        write_chunk(f, b"IEND", b"")


def read_chunk(f, chunk_type):
    size, = struct.unpack(">L",f.read(4))
    assert chunk_type == f.read(4), "unexpected chunk."
    data = f.read(size)
    checksum, = struct.unpack(">L",f.read(4))
    assert checksum == zlib.crc32(chunk_type + data), "bad chunk crc."
    return data


def png_load(filename):
    with open(filename,'rb') as f:
        assert f.read(8) == bytes([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), "bad png header."
        chunk_data = read_chunk(f,b"IHDR")
        width,height,*spec = struct.unpack(">2L5B",chunk_data)
        assert spec == [8,6,0,0,0], "uninplemented specification."

        chunk_data = read_chunk(f,b"IDAT")
        pixel_data = zlib.decompress(chunk_data)
        pixels = []
        for i in range(0, len(pixel_data), 4*width+1):
            row_filter, *row_data = pixel_data[i:i+4*width+1]
            assert row_filter == 0, "unimplemented row filter."
            pixels.append(list(struct.unpack(f">{width}L",bytes(row_data))))

        assert height == len(pixels)
        chunk_data = read_chunk(f,b"IEND")
        
    return pixels


if __name__ == "__main__":

    pixels_out = [
        [0xFF0000FF,0xFFFFFFFF],
        [0x000000FF,0x00000000],
    ]

    # pixels_out = [[0x00000000 for _ in range(600)] for _ in range(400)]


    png_save("test.png",pixels_out)
    pixels_in=png_load("test.png")

    for row in pixels_in:
        print(f"[{', '.join(f'0x{pixel:08x}' for pixel in row)}],")
    
    assert pixels_in == pixels_out
