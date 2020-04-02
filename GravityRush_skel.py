# Noesis Gravity Rush Remastered Bone Extractor

from inc_noesis import *
import noesis
import rapi
import os

debug = False

gr2_namehash = {}

def registerNoesisTypes():
    
    handle = noesis.register('Gravity Rush Remastered / 2 Skeleton', '.skel')
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    if debug:
        noesis.logPopup()  # please comment out when done.
    loadNameHashDict()
    return 1

gr2 = False

def noepyCheckType(data):
    file = NoeBitStream(data)
    if len(data) < 4:
        return 0
    header = file.readBytes(4).decode('ASCII').rstrip("\0")
    if  header == '20SE':
        return 1
    elif header == '60SE':
        gr2 = True
        return 1
    return 0
    
    
FNV1A_32_OFFSET = 0x811c9dc5
FNV1A_32_PRIME = 0x01000193

    
def fnv1a_32_str(string):
    # Set the offset basis
    hash = FNV1A_32_OFFSET

    # For each character
    for character in string:
        # Xor with the current character
        hash ^= ord(character)

        # Multiply by prime
        hash *= FNV1A_32_PRIME

        # Clamp
        hash &= 0xffffffff

    # Return the final hash as a number
    hash = hex(hash)[2:]
    if len(hash) == 7:
        hash = '0' + hash
    hash = hash[6:8]+hash[4:6]+hash[2:4]+hash[0:2]
    return hash

    
def loadNameHashDict():
    if not "gr_namehash" in globals():
        global gr_namehash
        gr_namehash = {}
        print(os.getcwd())
        count = 0
        for r, d, f in os.walk(os.getcwd()+'\GR_Hash_Dict'):
            for file in f:
                print("Scaning directory: %s" % file)
                if '.txt' in file:
                    txt = open(os.getcwd()+'\GR_Hash_Dict\\'+file, mode='r')
                    for line in txt:
                        line = line.split('\n')[0]
                        try:
                            gr_namehash[line.split('\t')[1]] = line.split('\t')[
                                0]
                            #print("Dictionary loaded: %s with name %s" % (line.split('\t')[1], line.split('\t')[0]))
                        except:
                            gr_namehash[line.split('\t')[0]] = fnv1a_32_str(
                                line.split('\t')[0])
                            print("Dictionary calculated: %s %s" % (
                                line.split('\t')[0], gr_namehash[line.split('\t')[0]]))
                        count += 1
        print("Dictionary loaded with %i strings" % count)
    else:
        print("Dictionary alread loaded")

def getNameFromHash(nameHash):
    nameHash = hex(nameHash)[2:]
    if len(nameHash) == 7:
        nameHash = '0' + nameHash
    nameHash = nameHash[6:8]+nameHash[4:6]+nameHash[2:4]+nameHash[0:2]
    try:
        return gr_namehash[nameHash]
    except:
        print("Can't find string of hash %s" % nameHash)
        return nameHash
    


# loading the bones!

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(0x10, NOESEEK_ABS)
    boneCount = bs.readUShort()
    bs.seek(0x18, NOESEEK_ABS)
    offsetToTransformInformation = bs.readUInt() + 0x18
    offsetToParentIndex = bs.readUInt() + 0x1C
    offsetToHashes = bs.readUInt() +  0x20
    print("Bone count: %i" % (boneCount))

    bs.seek(0x50, NOESEEK_ABS)

    boneRelations = []
    for boneIndex in range(0, int((offsetToTransformInformation - 0x50)/4)):
        boneRelation = [bs.readShort(),bs.readShort()]
        if boneIndex == 0 or boneRelation != boneRelations[-1]:
            boneRelations.append(boneRelation)
    

    bones = []
    for boneIndex in range(0, boneCount):
        # read name hash

        bs.seek(offsetToHashes + 4 * boneIndex, NOESEEK_ABS)
        boneName = getNameFromHash(bs.readUInt())
            
        # read parent bone index - I think this is wront in GR2 so comment it out for now

        
        bs.seek(offsetToParentIndex + 2 * boneIndex, NOESEEK_ABS)
        parentBoneIndex = bs.readUShort()
        

        # read bone data 

        bs.seek(offsetToTransformInformation + 48 * boneIndex, NOESEEK_ABS)
        rotation = NoeQuat.fromBytes(bs.readBytes(16))
        translation = NoeVec3.fromBytes(bs.readBytes(12))
        bs.seek(4, NOESEEK_REL)  
        scale = NoeVec3.fromBytes(bs.readBytes(12))
        
        boneMat = rotation.toMat43(transposed=1)
        boneMat[3] = translation
        '''
        boneMat[0][0] = scale[0]
        boneMat[1][1] = scale[1]
        boneMat[2][2] = scale[2]
        '''
        bones.append(NoeBone(boneIndex, boneName, boneMat, None, parentBoneIndex))

        
        if debug:
            print("Bone %i %s" % (boneIndex, boneName)) 
            #print("Parent Bone: %i" % (parentBoneIndex)) 
            print("Rotation: %f %f %f %f" % (rotation[0],rotation[1],rotation[2],rotation[3]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[0][0],bones[boneIndex].getMatrix()[0][1],bones[boneIndex].getMatrix()[0][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[1][0],bones[boneIndex].getMatrix()[1][1],bones[boneIndex].getMatrix()[1][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[2][0],bones[boneIndex].getMatrix()[2][1],bones[boneIndex].getMatrix()[2][2]))
            print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[3][0],bones[boneIndex].getMatrix()[3][1],bones[boneIndex].getMatrix()[3][2]))
            print()
            
    print("Bone globalization")
    for boneRelation in boneRelations:
        boneIndex = boneRelation[0]
        #globalLoaction = boneRelation[1] / 0x8000 > 0
        globalLoaction = False
        parrentBoneIndex = boneRelation[1] % 0x8000
        print("Bone %i X %i - %s > %s" % (boneIndex, parrentBoneIndex, bones[boneIndex].name, bones[parrentBoneIndex].name))
        if parrentBoneIndex != bones[boneIndex].parentIndex:
            print("Parrent Index mismatch %i %i" % (parrentBoneIndex, bones[boneIndex].parentIndex))
        if boneIndex >= 0 and boneIndex < boneCount and parrentBoneIndex >= 0 and parrentBoneIndex < boneCount:
            bones[boneIndex] = NoeBone(bones[boneIndex].index, bones[boneIndex].name, bones[boneIndex].getMatrix(), None, parrentBoneIndex) #Why is there isn't a NoeBone.setparrentIndex() :(
            if debug:
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[0][0],bones[boneIndex].getMatrix()[0][1],bones[boneIndex].getMatrix()[0][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[1][0],bones[boneIndex].getMatrix()[1][1],bones[boneIndex].getMatrix()[1][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[2][0],bones[boneIndex].getMatrix()[2][1],bones[boneIndex].getMatrix()[2][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[3][0],bones[boneIndex].getMatrix()[3][1],bones[boneIndex].getMatrix()[3][2]))
                print()
            if globalLoaction:
                print("Bone %i does not need to globalize" % boneIndex)
            else:
                bones[boneIndex].setMatrix(bones[boneIndex].getMatrix() * bones[ parrentBoneIndex].getMatrix())
            if debug:
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[0][0],bones[boneIndex].getMatrix()[0][1],bones[boneIndex].getMatrix()[0][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[1][0],bones[boneIndex].getMatrix()[1][1],bones[boneIndex].getMatrix()[1][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[2][0],bones[boneIndex].getMatrix()[2][1],bones[boneIndex].getMatrix()[2][2]))
                print("%f \t %f \t %f" % (bones[boneIndex].getMatrix()[3][0],bones[boneIndex].getMatrix()[3][1],bones[boneIndex].getMatrix()[3][2]))
                print()
    else:
            print("Error Bone globalization %i X %i" % (boneIndex, parrentBoneIndex))
    '''        
    print("Bone globalization")
    for i in range(0, boneCount):
        j = bones[i].parentIndex
        if j >= 0 and j < boneCount:
            if debug:
                print("Bone %i X %i  - %s > %s" % (i,j, bones[i].name, bones[j].name))
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
    else:
            print("Error Bone globalization %i X %i" % (i,j))
                
    '''
    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1

			