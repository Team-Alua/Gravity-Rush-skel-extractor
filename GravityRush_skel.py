# Noesis Gravity Rush Remastered Bone Extractor

from inc_noesis import *
import noesis
import rapi
import os
from GravityRush_common import *
from EdgeLib20 import *

debug = False


def registerNoesisTypes():

    handle = noesis.register('Gravity Rush 2 Skeleton', '.skel')
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    if debug:
        noesis.logPopup()  # please comment out when done.
    return 1


gr2 = False
global_scale = 1

def noepyCheckType(data):
    file = NoeBitStream(data)
    if len(data) < 4:
        return 0
    header = file.readBytes(4).decode('ASCII').rstrip("\0")
    if header == '20SE':
        return 0
    elif header == '60SE':
        gr2 = True
        return 1
    return 0

# loading the bones!


def noepyLoadModel(data, mdlList):
    pSkel = EdgeAnimationSkeleton(data)
    skeleton = ExtractSkeleton(pSkel)
    # printSkelLog(pSkel, skeleton)
    global noeSkeleton
    noeSkeleton = loadSkeleton(skeleton)

    mdl = NoeModel()
    mdl.setBones(noeSkeleton)
    mdlList.append(mdl)
    return 1


def loadSkeleton(skeleton):
    joints = []
    for jointIndex in range(skeleton.m_numJoints):
        jointName = getNameFromHash(skeleton.m_jointNameHashes[jointIndex])
        parentJointIndex = skeleton.m_parentIndices[jointIndex]
        rotation = NoeQuat(skeleton.m_basePose[jointIndex].m_rotation)
        translation = NoeVec3(skeleton.m_basePose[jointIndex].m_translation[:3]) * NoeVec3(
            [global_scale, global_scale, global_scale])
        scale = NoeVec3(skeleton.m_basePose[jointIndex].m_scale[:3])
        jointMat = rotation.toMat43(transposed=1)
        jointMat[3] = translation
        jointMat * - scale
        joints.append(NoeBone(jointIndex, jointName, jointMat, None, parentJointIndex))

    for joint in joints:
        joint.setMatrix(joint.getMatrix() *
                        joints[joint.parentIndex].getMatrix())

    return joints


def getSkel():
    global noeSkeleton
    print("This is from skel py")
    print(len(noeSkeleton))
    return noeSkeleton
