"""
**Build FBX files**
"""
import argparse
import glob
import os
from pathlib import Path

import fbx
import FbxCommon

outputPathDefault = f"{os.path.dirname(os.path.realpath(__file__))}/../../output/OGrEE/fbx/"
defaultPicture = f"{os.path.dirname(os.path.realpath(__file__))}/white.png"

def makeCube(manager):

    cubeMesh = fbx.FbxMesh.Create(manager, "")
    # A set of vertices which we will use to create a cube in the scene.
    cubeVertices = [
        fbx.FbxVector4(-1, -1, 1),  # 0 - vertex index.
        fbx.FbxVector4(1, -1, 1),  # 1
        fbx.FbxVector4(1, 1, 1),  # 2
        fbx.FbxVector4(-1, 1, 1),  # 3
        fbx.FbxVector4(-1, -1, -1),  # 4
        fbx.FbxVector4(1, -1, -1),  # 5
        fbx.FbxVector4(1, 1, -1),  # 6
        fbx.FbxVector4(-1, 1, -1),  # 7
    ]
    # The polygons (faces) of the cube.
    polygonVertices = [
        (0, 1, 2, 3),  # Face 1 - composed of the vertex index sequence: 0, 1, 2, and 3.
        (4, 5, 6, 7),  # Face 2
        (8, 9, 10, 11),  # Face 3
        (12, 13, 14, 15),  # Face 4
        (16, 17, 18, 19),  # Face 5
        (20, 21, 22, 23),  # Face 6
    ]
    # Define the new mesh's control points. Since we are defining a cubic mesh,
    # there are 4 control points per face, and there are six faces, for a total
    # of 24 control points.
    cubeMesh.InitControlPoints(24)
    # Face 1
    cubeMesh.SetControlPointAt(cubeVertices[0], 0)
    cubeMesh.SetControlPointAt(cubeVertices[1], 1)
    cubeMesh.SetControlPointAt(cubeVertices[2], 2)
    cubeMesh.SetControlPointAt(cubeVertices[3], 3)
    # Face 2
    cubeMesh.SetControlPointAt(cubeVertices[1], 4)
    cubeMesh.SetControlPointAt(cubeVertices[5], 5)
    cubeMesh.SetControlPointAt(cubeVertices[6], 6)
    cubeMesh.SetControlPointAt(cubeVertices[2], 7)
    # Face 3
    cubeMesh.SetControlPointAt(cubeVertices[5], 8)
    cubeMesh.SetControlPointAt(cubeVertices[4], 9)
    cubeMesh.SetControlPointAt(cubeVertices[7], 10)
    cubeMesh.SetControlPointAt(cubeVertices[6], 11)
    # Face 4
    cubeMesh.SetControlPointAt(cubeVertices[4], 12)
    cubeMesh.SetControlPointAt(cubeVertices[0], 13)
    cubeMesh.SetControlPointAt(cubeVertices[3], 14)
    cubeMesh.SetControlPointAt(cubeVertices[7], 15)
    # Face 5
    cubeMesh.SetControlPointAt(cubeVertices[3], 16)
    cubeMesh.SetControlPointAt(cubeVertices[2], 17)
    cubeMesh.SetControlPointAt(cubeVertices[6], 18)
    cubeMesh.SetControlPointAt(cubeVertices[7], 19)
    # Face 6
    cubeMesh.SetControlPointAt(cubeVertices[1], 20)
    cubeMesh.SetControlPointAt(cubeVertices[0], 21)
    cubeMesh.SetControlPointAt(cubeVertices[4], 22)
    cubeMesh.SetControlPointAt(cubeVertices[5], 23)

    layer = cubeMesh.GetLayer(0)
    if not layer:
        cubeMesh.CreateLayer()
        layer = cubeMesh.GetLayer(0)

    # Each polygon face will be assigned a unique material.
    matLayer = fbx.FbxLayerElementMaterial.Create(cubeMesh, "")
    matLayer.SetMappingMode(fbx.FbxLayerElement.eByPolygon)
    matLayer.SetReferenceMode(fbx.FbxLayerElement.eIndexToDirect)
    layer.SetMaterials(matLayer)

    # Create UV for Diffuse channel.
    UVDiffuseLayer = fbx.FbxLayerElementUV.Create(cubeMesh, "DiffuseUV")

    # Now we have set the UVs as eINDEX_TO_DIRECT reference
    # and in eBY_POLYGON_VERTEX mapping mode.
    UVDiffuseLayer.SetMappingMode(fbx.FbxLayerElement.eByPolygonVertex)
    UVDiffuseLayer.SetReferenceMode(fbx.FbxLayerElement.eIndexToDirect)
    vectors0 = fbx.FbxVector2(0, 0)
    vectors1 = fbx.FbxVector2(1, 0)
    vectors2 = fbx.FbxVector2(1, 1)
    vectors3 = fbx.FbxVector2(0, 1)

    UVDiffuseLayer.GetDirectArray().Add(vectors0)
    UVDiffuseLayer.GetDirectArray().Add(vectors1)
    UVDiffuseLayer.GetDirectArray().Add(vectors2)
    UVDiffuseLayer.GetDirectArray().Add(vectors3)

    # We must update the size of the index array.
    UVDiffuseLayer.GetIndexArray().SetCount(24)

    layer.SetUVs(UVDiffuseLayer, fbx.FbxLayerElement.eTextureDiffuse)

    # Now that the control points per polygon have been defined, we can create
    # the actual polygons within the mesh.
    for i in range(0, len(polygonVertices)):
        cubeMesh.BeginPolygon(i)
        for j in range(len(polygonVertices[i])):
            cubeMesh.AddPolygon(polygonVertices[i][j])
            UVDiffuseLayer.GetIndexArray().SetAt(i * 4 + j, j)
        cubeMesh.EndPolygon()

    normalXPos = fbx.FbxVector4(1, 0, 0, 1)
    normalXNeg = fbx.FbxVector4(-1, 0, 0, 1)
    normalYPos = fbx.FbxVector4(0, 1, 0, 1)
    normalYNeg = fbx.FbxVector4(0, -1, 0, 1)
    normalZPos = fbx.FbxVector4(0, 0, 1, 1)
    normalZNeg = fbx.FbxVector4(0, 0, -1, 1)

    normLayer = fbx.FbxLayerElementNormal.Create(cubeMesh, "")
    normLayer.SetMappingMode(fbx.FbxLayerElement.eByControlPoint)
    normLayer.SetReferenceMode(fbx.FbxLayerElement.eDirect)

    normLayer.GetDirectArray().Add(normalZPos)
    normLayer.GetDirectArray().Add(normalZPos)
    normLayer.GetDirectArray().Add(normalZPos)
    normLayer.GetDirectArray().Add(normalZPos)

    normLayer.GetDirectArray().Add(normalXPos)
    normLayer.GetDirectArray().Add(normalXPos)
    normLayer.GetDirectArray().Add(normalXPos)
    normLayer.GetDirectArray().Add(normalXPos)

    normLayer.GetDirectArray().Add(normalZNeg)
    normLayer.GetDirectArray().Add(normalZNeg)
    normLayer.GetDirectArray().Add(normalZNeg)
    normLayer.GetDirectArray().Add(normalZNeg)

    normLayer.GetDirectArray().Add(normalXNeg)
    normLayer.GetDirectArray().Add(normalXNeg)
    normLayer.GetDirectArray().Add(normalXNeg)
    normLayer.GetDirectArray().Add(normalXNeg)

    normLayer.GetDirectArray().Add(normalYPos)
    normLayer.GetDirectArray().Add(normalYPos)
    normLayer.GetDirectArray().Add(normalYPos)
    normLayer.GetDirectArray().Add(normalYPos)

    normLayer.GetDirectArray().Add(normalYNeg)
    normLayer.GetDirectArray().Add(normalYNeg)
    normLayer.GetDirectArray().Add(normalYNeg)
    normLayer.GetDirectArray().Add(normalYNeg)

    layer.SetNormals(normLayer)

    return cubeMesh


def addCube(manager,pScene, cubeName, cubeScale: tuple[float, float, float] = [1, 1, 1]):
    """Adds a cubic mesh to the scene."""
    # Create a new mesh node attribute in the scene, and set it as the new node's attribute
    newMesh = makeCube(manager)
    # create the node containing the mesh
    newNode = fbx.FbxNode.Create(manager, cubeName)
    newNode.SetNodeAttribute(newMesh)
    newNode.SetShadingMode(fbx.FbxNode.eTextureShading)
    newNode.LclScaling.Set(fbx.FbxDouble3(cubeScale[0], cubeScale[1], cubeScale[2]))
    newNode.LclTranslation.Set(fbx.FbxDouble3(0,0,0))
    
    rootNode = pScene.GetRootNode()
    rootNode.AddChild(newNode)
    return newMesh


def CreateTexture(manager, pFilename):
    lTexture = fbx.FbxFileTexture.Create(manager,"")
    lTexture.SetFileName(pFilename)
    lTexture.SetTextureUse(fbx.FbxTexture.eStandard)
    lTexture.SetMappingType(fbx.FbxTexture.eUV)
    lTexture.SetMaterialUse(fbx.FbxFileTexture.eModelMaterial)
    lTexture.SetSwapUV(False)
    lTexture.SetTranslation(0.0, 0.0)
    lTexture.SetScale(1.0, 1.0)
    lTexture.SetRotation(0.0, 0.0)
    return lTexture


def CreateMaterial(manager, name, texturePath):
    texture = CreateTexture(manager,texturePath)
    material = fbx.FbxSurfacePhong.Create(manager, name)
    material.Emissive.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
    material.Diffuse.Set(fbx.FbxDouble3(1.0, 1.0, 1.0))
    material.Ambient.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
    material.Specular.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
    material.TransparencyFactor.Set(0.0)
    material.Shininess.Set(0.1)
    material.ShadingModel.Set(fbx.FbxString("phong"))
    material.Diffuse.ConnectSrcObject(texture)
    return material


def saveScene(pFilename, pFbxManager, pFbxScene):
    """Save the scene using the Python FBX API"""
    exporter = fbx.FbxExporter.Create(pFbxManager, "")

    isInitialized = exporter.Initialize(pFilename)
    if isInitialized == False:
        raise Exception(
            "Exporter failed to initialize. Error returned: "
            + str(exporter.GetLastErrorString())
        )

    exporter.Export(pFbxScene)

    exporter.Destroy()

def CreateFBX(
    width: float,
    height: float,
    depth: float,
    name: str,
    front: str = "",
    back: str = "",
    left: str = "",
    right: str = "",
    top: str = "",
    bottom: str = "",
    outputPath=outputPathDefault,
) -> str:
    """
    Build an FBX file containing a box mesh with up to six textured faces

    :param float width: The width of the model
    :param float height: The height of the model
    :param float depth: The depth of the model
    :param str name: the name given to the FBX file
    :param str front: the path to the picture of the front face
    :param str back: the path to the picture of the back face
    :param str left: the path to the picture of the left face
    :param str right: the path to the picture of the right face
    :param str top: the path to the picture of the top face
    :param str bottom: the path to the picture of the bottom face
    :return: return the path to the newly created FBX file
    :rtype: str
    """

    front = defaultPicture if front == "" else front
    back = defaultPicture if back == "" else back
    left = defaultPicture if left == "" else left
    right = defaultPicture if right == "" else right
    top = defaultPicture if top == "" else top
    bottom = defaultPicture if bottom == "" else bottom


    manager,scene = FbxCommon.InitializeSdkObjects()
    cubeMesh = addCube(manager,scene, "cube", cubeScale=[width/2, height/2, depth/2])
    cubeNode = cubeMesh.GetNode()

    cubeNode.AddMaterial(CreateMaterial(manager,"",front))
    cubeNode.AddMaterial(CreateMaterial(manager,"",right))
    cubeNode.AddMaterial(CreateMaterial(manager,"",back))
    cubeNode.AddMaterial(CreateMaterial(manager,"",left))
    cubeNode.AddMaterial(CreateMaterial(manager,"",top))
    cubeNode.AddMaterial(CreateMaterial(manager,"",bottom))

    FbxCommon.SaveScene(manager, scene, outputPath + name + ".fbx", pEmbedMedia=True)

    return outputPath + name + ".fbx"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a FBX file containing a box mesh from its dimension and up to six faces"
    )
    parser.add_argument(
        "--WDH",
        help="""width,depth,height (cm)""",
        required=True,
    )
    parser.add_argument("--name", help="""name of the fbx""", default="FBXmodel")
    parser.add_argument("--front", help="""path to the front picture""", default="")
    parser.add_argument("--back", help="""path to the back picture""", default="")
    parser.add_argument("--left", help="""path to the left picture""", default="")
    parser.add_argument("--right", help="""path to the right picture""", default="")
    parser.add_argument("--top", help="""path to the top picture""", default="")
    parser.add_argument("--bottom", help="""path to the bottom picture""", default="")
    parser.add_argument(
        "--picFolder",
        help="""path to a folder containing pictures ending in -front,-back,...""",
    )
    parser.add_argument("-o", help="""output path""",default=outputPathDefault)

    args = vars(parser.parse_args())
    wdh = [float(s) for s in args["WDH"].split(",")]
    if "picFolder" in args.keys() and args["picFolder"] is not None:
        textures = sum(
            [
                glob.glob(args["picFolder"] + "/" + x)
                for x in ("*.png", "*.jpg", "*.jpeg")
            ],
            [],
        )
        for file in textures:
            if "front" in Path(file).stem:
                args["front"] = file
            elif "back" in Path(file).stem or "rear" in Path(file).stem:
                args["back"] = file
            elif "left" in Path(file).stem:
                args["left"] = file
            elif "top" in Path(file).stem:
                args["top"] = file
            elif "bottom" in Path(file).stem:
                args["bottom"] = file
            elif "right" in Path(file).stem:
                args["right"] = file
    CreateFBX(
        name=args["name"],
        width=wdh[0],
        depth=wdh[1],
        height=wdh[2],
        front=args["front"],
        back=args["back"],
        left=args["left"],
        right=args["right"],
        top=args["top"],
        bottom=args["bottom"],
        outputPath=args["o"],
    )
