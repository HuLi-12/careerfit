from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent / 'data'
SCORE_WEIGHTS = {
    'core_skill_match': 30,
    'project_experience_match': 25,
    'responsibility_match': 20,
    'resume_expression_quality': 15,
    'risk_control': 10,
}
MATCH_SCORE = {'strong': 1.0, 'medium': 0.7, 'weak': 0.4, 'none': 0.0}
RECOMMENDATION_LEVELS = [
    (85, '强匹配，建议优先投递或优先面试'),
    (70, '较匹配，建议优化后投递或进入初面'),
    (55, '弱匹配，需要明显补强'),
    (0, '不建议直接投递或暂不推荐进入面试'),
]
