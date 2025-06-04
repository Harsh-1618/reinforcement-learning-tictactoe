import numpy as np
from typing import Dict, List, Tuple, Any

import cython
cimport numpy as cnp
cnp.import_array()

def build_cube(int screen_height,
                int screen_width,
                float linear_spacing,
                float sub_cube_spacing,
                int pixel_scaling,
                float r1_unit,
                float k2_unit):

    cdef int r1_pixel = <int>(r1_unit * pixel_scaling)
    cdef int k2_pixel = <int>(k2_unit * pixel_scaling)
    cdef int sub_cube_spacing_pixel = <int>(sub_cube_spacing * pixel_scaling)

    cdef int k1_pixel = <int>((screen_height*k2_pixel*3)/(8*(r1_pixel+180))) # 120 instead of 180

    cdef cnp.ndarray[cnp.uint8_t, ndim=3] screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    cdef int x_displacement = <int>(screen.shape[1]/2)
    cdef int y_displacement = <int>(screen.shape[0]/2)

    # Making hollow square
    cdef cnp.ndarray[cnp.float32_t, ndim=1] points = np.arange(-r1_pixel, r1_pixel, linear_spacing, dtype=np.float32)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] x_points = np.concatenate(
        (
            np.ones((len(points),), dtype=np.float32) * points[0],
            np.ones((len(points),), dtype=np.float32) * points[-1],
            points[1:-1], # removing overlapping points
            points[1:-1]
        ), axis=0
    )
    cdef cnp.ndarray[cnp.float32_t, ndim=1] y_points = np.concatenate(
        (
            points,
            points,
            np.ones((len(points)-2,), dtype=np.float32) * points[0], # removing overlapping points
            np.ones((len(points)-2,), dtype=np.float32) * points[-1]
        ), axis=0
    )

    # Making hollow cube's core
    cdef cnp.ndarray[cnp.float32_t, ndim=1] center_cube_x = np.repeat(x_points[np.newaxis, :], len(points)-2, axis=0).flatten() # excluding front and back
    cdef cnp.ndarray[cnp.float32_t, ndim=1] center_cube_y = np.repeat(y_points[np.newaxis, :], len(points)-2, axis=0).flatten()
    cdef cnp.ndarray[cnp.float32_t, ndim=1] center_cube_z = np.repeat(points[1:-1], len(x_points)) # repeat Repeats each element of an array after themselves

    cdef cnp.ndarray[cnp.float32_t, ndim=2] xx, yy
    xx, yy = np.meshgrid(points, points) # for rest of the 2 faces
    cdef cnp.ndarray[cnp.float32_t, ndim=1] x_points_face = (xx.flatten()).astype(np.float32)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] y_points_face = (yy.flatten()).astype(np.float32)

    center_cube_x = np.concatenate((x_points_face, center_cube_x, x_points_face), axis=0)
    center_cube_y = np.concatenate((y_points_face, center_cube_y, y_points_face), axis=0)
    center_cube_z = np.concatenate((np.ones((len(x_points_face),), dtype=np.float32)*points[0], center_cube_z, np.ones((len(x_points_face),), dtype=np.float32)*points[-1]), axis=0)

    # Making full hollow cube
    # cdef Dict[str, Tuple[cnp.ndarray[cnp.float32_t, ndim=1], cnp.ndarray[cnp.float32_t, ndim=1], cnp.ndarray[cnp.float32_t, ndim=1]]] cube_dict = {} # keys -> xyz position
    cdef Dict[str, Tuple[cnp.ndarray, cnp.ndarray, cnp.ndarray]] cube_dict = {} # keys -> xyz position
    cdef List[str] sub_cubes = ["0_0_0","1_0_0","2_0_0","0_1_0","1_1_0","2_1_0","0_2_0","1_2_0","2_2_0",
                                "0_0_1","1_0_1","2_0_1","0_1_1","1_1_1","2_1_1","0_2_1","1_2_1","2_2_1",
                                "0_0_2","1_0_2","2_0_2","0_1_2","1_1_2","2_1_2","0_2_2","1_2_2","2_2_2"
    ]

    cdef int x_shift, y_shift, z_shift
    cdef int x_shift_pixel, y_shift_pixel, z_shift_pixel
    for cube in sub_cubes:
        x_shift, y_shift, z_shift = [int(c) for c in cube.split("_")]
        x_shift_pixel = (x_shift-1)*(sub_cube_spacing_pixel + 2*r1_pixel)
        y_shift_pixel = (y_shift-1)*(sub_cube_spacing_pixel + 2*r1_pixel)
        z_shift_pixel = (z_shift-1)*(sub_cube_spacing_pixel + 2*r1_pixel)

        cube_dict[cube] = (
            center_cube_x + x_shift_pixel,
            center_cube_y + y_shift_pixel,
            center_cube_z + z_shift_pixel,
        )

    return screen_height, screen, x_displacement, y_displacement, cube_dict, k1_pixel, k2_pixel

def render_cube(int screen_height,
                cnp.ndarray[cnp.uint8_t, ndim=3] screen,
                int x_displacement,
                int y_displacement,
                Dict[str, Tuple[cnp.ndarray, cnp.ndarray, cnp.ndarray]] cube_dict,
                int k1_pixel,
                int k2_pixel,
                float A,
                float B,
                Dict [str, Tuple[int, int, int]] sub_cube_colors):
    cdef cnp.float32_t cos_a, sin_a, cos_b, sin_b
    cdef Dict[Tuple[cnp.int32_t, cnp.int32_t], Tuple[cnp.float32_t, str, Tuple[int, int, int]]] show_points
    cdef cnp.ndarray[cnp.float32_t, ndim=1] cube_x, cube_y, cube_z
    cdef cnp.ndarray[cnp.float32_t, ndim=1] x_rotate1, y_rotate1, z_rotate1, x_rotate2, z_rotate_2
    cdef cnp.ndarray[cnp.int32_t, ndim=1] cube_x_proj, cube_y_proj, y_proj_plot
    cdef Tuple[cnp.int32_t, ...] x, y, z
    cdef Tuple[Tuple[int, int, int], ...] rgb
    cdef Tuple[int, ...] r, g, b

    screen[:, :, :] = 0
    # screen[y_displacement, :, :] = 255 # grid lines
    # screen[:, x_displacement, :] = 255

    cos_a = np.cos(A, dtype=np.float32)
    sin_a = np.sin(A, dtype=np.float32)
    cos_b = np.cos(B, dtype=np.float32)
    sin_b = np.sin(B, dtype=np.float32)

    show_points = {}
    for k, cube in cube_dict.items():
        cube_x = cube[0]
        cube_y = cube[1]
        cube_z = cube[2]

        # rotation along x axis
        x_rotate1 = cube_x
        y_rotate1 = cube_y*cos_a - cube_z*sin_a
        z_rotate1 = cube_y*sin_a + cube_z*cos_a

        # rotation along y axis
        x_rotate2 = x_rotate1*cos_b + z_rotate1*sin_b
        z_rotate2 = -x_rotate1*sin_b + z_rotate1*cos_b

        cube_x_proj = ((k1_pixel*x_rotate2)/(k2_pixel+z_rotate2)).astype(np.int32) + x_displacement
        cube_y_proj = ((k1_pixel*y_rotate1)/(k2_pixel+z_rotate2)).astype(np.int32) + y_displacement

        y_proj_plot = screen_height - 1 - cube_y_proj

        for i in range(len(cube_x_proj)):
            val = show_points.get((cube_x_proj[i], y_proj_plot[i]))
            if val is not None:
                if z_rotate2[i] < val[0]: # saving only the ones which are infront, i.e. whose z value is minimum
                    show_points[(cube_x_proj[i], y_proj_plot[i])] = (z_rotate2[i], k, sub_cube_colors[k])
            else:
                show_points[(cube_x_proj[i], y_proj_plot[i])] = (z_rotate2[i], k, sub_cube_colors[k])

    x, y = zip(*show_points.keys())
    *_, rgb = zip(*show_points.values())
    r, g, b = zip(*rgb)

    screen[y, x, 0] = np.array(r)
    screen[y, x, 1] = np.array(g)
    screen[y, x, 2] = np.array(b)
    
    return screen, show_points