from extractors.data_file_extractor import DataFileExtractor
from dictionary import Dictionary
import logging

from amulet_nbt import NamedTag, CompoundTag, ListTag, StringTag

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageExtractor(DataFileExtractor):
    extractor_name = 'storage'
    match_filenames = (r'command_storage_.*\.dat',)
    data_version_range = (1, 5000)

    def extract(self, dictionary: Dictionary, data: NamedTag) -> int:
        count = 0

        # 检查 data 和 contents 是否存在且为 CompoundTag
        if 'data' not in data or not isinstance(data['data'], CompoundTag):
            logger.warning("无效的数据结构：'data' 标签缺失或不是 CompoundTag")
            return 0
        if 'contents' not in data['data'] or not isinstance(data['data']['contents'], CompoundTag):
            logger.warning("无效的数据结构：'contents' 标签缺失或不是 CompoundTag")
            return 0

        for storage_name in data['data']['contents']:
            stack = [data['data']['contents'][storage_name]]
            while stack:
                tag = stack.pop()
                if isinstance(tag, CompoundTag):
                    for name in tag:
                        if isinstance(tag[name], StringTag):
                            s, n = dictionary.replace_other(str(tag[name]), f'storage.{storage_name}')
                            tag[name] = StringTag(s)
                            count += n
                            continue
                        stack.append(tag[name])
                    continue
                if isinstance(tag, ListTag):
                    for i in range(len(tag)):
                        if isinstance(tag[i], StringTag):
                            s, n = dictionary.replace_other(str(tag[i]), f'storage.{storage_name}')
                            tag[i] = StringTag(s)
                            count += n
                            continue
                        stack.append(tag[i])

        return count

extractor = StorageExtractor