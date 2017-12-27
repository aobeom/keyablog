## Introduction
Get [keyakizaka46]((http://www.keyakizaka46.com/s/k46o/diary/member?ima=0000)) Blogs.

Three Types of URL / 三种类型的链接:
+ [页数page](http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=20)
+ [篇数single](http://www.keyakizaka46.com/s/k46o/diary/detail/12487?ima=0000&cd=member)
+ [首页profile](http://www.keyakizaka46.com/s/k46o/artist/20?ima=0000)

URL RULES / 链接规则:
+ [页数page] diary/member/list?ima=0000&ct=**MemberCode**
+ [单篇single] diary/detail/**Number**?ima=0000&cd=member
+ [简介profile] artist/**MemberCode**?ima=0000

## Usage
```python
usage: keyablog [-h] [-p PAGERANGE | -s SINGLERANGE] -u URL

Keyakizaka46 Blog Download.

optional arguments:
  -p PAGERANGE    Download some blogs by page [0, 1-2, 3, 4-6 ...]
  -s SINGLERANGE  Download some blogs by single [1, +5, -3 ...]
  -u URL          Blog url

Example 1 - all blogs
python keyablog.py -u "http://www.keyakizaka46.com/s/k46o/artist/20?ima=0000" -p 0

Example 2 - Page 4
python keyablog.py -u "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=20" -p 4

Example 3 - Page 2 to Page 5
python keyablog.py -u "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=20" -p 2-5

Example 4 - The last 3 blogs
python keyablog.py -u "http://www.keyakizaka46.com/s/k46o/diary/detail/12487?ima=0000&cd=member" -s -2

Example 5 - Last blog
python keyablog.py -u "http://www.keyakizaka46.com/s/k46o/diary/detail/12487?ima=0000&cd=member" -s 1
```