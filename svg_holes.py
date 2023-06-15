import numpy as np
import svgpathtools as svgpath

from pypattern.generic_utils import vector_angle, close_enough, c_to_list, c_to_np, list_to_c

import pypattern as pyp

def split_half_svg_paths(paths):
    """Sepate SVG paths in half over the vertical line -- for insertion into a edge side
    
        Paths shapes restrictions: 
        1) every path in the provided list is assumed to form a closed loop that has 
        exactly 2 intersection points with a vetrical line passing though the middle of the shape
        2) The paths geometry should not be nested
            as to not create disconnected pieces of the edge when used in shape projection

    """
    # Shape Bbox
    bboxes = np.array([p.bbox() for p in paths])
    bbox = (min(bboxes[:, 0]), max(bboxes[:, 1]), min(bboxes[:, 2]), max(bboxes[:, 3]))
    center_x = (bbox[0] + bbox[1]) / 2

    # Mid-Intersection 
    inter_segment = svgpath.Line(
            center_x + 1j * bbox[2],
            center_x + 1j * bbox[3]
        )

    right, left = [], []
    for p in paths:
        # Intersect points
        intersect_t = p.intersect(inter_segment)

        if len(intersect_t) != 2: 
            raise ValueError(f'SplitSVGHole::ERROR::Each Provided Svg path should cross vertical like exactly 2 times')

        # Split
        from_T, to_T = intersect_t[0][0][0], intersect_t[1][0][0]
        if to_T < from_T:
            from_T, to_T = to_T, from_T

        side_1 = p.cropped(from_T, to_T)
        # This order should preserve continuity
        side_2 = svgpath.Path(*p.cropped(to_T, 1)._segments, *p.cropped(0, from_T)._segments)

        # Collect correctly
        if side_1.bbox()[2] > center_x:
            side_1, side_2 = side_2, side_1
        
        right.append(side_1)
        left.append(side_2)

    return left, right


paths, attributes = svgpath.svg2paths('./assets/img/Logo_adjusted.svg')

# Get the shapes
left, right = split_half_svg_paths(paths)

# Turn into Edge Sequences
left_seqs = [pyp.EdgeSequence.from_svg_path(p) for p in left]
right_seqs = [pyp.EdgeSequence.from_svg_path(p) for p in right]

# DEBUG
print(len(left_seqs), len(right_seqs))

# TODO Scaling

# TODO multi-sides projection

# TODO Put into the main library


# DEBUG
print(len(right), len(left))
# Vis
svgpath.wsvg(right, stroke_widths=[1] * len(right), filename='tmp/output_right.svg')
#svgpath.disvg(right, stroke_widths=[1] * len(right))
#svgpath.disvg(left, stroke_widths=[1] * len(left))