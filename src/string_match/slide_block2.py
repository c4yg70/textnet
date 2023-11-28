void LdZip::CompressBlock()
{
	# 0.清空前一个块的数据信息
	ClearPrevStatInfo();
	# 1.统计字符出现的个数
	StatAppearCount();
	# 2.构建Huffman树
	huffmanTree<ByteLengthInfo>byteLengthTree(_byteLengthInfo, ByteLengthInfo());
	huffmanTree<ByteLengthInfo>distTree(_distInfo, ByteLengthInfo());
	# 3.获取编码位长：将每个叶子节点高度
	# 4.生成Huffman编码：按照编码位长为第一字段，然后以字节大小为第二字段进行排序
	# 获取原字符和长度对应huffman中编码位长以及具体编码
	GetCodeLen(byteLengthTree.GetRoot(), _byteLengthInfo);
	GenerateHuffmanCode(_byteLengthInfo);
	# 获取距离对应huffman中编码位长以及具体编码
	GetCodeLen(distTree.GetRoot(), _distInfo);
	GenerateHuffmanCode(_distInfo);
	# 5.写解压缩时需要用到的信息----写编码位长
	WriteInfo(fOut);
	# 6.压缩
	uch bitInfo = 0;
	uch bitCount = 0;
	size_t flagIdx = 0;
	size_t distIdx = 0;
	uch CompressByteInfo = 0;
	uch CompressByteCount = 0;
	for (size_t i = 0; i < _byteLengthLz77.size(); i++)
	{
		if (0 == bitCount)
		{
			bitInfo = _flagLz77[flagIdx++];
			bitCount = 8;
		}
		if (bitInfo & 0x80)
		{
			# _byteLengthLz77[i]是长度
			# 压缩一个长度距离对
			CompressLengthDist(_byteLengthLz77[i], _distLz77[distIdx++], CompressByteInfo, CompressByteCount);
		}
		else
		{
			# _byteLengthLz77[i]是原字符
			# 压缩一个原字符
			CompressByte(_byteLengthLz77[i], CompressByteInfo, CompressByteCount);
		}

		bitInfo <<= 1;
		bitCount -= 1;
	}
	# 压缩一个256表示块结束
	CompressByte(256, CompressByteInfo, CompressByteCount);
	if (CompressByteCount > 0 && CompressByteCount < 8)
	{
		CompressByteInfo <<= (8 - CompressByteCount);
		fputc(CompressByteInfo, fOut);
	}
	# 将前一次Lz77的结果清空
	_byteLengthLz77.clear();
	_distLz77.clear();
	_flagLz77.clear();
}