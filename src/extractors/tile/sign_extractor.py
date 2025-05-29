from extractors.tile_extractor import TileExtractor
from dictionary import Dictionary
from settings import Settings

import itertools as it

from amulet.api.block_entity import BlockEntity


class SignExtractor(TileExtractor):
    extractor_name = "sign"
    match_tiles = ("sign", "hanging_sign")
    data_version_range = (3463, 6666)

    def __init__(self, settings: Settings) -> None:
        self.index = 1

    def extract(self, dictionary: Dictionary, tile: BlockEntity) -> int:
        count = 0
        from amulet_nbt import StringTag, CompoundTag, ListTag, ByteTag

        for side in ("front_text", "back_text"):
            if side not in tile.nbt:
                continue

            side_data = tile.nbt[side]
            if not isinstance(side_data, CompoundTag):
                continue

            messages = side_data.get("messages")
            if messages is None:
                continue

            # Handle new format with proper ListTag structure
            if isinstance(messages, ListTag):
                # Create new ListTag with correct data type (type 8)
                new_messages = ListTag(list_data_type=8)
                changed = False

                for line in range(4):
                    if line < len(messages):
                        message_data = messages[line]
                        if isinstance(message_data, CompoundTag):
                            old_text = str(
                                message_data.get("text", StringTag("")).value
                            )
                        else:
                            old_text = str(message_data)
                    else:
                        old_text = ""

                    new_text, n = dictionary.replace_component(
                        old_text, f"sign.{self.index}.{side}.{line}"
                    )

                    # Create new message entry with preserved properties
                    new_entry = CompoundTag()
                    if line < len(messages) and isinstance(messages[line], CompoundTag):
                        # Copy existing properties
                        for k, v in messages[line].items():
                            new_entry[k] = v

                    # Set text and default properties
                    new_entry["text"] = StringTag(new_text)
                    new_entry.setdefault("color", StringTag("black"))
                    new_entry.setdefault("has_glowing_text", ByteTag(0))

                    new_messages.append(new_entry)
                    if n > 0:
                        changed = True
                        count += n

                if changed:
                    side_data["messages"] = new_messages

            # Handle old format direct string messages
            elif isinstance(messages, (str, StringTag)):
                for line in range(4):
                    if line >= len(messages):
                        continue

                    old_text = str(messages[line])
                    new_text, n = dictionary.replace_component(
                        old_text, f"sign.{self.index}.{side}.{line}"
                    )
                    if n > 0:
                        messages[line] = new_text
                        count += n

        if count:
            self.index += 1
        return count


extractor = SignExtractor
