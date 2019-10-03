from typing import List
from Point import Point
from Segment import Segment
from Vector import Vector
from tools import rectangle_test, _nf2, triangle_signed_square, form_contours, unique_everseen
from matplotlib.collections import PolyCollection
import numpy as np
import random as rnd


class Polygon:
    def __init__(self, points: List[Point]):
        self.points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = [Point(point) for point in points]

    @property
    def square(self):
        """
        :return: signed square of convex Polygon
        """
        result = 0
        for i in range(1, len(self._points) - 1):
            result += triangle_signed_square(self._points[0], self._points[i], self._points[i + 1])

        return result

    @property
    def orientation(self):
        """
        :return:
        -1 - if orientation is left
        1 - if orientation is right
        """
        return np.sign(self.square)

    @property
    def vertex_number(self):
        """
        :return: number of vertex
        """
        return len(self._points)

    @property
    def edges(self):
        n = len(self._points)
        result = [Segment([self._points[i], self._points[i + 1]]) for i in range(n - 1)]
        result.append(Segment([self._points[n - 1], self._points[0]]))
        return result

    @property
    def is_convex(self):
        """
        :return:
        0 - if it's not convex
        1 - if it's convex
        """
        n = len(self._points) - 1
        begin_orient = _nf2(self._points[n], self._points[0], self._points[1])
        for i in range(1, n):
            current_orient = _nf2(self._points[i - 1], self._points[i], self._points[i + 1])
            if np.sign(begin_orient) != np.sign(current_orient):
                break
        else:
            last_orient = _nf2(self._points[n - 1], self._points[n], self._points[0])
            if np.sign(begin_orient) == np.sign(last_orient):
                return 1
        return 0

    def rectangle_test(self, point):
        """
        Find out if the point inside the rectangle, which is formed by min/max coords of the Polygon's points.

        Parameters
        ----------
        point : array-like

        Returns
        -------
        out : bool
        """
        return rectangle_test(self._points, point)

    def ray_test(self, point):
        """
        Find out if the point inside/outside the polygon.

        1 -- the point lies outside the polygon.
        0 -- the point lies on the edge of the polygon.
        -1 -- the point lies inside the polygon.

        Parameters
        ----------
        point : array_like

        Returns
        -------
        out : int
        """
        f, phi = [1, rnd.uniform(0, np.pi)]
        v = np.array([np.cos(phi), np.sin(phi)])

        for edge in self.edges:
            m = np.array([v, Vector(edge[1], edge[0])])
            if np.linalg.det(m) == 0:
                continue

            t1, t2 = np.dot(Vector(point, edge[0]), np.linalg.inv(m))
            if t1 > 0:    # if point on the ray, but not on the other side of it
                if t2 in (0., 1.):    # if the ray shoot in the end point of the edge
                    return self.ray_test(point)    # need to rerandom the ray
                elif 0 < t2 < 1:    # if the ray shoot between end points of the edge
                    f *= -1
            elif t1 == 0.:    # if the ray intersect edge line right in the start of itself
                if 0 <= t2 <= 1:    # and the intersection point lies on the edge
                    return 0    # return case: point lies on the edge

        return f

    def segment_clipping(self, segment, case="out"):
        """
        Return the result of inner/outer segment clipping.

        Parameters
        ----------
        segment : Segment
        case : str
            You should use case="out" for outer clipping and case="in" for inner.

        Returns
        -------
        out : list
            out contains the list of Segments.
        """
        case = (-1, 0) if case == "out" else (1, )    # define the allowed values for ray_test
        parameters = {0, 1}  # set of the end points parameters of the segment

        for edge in self.edges:
            intersection = Segment.intersection(segment, edge)
            if intersection[0] == 1:               # if segment and edge have intersection
                parameters.add(intersection[2])    # add t1 parameter of segment parametrization of intersection point

        parameters = list(parameters)
        parameters.sort()

        return [
            # build the segment between the intersection points using the parametrization of the segment
            Segment((segment.point_by_parameter(parameters[i]), segment.point_by_parameter(parameters[i + 1])))
            for i in range(0, len(parameters) - 1)
            # if the midpoint of the segment lies inside/outside (according to the clipping case) the polygon
            if self.ray_test(segment.point_by_parameter((parameters[i] + parameters[i + 1]) / 2)) in case
        ]

    def polygon_clipping(self, other, case="out"):
        """
        Find the polygon clipping.

        Parameters
        ----------
        other : Polygon
        case : str
            You should use case="out" for outer clipping and case="in" for inner.

        Returns
        -------
        out : list
            The out consists of lists of Segments which are formed contours.
        """
        segments = []    # init an empty list for the clipped segments

        for edge in self.edges:
            segments.extend(other.segment_clipping(edge, case=case))    # collect self clipped edges

        for edge in other.edges:
            segments.extend(self.segment_clipping(edge, case="out"))    # collect other clipped edges

        return form_contours(list(unique_everseen(segments)))    # form contours after deleting the duplicates

    def plot(self, ax, **kwargs):
        """
        Add polygon (PolyCollection) to the axes using kwargs.

        Parameters
        ----------
        ax : current Axes object .
        kwargs : key args are the same as in matplotlib.collections.PolyCollection.

        Returns
        -------
        out : PolyCollection
        """
        return ax.add_collection(PolyCollection([self._points], **kwargs))
