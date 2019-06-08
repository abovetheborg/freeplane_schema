Structure 1
```
A
+-- B
    +-- C
```
Structure 2
```
A
+-- B
+-- D
```

# Algorithm
1. Create list_1 with root of Structure 1 as the only element
1. Create list_2 with root of Structure 2 as the only element
1. While len(list_1)>0
    1. Pop list_1 -> node1
    1. Append children of node1 to list_1
    1. Add node1 to the 'treated_node' list
    1. Look for node1 in Structure 2
    1. If node1 is in structure 2, check if it is identical
        1. If not identical, add to 'modified_node' list
    1. If no in structure 2, add to 'in_structure1_only' list
1. Loop

1. While len(list_2)>0
    1. Pop list_2 -> node2
    1. Append children of node2 to list_2
    1. Check if node is in 'treated_node' list
        1. If in list exit iteration
    1. Look for node2 in Structure 1
    1. If node2 is in structure 1, check if it is identical
        1. If not identical, add to 'modified_node' (We should hit that part of the algorithm)
    1. If not in structure 1, add to 'in_structure2_only' list
1. Loop
    

# Node equality
- Same TEXT value
- Same ID
- Same CREATED value
- Same MODIFIED value
- Same number of children ?