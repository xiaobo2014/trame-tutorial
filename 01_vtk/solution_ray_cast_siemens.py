#!/usr/bin/env python

# Web imports
import os
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

# -----------------------------------------------------------------------------
# Example:    SimpleRayCast
# taken from: https://kitware.github.io/vtk-examples/site/Python/
# -----------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty,
)
from vtkmodules.vtkRenderingVolume import vtkFixedPointVolumeRayCastMapper
from vtkmodules.vtkRenderingVolume import vtkGPUVolumeRayCastMapper

# noinspection PyUnresolvedReferences
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLRayCastImageDisplayHelper


CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

colors = vtkNamedColors()

# This is a simple volume rendering example that
# uses a vtkFixedPointVolumeRayCastMapper

# Create the standard renderer, render window
# and interactor.
ren1 = vtkRenderer()

renWin = vtkRenderWindow()
renWin.AddRenderer(ren1)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()  # +++

# Create the reader for the data.
# reader = vtkStructuredPointsReader()
# reader.SetFileName(os.path.join(CURRENT_DIRECTORY, "../data/ironProt.vtk"))
reader = vtkXMLImageDataReader()
reader.SetFileName(os.path.join(CURRENT_DIRECTORY, "../data/vr.vti"))


# The property describes how the data will look.
volumeProperty = vtkVolumeProperty()
volumeProperty.SetIndependentComponents(1)
volumeProperty.SetInterpolationType(1)
volumeProperty.SetUseClippedVoxelIntensity(1)
volumeProperty.SetClippedVoxelIntensity(-10000000000)

# Create transfer mapping scalar value to color.
colorFun = vtkColorTransferFunction()
colorFun.AddRGBPoint( 25, 0.753, 0.086, 0.086)
colorFun.AddRGBPoint( 184, 1, 1, 0.776)
colorFun.AddRGBPoint( 323, 1, 0.941, 0.824)
colorFun.AddRGBPoint( 481, 1, 0.902, 0.718)
colorFun.AddRGBPoint( 650, 1, 0.961, 0.925)
volumeProperty.SetColor(colorFun)

# Create transfer mapping scalar value to opacity.
opacityFun = vtkPiecewiseFunction()
opacityFun.AddPoint(10, 0)
opacityFun.AddPoint(323, 0.92)
opacityFun.AddPoint(650, 1)
volumeProperty.SetScalarOpacity(opacityFun)


gradientFun = vtkPiecewiseFunction()
gradientFun.AddPoint(0, 0.5)
gradientFun.AddPoint(50, 0.1)
gradientFun.AddPoint(100, 0.3)
gradientFun.AddPoint(200, 0.15)
gradientFun.AddPoint(300, 0.3)
gradientFun.AddPoint(400, 0.65)
gradientFun.AddPoint(500, 0.8)
volumeProperty.SetGradientOpacity(gradientFun)


# scalar opacity unit distance
volumeProperty.SetScalarOpacityUnitDistance(0.05)


diffuseFactor = 1.0
volumeProperty.ShadeOn()
volumeProperty.SetAmbient (0.20 * diffuseFactor)
volumeProperty.SetDiffuse (0.90 * diffuseFactor)
volumeProperty.SetSpecular(0.30 * diffuseFactor)
volumeProperty.SetSpecularPower(15.0 * diffuseFactor)

volumeProperty.SetInterpolationTypeToLinear()


# The mapper / ray cast function know how to render the data.
# volumeMapper = vtkFixedPointVolumeRayCastMapper()
volumeMapper = vtkGPUVolumeRayCastMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())
volumeMapper.SetSampleDistance(1)
volumeMapper.SetImageSampleDistance(1)
volumeMapper.SetUseJittering(1)
volumeMapper.SetBlendModeToComposite()

# The volume holds the mapper and the property and
# can be used to position/orient the volume.
volume = vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

ren1.AddVolume(volume)
ren1.SetBackground(colors.GetColor3d("Wheat"))
ren1.GetActiveCamera().Azimuth(45)
ren1.GetActiveCamera().Elevation(30)
ren1.ResetCameraClippingRange()
ren1.ResetCamera()

# -----------------------------------------------------------------------------
# Web Application setup
# -----------------------------------------------------------------------------

server = get_server()
ctrl = server.controller

with SinglePageLayout(server) as layout:
    layout.title.set_text("Hello trame")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk.VtkRemoteView(renWin)
            # view = vtk.VtkLocalView(renWin)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
