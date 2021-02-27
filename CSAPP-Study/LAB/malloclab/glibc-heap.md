# glibc-heap学习

## free-chunk结构

chunk使用中
```
|----------------------|
|           pre_size   |
|----------------------|
|      chunk_size|a|m|p|    -->   chunk_size|a|m|p 
|----------------------|          a:来自主分配区还是非主分配区
|                      |          m:标记内存存在mmap段(1)还是heap段(0
|                      |          p:标记上一个chunk是否处于使用状态
|      User data       |          
|                      |
|----------------------|
```

free_chunk
```
|----------------------|
|       pre_size       |
|----------------------|
|      chunk_size|a|m|p|
|----------------------|
|          fd          |  fd: Forword pointer to next chunk in list
|----------------------|
|          bk          |  bk: back pointer to pre_chunk in list
|----------------------|
| (large bin) fd       |
| (large bin) bk       |
|                      |
|----------------------|
```

chunk 空间复用：chunk在使用中，下一个chunk的p = 1，且pre_size无效，可复用pre_size空间。

## fast bin分配

### free

  1. 判断next_chunk的size范围
  2. 检查Lock
  3. 覆盖data段内容（如果设置了perturb_byte）
  4. 获取对应的fast bin头节点
  5. 检测头节点是否与next_free一致(判断double free，中间插入chunk绕过)
  6. 头插法插入new_free
  7. head = new_free [LIFO]

### malloc

1. 获得fast bin下对应索引
2. 如果单线程直接更改头结果(head被取走，LIFO)
3. (这里使用TCACHE有一段额外操作)判断取出的chunk大小是否应该是对应的malloc的大小
4. 返回取出的chunk
   
## small bin分配

### malloc
1. 判断size in samll bin
2. 获取size对应的头节点
3. 若该链非空，则将末尾链分配出来[bin->bk]（small bin是双向链表）
4. 检测主分区是否设置为M

## unsorted bin && large bin（从fastbin smallbin中申请失败）

### malloc
1. 获取large bin index，同时检查是否存在fast bin，若存在fast bin，则调用malloc_consolidate释放fast bin
2. 反向遍历unsorted bin
3. 如果unsorted_bin中只有一个chunk且为last_remainder且size足够，则对last_remainder进行分割，分割后的剩余chunk作为新的last_remainder放入unsorted bin，并根据大小判断是否设置next size，返回切割出的chunk

**3 和 4为两个分支**

4. 检查victim->bk->fd == victim
5. 将victim从unsorted bin中脱链(unlink)
6. 如果victim大小刚好满足nb，直接分配出去。
   
**对unsorted bin进行清理**

7. 如果为small_bin_size，则用头插法加入对应的链并在bin_map标记
8. 如果为large_bin_size，且size比链中最小的还小，则放到尾部，否则循环查找，找到第一个小于size的子链头（因为是从大到小排序，所以可以得到需要加入的链）。今一步判断，若与子链头相等，则插在子链的第二个位置，若不等，则作为子链的头加入子链，然后插入到fwd的前一个(size > fwd->size)
   
**至此，unsorted bin被清理结束**

9. 如果申请的是large bin，在对应的large bin idx下找到第一个大于nb的size链，如果该size不唯一，取第二个进行分割，否则直接unlink使用。分割后，若剩余的remainder太小，直接set inuse，否则加入unsorted bin。
10. 若还没找到，获取下一个idx的头节点，获取bin map快速检查
11. 遍历查bin map，如果实在找不到，跳入use top chunk
12. 如果找到了，首先检查bin map对应的bin链是否为空，为空说明bin map出错，修改后继续遍历，若不为空，则进行9中一样的切割操作。
13. 如果找不到，山穷水尽了，用top chunk。首先检查size > av->system_mem，即检查top chunk空间是否足够，若够，则切割top chunk。
14. 如果还是没有解决问题，则再次检查fast bin（看看其他线程会不会放出来有用的chunk），循环至第3步。
15. 实在不行，就sysmalloc()了。

## fast bin后的统一free过程

1. 检查是否为mmap，是则直接munmap
2. 获取next chunk，检查是否与top chunk相邻
3. 检查new_free的in use状态，防double free
4. 检查next chunk大小是否异常
5. 覆盖new_free data段
6. 检查pre_chunk状态，进行合并，若pre_chunk->size与new_free->pre_size不冲突，unlink pre_chunk
7. 检查next_chunk是否与top chunk相邻，不是切空闲则合并，并unlink next_chunk，合并后的chunk头插加入unsored bin
8. 如果与top chunk相邻，直接合并加入top chunk
9. 检查合并后size是否查过阈值，若超出且存在fast bin，则malloc_consolidate收缩阈值。

## realloc

1. 检查chunksize是否正常
2. 检查old chunk是否为mmap
3. 获取next_chunk与next_chunk_size
4. 获取old size >= nb：new chunk = old chunk
5. 检查next_chunk是否为top chunk&&os + ns >= nb + minsize，通过则直接切割top chunk，结果直接返回。
6. next chunk不是top chunk且old size + new size >= nb，则newp = oldp, unlink next_chunk
7. 以上均不满足，直接调malloc，并进一步检测malloc出的p是否等于next_chunk，如果是的话，将old chunk与new chunk合并[同6少一步unlink]，进入下一步，否则直接返回malloc结果并free old chunk。
8. 同remainder一样进行切割，剩余部分free。

## unlink函数

将chunk从链中脱去。

1. 首先通过检查p->size == p->nextchunk->pre_size，判断chunk是否合法
2. 获取fd、bk，同时判断fd->bk、 bk->fd == p
3. 双向链表操作删除p节点
   
**small bin到此已结束**

4. p->fd_nextsize != NULL 说明是large bin中某size链的第一个
5. 检查p->fd_nextsize->bk_nextsize == p和p->bk_nextsize->fd_nextsize == p，防止double free。
6. 检查fd->fd_nextsize[判断fd是否为size头，也就是判断p所在的size链是否只有p]
7. 检查size链是否只有p_size，是的话fd的上下size全设为fd
8. 否则在size链中也进行双向链表操作删除节点。
   
## malloc_consolidate:

遍历fast bin进行free操作[free过程2~8]

## tcache机制

### 概述

结构与fast bin类似，根据chunk大小将chunk放入bins数组，bins有64项，max_size为0x400，每条链上最多7个chunk

tcache_bin->chunk-fd->chunk-fd->fd[链接部分与fastbin不同，不是链的chunk地址，而是链的fd(data)地址]

启用tcache时，优先使用tcache

### _int_free中

1. 检查p是否已在tcache中(p->key == tcache)
2. 如果不在，检查链中数量，不满则加
**2.29后加入，此前只验idx和是否满**
3. 如果出问题：LIBC_PROBE，遍历tcache，改到链中的p，报错

## _int_malloc中：

1. 如果fast_bin被取走一个，剩余的链上chunk将被放入tcache(不检查，可利用？)
2. small_bin与fast bin一样
3. unsorted bin中，本应分配出去的chunk将被放入tcache中，其他则正常被放入bin中，在遍历过程中，如果有被放入tcache的且unsorted bin中被处理的量大于limit[默认为无]则从tcache中取，unsorted bin处理完了还不行（指未达到limit），则若有放入tcache的，拿出使用