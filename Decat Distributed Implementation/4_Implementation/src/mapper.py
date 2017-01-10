
def getCoordinator(id, coordIndexToCoordProcessMapper):
    index = hash(id) % len(coordIndexToCoordProcessMapper)
    return coordIndexToCoordProcessMapper[index]