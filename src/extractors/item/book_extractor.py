from extractors.item_extractor import ItemExtractor
from dictionary import Dictionary
from settings import Settings
from amulet_nbt import NamedTag, StringTag, CompoundTag, ListTag
import json

class BookExtractor(ItemExtractor):
    extractor_name = 'book'
    match_items = ('written_book',)
    data_version_range = (222, 5000)

    def __init__(self, settings: Settings) -> None:
        self.index = 1

    def extract(self, dictionary: Dictionary, item: NamedTag) -> int:
        if 'components' not in item or 'minecraft:written_book_content' not in item['components']:
            return 0

        count = 0
        book_content = item['components']['minecraft:written_book_content']

        # 处理页面
        if 'pages' in book_content:
            for page_idx, page in enumerate(book_content['pages']):
                if 'raw' not in page:
                    continue

                raw = page['raw']
                # 如果 raw 是字符串，直接替换
                if isinstance(raw, StringTag):
                    raw, n = dictionary.replace_component(raw, f'book.{self.index}.content.page{page_idx}')
                    page['raw'] = raw
                    count += n
                # 如果 raw 是复杂对象，递归处理 text 和 extra
                elif isinstance(raw, (CompoundTag, dict)):
                    # 处理 text 字段
                    if 'text' in raw:
                        text_key = f'book.{self.index}.content.page{page_idx}.text'
                        text, n = dictionary.replace_other(str(raw['text']), text_key)
                        raw['text'] = StringTag(text)
                        count += n

                    # 处理 extra 字段
                    if 'extra' in raw and isinstance(raw['extra'], ListTag):
                        for i, extra_item in enumerate(raw['extra']):
                            if 'text' in extra_item:
                                extra_key = f'book.{self.index}.content.page{page_idx}.extra{i}'
                                text, n = dictionary.replace_other(str(extra_item['text']), extra_key)
                                extra_item['text'] = StringTag(text)
                                count += n

        # 处理标题
        if 'title' in book_content and 'minecraft:custom_name' not in item['components']:
            title = book_content['title']
            if isinstance(title, CompoundTag) and 'raw' in title and title['raw']:
                key = dictionary.add_entry(str(title['raw']), f'book.{self.index}.title')
                item['components']['minecraft:custom_name'] = StringTag(f'{{"translate":"{key}","italic":false}}')
                count += 1

        if count:
            self.index += 1
        return count

extractor = BookExtractor