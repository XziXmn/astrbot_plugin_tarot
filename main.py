import asyncio
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple

import PIL.Image
from PIL import UnidentifiedImageError

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image, Node, Nodes, Plain
from astrbot.api.star import Context, Star, register


class Tarot:
    def __init__(self, context: Context, config: AstrBotConfig):
        self.context = context
        self.tarot_json: Path = Path(__file__).parent / "tarot.json"
        resource_path_str: str = config.get("resource_path", "./resources")
        self.resource_path: Path = Path(__file__).parent / resource_path_str
        self.is_chain_reply: bool = config.get("chain_reply", True)
        self.include_ai_in_chain: bool = config.get("include_ai_in_chain", True)

        os.makedirs(self.resource_path, exist_ok=True)
        if not self.tarot_json.exists():
            logger.error("tarot.json 文件缺失，请确保资源完整！")
            raise FileNotFoundError("tarot.json 文件缺失，请确保资源完整！")
        logger.info(
            f"Tarot 插件初始化完成，资源路径: {self.resource_path}, "
            f"AI 解析加入转发: {self.include_ai_in_chain}"
        )

    def pick_theme(self) -> str:
        sub_themes_dir: List[str] = [
            f.name for f in self.resource_path.iterdir() if f.is_dir()
        ]
        if not sub_themes_dir:
            logger.error("本地塔罗牌主题为空，请检查资源目录！")
            raise FileNotFoundError("本地塔罗牌主题为空，请检查资源目录！")
        return random.choice(sub_themes_dir)

    def pick_sub_types(self, theme: str) -> List[str]:
        all_sub_types: List[str] = ["MajorArcana", "Cups", "Pentacles", "Swords", "Wands"]
        sub_types: List[str] = [
            f.name
            for f in (self.resource_path / theme).iterdir()
            if f.is_dir() and f.name in all_sub_types
        ]
        return sub_types or all_sub_types

    def _random_cards(self, all_cards: Dict, theme: str, num: int = 1) -> List[Dict]:
        sub_types: List[str] = self.pick_sub_types(theme)
        if not sub_types:
            logger.error(f"主题 {theme} 下无可用子类型！")
            raise ValueError(f"主题 {theme} 下无可用子类型！")
        subset: Dict = {k: v for k, v in all_cards.items() if v.get("type") in sub_types}
        if len(subset) < num:
            logger.error(
                f"主题 {theme} 的牌数量不足，需要 {num} 张，实际 {len(subset)} 张！"
            )
            raise ValueError(f"主题 {theme} 的牌数量不足！")
        cards_index: List[str] = random.sample(list(subset), num)
        return [v for k, v in subset.items() if k in cards_index]

    @staticmethod
    def _validate_formation(formation: Dict, formation_name: str) -> List[str]:
        """校验牌阵配置并返回可用的 representaions 列表。"""
        cards_num: int = formation.get("cards_num", 0)
        representations_pool = formation.get("representations", [])
        if not representations_pool:
            logger.error(f"牌阵 {formation_name} 缺少 representaions 配置")
            raise ValueError(f"牌阵 {formation_name} 配置异常，缺少 representaions")

        representations = random.choice(representations_pool)
        if len(representations) < cards_num:
            logger.error(
                f"牌阵 {formation_name} 的 representaions 长度 ({len(representations)}) "
                f"小于 cards_num ({cards_num})"
            )
            raise ValueError(f"牌阵 {formation_name} 配置异常，解读位置数量不足")
        return representations

    async def _get_text_and_image(
        self, theme: str, card_info: Dict
    ) -> Tuple[bool, str, str, bool]:
        _type: str = card_info.get("type")
        _name: str = card_info.get("pic")
        img_dir: Path = self.resource_path / theme / _type

        try:
            img_path = next(img_dir.glob(_name + ".*"))
        except StopIteration:
            logger.warning(f"图片 {theme}/{_type}/{_name} 不存在！")
            return (
                False,
                f"图片 {theme}/{_type}/{_name} 不存在，请检查资源完整性！",
                "",
                True,
            )

        try:
            with PIL.Image.open(img_path) as img:
                name_cn: str = card_info.get("name_cn")
                meaning = card_info.get("meaning")
                is_upright = random.random() < 0.5
                text = (
                    f"「{name_cn}{'正位' if is_upright else '逆位'}」"
                    f"「{meaning['up' if is_upright else 'down']}」\n"
                )
                if not is_upright:
                    rotated_img_name = f"{_name}_rotated.png"
                    rotated_img_path = img_dir / rotated_img_name
                    if not rotated_img_path.exists():
                        img = img.rotate(180)
                        img.save(rotated_img_path, format="png")
                        logger.info(f"保存旋转后的图片: {rotated_img_path}")
                    else:
                        logger.info(f"使用已存在的旋转图片: {rotated_img_path}")
                    final_path = str(rotated_img_path.resolve())
                else:
                    final_path = str(img_path.resolve())

                if not os.path.exists(final_path):
                    logger.error(f"图片文件不存在: {final_path}")
                    return False, f"图片文件 {final_path} 不存在！", "", True
                logger.info(f"使用图片路径: {final_path}")
                return True, text, final_path, is_upright
        except UnidentifiedImageError as e:
            logger.error(f"无法识别图片文件 {img_path}: {e}")
            return False, f"无法识别图片文件 {img_path}，请检查资源格式！", "", True
        except OSError as e:
            logger.error(f"读取图片文件失败 {img_path}: {e}")
            return False, f"读取塔罗牌图片失败: {e}", "", True

    async def _call_llm(
        self,
        event: AstrMessageEvent,
        prompt: str,
        system_prompt: str,
    ) -> str:
        """兼容新旧版本 AstrBot 的 LLM 调用封装。"""
        # 优先使用 v4.5.7+ 推荐的统一接口
        if hasattr(self.context, "llm_generate") and hasattr(
            self.context, "get_current_chat_provider_id"
        ):
            try:
                provider_id = await self.context.get_current_chat_provider_id(
                    umo=event.unified_msg_origin
                )
                llm_resp = await self.context.llm_generate(
                    chat_provider_id=provider_id,
                    prompt=prompt,
                    system_prompt=system_prompt,
                )
                return llm_resp.completion_text.strip()
            except Exception as e:
                logger.warning(f"llm_generate 调用失败，尝试回退到 text_chat: {e}")

        # 回退到旧版 Provider.text_chat 接口
        prov = self.context.get_using_provider(umo=event.unified_msg_origin)
        if not prov:
            raise RuntimeError("未找到可用的 LLM 提供商")

        llm_resp = await prov.text_chat(
            prompt=prompt,
            system_prompt=system_prompt,
        )
        return llm_resp.completion_text.strip()

    async def _match_formation(
        self, text: str, all_formations: Dict, event: AstrMessageEvent
    ) -> str:
        text = text.strip().lower()
        formation_names = list(all_formations.keys())
        keywords = [
            "情感",
            "爱情",
            "关系",
            "事业",
            "工作",
            "未来",
            "过去",
            "现状",
            "处境",
            "挑战",
            "建议",
        ]
        for formation in formation_names:
            for keyword in keywords:
                representations_pool = all_formations[formation].get("representations", [])
                if not representations_pool:
                    continue
                if keyword in text and keyword in " ".join(
                    representations_pool[0]
                ).lower():
                    logger.info(f"模糊匹配成功：用户输入 '{text}' 匹配到牌阵 '{formation}'")
                    return formation

        prompt = (
            f"用户输入了以下占卜指令：'{text}'。请根据输入内容，从以下牌阵中选择一个最匹配的牌阵"
            f"并返回其名称（仅返回名称，无需解释）：\n{', '.join(formation_names)}\n"
            f"如果无法明确匹配，返回 '随机选择'。"
        )
        try:
            matched_formation = await self._call_llm(
                event,
                prompt=prompt,
                system_prompt="你是一个塔罗牌专家，擅长根据用户意图选择合适的牌阵。",
            )
            if matched_formation == "随机选择" or matched_formation not in formation_names:
                logger.info(f"AI 匹配失败或返回随机选择，用户输入: '{text}'")
                return random.choice(formation_names)
            logger.info(f"AI 匹配成功：用户输入 '{text}' 匹配到牌阵 '{matched_formation}'")
            return matched_formation
        except Exception as e:
            logger.error(f"AI 匹配牌阵失败: {e}")
            return random.choice(formation_names)

    async def _generate_ai_interpretation(
        self,
        formation_name: str,
        cards_info: List[Dict],
        representations: List[str],
        is_upright_list: List[bool],
        user_input: str,
        event: AstrMessageEvent,
    ) -> str:
        prompt = (
            f"你是一位专业的塔罗牌占卜师，用户输入了以下完整占卜指令：'{user_input}'。\n"
            f"请根据以下信息为用户提供详细的占卜结果解析：\n\n"
        )
        prompt += f"牌阵：{formation_name}\n"
        prompt += "抽到的牌及位置：\n"
        for i, (card, rep, is_upright) in enumerate(
            zip(cards_info, representations, is_upright_list)
        ):
            position = f"第{i+1}张牌「{rep}」"
            card_text = (
                f"「{card['name_cn']}{'正位' if is_upright else '逆位'}」"
                f"「{card['meaning']['up' if is_upright else 'down']}」"
            )
            prompt += f"{position}: {card_text}\n"
        prompt += (
            f"\n请结合用户指令（'{user_input}'），分析牌阵的含义和每张牌的具体位置，"
            f"提供一个连贯的解析，解释这些牌可能对用户的生活、情感或决策的启示。"
            f"回答需简洁但有深度，约200-300字，重点突出用户输入的主题（如{user_input}）。"
            f"同时请确保解析结果整洁、可阅读性强，善用换行与颜表情（如😊、✨、🌟等）进行美化。"
        )
        try:
            return await self._call_llm(
                event,
                prompt=prompt,
                system_prompt="你是一个专业的塔罗牌占卜师，擅长提供深入且简洁的解析。",
            )
        except Exception as e:
            logger.error(f"生成 AI 解析失败: {e}")
            return "抱歉，AI 解析生成失败，请稍后再试。"

    async def divine(self, event: AstrMessageEvent, user_input: str = ""):
        try:
            theme: str = self.pick_theme()
            with open(self.tarot_json, "r", encoding="utf-8") as f:
                content = json.load(f)
                all_cards = content.get("cards")
                all_formations = content.get("formations")
                formation_name = await self._match_formation(
                    user_input, all_formations, event
                )
                formation = all_formations.get(formation_name)

            yield event.plain_result(f"启用{formation_name}，正在洗牌中...")

            cards_num: int = formation.get("cards_num")
            cards_info_list = self._random_cards(all_cards, theme, cards_num)
            is_cut: bool = formation.get("is_cut")
            representations: List[str] = self._validate_formation(formation, formation_name)

            is_upright_list = []
            results = []
            group_id = event.get_group_id()
            is_group_chat = group_id is not None

            bot_name = self.context.get_config().get("nickname", "占卜师")

            if self.is_chain_reply and is_group_chat:
                chain = Nodes([])
                for i in range(cards_num):
                    header = (
                        f"切牌「{representations[i]}」\n"
                        if (is_cut and i == cards_num - 1)
                        else f"第{i+1}张牌「{representations[i]}」\n"
                    )
                    flag, text, img_path, is_upright = await self._get_text_and_image(
                        theme, cards_info_list[i]
                    )
                    if not flag:
                        yield event.plain_result(text)
                        return
                    is_upright_list.append(is_upright)
                    node = Node(
                        uin=event.get_self_id(),
                        name=bot_name,
                        content=[Plain(header + text), Image.fromFileSystem(img_path)],
                    )
                    chain.nodes.append(node)
                    results.append((header, text, img_path))

                interpretation = await self._generate_ai_interpretation(
                    formation_name,
                    cards_info_list,
                    representations,
                    is_upright_list,
                    user_input,
                    event,
                )
                if self.include_ai_in_chain:
                    ai_node = Node(
                        uin=event.get_self_id(),
                        name=bot_name,
                        content=[Plain(f"\n“属于你的占卜分析！”\n{interpretation}")],
                    )
                    chain.nodes.append(ai_node)
                if not chain.nodes:
                    yield event.plain_result("无法生成塔罗牌结果，请稍后重试")
                    return
                logger.info(
                    f"群聊转发发送 {len(chain.nodes)} 张塔罗牌，"
                    f"AI 解析是否包含: {self.include_ai_in_chain}"
                )
                yield event.chain_result([chain])
                if not self.include_ai_in_chain:
                    yield event.plain_result(f"\n“属于你的占卜分析！”\n{interpretation}")
            else:
                for i in range(cards_num):
                    header = (
                        f"切牌「{representations[i]}」\n"
                        if (is_cut and i == cards_num - 1)
                        else f"第{i+1}张牌「{representations[i]}」\n"
                    )
                    flag, text, img_path, is_upright = await self._get_text_and_image(
                        theme, cards_info_list[i]
                    )
                    if not flag:
                        yield event.plain_result(text)
                        return
                    is_upright_list.append(is_upright)
                    yield event.plain_result(header + text)
                    yield event.image_result(img_path)
                    results.append((header, text, img_path))
                    if i < cards_num - 1:
                        await asyncio.sleep(2)

                interpretation = await self._generate_ai_interpretation(
                    formation_name,
                    cards_info_list,
                    representations,
                    is_upright_list,
                    user_input,
                    event,
                )
                yield event.plain_result(f"\n“属于你的占卜分析！”\n{interpretation}")
        except FileNotFoundError as e:
            logger.error(f"资源缺失: {e}")
            yield event.plain_result(f"资源缺失: {e}")
        except ValueError as e:
            logger.error(f"配置或数据异常: {e}")
            yield event.plain_result(f"占卜配置异常: {e}")
        except Exception as e:
            logger.error(f"占卜过程出错: {e}")
            yield event.plain_result(f"占卜失败: {e}")

    async def onetime_divine(self, event: AstrMessageEvent, user_input: str = ""):
        try:
            theme: str = self.pick_theme()
            with open(self.tarot_json, "r", encoding="utf-8") as f:
                content = json.load(f)
                all_cards = content.get("cards")
                card_info_list = self._random_cards(all_cards, theme)

            group_id = event.get_group_id()
            is_group_chat = group_id is not None

            flag, text, img_path, is_upright = await self._get_text_and_image(
                theme, card_info_list[0]
            )
            if not flag:
                yield event.plain_result(text)
                return

            bot_name = self.context.get_config().get("nickname", "占卜师")
            interpretation = await self._generate_ai_interpretation(
                "单张牌占卜",
                card_info_list,
                ["当前情况"],
                [is_upright],
                user_input,
                event,
            )

            if self.is_chain_reply and is_group_chat:
                chain = Nodes([])
                node = Node(
                    uin=event.get_self_id(),
                    name=bot_name,
                    content=[Plain("回应是" + text), Image.fromFileSystem(img_path)],
                )
                chain.nodes.append(node)
                if self.include_ai_in_chain:
                    ai_node = Node(
                        uin=event.get_self_id(),
                        name=bot_name,
                        content=[Plain(f"\n“属于你的占卜分析！”\n{interpretation}")],
                    )
                    chain.nodes.append(ai_node)
                if not chain.nodes:
                    yield event.plain_result("无法生成塔罗牌结果，请稍后重试")
                    return
                logger.info(
                    f"单张占卜群聊转发发送 {len(chain.nodes)} 条消息，"
                    f"AI 解析是否包含: {self.include_ai_in_chain}"
                )
                yield event.chain_result([chain])
                if not self.include_ai_in_chain:
                    yield event.plain_result(f"\n“属于你的占卜分析！”\n{interpretation}")
            else:
                yield event.plain_result("回应是" + text)
                yield event.image_result(img_path)
                yield event.plain_result(f"\n“属于你的占卜分析！”\n{interpretation}")
        except FileNotFoundError as e:
            logger.error(f"资源缺失: {e}")
            yield event.plain_result(f"资源缺失: {e}")
        except ValueError as e:
            logger.error(f"配置或数据异常: {e}")
            yield event.plain_result(f"占卜配置异常: {e}")
        except Exception as e:
            logger.error(f"单张占卜出错: {e}")
            yield event.plain_result(f"单张占卜失败: {e}")

    def switch_chain_reply(self, new_state: bool) -> str:
        self.is_chain_reply = new_state
        logger.info(f"群聊转发模式已切换为: {new_state}")
        return "占卜群聊转发模式已开启~" if new_state else "占卜群聊转发模式已关闭~"

    @staticmethod
    def _format_history(history: List[Dict[str, str]]) -> str:
        return "\n".join(
            f"{'用户' if h['role'] == 'user' else '占卜师大姐姐'}：{h['content']}"
            for h in history
        )

    async def _generate_sister_guidance(
        self, event: AstrMessageEvent, history: List[Dict[str, str]]
    ) -> str:
        history_text = self._format_history(history)
        prompt = (
            "你是一位温柔成熟的占卜师大姐姐。用户正在向你倾诉烦恼，"
            "你希望通过轻松的对话引导用户敞开心扉。\n"
            "请根据对话历史，用温柔、亲切、带颜表情的语气回复用户，"
            "回复控制在100字以内。不要直接给出占卜结果，只是继续引导对话。\n\n"
            f"对话历史：\n{history_text}\n\n请直接回复用户。"
        )
        try:
            return await self._call_llm(
                event,
                prompt=prompt,
                system_prompt="你是温柔成熟的占卜师大姐姐，擅长倾听和引导。",
            )
        except Exception as e:
            logger.error(f"生成引导回复失败: {e}")
            return "嗯~ 可以再说得具体一些吗？😊"

    async def _summarize_conversation(
        self, event: AstrMessageEvent, history: List[Dict[str, str]]
    ) -> str:
        history_text = self._format_history(history)
        prompt = (
            "你是一位占卜师大姐姐。请根据以下与用户的对话，"
            "总结用户的烦恼、问题和期望，用于后续的塔罗牌占卜。"
            "总结控制在100字以内，保留关键信息。\n\n"
            f"对话历史：\n{history_text}\n\n请输出总结。"
        )
        try:
            return await self._call_llm(
                event,
                prompt=prompt,
                system_prompt="你是专业的占卜师大姐姐，擅长总结用户诉求。",
            )
        except Exception as e:
            logger.error(f"总结对话失败: {e}")
            return "用户有一些烦恼想要占卜"

    async def sister_divine(self, event: AstrMessageEvent):
        """占卜师大姐姐模式：持续引导对话，最后进行专属占卜。"""
        try:
            from astrbot.core.utils.session_waiter import (
                SessionController,
                session_waiter,
            )
        except ImportError as e:
            logger.error(f"当前 AstrBot 版本不支持会话控制: {e}")
            yield event.plain_result("当前 AstrBot 版本不支持占卜师大姐姐模式，请升级后重试。")
            return

        opening = (
            "🔮 欢迎来到占卜师大姐姐模式~\n"
            "我会先陪你聊聊，听听你的烦恼，聊完后再为你进行一次专属占卜。\n"
            "随时发送「开始占卜」让我抽牌，发送「退出」可结束对话。"
        )
        yield event.plain_result(opening)

        history: List[Dict[str, str]] = []
        max_rounds = 5

        @session_waiter(timeout=300, record_history_chains=False)
        async def sister_waiter(controller: SessionController, event: AstrMessageEvent):
            nonlocal history
            user_msg = event.message_str.strip()

            if user_msg == "退出":
                await event.send(event.plain_result("已退出占卜师大姐姐模式，期待下次再见~"))
                controller.stop()
                return

            should_divine = (
                user_msg == "开始占卜"
                or len([h for h in history if h["role"] == "user"]) >= max_rounds
            )

            if should_divine:
                summary = await self._summarize_conversation(event, history)
                await event.send(
                    event.plain_result(f"💫 我了解了你的情况：\n{summary}\n\n现在为你进行专属占卜...")
                )
                async for result in self.onetime_divine(event, summary):
                    await event.send(result)
                controller.stop()
                return

            history.append({"role": "user", "content": user_msg})
            guidance = await self._generate_sister_guidance(event, history)
            history.append({"role": "assistant", "content": guidance})
            await event.send(event.plain_result(guidance))
            controller.keep(timeout=300, reset_timeout=True)

        try:
            await sister_waiter(event)
        except TimeoutError:
            yield event.plain_result("占卜师大姐姐等太久啦，会话已结束~")
        except Exception as e:
            logger.error(f"占卜师大姐姐模式出错: {e}")
            yield event.plain_result(f"占卜师大姐姐模式出错: {e}")

    async def terminate(self):
        """插件卸载/停用时可选清理运行时生成的旋转图片缓存。"""
        try:
            cleaned = 0
            for theme_dir in self.resource_path.iterdir():
                if not theme_dir.is_dir():
                    continue
                for sub_dir in theme_dir.iterdir():
                    if not sub_dir.is_dir():
                        continue
                    for rotated in sub_dir.glob("*_rotated.png"):
                        try:
                            rotated.unlink()
                            cleaned += 1
                            logger.info(f"清理旋转图片缓存: {rotated}")
                        except OSError as e:
                            logger.warning(f"清理旋转图片失败 {rotated}: {e}")
            if cleaned:
                logger.info(f"共清理 {cleaned} 张旋转图片缓存")
        except Exception as e:
            logger.error(f"terminate 清理缓存失败: {e}")


HELP_TEXT = (
    "赛博塔罗牌 v0.3.0\n"
    "[占卜] 随机选取牌阵进行占卜并提供 AI 解析，可附加关键词（如 '占卜 情感'）匹配牌阵\n"
    "[塔罗牌] 得到单张塔罗牌回应及 AI 解析\n"
    "[占卜师大姐姐] 进入持续引导对话，聊完后进行专属占卜\n"
    "[开启转发 / 关闭转发] 切换群聊转发模式"
)


@register("tarot", "XziXmn", "赛博塔罗牌占卜插件", "0.3.0")
class TarotPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.tarot = Tarot(context, config)

    async def terminate(self):
        await self.tarot.terminate()

    @filter.command("占卜")
    async def divine_handler(self, event: AstrMessageEvent, text: str = ""):
        try:
            if "帮助" in text:
                yield event.plain_result(HELP_TEXT)
            else:
                async for result in self.tarot.divine(event, text):
                    yield result
            event.stop_event()
        except Exception as e:
            logger.error(f"处理占卜命令失败: {e}")
            yield event.plain_result(f"占卜命令执行失败: {e}")

    @filter.command("塔罗牌")
    async def onetime_divine_handler(self, event: AstrMessageEvent, text: str = ""):
        try:
            if "帮助" in text:
                yield event.plain_result(HELP_TEXT)
            else:
                async for result in self.tarot.onetime_divine(event, text):
                    yield result
            event.stop_event()
        except Exception as e:
            logger.error(f"处理塔罗牌命令失败: {e}")
            yield event.plain_result(f"塔罗牌命令执行失败: {e}")

    @filter.command("开启转发")
    async def enable_chain_reply(self, event: AstrMessageEvent, text: str = ""):
        try:
            msg = self.tarot.switch_chain_reply(True)
            yield event.plain_result(msg)
            event.stop_event()
        except Exception as e:
            logger.error(f"开启转发失败: {e}")
            yield event.plain_result(f"开启转发失败: {e}")

    @filter.command("关闭转发")
    async def disable_chain_reply(self, event: AstrMessageEvent, text: str = ""):
        try:
            msg = self.tarot.switch_chain_reply(False)
            yield event.plain_result(msg)
            event.stop_event()
        except Exception as e:
            logger.error(f"关闭转发失败: {e}")
            yield event.plain_result(f"关闭转发失败: {e}")

    @filter.command("占卜师大姐姐")
    async def sister_divine_handler(self, event: AstrMessageEvent, text: str = ""):
        try:
            if "帮助" in text:
                yield event.plain_result(HELP_TEXT)
            else:
                async for result in self.tarot.sister_divine(event):
                    yield result
            event.stop_event()
        except Exception as e:
            logger.error(f"占卜师大姐姐模式失败: {e}")
            yield event.plain_result(f"占卜师大姐姐模式失败: {e}")
