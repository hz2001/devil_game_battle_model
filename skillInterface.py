from termcolor import colored

class skillInterface:
    '''
    技能接口
    '''
    def __init__(self,
                 skillName: str = "",
                 cd: float = 0,
                 type:str = "passive",
                 description:str = "",
                 castRange: float = 100) -> None:
        '''
        attributes for skills are:
            cool down, effects: varies among skills , type: passive/active
        '''
        self.skillName = skillName
        self.cd = cd
        self.type = type
        self.description = description
        self.castRange = castRange
    def cast(self, currentTime, caster, target):
        '''
        parameter： currentTime, caster, opponent
        placeholder， 每一个技能都需要不同的实现'''
        return
    def __repr__(self) -> str:
        return f"*{colored(self.skillName,'green')}*"


