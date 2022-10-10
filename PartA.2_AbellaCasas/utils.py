import random

"""
def getRandList(a, b, size, excluded):
    def go(acc):
        if len(acc) == size:
            return acc
        else:
            r = random.randint(a, b)
            if r not in excluded:
                return go(acc.append(r))
            else:
                return go(acc)
    return go([])
"""

def getRandList(a, b, size, excluded=[]):
    """Returns a list of unique random elements from [a,b] of the given size."""
    xs = []
    while(len(xs) < size):
        r = random.randint(a, b)
        if r not in excluded:
            if r not in xs:
                xs.append(r)
    return xs

if __name__=="__main__":
    print(getRandList(1,50, 10))
    print(getRandList(1,50, 10, [1,2,3,4,5,6,7,8,9,10]))

graph = {'A': ['B', 'C', 'E'],
         'B': ['A','D', 'E'],
         'C': ['A', 'F', 'G'],
         'D': ['B'],
         'E': ['A', 'B','D'],
         'F': ['C'],
         'G': ['C']}

def bfs(graph, x0):
    """Breadth First Search

    graph has to be a dictionary of the form

    { A: [B,C]
    , B: [D]
    , C: [D]
    , D: [ ]
    }

    """
    visited = []
    queue = [x0]
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            neighbours = graph[node]
            for neighbour in neighbours:
                queue.append(neighbour)
    return visited
