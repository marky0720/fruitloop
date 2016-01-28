from __future__ import absolute_import

import warnings
import pyglet.gl as gl

from . import mixins, Camera


class Scene(object):

    def __init__(self, meshes=[], camera=None, light=None, bgColor=(0., 0., 0., 1.)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)
        if len(set(mesh.data.name for mesh in self.meshes)) != len(self.meshes):
            warnings.warn('Warning: Mesh.data.names not all unique--log data will overwrite some meshes!')
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = mixins.Physical() if not light else light
        self.bgColor = mixins.Color(*bgColor)

    def update_matrices(self):
        """calls the "update_matrices" method on all meshes and camera, so that all data is current."""
        for obj in self.meshes + [self.camera]:
            obj.update_matrices()

    def draw(self, dest, shader=None, userdata={}):
        """Draw each visible mesh in the scene."""

        # Enable 3D OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # Clear and Refresh Screen
        gl.glClearColor(*self.bgColor.rgba)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Bind Shader
        shader.bind()

        # Send Uniforms that are constant across meshes.
        shader.uniform_matrixf('view_matrix', self.camera.view_matrix.T.ravel())
        shader.uniform_matrixf('projection_matrix', self.camera.projection_matrix)

        if self.shadow_rendering:
            shader.uniform_matrixf('shadow_projection_matrix', self.shadow_cam.projection_matrix.T.ravel())
            shader.uniform_matrixf('shadow_view_matrix', scene.light.view_matrix.T.ravel())

        shader.uniformf('light_position', *scene.light.position)
        shader.uniformf('camera_position', *scene.camera.position)

        shader.uniformi('hasShadow', int(self.shadow_rendering))
        shadow_slot = self.fbos['shadow'].texture_slot if scene == self.active_scene else self.fbos['vrshadow'].texture_slot
        shader.uniformi('ShadowMap', shadow_slot)
        shader.uniformi('grayscale', int(self.grayscale)

        for mesh in self.meshes:
            mesh._draw(dest=dest, shader=shader)

        # Unbind Shader
        shader.unbind()