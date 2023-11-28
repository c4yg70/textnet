# hashAddr：上一次哈希地址
#ch：三个字节中的第三个字节
# pos：三个字节中的第一个字节在窗口中的下标
#matchHead：如果匹配，保存匹配串的起始位置
void HashTable::InsertString(ush& hashAddr, uch ch, ush pos, ush& macthHead)
{
	HashFunc(hashAddr, ch);
	# 1.将hassAddr位置存储的前文中的匹配搬移到prev的pos位置
	_prev[pos & HASH_MASK] = _head[hashAddr];
	# 2.将前文中找到匹配的最近一个通过macthHead带出去
	macthHead = _head[hashAddr];
	# 3.将本次要插入的三个字节的首字节插入到head的headAddr位置
	_head[hashAddr] = pos;
}

ush Lz77::LongestMatch(ush matchHead, ush &matchDis,ush start)
{
	ush curMatchDis = 0;
	ush curMatchLength = 0;
	ush bestLen = 0;
	# 当使用掩码将start越界位置的值向_prev中搬移的时候有可能会覆盖之前_prev位置的值，如果之前该位置保存的下表为0
	# 则有可能会造成死循环，所以我们在这里需要控制查找的次数
	uch maxMatchCount = 255;

	# 往左侧找的时候不能找的太远
	ush limit = start >= MAX_DIS ? start - MAX_DIS : 0;
	do
	{
		uch* pstart = _pWin + start;
		uch* pend = pstart + MAX_MATCH;# 限制匹配字符串的长度
		uch* pbegin = _pWin + matchHead;

		curMatchDis = 0;
		curMatchLength = 0;

		while (pstart < pend && *pstart == *pbegin)
		{
			pstart++;
			pbegin++;
			curMatchLength++;
		}

		curMatchDis = start - matchHead;

		if (curMatchLength > bestLen)
		{
			bestLen = curMatchLength;
			matchDis = curMatchDis;
		}

	} while ((_ht.GetPrevMatch(matchHead) < limit) && maxMatchCount--);

	if (curMatchDis > MAX_DIS)
	{
		bestLen = 0;
	}

	return bestLen;
}

void Lz77::FillWindow(FILE* fIn, ull& lookahead, ush& start)
{
	if (start >= WSIZE + MAX_DIS)
	{
		# 1.需要将右窗口的数据搬移到做窗口，因为从start位置向前找的时候最远只能找MAX_DIS的距离（局部匹配原则）
		memcpy(_pWin, _pWin + WSIZE, WSIZE);
		start -= WSIZE;

		# 2.更新哈希表
		# 刚才在搬移的过程中，将右窗的数据搬移到了左窗，查找缓冲区中的字节的下标发生了变化，而哈希表中存储的就是查找缓冲区
		# 中三个字节一组首字节在窗口中的下标，既然下标发生了变化，必须要更新哈希表

		_ht.UpdataTable();

		# 3.往右窗中填充WSIZE的数据
		if (!feof(fIn))
		{
			lookahead += fread(_pWin + WSIZE, 1, WSIZE, fIn);
		}

	}
}

# 直接以二进制格式打开文件
FILE* fIn = fopen(fileName.c_str(), "rb");
# 计算文件的大小
fseek(fIn, 0, SEEK_END);
ull fileSize = ftell(fIn);
fseek(fIn, 0, SEEK_SET);
if (fileSize <= MIN_MATCH)
{
    # 文件大小小于3，关闭文件
}
# 向窗口中读取数据
ull lookhead = fread(_pWin, 1, 2 * WSIZE, fIn);
# 需要先将前两个字节读入hashTable
for (uch i = 0; i < MIN_MATCH - 1; i++)
{
	_ht.InsertString(hashAddr, _pWin[i], i, matchHead);
}
while (lookhead)
	{
		# 将要查找的字串插入hashTable中，找距离最近的一个匹配串，通过出参带出来
_ht.InsertString(hashAddr, _pWin[start + 2], start, matchHead);
		# 查找缓冲区中存在匹配的字符串
		if (matchHead != 0)
		{
            # 在查找缓冲区中找到了匹配的字符串
			# 找最长匹配
		}
		if (matchLength < MIN_MATCH)
		{
			# 没有找到符合条件的匹配串（匹配长度大于等于3的字符串 ）
			# 将原字符串直接写入压缩文件中
		}
		else
		{
			# 找到了匹配
			# 将长度和距离写入压缩文件
			# 这里需要将匹配上的那部分字符串也放入哈希表中
		}
		if (lookhead <= MIN_LOOKAHEAD)
		{
			# 向窗口中填充数据
		}
	}
# 额外处理最后剩余的不足8bit的字节
	if (bitCount > 0 && bitCount < 8){}
}