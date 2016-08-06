# conceptnet-lightweight
Provides easy, lightweight lookup for english-only assertions from ConceptNet5.
## Example
```python
from conceptnet import ConceptNet

cn = ConceptNet()
for concept in cn.related('UsedFor', cn.concept('tool')):
    print('A tool is used for', cn.string(concept))
```
## Time and Memory
* Lookup is at O(log n) using binary search.
* Memory usage is at 700MB on a Windows x64 machine.
