# Noesis Gravity Rush Remastered Bone Extractor

from inc_noesis import *
import noesis
import rapi

debug = False

def registerNoesisTypes():
    handle = noesis.register('Gravity Rush Remastered Skeleton', '.skel'
                             )
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    if debug:
        noesis.logPopup()  # please comment out when done.
    return 1


def noepyCheckType(data):
    file = NoeBitStream(data)
    if len(data) < 4:
        return 0
    if file.readBytes(4).decode('ASCII').rstrip("\0") != '20SE':
        return 0
    return 1


# loading the bones!

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(0x10, NOESEEK_ABS)
    boneCount = bs.readUShort()
    bs.seek(0x18, NOESEEK_ABS)
    relativeOffsetToTransformInformation = bs.readUInt() + 0x18
    relativeOffsetToParentIndex = bs.readUInt() + 0x1C
    relativeOffsetToHashes = bs.readUInt() +  0x20
    print("Bone count: %i" % (boneCount))

    bones = []
    for boneIndex in range(0, boneCount):

        # read name hash

        bs.seek(relativeOffsetToHashes + 4 * boneIndex, NOESEEK_ABS)
        boneHash = bs.readUInt()

        # read parent bone index

        bs.seek(relativeOffsetToParentIndex + 2 * boneIndex,
                NOESEEK_ABS)
        parentBoneIndex = bs.readUShort()

        # read bone data

        bs.seek(relativeOffsetToTransformInformation + 48 * boneIndex, NOESEEK_ABS)
        rotation = NoeQuat.fromBytes(bs.readBytes(16))
        translation = NoeVec3.fromBytes(bs.readBytes(12))
        bs.seek(4, NOESEEK_REL)  
        scale = NoeVec3.fromBytes(bs.readBytes(12))
        
        boneMat = rotation.toMat43(transposed=1)
        boneMat[3] = translation
        bones.append(NoeBone(boneIndex, “Bone%i" % (boneIndex), boneMat, None, parentBoneIndex))
        
        if debug:
            print("Bone %i %s" % (boneIndex, hex(boneHash))) 
            print("Parent Bone: %i" % (parentBoneIndex)) 
            print("Rotation: %f %f %f %f" % (rotation[0],rotation[1],rotation[2],rotation[3]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[0][0],bones[boneIndex].getMatrix()[0][1],bones[boneIndex].getMatrix()[0][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[1][0],bones[boneIndex].getMatrix()[1][1],bones[boneIndex].getMatrix()[1][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[2][0],bones[boneIndex].getMatrix()[2][1],bones[boneIndex].getMatrix()[2][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[3][0],bones[boneIndex].getMatrix()[3][1],bones[boneIndex].getMatrix()[3][2]))
            print()
            
    print("Bone globalization")
    for i in range(0, boneCount):
        j = bones[i].parentIndex
        if j != 65535: # 65535 = -1
            if debug:
                print("Bone %i X %i" % (i,j))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[0][0],bones[i].getMatrix()[0][1],bones[i].getMatrix()[0][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[1][0],bones[i].getMatrix()[1][1],bones[i].getMatrix()[1][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[2][0],bones[i].getMatrix()[2][1],bones[i].getMatrix()[2][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[3][0],bones[i].getMatrix()[3][1],bones[i].getMatrix()[3][2]))
                print()
            bones[i].setMatrix(bones[i].getMatrix() * bones[j].getMatrix())
            if debug:
                print("%f \t %f \t %f" % (bones[i].getMatrix()[0][0],bones[i].getMatrix()[0][1],bones[i].getMatrix()[0][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[1][0],bones[i].getMatrix()[1][1],bones[i].getMatrix()[1][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[2][0],bones[i].getMatrix()[2][1],bones[i].getMatrix()[2][2]))
                print("%f \t %f \t %f" % (bones[i].getMatrix()[3][0],bones[i].getMatrix()[3][1],bones[i].getMatrix()[3][2]))
                print()
                

    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1

			