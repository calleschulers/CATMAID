/* -*- mode: espresso; espresso-indent-level: 8; indent-tabs-mode: t -*- */

(function(CATMAID) {

  "use strict";

  /** orientations */
  Stack.ORIENTATION_XY = 0;
  Stack.ORIENTATION_XZ = 1;
  Stack.ORIENTATION_ZY = 2;

  /**
   * A Stack is created with a given pixel resolution, pixel dimension, a
   * translation relative to the project and lists of planes to be excluded
   * (e.g. missing sections in serial section microscopy and missing frames in a
   * time series).
   */
  function Stack(
      id,             //!< {Integer} the stack's id
      title,            //!< {String} the stack's title
      dimension,          //!< {Array} pixel dimensions [x, y, z, ...]
      resolution,         //!< {Array} physical resolution in units/pixel [x, y, z, ...]
      translation,        //!< @todo replace by an affine transform
      skip_planes,        //!< {Array} planes to be excluded from the stack's view [[z,t,...], [z,t,...], ...]
      num_zoom_levels,      //!< {int} that defines the number of available non-artificial zoom levels
      max_zoom_level,       //!< {int} that defines the maximum available zoom level
      description,         //!< {String} of arbitrary meta data
      metadata,
      orientation,         //!< {Integer} orientation (0: xy, 1: xz, 2: yz)
      canaryLocation,
      placeholderColor,
      mirrors
    ) {
    // initialize
    var self = this;

    self.id = id;
    self.title = title;
    self.resolution = resolution;
    self.translation = translation;
    self.dimension = dimension;

    // all possible slices
    self.slices = [];
    self.broken_slices = [];
    for ( var i = 0; i < dimension.z; ++i )
    {
      if ( !skip_planes[ i ] )
        self.slices.push( i );
      else
        self.broken_slices.push( i );
    }

    var MAX_X = dimension.x - 1;   //!< the last possible x-coordinate
    var MAX_Y = dimension.y - 1;   //!< the last possible y-coordinate
    var MAX_Z = dimension.z - 1;   //!< the last possible z-coordinate
    self.MAX_X = MAX_X;
    self.MAX_Y = MAX_Y;
    self.MAX_Z = MAX_Z;

    //! estimate the zoom levels
    if ( num_zoom_levels < 0 ) {
      self.MAX_S = 0;
      var max_dim = Math.max( MAX_X, MAX_Y );
      var min_size = 1024;
      while ( max_dim / Math.pow( 2, self.MAX_S ) > min_size )
        ++self.MAX_S;
    } else {
      self.MAX_S = num_zoom_levels;
    }
    self.MIN_S = max_zoom_level;

    self.description = description;
    self.metadata = metadata;
    self.orientation = orientation;
    self.canaryLocation = canaryLocation;
    self.placeholderColor = placeholderColor;
    self.mirrors = mirrors;
    self.mirrors.sort(function (a, b) {
      return a.position - b.position;
    });

    /**
     * Project x-coordinate for stack coordinates
     */
    switch ( orientation )
    {
    case Stack.ORIENTATION_ZY:
      this.stackToProjectX = function( zs, ys, xs )
      {
        return zs * resolution.z + translation.x;
      };
      break;
    default:
      this.stackToProjectX = function( zs, ys, xs )
      {
        return xs * resolution.x + translation.x;
      };
    }

    /**
     * Project y-coordinate for stack coordinates
     */
    switch ( orientation )
    {
    case Stack.ORIENTATION_XZ:
      this.stackToProjectY = function( zs, ys, xs )
      {
        return zs * resolution.z + translation.y;
      };
      break;
    default:
      this.stackToProjectY = function( zs, ys, xs )
      {
        return ys * resolution.y + translation.y;
      };
    }

    /**
     * Project z-coordinate for stack coordinates
     */
    switch ( orientation )
    {
    case Stack.ORIENTATION_XZ:
      this.stackToProjectZ = function( zs, ys, xs )
      {
        return ys * resolution.y + translation.z;
      };
      break;
    case Stack.ORIENTATION_ZY:
      this.stackToProjectZ = function( zs, ys, xs )
      {
        return xs * resolution.x + translation.z;
      };
      break;
    default:
      this.stackToProjectZ = function( zs, ys, xs )
      {
        return zs * resolution.z + translation.z;
      };
    }


    /**
     * Stack x-coordinate from project coordinates, without clamping to the
     * stack bounds.
     */
    switch ( orientation )
    {
    case Stack.ORIENTATION_ZY:
      this.projectToUnclampedStackX = function( zp, yp, xp )
      {
        return ( zp - translation.z ) / resolution.x;
      };
      break;
    default:
      this.projectToUnclampedStackX = function( zp, yp, xp )
      {
        return ( xp - translation.x ) / resolution.x;
      };
    }

    /**
     * Stack x-coordinate from project coordinates, clamped to the stack
     * bounds.
     */
    this.projectToStackX = function( zp, yp, xp )
    {
      return Math.max( 0, Math.min( MAX_X, this.projectToUnclampedStackX( zp, yp, xp ) ) );
    };

    /**
     * Stack y-coordinate from project coordinates, without clamping to the
     * stack bounds.
     */
    switch ( orientation )
    {
    case Stack.ORIENTATION_XZ:
      this.projectToUnclampedStackY = function( zp, yp, xp )
      {
        return ( zp - translation.z ) / resolution.y;
      };
      break;
    default:  // xy
      this.projectToUnclampedStackY = function( zp, yp, xp )
      {
        return ( yp - translation.y ) / resolution.y;
      };
    }

    /**
     * Stack y-coordinate from project coordinates, clamped to the stack
     * bounds.
     */
    this.projectToStackY = function( zp, yp, xp )
    {
      return Math.max( 0, Math.min( MAX_Y, this.projectToUnclampedStackY( zp, yp, xp ) ) );
    };


    /**
     * Stack z-coordinate from project coordinates. In stack space, Z is
     * discrete and by convention, coordinates between one section and the next
     * are projected onto the first.
     */
    var projectToStackZ;
    switch ( orientation )
    {
    case Stack.ORIENTATION_XZ:
      projectToStackZ = function( zp, yp, xp )
      {
        return Math.floor( ( yp - translation.y ) / resolution.z );
      };
      break;
    case Stack.ORIENTATION_ZY:
      projectToStackZ = function( zp, yp, xp )
      {
        return Math.floor( ( xp - translation.x ) / resolution.z );
      };
      break;
    default:
      projectToStackZ = function( zp, yp, xp )
      {
        return Math.floor( ( zp - translation.z ) / resolution.z );
      };
    }

    this.projectToLinearStackZ = projectToStackZ;


    /**
     * Stack z-coordinate from project coordinates, without clamping to the
     * stack bounds.
     */
    this.projectToUnclampedStackZ = function( zp, yp, xp )
    {
      var z1, z2;
      z1 = z2 = projectToStackZ( zp, yp, xp );
      while ( skip_planes[ z1 ] && skip_planes[ z2 ] )
      {
        z1 = Math.max( 0, z1 - 1 );
        z2 = Math.min( MAX_Z, z2 + 1 );
      }
      return skip_planes[ z1 ] ? z2 : z1;
    };

    /**
     * Stack y-coordinate from project coordinates, clamped to the stack
     * bounds.
     */
    this.projectToStackZ = function( zp, yp, xp )
    {
      return Math.max( 0, Math.min( MAX_Z, this.projectToUnclampedStackZ( zp, yp, xp ) ) );
    };

    /**
     * Project x-resolution for a given zoom level.
     */
    this.stackToProjectSX = function (s) {
      return this.resolution.x * Math.pow(2, s);
    };

    /**
     * Stack zoom level for a given x-resolution.
     */
    this.projectToStackSX = function (res) {
      return Math.log(res / this.resolution.x) / Math.LN2;
    };

    /**
     * Transfer the limiting coordinates of an orthogonal box from stack to
     * project coordinates.  Transferred coordinates are written into
     * projectBox.  This method is faster than createStackToProjectBox because
     * it does not generate new objects (Firefox 20%, Chromium 100% !)
     *
     *  @param stackBox   {{min: {x, y, z}, max: {x, y, z}}}
     *  @param projectBox {{min: {x, y, z}, max: {x, y, z}}}
     */
    this.stackToProjectBox = function( stackBox, projectBox )
    {
      projectBox.min.x = self.stackToProjectX( stackBox.min.z, stackBox.min.y, stackBox.min.x );
      projectBox.min.y = self.stackToProjectY( stackBox.min.z, stackBox.min.y, stackBox.min.x );
      projectBox.min.z = self.stackToProjectZ( stackBox.min.z, stackBox.min.y, stackBox.min.x );

      projectBox.max.x = self.stackToProjectX( stackBox.max.z, stackBox.max.y, stackBox.max.x );
      projectBox.max.y = self.stackToProjectY( stackBox.max.z, stackBox.max.y, stackBox.max.x );
      projectBox.max.z = self.stackToProjectZ( stackBox.max.z, stackBox.max.y, stackBox.max.x );

      return projectBox;
    };


    /**
     * Create a new box from an orthogonal box by transferring its limiting
     * coordinates from stack to project coordinates.
     *
     *  @param stackBox {{min: {x, y, z}, max: {x, y, z}}}
     */
    this.createStackToProjectBox = function( stackBox )
    {
      return this.stackToProjectBox(stackBox, {min: {}, max: {}});
    };

    /**
     * Create a new stack box representing the extents of the stack.
     * @return {{min: {x, y, z}, max: {x, y, z}}} extents of the stack in stack coordinates
     */
    this.createStackExtentsBox = function () {
      return {
        min: {x:     0, y:     0, z:     0},
        max: {x: MAX_X, y: MAX_Y, z: MAX_Z}
      };
    };

    /**
     * Return whether a given section number is marked as broken.
     *
     * @param  {Number}  section Stack z coordinate of the section to check
     * @return {Boolean}         True if the section is marked as broken.
     */
    self.isSliceBroken = function (section) {
      return -1 !== self.broken_slices.indexOf(section);
    };

    /**
     * Return the distance to the closest valid section number before the
     * given one. Or null if there is none.
     */
    self.validZDistanceBefore = function(section) {
      return self.validZDistanceByStep(section, -1);
    };

    /**
     * Return the distance to the closest valid section after the given one.
     * Or null if there is none.
     */
    self.validZDistanceAfter = function (section) {
      return self.validZDistanceByStep(section, 1);
    };

    /**
     * Return the distance to the closest valid section relative to the given
     * one in strided steps.
     */
    self.validZDistanceByStep = function (section, step) {
      var adj = section;
      while (true) {
        adj = adj + step;
        if (adj > self.MAX_Z || adj < 0) return null;
        if (!self.isSliceBroken(adj)) return adj - section;
      }
    };

    self.createTileSourceForMirror = function (mirrorIdx) {
      var mirror = self.mirrors[mirrorIdx];
      if (!mirror) {
        throw new CATMAID.ValueError("No mirror with index " + mirrorIdx + " available");
      }
      var selectedMirror = mirror;

      return CATMAID.getTileSource(
          selectedMirror.tile_source_type,
          selectedMirror.image_base,
          selectedMirror.file_extension,
          selectedMirror.tile_width,
          selectedMirror.tile_height);
    };
  }

  /**
   * Get all available stacks for a given project, optionally sorted by name.
   */
  Stack.list = function(projectId, sort) {
    var stacks = CATMAID.fetch(projectId + '/stacks');
    if (sort) {
      stacks = stacks.then(function(stacks) {
        return stacks.sort(function(a, b) {
          return CATMAID.tools.compareStrings(a.title, b.title);
        });
      });
    }

    return stacks;
  };

  CATMAID.Stack = Stack;

})(CATMAID);
