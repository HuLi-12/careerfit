from config import DATA_DIR
from services.utils import load_json, unique
class SkillNormalizer:
    def __init__(self): self.alias=load_json(DATA_DIR/'skill_alias_map.json', {})
    def key(self,s): return (s or '').lower().replace(' ','').replace('-','').replace('_','').strip()
    def normalize(self,s): return self.alias.get(self.key(s), (s or '').strip())
    def many(self,items): return unique([self.normalize(x) for x in items])
