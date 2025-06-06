from extractors.entity_extractor import EntityExtractor
from extractor_pass import ExtractorPass
from dictionary import Dictionary
from extract import handle_item
from settings import Settings

from amulet.api.entity import Entity

class VillagerExtractor(EntityExtractor):
    extractor_name = 'villager'
    match_entities = ('villager', 'zombie_villager', 'wandering_trader')
    data_version_range = (1952, 5000)

    def __init__(self, settings: Settings) -> None:
        self.item_extractors = [x(settings) for x in settings.extractors[ExtractorPass.ITEM]]

    def extract(self, dictionary: Dictionary, entity: Entity) -> int:
        count = 0

        if 'Offers' in entity.nbt:
            for offer in entity.nbt['Offers']['Recipes']:
                if 'buy' in offer:
                    count += handle_item(offer['buy'], dictionary, self.item_extractors)
                if 'buyB' in offer:
                    count += handle_item(offer['buyB'], dictionary, self.item_extractors)
                if 'sell' in offer:
                    count += handle_item(offer['sell'], dictionary, self.item_extractors)

        return count

extractor = VillagerExtractor
