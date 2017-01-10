# this is used throughout the program to get the right coordinator
# for a particular subject or resource by their id

def getCoordinator(id, coordIndexToCoordProcessMapper):
    index = hash(id)%len(coordIndexToCoordProcessMapper)
    return coordIndexToCoordProcessMapper[index]