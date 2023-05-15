import numpy as np
from scipy.spatial.transform import Rotation as R

# Custom
import pypattern as pyp

# Other assets

from .bands import BandPanel
from .circle_skirt import CircleArcPanel


# Collar shapes withough extra panels
def VNeckHalf(depth, width, **kwargs):
    """Simple VNeck design"""

    edges = pyp.EdgeSequence(pyp.Edge([0, 0], [width / 2,-depth]))
    
    return edges


def SquareNeckHalf(depth, width, **kwargs):
    """Square design"""

    edges = pyp.esf.from_verts([0, 0], [0, -depth], [width / 2, -depth])
    
    return edges

def TrapezoidNeckHalf(depth, width, angle=90, **kwargs):
    """Trapesoid neck design"""

    # Special case when angle = 180 (sin = 0)
    if (pyp.utils.close_enough(angle, 180, tol=1) 
            or pyp.utils.close_enough(angle, 0, tol=1)):
        # degrades into VNeck
        return VNeckHalf(depth, width)

    angle = np.deg2rad(angle)

    edges = pyp.esf.from_verts([0, 0], [-depth * np.cos(angle) / np.sin(angle), -depth], [width / 2, -depth])

    return edges


# Collar shapes withough extra panels
def CurvyNeckHalf(depth, width, **kwargs):
    """Testing Curvy Collar design"""

    edges = pyp.EdgeSequence(pyp.CurveEdge(
        [0, 0], [width / 2,-depth], 
        [[0.4, 0.3], [0.8, -0.5]]))
    
    return edges


def CircleArcNeckHalf(depth, width, angle=90, **kwargs):
    """Collar with a side represented by a circle arc"""
    # 1/4 of a circle
    edges = pyp.EdgeSequence(pyp.CircleEdge.from_points_angle(
        [0, 0], [width / 2,-depth], arc_angle=np.deg2rad(angle),
        right=True
    ))

    return edges

def CircleNeckHalf(depth, width, **kwargs):
    """Collar that forms a perfect circle arc when halfs are stitched"""

    # Take a full desired arc and half it!
    circle = pyp.CircleEdge.from_three_points([0, 0], [width, 0], [width / 2, -depth])

    subdiv = circle.subdivide_len([0.5, 0.5])

    return pyp.EdgeSequence(subdiv[0])


# # ------ Collars with panels ------

class Turtle(pyp.Component):

    def __init__(self, tag, body, design, length_f, length_b) -> None:
        super().__init__(f'Turtle_{tag}')

        depth = design['collar']['component']['depth']['v']

        height_p = body['height'] - body['head_l'] + depth
        self.front = BandPanel(
            f'{tag}_turtle_front', length_f, depth).translate_by([-length_f / 2, height_p, 10])
        self.back = BandPanel(
            f'{tag}_turtle_back', length_b, depth).translate_by([-length_b / 2, height_p, -10])

        self.stitching_rules.append((
            self.front.interfaces['right'], 
            self.back.interfaces['right']
        ))

        self.interfaces = {
            'front': self.front.interfaces['left'],
            'back': self.back.interfaces['left'],
            'bottom': pyp.Interface.from_multiple(
                self.front.interfaces['bottom'],
                self.back.interfaces['bottom']
            )
        }

class SimpleLapelPanel(pyp.Panel):
    """A panel for the front part of simple Lapel"""
    def __init__(self, name, length, max_depth) -> None:
        super().__init__(name)

        self.edges = pyp.esf.from_verts(
            [0, 0], [max_depth, 0], [max_depth, -length]
        )

        self.edges.append(
            pyp.CurveEdge(
                self.edges[-1].end, 
                self.edges[0].start, 
                [[0.7, 0.2]]
            )
        )

        self.interfaces = {
            'to_collar': pyp.Interface(self, self.edges[0]),
            'to_bodice': pyp.Interface(self, self.edges[1])
        }



class SimpleLapel(pyp.Component):

    def __init__(self, tag, body, design, length_f, length_b) -> None:
        super().__init__(f'Turtle_{tag}')

        depth = design['collar']['component']['depth']['v']
        standing = design['collar']['component']['lapel_standing']['v']

        # TODO Place correctly on a side
        height_p = body['height'] - body['head_l'] + depth * 2
        
        self.front = SimpleLapelPanel(
            f'{tag}_lapel_front', length_f, depth).translate_by([-length_f / 2, height_p, 30])

        if standing:
            self.back = BandPanel(
                f'{tag}_lapel_back', length_b, depth).translate_by([-length_b / 2, height_p, -10])
        else:
            # TODO Add a curved back panel
            rad = length_f / (np.pi / 2)
            self.back = CircleArcPanel(
                f'{tag}_lapel_back', rad, depth, np.pi / 2
            ).translate_by([-length_b, height_p, -10])
            self.back.rotate_by(R.from_euler('XYZ', [90, 45, 0], degrees=True))


        self.stitching_rules.append((
            self.front.interfaces['to_collar'], 
            self.back.interfaces['right'] if standing else self.back.interfaces['left']
        ))

        self.interfaces = {
            #'front': NOTE: no front interface here
            'back': self.back.interfaces['left'] if standing else self.back.interfaces['right'],
            'bottom': pyp.Interface.from_multiple(
                self.front.interfaces['to_bodice'],
                self.back.interfaces['bottom'] if standing else self.back.interfaces['top'],
            )
        }


