from extractors.item_extractor import ItemExtractor
from extract import handle_entity, handle_tile, handle_item
from extractor_pass import ExtractorPass
from dictionary import Dictionary
from settings import Settings

from collections import defaultdict

from amulet.api.block_entity import BlockEntity
from amulet.api.entity import Entity
from amulet_nbt import NamedTag, CompoundTag, StringTag

class GeneralItemExtractor(ItemExtractor):
    extractor_name = 'item'
    match_items = ('.*',)
    data_version_range = (819, 6666)

    def __init__(self, settings: Settings) -> None:
        self.indexes = defaultdict(lambda: 1)
        self.entity_extractors = [x(settings) for x in settings.extractors[ExtractorPass.ENTITY]]
        self.tile_extractors = [x(settings) for x in settings.extractors[ExtractorPass.TILE]]
        self.item_extractors = [x(settings) for x in settings.extractors[ExtractorPass.ITEM]]

    def extract(self, dictionary: Dictionary, item: NamedTag) -> int:
        if 'components' not in item:
            return 0

        count = 0
        namespace, base_name = str(item['id']).split(':')

        if 'minecraft:custom_name' in item['components']:
            item['components']['minecraft:custom_name'], n = dictionary.replace_component(item['components']['minecraft:custom_name'], f'item.{base_name}.{self.indexes[base_name]}.name')
            count += n

        if 'minecraft:item_name' in item['components']:
            item['components']['minecraft:item_name'], n = dictionary.replace_component(item['components']['minecraft:item_name'], f'item.{base_name}.{self.indexes[base_name]}.item_name')
            count += n

        if 'minecraft:lore' in item['components']:
            for line in range(len(item['components']['minecraft:lore'])):
                lore_entry = item['components']['minecraft:lore'][line]
                if isinstance(lore_entry, CompoundTag) and 'text' in lore_entry:
                    new_text, n = dictionary.replace_component(lore_entry['text'], f'item.{base_name}.{self.indexes[base_name]}.lore.line{line}')
                    item['components']['minecraft:lore'][line] = CompoundTag({'text': StringTag(new_text)})
                    count += n

        if count:
            self.indexes[base_name] += 1

        if 'minecraft:block_entity_data' in item['components']:
            namespace, base_name = str(item['components']['minecraft:block_entity_data']['id']).split(':')
            tile = BlockEntity(namespace, base_name, 0, 0, 0, item['components']['minecraft:block_entity_data'])
            count += handle_tile(tile, dictionary, self.tile_extractors)

        if 'minecraft:container' in item['components']:
            for container_item in item['components']['minecraft:container']:
                inner_item = container_item['item']
                count += handle_item(inner_item, dictionary, self.item_extractors)

        if 'minecraft:entity_data' in item['components']:
            namespace, base_name = str(item['components']['minecraft:entity_data']['id']).split(':')
            entity = Entity(namespace, base_name, 0.0, 0.0, 0.0, item['components']['minecraft:entity_data'])
            count += handle_entity(entity, dictionary, self.entity_extractors)

        return count

extractor = GeneralItemExtractor