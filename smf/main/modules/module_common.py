

def GetWeightByPriority(priority):
    if priority == 'high':
        return 1
    if priority == 'medium':
        return 0.66
    if priority == 'low':
        return 0.33
    return 1

def GetCategoryLabel(letters):
    if letters == 'cc':
        return 'Common'
    elif letters == 'cd':
        return 'Courses'
    elif letters == 'cb':
        return 'Pychology'