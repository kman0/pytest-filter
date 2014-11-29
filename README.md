pytest-filter
=============

Simple exclusions for py.test based on .pytest-filter files

Note: The files are filtered after the collection of tests is complete.

The exclusion/inclusion of tests is based on node ids.


### Sections in .ini file *(in order of execution)*
1. exclude-prefix *(Only prefix is matched)*
    - Tests' node id with matching prefixes are be de-selected from execution
2. exclude-mark *(Entire mark is matched)*
    - Tests that contain the mark are de-selected 
3. exclude-node *(Entire node id is matched)*
    - Tests' node id with matching node id is de-selected from execution. 
3. include-prefix *(Only prefix is matched)*
    - Any collected tests' node id that match one of the prefixes will be re-selected for execution
5. include-mark *(Entire mark is matched)*
    - Tests that contain the mark are re-selected 
6. include-node *(Entire node id is matched)*
    - Tests are re-selected for execution(must be excluded by one of the exclude section)
6. skip-node *(Entire node id is matched)*
    - Matching tests are skipped

.pytest-filter.ini contents
---------------------------
```
[exclude-prefix]

[exclude-mark]

[exclude-node]

[include-prefix]

[include-mark]

[include-node]

[skip-node]

```