from extractors.data_file_extractor import DataFileExtractor
from dictionary import Dictionary

from amulet_nbt import NamedTag

class ScoreExtractor(DataFileExtractor):
    extractor_name = 'score'
    match_filenames = (r'scoreboard\.dat',)
    data_version_range = (1, 5000)

    def extract(self, dictionary: Dictionary, data: NamedTag) -> int:
        count = 0

        # 处理 Objectives
        for score in data['data']['Objectives']:
            score['DisplayName'], n = dictionary.replace_component(score['DisplayName'], f'score.{score["Name"]}.name')
            count += n

        # 处理 Teams
        for team in data['data']['Teams']:
            # 处理 DisplayName
            team['DisplayName'], n = dictionary.replace_component(team['DisplayName'], f'team.{team["Name"]}.name')
            count += n

            # 处理 MemberNamePrefix（如果存在）
            if 'MemberNamePrefix' in team:
                team['MemberNamePrefix'], m = dictionary.replace_component(team['MemberNamePrefix'], f'team.{team["Name"]}.prefix')
                count += m
            else:
                m = 0

            # 处理 MemberNameSuffix（如果存在）
            if 'MemberNameSuffix' in team:
                team['MemberNameSuffix'], l = dictionary.replace_component(team['MemberNameSuffix'], f'team.{team["Name"]}.suffix')
                count += l
            else:
                l = 0

        return count

extractor = ScoreExtractor