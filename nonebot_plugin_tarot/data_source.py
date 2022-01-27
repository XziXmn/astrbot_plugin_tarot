from random import sample, shuffle
from pathlib import Path 
import os
import nonebot

_TAROT_PATH = nonebot.get_driver().config.tarot_path
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "resource")
TAROT_PATH = DEFAULT_PATH if not _TAROT_PATH else _TAROT_PATH

class Cards() :
    def __init__(self, num: int):
        '''
            为了模拟抽牌过程，所以会将卡组打乱，然后从小到大进行抽牌
            所以稍微牺牲点性能没问题的对吧！
        '''
        names = list(cards.keys())
        shuffle(names)
        self.selected = [names[card_id] for card_id in sample(range(0,78), num)]
        self.showed = 0

    # 揭示牌（玄学当然要有仪式感！）
    def reveal(self):
        card_key = self.selected[self.showed]               # 牌名
        card_meaning = cards[card_key]                      # 含义
        image_file = Path(TAROT_PATH) / (card_key + ".jpg") # 图片路径
        self.showed += 1
        return card_key, card_meaning, image_file


#不是最终版本。从愚者开始是改过的含义。前边的之后会改。——lolifish
cards = {
    "圣杯1": "家庭生活之幸福，别的牌可给予其更多内涵，如宾客来访、宴席、吵架",
    "圣杯10": "家庭幸福，预料之外的好消息",
    "圣杯2": "成功和好运，但细心、专心会是获取它们的必要条件",
    "圣杯3": "切忌轻率、鲁莽，它们会给事业带来厄运",
    "圣杯4": "不易说服的人，未婚的男子或女子，婚姻推迟",
    "圣杯5": "无根据的嫉妒，缺乏果断误了大事，且逃避责任",
    "圣杯6": "轻信，你容易被欺骗，特别是被不值得信任的同伴欺骗",
    "圣杯7": "善变或食言，提防过分乐观的朋友和无主见的熟人",
    "圣杯8": "令人愉快的公司或友谊，聚合或有计划的庆祝活动",
    "圣杯9": "梦里与愿望实现，好运与财富",
    "圣杯侍者": "一个永远的亲密朋友，或许是分别很久的童年朋友或初恋情人",
    "圣杯国王": "诚实、善良的男子，但容易草率地做出决定，并不可依赖",
    "圣杯王后": "忠诚、钟情的女人，温柔大方，惹人怜爱",
    "圣杯骑士": "假朋友，来自远方陌生的人，勾引者，应当把握当前命运",
    "宝剑1": "不幸，坏消息，充满嫉妒的情感",
    "宝剑10": "悲伤，否定好兆头",
    "宝剑2": "变化，分离",
    "宝剑3": "一次旅行，爱情或婚姻的不幸",
    "宝剑4": "疾病，经济困难，嫉妒，各种小灾难拖延工作的进度",
    "宝剑5": "克服困难，获得生意成功或者和谐的伙伴",
    "宝剑6": "只要有坚韧不拔的毅力，就能完成计划",
    "宝剑7": "与朋友争吵，招来许多麻烦",
    "宝剑8": "谨慎，看似朋友的人可能成为敌人",
    "宝剑9": "疾病、灾难、或各种不幸",
    "宝剑侍者": "嫉妒或者懒惰的人，事业上的障碍，或许是骗子",
    "宝剑国王": "野心勃勃、妄想驾驭一切",
    "宝剑王后": "奸诈，不忠，一个寡妇或被抛弃的人",
    "宝剑骑士": "传奇中的豪爽人物，喜好奢侈放纵，但勇敢、有创业精神",
    "权杖1": "财富与事业的成功，终生的朋友和宁静的心境",
    "权杖10": "意想不到的好运，长途旅行，但可能会失去一个亲密的朋友",
    "权杖2": "失望，来自朋友或生意伙伴的反对",
    "权杖3": "不止一次的婚姻",
    "权杖4": "谨防一个项目的失败，虚假或不可靠的朋友起到了破坏作用",
    "权杖5": "娶一个富婆",
    "权杖6": "有利可图的合伙",
    "权杖7": "好运与幸福，但应提防某个异性",
    "权杖8": "贪婪，可能花掉不属于自己的钱",
    "权杖9": "和朋友争辩，固执的争吵",
    "权杖侍者": "一个诚挚但缺乏耐心的朋友，善意的奉承",
    "权杖国王": "一个诚挚的男人，慷慨忠实",
    "权杖王后": "一个亲切善良的人，但爱发脾气",
    "权杖骑士": "幸运地得到亲人或陌生人的帮助",
    "钱币1": "重要的消息，或珍贵的礼物",
    "钱币10": "把钱作为目标，但并不一定会如愿以偿",
    "钱币2": "热恋，但会遭到朋友反对",
    "钱币3": "争吵，官司，或家庭纠纷",
    "钱币4": "不幸或秘密的背叛，来自不忠的朋友，或家庭纠纷",
    "钱币5": "意外的消息，生意成功、愿望实现、或美满的婚姻",
    "钱币6": "早婚，但也会早早结束，第二次婚姻也无好兆头",
    "钱币7": "谎言，谣言，恶意的批评，运气糟透的赌徒",
    "钱币8": "晚年婚姻，或一次旅行，可能带来结合",
    "钱币9": "强烈的旅行愿望，嗜好冒险，渴望生命得到改变",
    "钱币侍者": "一个自私、嫉妒的亲戚，或一个带来坏消息的使者",
    "钱币国王": "一个脾气粗暴的男人，固执而充满复仇心，与他对抗会招来危险",
    "钱币王后": "卖弄风情的女人，乐于干涉别人的事情，诽谤和谣言",
    "钱币骑士": "一个有耐心、有恒心的男人，发明家或科学家",
    "愚者": "旅行：希望寻求未来的机会，但缺乏明确的具体计划。没有顾虑反而会给你带来意想不到的成功。然而没有远见，容易产生动摇，当遇到太多障碍的时候往往会失去原有的目标。",
    "魔术师": "创造：渐渐地，创造性的方式会在你面前展开，从而帮助你快速获得成功。",
    "女教皇": " 智慧：正确使用智慧，通常会做出很好的判断。但一些领域需要更高的远见。某些未知的变化可能是您最不期望的。",
    "女皇": "丰收：它表示强大，充满活力和智慧的本性。花更多的时间理解自然，培养一种宽容的态度，理解别人的问题。反思他人的爱，并在执行职责时释出善意。",
    "皇帝": "支配：明智，稳定和保护，为身边的人提供指导。坚持计划，以有组织的方式执行它们。",
    "教皇": "援助：希望保守而不是创新。从明智的导师那里寻求智慧和知识，以获得更高的意识。",
    "恋人": "结合：在相互信任和吸引力的基础上分享强大而亲密的联系。在选择方向前深入分析感受，动机以及可用选项。",
    "战车": "胜利：适当地运用意志力，信心和纪律，能够克服反对意见。大胆，但要控制冲动，把它们引导到更有创意的事情上。",
    "力量": "意志：相信自己，用温和的行为和成熟来控制不愉快的情况。忽略不完美之处，并为其他人提供改进空间。实现内在优势，放下目前的负面情绪",
    "隐士": "寻求：当前的时机适合寻找生活中的最终目标并努力实现目标。有限的物质欲望可以帮助你关注重要方面，并提出可行的解决方案。你可以引导他人到达正确的目的地。不要过于习于孤独。",
    "命运之轮": "轮转：积极的变化即将来临。自信随和将帮助您在不降低自尊的情况下度过生活的起伏。更专注于自己的意图，保持乐观将带来繁荣和幸福。最重要的是，善行会带来预期的结果。然而，不要自满，因为宇宙中没有东西是永恒的。",
    "正义": "均衡：对自己的行为负责并做出相应判断。生活中的事件会以平衡的方式解决。",
    "吊人": "牺牲：采取一些旧的信念、态度或友谊。学会承担责任。然而这并不意味着你会责怪自己并阻止你继续前进。",
    "死神": "结束：象征着生命中重要方面的终结，但这反过来可能会带来更有价值的东西。它代表着无敌，纯洁，勇敢，牺牲和实现。",
    "节制": "净化：避免极端，并试着保持温和的生活，采用中间道路来实现和谐。耐心评估当前情况，然后根据面临的任何新情况进行调整。",
    "恶魔": "诅咒：绝望或痴迷，对生活抱有悲观的看法，处于无益的阶段。摆脱负面模式，为生活带来积极的变化、了解真相。",
    "高塔": "毁灭：象征着意想不到的变化，导致无法预料的事件。试着质疑自己的看法，以便发现问题所在。",
    "星星": "希望：处于一个充满活力，精神稳定，冷静和对自己更深刻理解的积极阶段。经历的艰难挑战正帮助您进行彻底的转型并拥抱新的机遇、从新的角度看待生活。",
    "月亮": "不安：一切似乎都很正常，但却感到怀疑。难以专注于生活中的重要事情。仅仅根据事实与内在的自我联系并理解现实。",
    "太阳": "生命：积极的能量将帮助你获得完成某事的快乐。通过自信，热情和辛劳，能够体验到一种充实与快乐。过上简单的生活，以充分享受自由和启蒙的果实。",
    "审判": "复活：审判是更新，知识和更高思想的象征。根据自己的直觉和智慧做出决定，它们将在未来的日子里带来重大变化。",
    "世界": "达成：世界象征着完成旅程的快乐，也是体验生活其他方面的新开端。坚如磐石，勇敢面对任何局面，不会崩溃。利用知识和经验，通过教育或社会工作向世界回馈一些东西。"
}

meanings = {
    "第一张牌": "代表过去，即已经发生的事",
    "第二张牌": "代表问题导致的局面",
    "第三张牌": "表示困难可能有的解决方法",
    "切牌": "表示问卜者的主观想法",
}
