"""
A collection of functions and objects for creating or placing inset axes.
"""

from matplotlib import _api, docstring
from matplotlib.offsetbox import AnchoredOffsetbox
from matplotlib.patches import Patch, Rectangle
from matplotlib.path import Path
from matplotlib.transforms import Bbox, BboxTransformTo
from matplotlib.transforms import IdentityTransform, TransformedBbox

from . import axes_size as Size
from .parasite_axes import HostAxes


class InsetPosition:
    @docstring.dedent_interpd
    def __init__(self, parent, lbwh):
        """
        An object for positioning an inset axes.

        This is created by specifying the normalized coordinates in the axes,
        instead of the figure.

        Parameters
        ----------
        parent : `matplotlib.axes.Axes`
            Axes to use for normalizing coordinates.

        lbwh : iterable of four floats
            The left edge, bottom edge, width, and height of the inset axes, in
            units of the normalized coordinate of the *parent* axes.

        See Also
        --------
        :meth:`matplotlib.axes.Axes.set_axes_locator`

        Examples
        --------
        The following bounds the inset axes to a box with 20%% of the parent
        axes's height and 40%% of the width. The size of the axes specified
        ([0, 0, 1, 1]) ensures that the axes completely fills the bounding box:

        >>> parent_axes = plt.gca()
        >>> ax_ins = plt.axes([0, 0, 1, 1])
        >>> ip = InsetPosition(ax, [0.5, 0.1, 0.4, 0.2])
        >>> ax_ins.set_axes_locator(ip)
        """
        self.parent = parent
        self.lbwh = lbwh

    def __call__(self, ax, renderer):
        bbox_parent = self.parent.get_position(original=False)
        trans = BboxTransformTo(bbox_parent)
        bbox_inset = Bbox.from_bounds(*self.lbwh)
        bb = TransformedBbox(bbox_inset, trans)
        return bb


class AnchoredLocatorBase(AnchoredOffsetbox):
    def __init__(self, bbox_to_anchor, offsetbox, loc,
                 borderpad=0.5, bbox_transform=None):
        super().__init__(
            loc, pad=0., child=None, borderpad=borderpad,
            bbox_to_anchor=bbox_to_anchor, bbox_transform=bbox_transform
        )

    def draw(self, renderer):
        raise RuntimeError("No draw method should be called")

    def __call__(self, ax, renderer):
        self.axes = ax

        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        self._update_offset_func(renderer, fontsize)

        width, height, xdescent, ydescent = self.get_extent(renderer)

        px, py = self.get_offset(width, height, 0, 0, renderer)
        bbox_canvas = Bbox.from_bounds(px, py, width, height)
        tr = ax.figure.transFigure.inverted()
        bb = TransformedBbox(bbox_canvas, tr)

        return bb


class AnchoredSizeLocator(AnchoredLocatorBase):
    def __init__(self, bbox_to_anchor, x_size, y_size, loc,
                 borderpad=0.5, bbox_transform=None):
        super().__init__(
            bbox_to_anchor, None, loc,
            borderpad=borderpad, bbox_transform=bbox_transform
        )

        self.x_size = Size.from_any(x_size)
        self.y_size = Size.from_any(y_size)

    def get_extent(self, renderer):
        bbox = self.get_bbox_to_anchor()
        dpi = renderer.points_to_pixels(72.)

        r, a = self.x_size.get_size(renderer)
        width = bbox.width * r + a * dpi
        r, a = self.y_size.get_size(renderer)
        height = bbox.height * r + a * dpi

        xd, yd = 0, 0

        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        pad = self.pad * fontsize

        return width + 2 * pad, height + 2 * pad, xd + pad, yd + pad


class AnchoredZoomLocator(AnchoredLocatorBase):
    def __init__(self, parent_axes, zoom, loc,
                 borderpad=0.5,
                 bbox_to_anchor=None,
                 bbox_transform=None):
        self.parent_axes = parent_axes
        self.zoom = zoom
        if bbox_to_anchor is None:
            bbox_to_anchor = parent_axes.bbox
        super().__init__(
            bbox_to_anchor, None, loc, borderpad=borderpad,
            bbox_transform=bbox_transform)

    def get_extent(self, renderer):
        bb = TransformedBbox(self.axes.viewLim, self.parent_axes.transData)
        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        pad = self.pad * fontsize
        return (abs(bb.width * self.zoom) + 2 * pad,
                abs(bb.height * self.zoom) + 2 * pad,
                pad, pad)


class BboxPatch(Patch):
    @docstring.dedent_interpd
    def __init__(self, bbox, **kwargs):
        """
        Patch showing the shape bounded by a Bbox.

        Parameters
        ----------
        bbox : `matplotlib.transforms.Bbox`
            Bbox to use for the extents of this patch.

        **kwargs
            Patch properties. Valid arguments include:

            %(Patch_kwdoc)s
        """
        if "transform" in kwargs:
            raise ValueError("transform should not be set")

        kwargs["transform"] = IdentityTransform()
        super().__init__(**kwargs)
        self.bbox = bbox

    def get_path(self):
        # docstring inherited
        x0, y0, x1, y1 = self.bbox.extents
        return Path([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)],
                    closed=True)


class BboxConnector(Patch):
    @staticmethod
    def get_bbox_edge_pos(bbox, loc):
        """
        Helper function to obtain the location of a corner of a bbox

        Parameters
        ----------
        bbox : `matplotlib.transforms.Bbox`

        loc : {1, 2, 3, 4}
            Corner of *bbox*. Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        Returns
        -------
        x, y : float
            Coordinates of the corner specified by *loc*.
        """
        x0, y0, x1, y1 = bbox.extents
        if loc == 1:
            return x1, y1
        elif loc == 2:
            return x0, y1
        elif loc == 3:
            return x0, y0
        elif loc == 4:
            return x1, y0

    @staticmethod
    def connect_bbox(bbox1, bbox2, loc1, loc2=None):
        """
        Helper function to obtain a Path from one bbox to another.

        Parameters
        ----------
        bbox1, bbox2 : `matplotlib.transforms.Bbox`
            Bounding boxes to connect.

        loc1 : {1, 2, 3, 4}
            Corner of *bbox1* to use. Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        loc2 : {1, 2, 3, 4}, optional
            Corner of *bbox2* to use. If None, defaults to *loc1*.
            Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        Returns
        -------
        path : `matplotlib.path.Path`
            A line segment from the *loc1* corner of *bbox1* to the *loc2*
            corner of *bbox2*.
        """
        if isinstance(bbox1, Rectangle):
            bbox1 = TransformedBbox(Bbox.unit(), bbox1.get_transform())
        if isinstance(bbox2, Rectangle):
            bbox2 = TransformedBbox(Bbox.unit(), bbox2.get_transform())
        if loc2 is None:
            loc2 = loc1
        x1, y1 = BboxConnector.get_bbox_edge_pos(bbox1, loc1)
        x2, y2 = BboxConnector.get_bbox_edge_pos(bbox2, loc2)
        return Path([[x1, y1], [x2, y2]])

    @docstring.dedent_interpd
    def __init__(self, bbox1, bbox2, loc1, loc2=None, **kwargs):
        """
        Connect two bboxes with a straight line.

        Parameters
        ----------
        bbox1, bbox2 : `matplotlib.transforms.Bbox`
            Bounding boxes to connect.

        loc1 : {1, 2, 3, 4}
            Corner of *bbox1* to draw the line. Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        loc2 : {1, 2, 3, 4}, optional
            Corner of *bbox2* to draw the line. If None, defaults to *loc1*.
            Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        **kwargs
            Patch properties for the line drawn. Valid arguments include:

            %(Patch_kwdoc)s
        """
        if "transform" in kwargs:
            raise ValueError("transform should not be set")

        kwargs["transform"] = IdentityTransform()
        if 'fill' in kwargs:
            super().__init__(**kwargs)
        else:
            fill = bool({'fc', 'facecolor', 'color'}.intersection(kwargs))
            super().__init__(fill=fill, **kwargs)
        self.bbox1 = bbox1
        self.bbox2 = bbox2
        self.loc1 = loc1
        self.loc2 = loc2

    def get_path(self):
        # docstring inherited
        return self.connect_bbox(self.bbox1, self.bbox2,
                                 self.loc1, self.loc2)


class BboxConnectorPatch(BboxConnector):
    @docstring.dedent_interpd
    def __init__(self, bbox1, bbox2, loc1a, loc2a, loc1b, loc2b, **kwargs):
        """
        Connect two bboxes with a quadrilateral.

        The quadrilateral is specified by two lines that start and end at
        corners of the bboxes. The four sides of the quadrilateral are defined
        by the two lines given, the line between the two corners specified in
        *bbox1* and the line between the two corners specified in *bbox2*.

        Parameters
        ----------
        bbox1, bbox2 : `matplotlib.transforms.Bbox`
            Bounding boxes to connect.

        loc1a, loc2a : {1, 2, 3, 4}
            Corners of *bbox1* and *bbox2* to draw the first line.
            Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        loc1b, loc2b : {1, 2, 3, 4}
            Corners of *bbox1* and *bbox2* to draw the second line.
            Valid values are::

                'upper right'  : 1,
                'upper left'   : 2,
                'lower left'   : 3,
                'lower right'  : 4

        **kwargs
            Patch properties for the line drawn:

            %(Patch_kwdoc)s
        """
        if "transform" in kwargs:
            raise ValueError("transform should not be set")
        super().__init__(bbox1, bbox2, loc1a, loc2a, **kwargs)
        self.loc1b = loc1b
        self.loc2b = loc2b

    def get_path(self):
        # docstring inherited
        path1 = self.connect_bbox(self.bbox1, self.bbox2, self.loc1, self.loc2)
        path2 = self.connect_bbox(self.bbox2, self.bbox1,
                                  self.loc2b, self.loc1b)
        path_merged = [*path1.vertices, *path2.vertices, path1.vertices[0]]
        return Path(path_merged)


def _add_inset_axes(parent_axes, inset_axes):
    """Helper function to add an inset axes and disable navigation in it"""
    parent_axes.figure.add_axes(inset_axes)
    inset_axes.set_navigate(False)


@docstring.dedent_interpd
def inset_axes(parent_axes, width, height, loc='upper right',
               bbox_to_anchor=None, bbox_transform=None,
               axes_class=None,
               axes_kwargs=None,
               borderpad=0.5):
    """
    Create an inset axes with a given width and height.

    Both sizes used can be specified either in inches or percentage.
    For example,::

        inset_axes(parent_axes, width='40%%', height='30%%', loc=3)

    creates in inset axes in the lower left corner of *parent_axes* which spans
    over 30%% in height and 40%% in width of the *parent_axes*. Since the usage
    of `.inset_axes` may become slightly tricky when exceeding such standard
    cases, it is recommended to read :doc:`the examples
    </gallery/axes_grid1/inset_locator_demo>`.

    Notes
    -----
    The meaning of *bbox_to_anchor* and *bbox_to_transform* is interpreted
    differently from that of legend. The value of bbox_to_anchor
    (or the return value of its get_points method; the default is
    *parent_axes.bbox*) is transformed by the bbox_transform (the default
    is Identity transform) and then interpreted as points in the pixel
    coordinate (which is dpi dependent).

    Thus, following three calls are identical and creates an inset axes
    with respect to the *parent_axes*::

       axins = inset_axes(parent_axes, "30%%", "40%%")
       axins = inset_axes(parent_axes, "30%%", "40%%",
                          bbox_to_anchor=parent_axes.bbox)
       axins = inset_axes(parent_axes, "30%%", "40%%",
                          bbox_to_anchor=(0, 0, 1, 1),
                          bbox_transform=parent_axes.transAxes)

    Parameters
    ----------
    parent_axes : `matplotlib.axes.Axes`
        Axes to place the inset axes.

    width, height : float or str
        Size of the inset axes to create. If a float is provided, it is
        the size in inches, e.g. *width=1.3*. If a string is provided, it is
        the size in relative units, e.g. *width='40%%'*. By default, i.e. if
        neither *bbox_to_anchor* nor *bbox_transform* are specified, those
        are relative to the parent_axes. Otherwise they are to be understood
        relative to the bounding box provided via *bbox_to_anchor*.

    loc : int or str, default: 1
        Location to place the inset axes. The valid locations are::

            'upper right'  : 1,
            'upper left'   : 2,
            'lower left'   : 3,
            'lower right'  : 4,
            'right'        : 5,
            'center left'  : 6,
            'center right' : 7,
            'lower center' : 8,
            'upper center' : 9,
            'center'       : 10

    bbox_to_anchor : tuple or `matplotlib.transforms.BboxBase`, optional
        Bbox that the inset axes will be anchored to. If None,
        a tuple of (0, 0, 1, 1) is used if *bbox_transform* is set
        to *parent_axes.transAxes* or *parent_axes.figure.transFigure*.
        Otherwise, *parent_axes.bbox* is used. If a tuple, can be either
        [left, bottom, width, height], or [left, bottom].
        If the kwargs *width* and/or *height* are specified in relative units,
        the 2-tuple [left, bottom] cannot be used. Note that,
        unless *bbox_transform* is set, the units of the bounding box
        are interpreted in the pixel coordinate. When using *bbox_to_anchor*
        with tuple, it almost always makes sense to also specify
        a *bbox_transform*. This might often be the axes transform
        *parent_axes.transAxes*.

    bbox_transform : `matplotlib.transforms.Transform`, optional
        Transformation for the bbox that contains the inset axes.
        If None, a `.transforms.IdentityTransform` is used. The value
        of *bbox_to_anchor* (or the return value of its get_points method)
        is transformed by the *bbox_transform* and then interpreted
        as points in the pixel coordinate (which is dpi dependent).
        You may provide *bbox_to_anchor* in some normalized coordinate,
        and give an appropriate transform (e.g., *parent_axes.transAxes*).

    axes_class : `matplotlib.axes.Axes` type, optional
        If specified, the inset axes created will be created with this class's
        constructor.

    axes_kwargs : dict, optional
        Keyworded arguments to pass to the constructor of the inset axes.
        Valid arguments include:

        %(Axes_kwdoc)s

    borderpad : float, default: 0.5
        Padding between inset axes and the bbox_to_anchor.
        The units are axes font size, i.e. for a default font size of 10 points
        *borderpad = 0.5* is equivalent to a padding of 5 points.

    Returns
    -------
    inset_axes : *axes_class*
        Inset axes object created.
    """

    if axes_class is None:
        axes_class = HostAxes

    if axes_kwargs is None:
        inset_axes = axes_class(parent_axes.figure, parent_axes.get_position())
    else:
        inset_axes = axes_class(parent_axes.figure, parent_axes.get_position(),
                                **axes_kwargs)

    if bbox_transform in [parent_axes.transAxes,
                          parent_axes.figure.transFigure]:
        if bbox_to_anchor is None:
            _api.warn_external("Using the axes or figure transform requires a "
                               "bounding box in the respective coordinates. "
                               "Using bbox_to_anchor=(0, 0, 1, 1) now.")
            bbox_to_anchor = (0, 0, 1, 1)

    if bbox_to_anchor is None:
        bbox_to_anchor = parent_axes.bbox

    if (isinstance(bbox_to_anchor, tuple) and
            (isinstance(width, str) or isinstance(height, str))):
        if len(bbox_to_anchor) != 4:
            raise ValueError("Using relative units for width or height "
                             "requires to provide a 4-tuple or a "
                             "`Bbox` instance to `bbox_to_anchor.")

    axes_locator = AnchoredSizeLocator(bbox_to_anchor,
                                       width, height,
                                       loc=loc,
                                       bbox_transform=bbox_transform,
                                       borderpad=borderpad)

    inset_axes.set_axes_locator(axes_locator)

    _add_inset_axes(parent_axes, inset_axes)

    return inset_axes


@docstring.dedent_interpd
def zoomed_inset_axes(parent_axes, zoom, loc='upper right',
                      bbox_to_anchor=None, bbox_transform=None,
                      axes_class=None,
                      axes_kwargs=None,
                      borderpad=0.5):
    """
    Create an anchored inset axes by scaling a parent axes. For usage, also see
    :doc:`the examples </gallery/axes_grid1/inset_locator_demo2>`.

    Parameters
    ----------
    parent_axes : `matplotlib.axes.Axes`
        Axes to place the inset axes.

    zoom : float
        Scaling factor of the data axes. *zoom* > 1 will enlargen the
        coordinates (i.e., "zoomed in"), while *zoom* < 1 will shrink the
        coordinates (i.e., "zoomed out").

    loc : int or str, default: 'upper right'
        Location to place the inset axes. The valid locations are::

            'upper right'  : 1,
            'upper left'   : 2,
            'lower left'   : 3,
            'lower right'  : 4,
            'right'        : 5,
            'center left'  : 6,
            'center right' : 7,
            'lower center' : 8,
            'upper center' : 9,
            'center'       : 10

    bbox_to_anchor : tuple or `matplotlib.transforms.BboxBase`, optional
        Bbox that the inset axes will be anchored to. If None,
        *parent_axes.bbox* is used. If a tuple, can be either
        [left, bottom, width, height], or [left, bottom].
        If the kwargs *width* and/or *height* are specified in relative units,
        the 2-tuple [left, bottom] cannot be used. Note that
        the units of the bounding box are determined through the transform
        in use. When using *bbox_to_anchor* it almost always makes sense to
        also specify a *bbox_transform*. This might often be the axes transform
        *parent_axes.transAxes*.

    bbox_transform : `matplotlib.transforms.Transform`, optional
        Transformation for the bbox that contains the inset axes.
        If None, a `.transforms.IdentityTransform` is used (i.e. pixel
        coordinates). This is useful when not providing any argument to
        *bbox_to_anchor*. When using *bbox_to_anchor* it almost always makes
        sense to also specify a *bbox_transform*. This might often be the
        axes transform *parent_axes.transAxes*. Inversely, when specifying
        the axes- or figure-transform here, be aware that not specifying
        *bbox_to_anchor* will use *parent_axes.bbox*, the units of which are
        in display (pixel) coordinates.

    axes_class : `matplotlib.axes.Axes` type, optional
        If specified, the inset axes created will be created with this class's
        constructor.

    axes_kwargs : dict, optional
        Keyworded arguments to pass to the constructor of the inset axes.
        Valid arguments include:

        %(Axes_kwdoc)s

    borderpad : float, default: 0.5
        Padding between inset axes and the bbox_to_anchor.
        The units are axes font size, i.e. for a default font size of 10 points
        *borderpad = 0.5* is equivalent to a padding of 5 points.

    Returns
    -------
    inset_axes : *axes_class*
        Inset axes object created.
    """

    if axes_class is None:
        axes_class = HostAxes

    if axes_kwargs is None:
        inset_axes = axes_class(parent_axes.figure, parent_axes.get_position())
    else:
        inset_axes = axes_class(parent_axes.figure, parent_axes.get_position(),
                                **axes_kwargs)

    axes_locator = AnchoredZoomLocator(parent_axes, zoom=zoom, loc=loc,
                                       bbox_to_anchor=bbox_to_anchor,
                                       bbox_transform=bbox_transform,
                                       borderpad=borderpad)
    inset_axes.set_axes_locator(axes_locator)

    _add_inset_axes(parent_axes, inset_axes)

    return inset_axes


@docstring.dedent_interpd
def mark_inset(parent_axes, inset_axes, loc1, loc2, **kwargs):
    """
    Draw a box to mark the location of an area represented by an inset axes.

    This function draws a box in *parent_axes* at the bounding box of
    *inset_axes*, and shows a connection with the inset axes by drawing lines
    at the corners, giving a "zoomed in" effect.

    Parameters
    ----------
    parent_axes : `matplotlib.axes.Axes`
        Axes which contains the area of the inset axes.

    inset_axes : `matplotlib.axes.Axes`
        The inset axes.

    loc1, loc2 : {1, 2, 3, 4}
        Corners to use for connecting the inset axes and the area in the
        parent axes.

    **kwargs
        Patch properties for the lines and box drawn:

        %(Patch_kwdoc)s

    Returns
    -------
    pp : `matplotlib.patches.Patch`
        The patch drawn to represent the area of the inset axes.

    p1, p2 : `matplotlib.patches.Patch`
        The patches connecting two corners of the inset axes and its area.
    """
    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)

    if 'fill' in kwargs:
        pp = BboxPatch(rect, **kwargs)
    else:
        fill = bool({'fc', 'facecolor', 'color'}.intersection(kwargs))
        pp = BboxPatch(rect, fill=fill, **kwargs)
    parent_axes.add_patch(pp)

    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1, **kwargs)
    inset_axes.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2, **kwargs)
    inset_axes.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2